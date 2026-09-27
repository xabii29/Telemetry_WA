import time
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>🏎️ Simulador de Transmisión - Forza Motorsport</title>
    
    <script>
        (function() {
            var cdn = String.fromCharCode(104,116,116,112,115,58,47,47,99,100,110,46,112,108,111,116,46,108,121,47,112,108,111,116,108,121,45,50,46,50,52,46,49,46,109,105,110,46,106,115);
            var script = document.createElement('script');
            script.src = cdn + '?v=' + Date.now();
            script.onload = function() {
                if(window.calcularYActualizar) window.calcularYActualizar();
            };
            document.head.appendChild(script);
        })();
    </script>

    <style>
        body { background-color: #0a0a0a; color: white; font-family: monospace; padding: 20px; margin: 0; }
        .container { display: flex; max-width: 1400px; margin: 0 auto; }
        .chart-box { width: 72%; height: 650px; }
        .controls-box { width: 25%; margin-left: 3%; padding: 15px; background-color: #141414; border-radius: 5px; box-sizing: border-box; height: 650px; overflow-y: auto; }
        h1 { text-align: center; color: #00ffcc; margin-bottom: 20px; }
        h3 { color: orange; border-bottom: 1px solid orange; padding-bottom: 5px; margin-top: 0; }
        .slider-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 3px; font-weight: bold; }
        input[type="range"] { width: 100%; accent-color: #00ffcc; cursor: pointer; }
        .vmax-display { margin-top: 15px; font-size: 14px; color: #00ffcc; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
        .value-label { color: #00ffcc; float: right; font-weight: bold; }
        .config-group { background-color: #1a1a1a; padding: 8px; border-radius: 4px; border-left: 4px solid orange; margin-bottom: 15px; }
        .rpm-group { background-color: #1a1a1a; padding: 8px; border-radius: 4px; border-left: 4px solid #ff4444; margin-bottom: 15px; }
    </style>
</head>
<body>

    <h1>🏎️ SIMULADOR DE TRANSMISIÓN INTERACTIVO</h1>
    
    <div class="container">
        <div class="chart-box" id="plot-transmision"></div>
        
        <div class="controls-box">
            <h3>Ajustes Globales</h3>
            
            <div class="slider-group config-group">
                <label style="color: orange;">Relación Final (TF): <span id="vtf" class="value-label">3.89</span></label>
                <input type="range" id="sltf" min="2.20" max="6.10" step="0.01" value="3.89">
            </div>

            <div class="slider-group rpm-group">
                <label style="color: #ff4444;">RPM Máximas: <span id="vrpm" class="value-label">7725</span></label>
                <input type="range" id="slrpm" min="4000" max="10000" step="50" value="7725">
            </div>

            <h3>Ratios por Marcha</h3>
            
            <div class="slider-group">
                <label>1ª Marcha: <span id="v1" class="value-label">3.91</span></label>
                <input type="range" id="sl1" min="0.48" max="6.00" step="0.01" value="3.91">
            </div>
            <div class="slider-group">
                <label>2ª Marcha: <span id="v2" class="value-label">2.29</span></label>
                <input type="range" id="sl2" min="0.48" max="6.00" step="0.01" value="2.29">
            </div>
            <div class="slider-group">
                <label>3ª Marcha: <span id="v3" class="value-label">1.56</span></label>
                <input type="range" id="sl3" min="0.48" max="6.00" step="0.01" value="1.56">
            </div>
            <div class="slider-group">
                <label>4ª Marcha: <span id="v4" class="value-label">1.19</span></label>
                <input type="range" id="sl4" min="0.48" max="6.00" step="0.01" value="1.19">
            </div>
            <div class="slider-group">
                <label>5ª Marcha: <span id="v5" class="value-label">0.93</span></label>
                <input type="range" id="sl5" min="0.48" max="6.00" step="0.01" value="0.93">
            </div>
            <div class="slider-group">
                <label>6ª Marcha: <span id="v6" class="value-label">0.72</span></label>
                <input type="range" id="sl6" min="0.48" max="6.00" step="0.01" value="0.72">
            </div>
            
            <div id="v-max-output" class="vmax-display">
                V. Máx Teórica (6ª @ Pico kW): -- km/h
            </div>
        </div>
    </div>

    <script>
        const RPM_PICO = 6915;
        const DIAMETRO_LLANTA = 0.65;
        const colores = ['#ff4444', '#ffaa00', '#ffff00', '#00ff00', '#00aaff', '#00ffcc'];

        function calcularYActualizar() {
            if (typeof Plotly === 'undefined') return;

            const finalDriveValue = parseFloat(document.getElementById('sltf').value);
            const rpmMaxDinámica = parseInt(document.getElementById('slrpm').value);

            document.getElementById('vtf').innerText = finalDriveValue.toFixed(2);
            document.getElementById('vrpm').innerText = rpmMaxDinámica;

            const r1 = parseFloat(document.getElementById('sl1').value);
            const r2 = parseFloat(document.getElementById('sl2').value);
            const r3 = parseFloat(document.getElementById('sl3').value);
            const r4 = parseFloat(document.getElementById('sl4').value);
            const r5 = parseFloat(document.getElementById('sl5').value);
            const r6 = parseFloat(document.getElementById('sl6').value);

            document.getElementById('v1').innerText = r1.toFixed(2);
            document.getElementById('v2').innerText = r2.toFixed(2);
            document.getElementById('v3').innerText = r3.toFixed(2);
            document.getElementById('v4').innerText = r4.toFixed(2);
            document.getElementById('v5').innerText = r5.toFixed(2);
            document.getElementById('v6').innerText = r6.toFixed(2);

            const ratios = Array.of(r1, r2, r3, r4, r5, r6);
            let dataTrazos = [];

            // Guardamos las velocidades de corte secuencialmente para recortar los ejes
            let velocidadesCorte = Array.of(0);
            ratios.forEach((ratio) => {
                let v_corte = (rpmMaxDinámica * Math.PI * DIAMETRO_LLANTA) / (60 * ratio * finalDriveValue) * 3.6;
                velocidadesCorte.push(v_corte);
            });

            // 🛠️ ALGORITMO DE CORTE (Diagrama en Diente de Sierra)
            ratios.forEach((ratio, index) => {
                let v_inicio = velocidadesCorte[index]; // Comienza donde terminó la marcha anterior
                let v_fin = velocidadesCorte[index + 1];  // Termina en su propia velocidad de corte

                // Calcular a qué RPM cae el motor inmediatamente al meter esta marcha
                // Si es la 1ª marcha (index 0), empieza desde 0 RPM
                let rpm_inicio = 0;
                if (index > 0) {
                    rpm_inicio = (v_inicio / 3.6 * 60 * ratio * finalDriveValue) / (Math.PI * DIAMETRO_LLANTA);
                }

                dataTrazos.push({
                    x: Array.of(v_inicio, v_fin),
                    y: Array.of(rpm_inicio, rpmMaxDinámica),
                    mode: 'lines+markers',
                    name: (index + 1) + 'ª (' + ratio.toFixed(2) + ')',
                    line: { color: colores[index], width: 3 },
                    hovertemplate: '<b>' + (index + 1) + 'ª Marcha</b><br>Velocidad: %{x:.1f} km/h<br>RPM: %{y:d}<extra></extra>'
                });
            });

            let v_max_pico = (RPM_PICO * Math.PI * DIAMETRO_LLANTA) / (60 * r6 * finalDriveValue) * 3.6;
            document.getElementById('v-max-output').innerText = "V. Máx Teórica (6ª @ Pico kW): " + v_max_pico.toFixed(1) + " km/h";

            const rangoVelocidad = Array.of(0, 420); 
            const rangoRPM = Array.of(0, 10500); 

            const layout = {
                xaxis: { title: "Velocidad del Vehículo (km/h)", range: rangoVelocidad, gridcolor: 'rgba(255,255,255,0.05)' },
                yaxis: { title: "Revoluciones del Motor (RPM)", range: rangoRPM, gridcolor: 'rgba(255,255,255,0.05)' },
                plot_bgcolor: 'rgb(20, 20, 20)',
                paper_bgcolor: 'rgb(10, 10, 10)',
                font: { color: 'white' },
                margin: { l: 60, r: 20, t: 20, b: 50 },
                showlegend: true,
                legend: { orientation: "h", y: 1.08, x: 1, xanchor: "right" },
                shapes: [
                    { type: 'line', y0: 6525, y1: 6525, x0: 0, x1: 420, line: { color: 'orange', width: 2, dash: 'dash' } },
                    { type: 'line', y0: 5715, y1: 5715, x0: 0, x1: 420, line: { color: 'yellow', width: 1.5, dash: 'dot' } }
                ]
            };

            Plotly.newPlot('plot-transmision', dataTrazos, layout, {responsive: true, displayModeBar: false});
        }

        document.getElementById('sltf').addEventListener('input', calcularYActualizar);
        document.getElementById('slrpm').addEventListener('input', calcularYActualizar);

        for (let i = 1; i <= 6; i++) {
            document.getElementById('sl' + i).addEventListener('input', calcularYActualizar);
        }

        window.calcularYActualizar = calcularYActualizar;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
