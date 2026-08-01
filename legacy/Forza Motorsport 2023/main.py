"""
Servidor FastAPI para telemetría de Forza Motorsport.

Reemplaza la GUI de PySide6/PyQtGraph por un servidor web local:
  - La lógica de captura UDP (bins, criterio independiente Power/Torque,
    filtro de embrague, detección de auto) es la MISMA que ya validamos
    en dyno_gui.py -- solo cambia el "mensajero" final.
  - En vez de Signal.emit() hacia una ventana Qt, mandamos JSON por
    WebSocket hacia cualquier navegador conectado (PC o celular).

Cómo correrlo:
    python main.py
Luego abre http://127.0.0.1:8000 en tu PC, o escanea el QR con tu
celular (debe estar en la misma red WiFi que la PC).
"""

import asyncio
import base64
import json
import os
import re
import socket
import struct
import sys
import time
import webbrowser

import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from car_lookup import get_car_name, get_car_aspiration

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que corre AL ARRANCAR (equivalente a on_event("startup")):
    # lanzamos la captura UDP como tarea de fondo, sin bloquear el servidor.
    asyncio.create_task(udp_capture_loop())
    yield
    # Código que correría AL APAGAR el servidor iría aquí, después del yield
    # (no lo necesitamos por ahora, pero el patrón lo deja listo).


app = FastAPI(lifespan=lifespan)


# ==========================================================================
# MANEJO DE RUTAS PARA PYINSTALLER (.EXE)
# ==========================================================================
def get_resource_path(relative_path):
    """
    Cuando el proyecto corre normal con 'python main.py', los archivos
    (BD/, static/) están junto a este script. Pero cuando PyInstaller
    empaqueta todo en un .exe, los extrae a una carpeta temporal
    (sys._MEIPASS) distinta -- hay que detectar cuál caso aplica.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# ==========================================================================
# DETECCIÓN DE IP LOCAL (para mostrar la URL correcta al celular)
# ==========================================================================
def get_local_ip():
    """
    Truco estándar: 'conectamos' un socket UDP a una IP pública (8.8.8.8)
    sin mandar realmente ningún byte -- esto obliga al sistema operativo
    a elegir qué interfaz de red usaría, y así sabemos nuestra IP en la
    red local (ej. 192.168.1.X) sin depender de librerías externas.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# ==========================================================================
# CONFIGURACIÓN DE CAPTURA (idéntica a dyno_gui.py, ya validada)
# ==========================================================================
UDP_IP = "0.0.0.0"
UDP_PORT = 8000

BIN_SIZE = 30
ACCEL_THRESHOLD = 250
TRIM_PERCENT = 0.10
PEDALS_BROADCAST_INTERVAL = 1 / 20  # ~20 mensajes por segundo, no 60
TRACK_BROADCAST_INTERVAL = 1 / 15   # ~15 puntos por segundo, suficiente resolución

# Formato REAL del paquete Forza Motorsport (2023), "Car Dash", 331 bytes.
# (El struct del otro código era genérico e incorrecto -- este es el que
# ya validamos byte por byte contigo, incluyendo la extensión de FM2023
# con TrackOrdinal + TireWear.)
FORMAT = (
    "<"
    "i" "I"
    "f f f"
    "f f f" "f f f" "f f f" "f f f"
    "f f f f" "f f f f" "f f f f"
    "i i i i"
    "f f f f" "f f f f" "f f f f" "f f f f" "f f f f"
    "i i i i" "i"
    "f f f" "f" "f" "f"
    "f f f f" "f" "f" "f"
    "f f f" "f" "H" "B"
    "B B B B" "B" "b b b"
    "i" "f f f f"
)

FIELDS = [
    "IsRaceOn", "TimestampMS",
    "EngineMaxRpm", "EngineIdleRpm", "CurrentEngineRpm",
    "AccelerationX", "AccelerationY", "AccelerationZ",
    "VelocityX", "VelocityY", "VelocityZ",
    "AngularVelocityX", "AngularVelocityY", "AngularVelocityZ",
    "Yaw", "Pitch", "Roll",
    "SuspTravel_FL", "SuspTravel_FR", "SuspTravel_RL", "SuspTravel_RR",
    "TireSlipRatio_FL", "TireSlipRatio_FR", "TireSlipRatio_RL", "TireSlipRatio_RR",
    "WheelRotSpeed_FL", "WheelRotSpeed_FR", "WheelRotSpeed_RL", "WheelRotSpeed_RR",
    "RumbleStrip_FL", "RumbleStrip_FR", "RumbleStrip_RL", "RumbleStrip_RR",
    "PuddleDepth_FL", "PuddleDepth_FR", "PuddleDepth_RL", "PuddleDepth_RR",
    "SurfaceRumble_FL", "SurfaceRumble_FR", "SurfaceRumble_RL", "SurfaceRumble_RR",
    "TireSlipAngle_FL", "TireSlipAngle_FR", "TireSlipAngle_RL", "TireSlipAngle_RR",
    "TireCombinedSlip_FL", "TireCombinedSlip_FR", "TireCombinedSlip_RL", "TireCombinedSlip_RR",
    "SuspTravelMeters_FL", "SuspTravelMeters_FR", "SuspTravelMeters_RL", "SuspTravelMeters_RR",
    "CarOrdinal", "CarClass", "CarPerformanceIndex", "DrivetrainType",
    "NumCylinders",
    "PositionX", "PositionY", "PositionZ",
    "Speed", "Power", "Torque",
    "TireTemp_FL", "TireTemp_FR", "TireTemp_RL", "TireTemp_RR",
    "Boost", "Fuel", "DistanceTraveled",
    "BestLap", "LastLap", "CurrentLap", "CurrentRaceTime",
    "LapNumber", "RacePosition",
    "Accel", "Brake", "Clutch", "HandBrake",
    "Gear",
    "Steer", "NormalizedDrivingLine", "NormalizedAIBrakeDifference",
    "TrackOrdinal",
    "TireWear_FL", "TireWear_FR", "TireWear_RL", "TireWear_RR",
]

PACKET_SIZE = struct.calcsize(FORMAT)


# ==========================================================================
# ESTADO DE LA PISTA (independiente del dyno -- no se reinicia con él)
# ==========================================================================
class TrackState:
    """
    Acumula puntos de posición (X, Z -- el plano horizontal en Forza,
    Y es la altura) con un color por punto: verde si se acelera más de
    lo que se frena en ese instante, rojo si es al revés, sin color si
    ninguno de los dos está presionado.

    A diferencia de CaptureState (dyno), aquí SÍ se guarda el historial
    completo de puntos -- el objetivo es dibujar el trazado completo de
    la pista, no un resumen por bins.
    """
    def __init__(self):
        self.points = []          # [{"x":.., "z":.., "color": "green"|"red"|None}, ...]
        self.track_ordinal = None  # se guarda el primero que se vea, solo informativo
        self.last_broadcast = 0.0

    def add_point(self, x, z, accel, brake, track_ordinal):
        if self.track_ordinal is None:
            self.track_ordinal = track_ordinal

        if accel > brake:
            color = "green"
        elif brake > accel:
            color = "red"
        else:
            color = None

        self.points.append({"x": x, "z": z, "color": color})

    def reset(self):
        self.points = []
        self.track_ordinal = None

    def to_dict(self):
        return {
            "type": "track_state",
            "track_ordinal": self.track_ordinal,
            "points": self.points,
        }


track_state = TrackState()


# ==========================================================================
# ESTADO COMPARTIDO DE LA CAPTURA
# ==========================================================================
# A diferencia de Qt (donde el estado vivía en la ventana), aquí el
# estado vive en un objeto simple en memoria del servidor. Cualquier
# cliente (PC o celular) que se conecte por WebSocket recibe el MISMO
# estado -- si dos personas ven el dashboard a la vez, ambas ven la
# misma curva actualizándose en vivo.
class CaptureState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.running = True
        self.car_info = None
        self.car_name = None
        self.car_aspiration = None
        self.has_boost_detected = False
        self.bins_dict = {}
        self.bin_edges = None
        self.total_bins = 0
        self.last_pedals_broadcast = 0.0

    def build_bins(self, idle_rpm, max_rpm, bin_size, trim_percent):
        full_range = max_rpm - idle_rpm
        trim_amount = full_range * trim_percent
        effective_start = idle_rpm + trim_amount
        effective_end = max_rpm - trim_amount
        start = int(effective_start // bin_size) * bin_size
        end = int(effective_end // bin_size) * bin_size + bin_size
        edges = list(range(start, end, bin_size))
        return {edge: None for edge in edges}, edges

    def get_bin_key(self, rpm):
        idx = int((rpm - self.bin_edges[0]) // BIN_SIZE)
        if idx < 0 or idx >= len(self.bin_edges):
            return None
        return self.bin_edges[idx]

    def to_dict(self):
        """Serializa el estado completo para mandarlo por WebSocket."""
        points = []
        for edge in sorted(self.bin_edges) if self.bin_edges else []:
            data_bin = self.bins_dict.get(edge)
            if data_bin is not None:
                points.append({
                    "rpm": edge + BIN_SIZE / 2,
                    "power_w": data_bin["Power_W"],
                    "torque_nm": data_bin["Torque_Nm"],
                })

        filled = sum(1 for v in self.bins_dict.values() if v is not None)

        return {
            "car_info": self.car_info,
            "car_name": self.car_name,
            "car_aspiration": self.car_aspiration,
            "has_boost_detected": self.has_boost_detected,
            "points": points,
            "filled": filled,
            "total_bins": self.total_bins,
        }


state = CaptureState()


# ==========================================================================
# CAPTURA UDP (misma lógica que UDPListener de dyno_gui.py, sin Qt)
# ==========================================================================
async def udp_capture_loop():
    """
    Corre como una TAREA asíncrona de FastAPI (no un QThread, pero
    cumple el mismo propósito: no bloquear el resto del servidor
    mientras espera paquetes UDP).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    loop = asyncio.get_event_loop()
    print(f"Escuchando telemetría UDP en {UDP_IP}:{UDP_PORT} ...")

    while True:
        try:
            data = await loop.sock_recv(sock, 2048)
        except Exception as e:
            print(f"Error de socket: {e}")
            await asyncio.sleep(0.5)
            continue

        if len(data) != PACKET_SIZE:
            continue

        values = struct.unpack(FORMAT, data)
        row = dict(zip(FIELDS, values))

        if row["IsRaceOn"] != 1:
            continue

        # Detección automática de cambio de auto: si ya teníamos un auto
        # detectado y este paquete trae un CarOrdinal DISTINTO, significa
        # que el usuario cambió de auto en el juego sin presionar
        # "Reiniciar" -- reseteamos todo el estado antes de seguir, para
        # no mezclar bins calculados para el rango de RPM del auto viejo
        # con datos del auto nuevo (esto era la causa real del "lag":
        # el auto anterior seguía "vivo" en el backend).
        if state.car_info is not None and row["CarOrdinal"] != state.car_info["CarOrdinal"]:
            print(f"Cambio de auto detectado (Ordinal {state.car_info['CarOrdinal']} -> "
                  f"{row['CarOrdinal']}). Reiniciando captura automáticamente.")
            state.reset()
            await broadcast_state()

        # Detección de boost: basta con verlo UNA VEZ en toda la sesión
        # para saber que el motor no es naturalmente aspirado. No depende
        # del filtro de acelerador/potencia que usan los bins -- es
        # información de configuración del motor, no del muestreo de curva.
        if row["Boost"] > 0:
            state.has_boost_detected = True

        # Primer paquete válido: detectamos el auto y armamos los bins
        if state.bin_edges is None:
            idle_rpm = row["EngineIdleRpm"]
            max_rpm = row["EngineMaxRpm"]
            state.bins_dict, state.bin_edges = state.build_bins(
                idle_rpm, max_rpm, BIN_SIZE, TRIM_PERCENT
            )
            state.total_bins = len(state.bin_edges)

            state.car_info = {
                "CarOrdinal": row["CarOrdinal"],
                "CarPerformanceIndex": row["CarPerformanceIndex"],
                "DrivetrainType": row["DrivetrainType"],
                "NumCylinders": row["NumCylinders"],
                "EngineIdleRpm": idle_rpm,
                "EngineMaxRpm": max_rpm,
            }
            state.car_name = get_car_name(row["CarOrdinal"])
            state.car_aspiration = get_car_aspiration(row["CarOrdinal"])
            print(f"Auto detectado: {state.car_name or row['CarOrdinal']}")

        # --- Pedales: se transmiten con throttle (~20/seg, no los 60/seg
        # crudos del paquete) -- mandar cada paquete sin límite saturaba
        # el WebSocket y causaba desconexiones cada ~10 segundos. 20/seg
        # sigue siendo fluido visualmente y es mucho más ligero.
        now = time.time()
        if now - state.last_pedals_broadcast >= PEDALS_BROADCAST_INTERVAL:
            await broadcast_pedals(row["Accel"], row["Brake"])
            state.last_pedals_broadcast = now

        # --- Pista: se acumula independiente del dyno, con su propio
        # throttle (~15/seg -- suficiente resolución para un trazado
        # suave sin saturar memoria ni el WebSocket con miles de puntos
        # por minuto). PositionX/Z son el plano horizontal en Forza.
        if now - track_state.last_broadcast >= TRACK_BROADCAST_INTERVAL:
            track_state.add_point(
                row["PositionX"], row["PositionZ"],
                row["Accel"], row["Brake"],
                row["TrackOrdinal"],
            )
            await broadcast_track()
            track_state.last_broadcast = now

        clutch_ok = (row["Clutch"] == 0) or (row["Clutch"] == 255)
        is_valid = (row["Accel"] >= ACCEL_THRESHOLD) and (row["Power"] > 0) and clutch_ok
        if not is_valid:
            continue

        rpm = row["CurrentEngineRpm"]
        key = state.get_bin_key(rpm)
        if key is None:
            continue

        new_power_w = row["Power"]
        new_torque_nm = row["Torque"]

        is_new_bin = state.bins_dict[key] is None

        if is_new_bin:
            state.bins_dict[key] = {"Power_W": new_power_w, "Torque_Nm": new_torque_nm}
        else:
            # Power y Torque se evalúan y actualizan de forma INDEPENDIENTE
            # (el bug que encontraste: un paquete con mejor Power pero peor
            # Torque ya no sobreescribe ambos juntos).
            if new_power_w > state.bins_dict[key]["Power_W"]:
                state.bins_dict[key]["Power_W"] = new_power_w
            if new_torque_nm > state.bins_dict[key]["Torque_Nm"]:
                state.bins_dict[key]["Torque_Nm"] = new_torque_nm

        # Notificar a todos los WebSockets conectados
        await broadcast_state()


# ==========================================================================
# WEBSOCKET: el "mensajero" hacia cualquier navegador conectado
# ==========================================================================
connected_clients: list[WebSocket] = []


async def broadcast_json(payload_dict):
    """
    Función genérica de envío -- todos los broadcast_* (state, pedals,
    track) comparten esta misma lógica de "mandar a todos, limpiar los
    que fallen", así que vive en un solo lugar en vez de repetirse tres
    veces con el mismo manejo de errores.
    """
    if not connected_clients:
        return
    payload = json.dumps(payload_dict)
    stale_clients = []
    for client in connected_clients:
        try:
            await client.send_text(payload)
        except Exception:
            stale_clients.append(client)
    for client in stale_clients:
        # Puede que este cliente ya haya sido removido por el bloque
        # except WebSocketDisconnect del propio endpoint (condición de
        # carrera: ambos lados detectan la desconexión casi al mismo
        # tiempo) -- por eso removemos de forma segura, sin volver a
        # lanzar error si ya no está en la lista.
        if client in connected_clients:
            connected_clients.remove(client)


async def broadcast_state():
    """Manda el estado actual del dyno a todos los navegadores conectados."""
    await broadcast_json({"type": "dyno_state", **state.to_dict()})


async def broadcast_pedals(accel, brake):
    """
    Mensaje LIGERO y SEPARADO del estado del dyno -- se manda con
    throttle (~20/seg), marcado con type="pedals" para que el frontend
    lo distinga de "dyno_state" sin re-renderizar toda la gráfica de
    dyno solo por el movimiento de pedales.
    """
    await broadcast_json({
        "type": "pedals",
        "timestamp": time.time(),
        "accel": accel,   # 0-255, crudo del paquete
        "brake": brake,   # 0-255, crudo del paquete
    })


async def broadcast_track():
    """
    Manda el estado completo de la pista (todos los puntos acumulados
    hasta ahora) a todos los navegadores conectados. A diferencia de
    pedals, aquí SÍ se manda el historial completo en cada mensaje --
    el frontend redibuja el trazado entero, no solo el punto nuevo.
    """
    await broadcast_json(track_state.to_dict())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"Cliente conectado. Total: {len(connected_clients)}")

    # Al conectarse, mandamos el estado actual de inmediato (por si ya
    # había datos capturados antes de que este cliente se uniera).
    await websocket.send_text(json.dumps({"type": "dyno_state", **state.to_dict()}))
    await websocket.send_text(json.dumps(track_state.to_dict()))

    try:
        while True:
            # Esperamos mensajes del cliente (ej. "stop", "restart").
            msg = await websocket.receive_text()
            if msg == "stop":
                state.running = False
            elif msg == "restart":
                state.reset()
                await broadcast_state()
            elif msg == "restart_track":
                # Comando SEPARADO del restart del dyno -- la pista se
                # acumula independiente de la sesión de captura de HP/Torque.
                track_state.reset()
                await broadcast_track()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"Cliente desconectado. Total: {len(connected_clients)}")


# ==========================================================================
# RUTAS HTTP: página principal (con QR) y el dashboard real
# ==========================================================================
QR_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Forza Dyno -- Servidor activo</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1c1c1a; color: #f1efe8;
                text-align: center; padding: 40px; }}
        .card {{ background: #2c2c2a; padding: 24px; border-radius: 12px; display: inline-block; }}
        #qrcode {{ background: white; padding: 12px; border-radius: 8px; display: inline-block; margin: 16px 0; }}
        h1 {{ color: #1d9e75; }}
        a {{ color: #1d9e75; }}
    </style>
</head>
<body>
    <h1>Forza Dyno -- Servidor activo</h1>
    <p><a href="/dashboard">Abrir el dashboard en esta PC</a></p>
    <div class="card">
        <h3>Ver desde el celular</h3>
        <p>Escanea este código (misma red WiFi que la PC):</p>
        <div id="qrcode"></div>
        <p>{dashboard_url}</p>
    </div>
    <script>
        new QRCode(document.getElementById("qrcode"), {{
            text: "{dashboard_url}",
            width: 200,
            height: 200
        }});
    </script>
</body>
</html>
"""


@app.get("/")
async def serve_index():
    local_ip = get_local_ip()
    dashboard_url = f"http://{local_ip}:8000/dashboard"
    return HTMLResponse(QR_PAGE_TEMPLATE.format(dashboard_url=dashboard_url))


@app.get("/dashboard")
async def serve_dashboard():
    static_path = get_resource_path(os.path.join("static", "index.html"))
    with open(static_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# Sirve app.js y cualquier otro archivo estático desde /static/
app.mount("/static", StaticFiles(directory=get_resource_path("static")), name="static")


# ==========================================================================
# GUARDADO DE RESULTADOS (misma lógica que dyno_gui.py: limpieza de
# outliers + carpeta por auto/motor+PI)
# ==========================================================================
def remove_outliers(df, column, threshold=0.12):
    """
    Detecta puntos donde el valor cae más de `threshold` respecto al
    promedio de sus dos vecinos, y los reemplaza por interpolación
    lineal -- deja los vecinos intactos (no es una media móvil ciega).
    """
    values = df[column].to_numpy(dtype=float)
    is_outlier = [False] * len(values)

    for i in range(1, len(values) - 1):
        neighbor_avg = (values[i - 1] + values[i + 1]) / 2
        if neighbor_avg == 0:
            continue
        drop = (neighbor_avg - values[i]) / neighbor_avg
        if drop > threshold:
            is_outlier[i] = True

    df = df.copy()
    df.loc[is_outlier, column] = None
    df[column] = df[column].interpolate(method="linear")
    return df


def sanitize(name):
    return re.sub(r'[<>:"/\\|?*\']', '', name).strip()


def build_output_folder(car_info, car_name, car_aspiration, has_boost_detected):
    """
    Construye: resultados/<auto>/<motor+PI>/
    Mismo patrón ya validado en la versión Qt -- reemplaza si coincide
    auto + cilindros + aspiración + boost + PI, crea carpeta nueva si cambia.
    """
    if car_info is None:
        car_folder = "auto_desconocido"
        engine_folder = "motor_desconocido"
    else:
        car_id = car_name if car_name else f"Auto_{car_info['CarOrdinal']}"
        car_folder = sanitize(car_id)

        cylinders = car_info.get("NumCylinders")
        pi = car_info.get("CarPerformanceIndex")
        cyl_part = f"{int(cylinders)}cyl" if cylinders else "motor"
        asp_part = f"_{car_aspiration}" if car_aspiration else ""
        boost_part = "_Boosted" if has_boost_detected else "_NA"
        pi_part = f"_PI{int(pi)}" if pi else ""
        engine_folder = sanitize(f"{cyl_part}{asp_part}{boost_part}{pi_part}")

    folder_path = os.path.join("resultados", car_folder, engine_folder)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


@app.post("/save")
async def save_results(request: Request):
    if not state.bin_edges or state.total_bins == 0:
        return JSONResponse({"error": "No hay datos capturados todavía."}, status_code=400)

    points = state.to_dict()["points"]
    if not points:
        return JSONResponse({"error": "No hay puntos válidos que guardar."}, status_code=400)

    df = pd.DataFrame(points).rename(columns={
        "rpm": "RPM", "power_w": "Power_W", "torque_nm": "Torque_Nm"
    }).sort_values("RPM").reset_index(drop=True)

    df_clean = remove_outliers(df, "Power_W", threshold=0.12)
    df_clean = remove_outliers(df_clean, "Torque_Nm", threshold=0.12)

    df_clean["HP"] = df_clean["Power_W"] / 745.7
    df_clean["Power_kW"] = df_clean["Power_W"] / 1000
    df_clean["Torque_lbft"] = df_clean["Torque_Nm"] * 0.7376

    folder_path = build_output_folder(
        state.car_info, state.car_name, state.car_aspiration, state.has_boost_detected
    )
    csv_path = os.path.join(folder_path, "dyno_result.csv")
    df_clean.to_csv(csv_path, index=False)

    # La imagen viaja como PNG en base64 desde el navegador (Plotly.toImage()
    # la genera del lado del cliente, ya que el servidor Python nunca
    # renderiza la gráfica -- Plotly.js vive enteramente en el navegador).
    image_saved = False
    try:
        body = await request.json()
        image_base64 = body.get("image_base64")
        if image_base64:
            # El data URL viene como "data:image/png;base64,AAAA..."
            header, encoded = image_base64.split(",", 1)
            png_bytes = base64.b64decode(encoded)
            png_path = os.path.join(folder_path, "dyno_result.png")
            with open(png_path, "wb") as f:
                f.write(png_bytes)
            image_saved = True
    except Exception as e:
        print(f"No se pudo guardar la imagen: {e}")

    print(f"Resultado guardado en {csv_path} ({len(df_clean)} puntos, imagen: {image_saved})")
    return JSONResponse({"folder": folder_path, "points": len(df_clean), "image_saved": image_saved})


# ==========================================================================
# ARRANQUE DEL SERVIDOR
# ==========================================================================


if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 55)
    print(" SERVIDOR FORZA DYNO INICIADO")
    print(f" PC:      http://127.0.0.1:8000")
    print(f" Celular: http://{local_ip}:8000  (misma red WiFi)")
    print("=" * 55)

    # threading.Timer no depende de que exista un event loop de asyncio
    # activo en este punto (uvicorn.run() todavía no lo ha creado) --
    # evita el DeprecationWarning de asyncio.get_event_loop() sin un
    # loop corriendo.
    import threading
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8000")).start()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")