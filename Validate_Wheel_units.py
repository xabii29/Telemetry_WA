"""
Script de VALIDACIÓN -- no es parte del dashboard todavía.

Objetivo: confirmar la unidad real de WheelRotSpeed antes de usar
physics_model.py con confianza.

Cómo usarlo:
  1. Corre este script.
  2. Maneja en línea recta, en cualquier marcha, a velocidad razonablemente
     constante durante unos segundos (no acelerando ni frenando fuerte).
  3. Observa los valores impresos: si asumiendo rad/s el diámetro de
     llanta calculado da un número físicamente razonable (~0.55-0.70 m
     para un auto deportivo), la unidad asumida es correcta.
  4. Si el diámetro sale absurdo (ej. 0.05 m o 15 m), prueba con la
     otra hipótesis (RPM en vez de rad/s) y compara.
"""

import socket
import struct
import math

UDP_IP = "0.0.0.0"
UDP_PORT = 8000

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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Escuchando en {UDP_IP}:{UDP_PORT} -- maneja en línea recta a velocidad constante.")
print("Ctrl+C para detener.\n")

print(f"{'Speed(km/h)':<14}{'WheelRotSpeed_RL':<20}{'Diametro si rad/s':<20}{'Diametro si RPM'}")

try:
    while True:
        data, addr = sock.recvfrom(2048)
        if len(data) != PACKET_SIZE:
            continue

        values = struct.unpack(FORMAT, data)
        row = dict(zip(FIELDS, values))

        if row["IsRaceOn"] != 1:
            continue

        speed_mps = row["Speed"]
        if speed_mps < 3.0:  # ignorar mientras casi no te muevas
            continue

        wheel_rot = row["WheelRotSpeed_RL"]  # RWD: rueda motriz trasera
        if wheel_rot == 0:
            continue

        speed_kmh = speed_mps * 3.6

        # Hipótesis 1: el campo viene en rad/s
        radio_si_rads = speed_mps / abs(wheel_rot)
        diametro_si_rads = radio_si_rads * 2

        # Hipótesis 2: el campo viene en RPM
        rot_rads_desde_rpm = abs(wheel_rot) * 2 * math.pi / 60
        radio_si_rpm = speed_mps / rot_rads_desde_rpm
        diametro_si_rpm = radio_si_rpm * 2

        print(f"{speed_kmh:<14.1f}{wheel_rot:<20.2f}{diametro_si_rads:<20.3f}{diametro_si_rpm:.3f}")

except KeyboardInterrupt:
    print("\nDetenido. Compara qué columna dio valores consistentes (~0.55-0.70 m)")
    print("mientras la velocidad cambiaba -- esa es la unidad real del campo.")
finally:
    sock.close()