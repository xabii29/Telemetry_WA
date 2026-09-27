"""
Replay de telemetría UDP grabada -- para desarrollo sin el juego encendido.

Lee una carpeta de captura generada por capture_udp.py (raw.bin +
index.csv) y retransmite los datagramas por UDP al puerto que use tu
servidor FastAPI (por defecto 8000), respetando el timing ORIGINAL
entre paquetes (columna t_ms de index.csv) -- así se siente como una
sesión real de manejo, con las mismas pausas y ráfagas que hubo en la
captura real, no un flujo artificial a ritmo constante.

Se repite en LOOP INFINITO hasta que lo detengas con Ctrl+C -- ideal
para dejarlo corriendo de fondo mientras iteras en el servidor o los
módulos del frontend, sin tener que encender el juego cada vez.

Uso:
    python replay_udp.py --capture-dir captura_20260801_012512
    python replay_udp.py
    python replay_udp.py --capture-dir /ruta/a/captura_001
    python replay_udp.py --port 8000 --speed 2.0   # el doble de rápido
    python replay_udp.py --once                     # una sola pasada, sin loop
"""

from __future__ import annotations

import argparse
import csv
import socket
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reproduce una captura UDP grabada, en loop, respetando el timing original."
    )
    parser.add_argument(
        "--capture-dir",
        default=".",
        help="Carpeta con raw.bin + index.csv (por defecto, la carpeta actual).",
    )
    parser.add_argument(
        "--host",
        default="192.168.1.102",
        help="A qué host mandar los paquetes (por defecto 127.0.0.1, tu propio servidor).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto UDP de destino -- debe coincidir con UDP_PORT de tu main.py (por defecto 8000).",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1,
        help="Multiplicador de velocidad de reproducción. 1.0 = tiempo real, 2.0 = el doble de rápido.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Reproducir una sola vez y detenerse, en vez de loop infinito.",
    )
    return parser.parse_args()


def load_capture(capture_dir: Path):
    """Carga los datagramas crudos en memoria, ya separados según index.csv."""
    raw_path = capture_dir / "raw.bin"
    index_path = capture_dir / "index.csv"

    if not raw_path.exists() or not index_path.exists():
        raise FileNotFoundError(
            f"No se encontró raw.bin o index.csv en {capture_dir.resolve()}"
        )

    with raw_path.open("rb") as f:
        raw_bytes = f.read()

    packets = []  # [(t_ms, bytes), ...]
    with index_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            offset = int(row["offset_bytes"])
            size = int(row["size_bytes"])
            t_ms = int(row["t_ms"])
            packets.append((t_ms, raw_bytes[offset : offset + size]))

    return packets


def main() -> int:
    args = parse_args()
    capture_dir = Path(args.capture_dir)

    print(f"Cargando captura desde: {capture_dir.resolve()}")
    packets = load_capture(capture_dir)
    print(f"{len(packets)} paquetes cargados.")

    if not packets:
        print("La captura no tiene paquetes -- nada que reproducir.")
        return 1

    duration_s = packets[-1][0] / 1000.0
    print(f"Duración original: {duration_s:.1f} s")
    print(f"Reproduciendo hacia {args.host}:{args.port} a velocidad x{args.speed}")
    print(f"Modo: {'una sola pasada' if args.once else 'LOOP INFINITO'}")
    print("Ctrl+C para detener.\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (args.host, args.port)

    loop_count = 0
    try:
        while True:
            loop_count += 1
            print(f"--- Vuelta {loop_count} ---")

            playback_start = time.monotonic()
            for t_ms, data in packets:
                # El tiempo que "debería" haber pasado desde el inicio de
                # esta vuelta, ajustado por el multiplicador de velocidad.
                target_elapsed = (t_ms / 1000.0) / args.speed
                actual_elapsed = time.monotonic() - playback_start
                sleep_time = target_elapsed - actual_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

                sock.sendto(data, dest)

            if args.once:
                print("\nReproducción completa (una sola pasada).")
                break

    except KeyboardInterrupt:
        print(f"\nDetenido por el usuario tras {loop_count} vuelta(s).")
    finally:
        sock.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#--capture-dir captura_20260801_012512