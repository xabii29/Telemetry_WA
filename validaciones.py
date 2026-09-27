"""
VALIDACIONES UNIFICADAS -- diámetro de llanta + ratio de transmisión.

Corre ambas pruebas a la vez mientras manejas normal. Cada paquete válido
se guarda como una fila en 'validaciones.csv', con toda la info cruda
necesaria para que ambos cálculos (y cualquier otro que se necesite
después) se puedan volver a hacer o revisar con calma, sin depender de
lo que se vea en la consola en el momento.

Cómo usarlo:
  1. (Opcional pero recomendado) Anota el índice de la marcha que vas a
     usar, desde la pantalla de tuning del juego, antes de manejar.
  2. Corre este script: python validaciones.py
  3. Maneja normal -- acelera, cambia de marcha, ve a velocidad
     constante en algún tramo. No hace falta nada especial, el script
     filtra solo las muestras válidas para cada cálculo.
  4. Ctrl+C para detener. Se guarda validaciones.csv con todo lo
     capturado, listo para analizar después.

Qué queda registrado en cada fila:
  - Datos crudos (RPM motor, velocidad, rueda, marcha, embrague)
  - Los DOS cálculos ya resueltos (diámetro de llanta, ratio de
    transmisión), cuando la fila cumple las condiciones de validez de
    cada uno -- si no las cumple, esa columna queda vacía en esa fila,
    pero la fila se guarda de todos modos (por si sirve para otro
    análisis después).
"""

import socket
import struct
import csv
import math
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 8000
OUTPUT_CSV = "validaciones_wrx.csv"

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

# Columnas del CSV de salida
CSV_COLUMNS = [
    "timestamp", "car_ordinal", "drivetrain_type", "gear", "clutch",
    "speed_kmh", "engine_rpm",
    "wheel_rot_FL", "wheel_rot_FR", "wheel_rot_RL", "wheel_rot_RR",
    "diametro_llanta_no_motriz_m",   # calculado solo si aplica
    "ratio_transmision_motriz",       # calculado solo si aplica
]


def calcular_diametro(speed_mps, wheel_rot_rads):
    """Diámetro rodante = (Speed / |WheelRotSpeed|) * 2, con WheelRotSpeed en rad/s."""
    if speed_mps < 3.0 or wheel_rot_rads == 0:
        return None
    radio = speed_mps / abs(wheel_rot_rads)
    return round(radio * 2, 4)


def calcular_ratio_transmision(engine_rpm, wheel_rot_rads, clutch):
    """Ratio motor/rueda, solo válido con embrague en extremos (0 o 255)."""
    if clutch not in (0, 255):
        return None
    if wheel_rot_rads == 0 or engine_rpm < 500:
        return None
    rpm_rueda = abs(wheel_rot_rads) * 60 / (2 * math.pi)
    if rpm_rueda == 0:
        return None
    return round(engine_rpm / rpm_rueda, 4)


def rueda_no_motriz(drivetrain_type, row):
    """Regresa WheelRotSpeed de una rueda NO motriz, según tracción. None si AWD."""
    if drivetrain_type == 0:    # FWD -> trasera no jala
        return row["WheelRotSpeed_RL"]
    elif drivetrain_type == 1:  # RWD -> delantera no jala
        return row["WheelRotSpeed_FL"]
    elif drivetrain_type == 2:  # RWD -> delantera no jala
            return row["WheelRotSpeed_FL"]
    else:                        # AWD -> ninguna es puramente no motriz
        return None


def rueda_motriz(drivetrain_type, row):
    """Regresa WheelRotSpeed de una rueda MOTRIZ, según tracción."""
    if drivetrain_type == 0:    # FWD -> delantera jala
        return row["WheelRotSpeed_FL"]
    elif drivetrain_type == 1:  # RWD -> trasera jala
        return row["WheelRotSpeed_RL"]
    else:                        # AWD -> cualquiera, con la ambigüedad ya conocida
        return row["WheelRotSpeed_RL"]


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Escuchando en {UDP_IP}:{UDP_PORT}")
    print(f"Guardando en {OUTPUT_CSV}")
    print("Maneja normal -- acelera, cambia de marcha, ve a velocidad constante.")
    print("Ctrl+C para detener y cerrar el archivo.\n")

    rows_written = 0
    last_gear = None

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        try:
            while True:
                data, addr = sock.recvfrom(2048)
                if len(data) != PACKET_SIZE:
                    continue

                values = struct.unpack(FORMAT, data)
                row = dict(zip(FIELDS, values))

                if row["IsRaceOn"] != 1:
                    continue

                drivetrain = row["DrivetrainType"]
                gear = row["Gear"]
                clutch = row["Clutch"]
                speed_mps = row["Speed"]
                engine_rpm = row["CurrentEngineRpm"]

                if gear != last_gear:
                    print(f"Marcha: {gear}")
                    last_gear = gear

                # --- Diámetro: usa la rueda NO motriz ---
                wheel_no_motriz = rueda_no_motriz(drivetrain, row)
                diametro = None
                if wheel_no_motriz is not None:
                    diametro = calcular_diametro(speed_mps, wheel_no_motriz)

                # --- Ratio de transmisión: usa la rueda MOTRIZ ---
                wheel_motriz = rueda_motriz(drivetrain, row)
                ratio = calcular_ratio_transmision(engine_rpm, wheel_motriz, clutch)

                writer.writerow({
                    "timestamp": round(time.time(), 3),
                    "car_ordinal": row["CarOrdinal"],
                    "drivetrain_type": drivetrain,
                    "gear": gear,
                    "clutch": clutch,
                    "speed_kmh": round(speed_mps * 3.6, 2),
                    "engine_rpm": round(engine_rpm, 1),
                    "wheel_rot_FL": round(row["WheelRotSpeed_FL"], 3),
                    "wheel_rot_FR": round(row["WheelRotSpeed_FR"], 3),
                    "wheel_rot_RL": round(row["WheelRotSpeed_RL"], 3),
                    "wheel_rot_RR": round(row["WheelRotSpeed_RR"], 3),
                    "diametro_llanta_no_motriz_m": diametro,
                    "ratio_transmision_motriz": ratio,
                })
                rows_written += 1

                if rows_written % 60 == 0:
                    print(f"  {rows_written} filas guardadas...")

        except KeyboardInterrupt:
            print(f"\nDetenido. {rows_written} filas guardadas en {OUTPUT_CSV}")
            print("Comparte este archivo para analizar diámetro de llanta y")
            print("ratio de transmisión juntos.")
        finally:
            sock.close()


if __name__ == "__main__":
    main()