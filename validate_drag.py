"""
VALIDACIÓN -- fuerza de arrastre aerodinámico (fuerza_arrastre en physics_model.py).

Objetivo doble:
  1. Confirmar cuál de los tres ejes (AccelerationX/Y/Z) es el
     LONGITUDINAL (el que importa para detectar "velocidad máxima
     sostenida"), comparándolos contra una aceleración calculada de
     forma independiente (derivada de la variación de Speed entre
     paquetes consecutivos).
  2. Registrar Power y Speed en los momentos de aceleración ~0, que es
     donde fuerza_arrastre() = Power / Speed tiene sentido físico real.

Cómo usarlo:
  1. Corre este script: python validate_drag.py
  2. Ve a una recta larga (mientras más larga mejor -- Le Mans, Nordschleife,
     cualquier recta donde puedas sostener el acelerador a fondo varios
     segundos seguidos) y ACELERA A FONDO en la marcha más alta hasta
     llegar a tu velocidad máxima real y quedarte ahí unos segundos.
  3. No hace falta hacer nada especial más que eso -- el script guarda
     TODO mientras corre (no solo los momentos de equilibrio), para que
     después se pueda filtrar y comparar con calma.
  4. Ctrl+C para detener.

Qué esperar al analizar el CSV después:
  - En el tramo de "velocidad máxima sostenida", Speed debería dejar de
    subir (curva plana) y la aceleración derivada (accel_derivada_speed)
    debería acercarse a 0.
  - Alguno de accel_x, accel_y, accel_z debería seguir ese mismo patrón
    (bajar a ~0 junto con accel_derivada_speed) -- ese es el eje
    longitudinal real. Los otros dos ejes deberían verse "ruidosos" o
    sin relación clara con el momento de equilibrio.
"""

import socket
import struct
import csv
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 8000
OUTPUT_CSV = "validacion_arrastre_wrx.csv"

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

CSV_COLUMNS = [
    "timestamp", "car_ordinal", "gear", "accel_pedal", "clutch",
    "speed_kmh", "speed_mps", "power_w", "rpm",
    "accel_x", "accel_y", "accel_z",
    "accel_derivada_speed_mps2",   # calculada aquí, comparar contra accel_x/y/z
    "fuerza_arrastre_N",            # solo si accel_derivada esta cerca de 0
]

# Umbral para considerar "velocidad máxima sostenida" -- ajustable si
# hace falta después de ver los primeros resultados.
TOLERANCIA_ACCEL = 0.15  # m/s^2


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Escuchando en {UDP_IP}:{UDP_PORT}")
    print(f"Guardando en {OUTPUT_CSV}")
    print("Ve a una recta larga, acelera a fondo hasta velocidad máxima")
    print("y mantente ahí unos segundos. Ctrl+C para detener.\n")

    rows_written = 0
    prev_speed_mps = None
    prev_timestamp = None

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

                now = time.time()
                speed_mps = row["Speed"]

                # --- Aceleración derivada de Speed entre paquetes consecutivos ---
                accel_derivada = None
                if prev_speed_mps is not None and prev_timestamp is not None:
                    dt = now - prev_timestamp
                    if dt > 0:
                        accel_derivada = (speed_mps - prev_speed_mps) / dt

                prev_speed_mps = speed_mps
                prev_timestamp = now

                # --- Fuerza de arrastre, solo si estamos en equilibrio ---
                fuerza = None
                if (accel_derivada is not None
                        and abs(accel_derivada) <= TOLERANCIA_ACCEL
                        and speed_mps > 1.0
                        and row["Accel"] >= 250):  # acelerador a fondo
                    fuerza = round(row["Power"] / speed_mps, 2)

                writer.writerow({
                    "timestamp": round(now, 3),
                    "car_ordinal": row["CarOrdinal"],
                    "gear": row["Gear"],
                    "accel_pedal": row["Accel"],
                    "clutch": row["Clutch"],
                    "speed_kmh": round(speed_mps * 3.6, 2),
                    "speed_mps": round(speed_mps, 3),
                    "power_w": round(row["Power"], 1),
                    "rpm": round(row["CurrentEngineRpm"], 1),
                    "accel_x": round(row["AccelerationX"], 4),
                    "accel_y": round(row["AccelerationY"], 4),
                    "accel_z": round(row["AccelerationZ"], 4),
                    "accel_derivada_speed_mps2": round(accel_derivada, 4) if accel_derivada is not None else None,
                    "fuerza_arrastre_N": fuerza,
                })
                rows_written += 1

                if rows_written % 60 == 0:
                    marca = " <- posible equilibrio" if fuerza is not None else ""
                    print(f"  {rows_written} filas | {speed_mps*3.6:.0f} km/h | "
                          f"accel_deriv={accel_derivada:.3f} m/s²{marca}" if accel_derivada is not None
                          else f"  {rows_written} filas...")

        except KeyboardInterrupt:
            print(f"\nDetenido. {rows_written} filas guardadas en {OUTPUT_CSV}")
            print("Comparte este archivo para analizar el eje longitudinal real")
            print("y la fuerza de arrastre en los tramos de velocidad máxima.")
        finally:
            sock.close()


if __name__ == "__main__":
    main()