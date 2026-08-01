// ============================================================
// app.js -- el "MainWindow" de la versión web.
// En Qt, esto era la clase MainWindow reaccionando a Signals.
// Aquí, es este archivo reaccionando a mensajes de WebSocket.
// ============================================================

// --- Navegación por pestañas ---
// Todo vive en un solo HTML (SPA): cambiar de pestaña solo oculta/muestra
// secciones con CSS, nunca recarga la página ni reabre el WebSocket --
// por eso los 4 módulos pueden compartir la misma conexión y el mismo
// estado en vivo sin duplicar nada.
document.querySelectorAll(".nav-tab").forEach(tabButton => {
    tabButton.addEventListener("click", () => {
        const targetTab = tabButton.dataset.tab;

        document.querySelectorAll(".nav-tab").forEach(b => b.classList.remove("active"));
        tabButton.classList.add("active");

        document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
        document.getElementById(`tab-${targetTab}`).classList.add("active");

        // Plotly necesita que le avisen "el contenedor cambió de tamaño"
        // cada vez que una gráfica pasa de oculta (display:none) a visible,
        // porque mientras estaba oculta no pudo calcular sus dimensiones reales.
        if (targetTab === "home") {
            Plotly.Plots.resize("plot-home-dyno");
            Plotly.Plots.resize("plot-pedals");
            Plotly.Plots.resize("plot-home-pista");
        }
        if (targetTab === "dyno") Plotly.Plots.resize("plot");
        if (targetTab === "pista") Plotly.Plots.resize("plot-track");
    });
});

let latestState = null;  // el último mensaje recibido del servidor
let ws = null;

// --- Conexión WebSocket con reconexión automática ---
// Si el WebSocket se cae (red inestable, el navegador lo suspende en
// segundo plano en el celular, etc.), antes se quedaba "congelado" con
// el último estado -- ahora detectamos el cierre y reconectamos solo.
function connectWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        console.log("Conectado al servidor de telemetría.");
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === "pedals") {
            updatePedalsChart(msg);
            return;  // no toca latestState ni la gráfica de dyno
        }

        if (msg.type === "track_state") {
            updateTrackChart(msg);
            return;
        }

        // Cualquier otro mensaje (o sin "type", por compatibilidad) se
        // trata como el estado completo del dyno.
        latestState = msg;
        updateUI(latestState);
    };

    ws.onclose = (event) => {
        console.log(`Conexión cerrada. code=${event.code} reason="${event.reason}" wasClean=${event.wasClean}. Reintentando en 1.5s...`);
        setTimeout(connectWebSocket, 1500);
    };

    ws.onerror = (event) => {
        console.log("WebSocket error:", event);
        ws.close();  // onclose se encarga de programar la reconexión
    };
}

connectWebSocket();

// --- Conversión de unidades (igual que redraw_plot() en Qt) ---
function convertPower(watts, unit) {
    return unit === "HP" ? watts / 745.7 : watts / 1000;
}

function convertTorque(nm, unit) {
    return unit === "lbft" ? nm * 0.7376 : nm;
}

// --- Inicializar la gráfica de Plotly (una sola vez) ---
const plotDiv = document.getElementById("plot");

const layout = {
    paper_bgcolor: "#2c2c2a",
    plot_bgcolor: "#2c2c2a",
    font: { color: "#f1efe8" },
    margin: { l: 60, r: 60, t: 20, b: 40 },
    xaxis: { title: "RPM", gridcolor: "#444441" },
    yaxis: { title: "HP", gridcolor: "#444441", color: "#d85a30" },
    yaxis2: {
        title: "Torque",
        overlaying: "y",
        side: "right",
        color: "#1d9e75",
        showgrid: false,
    },
    shapes: [],   // aquí van la banda de potencia y las líneas verticales
    showlegend: false,
};

Plotly.newPlot(plotDiv, [
    { x: [], y: [], name: "HP", mode: "lines", line: { color: "#d85a30", width: 2 } },
    { x: [], y: [], name: "Torque", mode: "lines", yaxis: "y2",
      line: { color: "#1d9e75", width: 2, dash: "dash" } },
], layout, { responsive: true, displayModeBar: false });

// --- Segunda instancia de Plotly, para la pestaña Home ---
// Home no tiene selector de unidades (siempre HP / lb-ft, fijo), y es
// una mini-vista dentro del grid 2x2 de Home -- por eso vive en su propio
// div con su propio layout compacto, aunque reciba los mismos datos del
// WebSocket que la gráfica grande de Dyno.
const plotHomeDiv = document.getElementById("plot-home-dyno");

const layoutHome = {
    paper_bgcolor: "#2c2c2a",
    plot_bgcolor: "#2c2c2a",
    font: { color: "#f1efe8", size: 11 },
    margin: { l: 40, r: 40, t: 10, b: 30 },
    xaxis: { title: "RPM", gridcolor: "#444441" },
    yaxis: { title: "HP", gridcolor: "#444441", color: "#d85a30" },
    yaxis2: {
        title: "Torque",
        overlaying: "y",
        side: "right",
        color: "#1d9e75",
        showgrid: false,
    },
    shapes: [],
    showlegend: false,
};

Plotly.newPlot(plotHomeDiv, [
    { x: [], y: [], name: "HP", mode: "lines", line: { color: "#d85a30", width: 2 } },
    { x: [], y: [], name: "Torque", mode: "lines", yaxis: "y2",
      line: { color: "#1d9e75", width: 2, dash: "dash" } },
], layoutHome, { responsive: true, displayModeBar: false });


// --- Gráfica de pedales: acelerador y freno en tiempo real, tipo
// osciloscopio con ventana deslizante (los últimos ~12 segundos) ---
// Útil para trail braking: ver cómo se solapan (o no) el soltar el
// freno y pisar el acelerador en la entrada/salida de una curva.
const PEDALS_WINDOW_SECONDS = 12;
const plotPedalsDiv = document.getElementById("plot-pedals");

let pedalsAccelHistory = [];  // [{t: timestamp, v: 0-100}, ...]
let pedalsBrakeHistory = [];
let pedalsStartTime = null;   // referencia para el eje X relativo, en segundos

const layoutPedals = {
    paper_bgcolor: "#2c2c2a",
    plot_bgcolor: "#2c2c2a",
    font: { color: "#f1efe8", size: 10 },
    margin: { l: 35, r: 10, t: 10, b: 25 },
    xaxis: {
        title: "segundos",
        gridcolor: "#444441",
        range: [0, PEDALS_WINDOW_SECONDS],
    },
    yaxis: {
        gridcolor: "#444441",
        range: [0, 100],
        tickvals: [0, 50, 100],
    },
    shapes: [],
    showlegend: false,
};

Plotly.newPlot(plotPedalsDiv, [
    { x: [], y: [], name: "Acelerador", mode: "lines",
      line: { color: "#1d9e75", width: 2 },
      fill: "tozeroy", fillcolor: "rgba(29, 158, 117, 0.15)" },
    { x: [], y: [], name: "Freno", mode: "lines",
      line: { color: "#d85a30", width: 2 },
      fill: "tozeroy", fillcolor: "rgba(216, 90, 48, 0.15)" },
], layoutPedals, { responsive: true, displayModeBar: false });

function updatePedalsChart(msg) {
    const nowSeconds = msg.timestamp;
    if (pedalsStartTime === null) pedalsStartTime = nowSeconds;

    // Accel/Brake vienen 0-255 (crudo del paquete) -- convertir a 0-100%
    const accelPct = (msg.accel / 255) * 100;
    const brakePct = (msg.brake / 255) * 100;

    pedalsAccelHistory.push({ t: nowSeconds, v: accelPct });
    pedalsBrakeHistory.push({ t: nowSeconds, v: brakePct });

    // Ventana deslizante: descartar todo lo más viejo que el límite
    const cutoff = nowSeconds - PEDALS_WINDOW_SECONDS;
    pedalsAccelHistory = pedalsAccelHistory.filter(p => p.t >= cutoff);
    pedalsBrakeHistory = pedalsBrakeHistory.filter(p => p.t >= cutoff);

    // Eje X relativo: 0 = el punto más viejo visible, PEDALS_WINDOW_SECONDS = ahora
    const windowStart = nowSeconds - PEDALS_WINDOW_SECONDS;
    const accelX = pedalsAccelHistory.map(p => p.t - windowStart);
    const accelY = pedalsAccelHistory.map(p => p.v);
    const brakeX = pedalsBrakeHistory.map(p => p.t - windowStart);
    const brakeY = pedalsBrakeHistory.map(p => p.v);

    Plotly.update(plotPedalsDiv, {
        x: [accelX, brakeX],
        y: [accelY, brakeY],
    });
}


// --- Gráfica de pista: trazado en el plano X/Z, coloreado por
// acelerando (verde) / frenando (rojo) / neutro (gris) ---
const plotTrackHomeDiv = document.getElementById("plot-home-pista");
const plotTrackDiv = document.getElementById("plot-track");

const layoutTrackBase = {
    paper_bgcolor: "#2c2c2a",
    plot_bgcolor: "#2c2c2a",
    font: { color: "#f1efe8" },
    showlegend: false,
    xaxis: { gridcolor: "#444441", scaleanchor: "y", showticklabels: false },
    yaxis: { gridcolor: "#444441", showticklabels: false },
};

Plotly.newPlot(plotTrackHomeDiv, [], { ...layoutTrackBase, margin: { l: 10, r: 10, t: 10, b: 10 }, font: { size: 10 } },
    { responsive: true, displayModeBar: false });
Plotly.newPlot(plotTrackDiv, [], { ...layoutTrackBase, margin: { l: 20, r: 20, t: 20, b: 20 } },
    { responsive: true, displayModeBar: false });

const TRACK_COLORS = { green: "#1d9e75", red: "#d85a30", null: "#5f5e5a" };

function buildTrackSegments(points) {
    // Plotly no pinta una sola línea con varios colores a la vez -- hay
    // que partir el trazado en "segmentos" (tramos consecutivos del
    // mismo color) y dibujar cada uno como su propia traza. Se incluye
    // un punto de traslape entre segmentos consecutivos para que no se
    // vean cortes/huecos visuales en la unión.
    const segments = [];
    if (points.length === 0) return segments;

    let currentColor = points[0].color;
    let currentX = [points[0].x];
    let currentZ = [points[0].z];

    for (let i = 1; i < points.length; i++) {
        const p = points[i];
        if (p.color !== currentColor) {
            // cerrar el segmento actual con este punto también (traslape)
            currentX.push(p.x);
            currentZ.push(p.z);
            segments.push({ color: currentColor, x: currentX, z: currentZ });
            currentColor = p.color;
            currentX = [p.x];
            currentZ = [p.z];
        } else {
            currentX.push(p.x);
            currentZ.push(p.z);
        }
    }
    segments.push({ color: currentColor, x: currentX, z: currentZ });
    return segments;
}

function updateTrackChart(msg) {
    const segments = buildTrackSegments(msg.points);

    const traces = segments.map(seg => ({
        x: seg.x,
        y: seg.z,
        mode: "lines",
        line: { color: TRACK_COLORS[seg.color], width: 3 },
        hoverinfo: "skip",
    }));

    Plotly.react(plotTrackHomeDiv, traces, plotTrackHomeDiv.layout);
    Plotly.react(plotTrackDiv, traces, plotTrackDiv.layout);
}

document.getElementById("btn-restart-track").addEventListener("click", () => {
    ws.send("restart_track");
});


// --- Actualizar toda la UI con el estado recibido ---
function updateUI(state) {
    updateCarDetails(state);
    updateProgress(state);
    updatePlot(state);
    updateButtons(state);
}

function updateCarDetails(state) {
    const carNameEl = document.getElementById("car-name");

    if (!state.car_info) {
        carNameEl.textContent = "Esperando datos...";
        return;
    }
    const displayName = state.car_name || `Auto #${state.car_info.CarOrdinal}`;
    carNameEl.textContent = displayName;

    const drivetrainMap = { 0: "FWD", 1: "RWD", 2: "AWD" };
    document.getElementById("detail-pi").textContent = state.car_info.CarPerformanceIndex;

    // "Motor {cilindros} cil." + sufijo Boosted/N/A -- el sufijo se basa
    // en si en algún momento de la sesión se detectó Boost > 0, no en
    // el criterio de muestreo de los bins (ver has_boost_detected).
    const cylinders = state.car_info.NumCylinders;
    const boostSuffix = state.has_boost_detected ? "Boosted" : "N/A";
    document.getElementById("detail-engine").textContent = `Motor ${cylinders} cil. (${boostSuffix})`;

    document.getElementById("detail-drivetrain").textContent = drivetrainMap[state.car_info.DrivetrainType] || "?";
}

function updateProgress(state) {
    const pct = state.total_bins > 0 ? (state.filled / state.total_bins) * 100 : 0;
    document.getElementById("progress-bar-inner").style.width = `${pct}%`;
    document.getElementById("progress-text").textContent = `Precisión ${pct.toFixed(0)}%`;
}

function updatePlot(state) {
    const powerUnit = document.getElementById("power-unit").value;
    const torqueUnit = document.getElementById("torque-unit").value;

    // Los puntos ya vienen ordenados por RPM desde el servidor.
    const rpmValues = state.points.map(p => p.rpm);
    const powerValues = state.points.map(p => convertPower(p.power_w, powerUnit));
    const torqueValues = state.points.map(p => convertTorque(p.torque_nm, torqueUnit));

    Plotly.update(plotDiv, {
        x: [rpmValues, rpmValues],
        y: [powerValues, torqueValues],
    });

    Plotly.relayout(plotDiv, {
        "yaxis.title": powerUnit,
        "yaxis2.title": `Torque (${torqueUnit === "lbft" ? "lb-ft" : "Nm"})`,
    });

    updateReferenceMarkers(plotDiv, rpmValues, powerValues, torqueValues, powerUnit, torqueUnit,
        { peakHp: "peak-hp", peakTorque: "peak-torque", band: "band" });

    // --- Home: siempre en HP / lb-ft, sin importar los selectores de Dyno ---
    const powerValuesHome = state.points.map(p => convertPower(p.power_w, "HP"));
    const torqueValuesHome = state.points.map(p => convertTorque(p.torque_nm, "lbft"));

    Plotly.update(plotHomeDiv, {
        x: [rpmValues, rpmValues],
        y: [powerValuesHome, torqueValuesHome],
    });

    updateReferenceMarkers(plotHomeDiv, rpmValues, powerValuesHome, torqueValuesHome, "HP", "lbft", null);
}

function updateReferenceMarkers(targetDiv, rpmValues, powerValues, torqueValues, powerUnit, torqueUnit, cardIds) {
    if (rpmValues.length < 3) {
        // Limpiar explícitamente los shapes -- antes esto hacía "return"
        // y dejaba dibujados el rectángulo de banda y las líneas
        // verticales de la corrida ANTERIOR, dando la impresión de que
        // "Reiniciar" no había funcionado.
        Plotly.relayout(targetDiv, { shapes: [] });
        if (cardIds) {
            document.getElementById(cardIds.peakHp).textContent = "--";
            document.getElementById(cardIds.peakTorque).textContent = "--";
            document.getElementById(cardIds.band).textContent = "--";
        }
        return;
    }

    // --- Pico de HP ---
    let idxHpPeak = 0;
    for (let i = 1; i < powerValues.length; i++) {
        if (powerValues[i] > powerValues[idxHpPeak]) idxHpPeak = i;
    }
    const rpmHpPeak = rpmValues[idxHpPeak];
    const hpPeakValue = powerValues[idxHpPeak];

    // --- Pico de Torque ---
    let idxTorquePeak = 0;
    for (let i = 1; i < torqueValues.length; i++) {
        if (torqueValues[i] > torqueValues[idxTorquePeak]) idxTorquePeak = i;
    }
    const rpmTorquePeak = rpmValues[idxTorquePeak];
    const torquePeakValue = torqueValues[idxTorquePeak];

    // --- Banda de potencia (>=90% del pico) ---
    const bandThreshold = 0.90;
    const cutoff = hpPeakValue * bandThreshold;
    const inBand = rpmValues.filter((_, i) => powerValues[i] >= cutoff);
    const bandLow = inBand.length ? Math.min(...inBand) : rpmHpPeak;
    const bandHigh = inBand.length ? Math.max(...inBand) : rpmHpPeak;

    // Dibujar como "shapes" de Plotly: rectángulo + 2 líneas verticales
    Plotly.relayout(targetDiv, {
        shapes: [
            {
                type: "rect", xref: "x", yref: "paper",
                x0: bandLow, x1: bandHigh, y0: 0, y1: 1,
                fillcolor: "rgba(186, 117, 23, 0.15)",
                line: { color: "rgba(186, 117, 23, 0.5)", width: 1 },
            },
            {
                type: "line", xref: "x", yref: "paper",
                x0: rpmHpPeak, x1: rpmHpPeak, y0: 0, y1: 1,
                line: { color: "#d85a30", width: 1.5, dash: "dash" },
            },
            {
                type: "line", xref: "x", yref: "paper",
                x0: rpmTorquePeak, x1: rpmTorquePeak, y0: 0, y1: 1,
                line: { color: "#1d9e75", width: 1.5, dash: "dash" },
            },
        ],
    });

    // Actualizar las tarjetas del panel lateral, SOLO si se pasaron IDs
    // (Home no tiene panel lateral, así que ahí cardIds es null).
    if (cardIds) {
        document.getElementById(cardIds.peakHp).textContent =
            `${hpPeakValue.toFixed(0)} ${powerUnit} @ ${rpmHpPeak.toFixed(0)} RPM`;
        document.getElementById(cardIds.peakTorque).textContent =
            `${torquePeakValue.toFixed(0)} ${torqueUnit === "lbft" ? "lb-ft" : "Nm"} @ ${rpmTorquePeak.toFixed(0)} RPM`;
        document.getElementById(cardIds.band).textContent =
            `${bandLow.toFixed(0)} - ${bandHigh.toFixed(0)} RPM`;
    }
}

function updateButtons(state) {
    const isComplete = state.total_bins > 0 && state.filled === state.total_bins;
    // Nota: el botón Guardar/Reiniciar se habilita cuando el SERVIDOR
    // reporte que la captura se detuvo -- por ahora, referencia simple
    // basada en si ya se completó (se puede refinar mandando un campo
    // "stopped" explícito desde el backend más adelante).
    document.getElementById("btn-save").disabled = !state.car_info;
    document.getElementById("btn-restart").disabled = !state.car_info;
}

// --- Botones: mandan un mensaje simple de texto por el WebSocket ---
document.getElementById("btn-stop").addEventListener("click", () => {
    ws.send("stop");
});

document.getElementById("btn-restart").addEventListener("click", () => {
    ws.send("restart");
});

document.getElementById("btn-save").addEventListener("click", () => {
    const statusEl = document.getElementById("save-status");
    statusEl.textContent = "Generando imagen...";

    // Plotly.toImage() renderiza el estado ACTUAL de la gráfica (tal
    // como se ve en pantalla, con las unidades y shapes vigentes) como
    // PNG en base64 -- esto vive en el navegador, el servidor Python
    // nunca "ve" la gráfica directamente, así que hay que generarla
    // aquí y mandarla como parte del POST.
    Plotly.toImage(plotDiv, { format: "png", width: 1000, height: 600 })
        .then(dataUrl => {
            statusEl.textContent = "Guardando...";
            return fetch("/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_base64: dataUrl }),
            });
        })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                statusEl.textContent = `Error: ${data.error}`;
            } else {
                statusEl.textContent = `Guardado en: ${data.folder}`;
            }
        })
        .catch(err => {
            statusEl.textContent = `Error al guardar: ${err}`;
        });
});

// --- Cambiar de unidad redibuja inmediatamente con el último estado conocido ---
document.getElementById("power-unit").addEventListener("change", () => {
    if (latestState) updatePlot(latestState);
});
document.getElementById("torque-unit").addEventListener("change", () => {
    if (latestState) updatePlot(latestState);
});