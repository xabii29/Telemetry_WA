import socket
import struct
import csv
import os
import re

UDP_IP = "0.0.0.0"
UDP_PORT = 8000

name = "pruebas_pista"
patron = re.compile(rf"{name}_(\d+)\.csv")

numeros =[]
for archivo in os.listdir(os.curdir):
    coincide = patron.match(archivo)
    if coincide:
        numeros.append(int(coincide.group(1)))
if numeros:
    n_idx = max(numeros)+1
    OUTPUT_CSV = f"{name}_{n_idx}.csv"
else:
    OUTPUT_CSV = name + ".csv"
FORMAT = (
    "<"
    "i" "I"
    "f f f"
    "f f f" 
    "f f f" 
    "f f f" 
    "f f f"
    "f f f f" 
    "f f f f" 
    "f f f f"
    "i i i i"
    "f f f f" 
    "f f f f" 
    "f f f f" 
    "f f f f" 
    "f f f f"
    "i i i i" 
    "i"
    "f f f"
    "f" "f" "f"
    "f f f f" 
    "f" "f" "f"
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
    "Pista", "PositionX", "PositionY", "PositionZ", "DistanceTraveled"         
]


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Escuchando en {UDP_IP}:{UDP_PORT}")
    print(f"Guardando en {OUTPUT_CSV}")

    rows_written = 0

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

                writer.writerow({
                    "Pista" : row["TrackOrdinal"],
                    "PositionX": row["PositionX"],
                    "PositionY": row["PositionY"],
                    "PositionZ": row["PositionZ"],
                    "DistanceTraveled": row["DistanceTraveled"]
                })
                rows_written += 1

                if rows_written % 60 == 0:
                    print(f"  {rows_written} filas |")

        except KeyboardInterrupt:
            print(f"\nDetenido. {rows_written} filas guardadas en {OUTPUT_CSV}")
            print("Este archivo guarda los valores de posicion para mapear circuitos")
        finally:
            sock.close()


if __name__ == "__main__":
    main()