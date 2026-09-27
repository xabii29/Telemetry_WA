"""
Captura de telemetría UDP cruda — Forza Motorsport (2023)

Este script NO decodifica ni interpreta la telemetría. Su único trabajo es
escuchar el puerto UDP configurado en el juego y guardar los datagramas
crudos en disco, junto con metadatos mínimos (tamaño, timestamp relativo).

Uso previsto: generar el fixture trazable que hoy falta en el proyecto
(ver docs/PROTOCOL.md y docs/HANDOFF.md — "Próximo paso recomendado").

No pertenece a backend/ ni a legacy/. Es una herramienta puntual, fuera de
la arquitectura del producto, que sirve para producir evidencia real.

--------------------------------------------------------------------------
Configuración en Forza Motorsport (2023):

    Configuración > HUD y visualización > Datos de telemetría (Data Out)
    - Activar: Sí
    - IP de destino: la IP de esta máquina (127.0.0.1 si el juego corre
      en la misma PC, o la IP LAN si corre en otra consola/PC)
    - Puerto de destino: el mismo que uses aquí con --port (por defecto 5300)
    - Formato de datos: "Car Dash" o "Sled" (cualquiera sirve para esta
      primera captura; anota cuál usaste, porque cambia el tamaño y
      layout del paquete)

--------------------------------------------------------------------------
Uso:

    python capture_udp.py
    python capture_udp.py --port 5300 --out captura_001 --max-packets 2000
    python capture_udp.py --duration 60

Salida (todo dentro de --out, por defecto ./captura_<timestamp>/):

    raw.bin        Todos los datagramas concatenados, sin separadores.
    index.csv      Una fila por datagrama: offset, tamaño en bytes,
                   timestamp relativo en ms desde el primer paquete.
    manifest.json  Metadatos de la sesión de captura (host, puerto,
                   cantidad de paquetes, duración, tamaños vistos).

Detener con Ctrl+C en cualquier momento; el script cierra los archivos
de forma segura y escribe el manifest con lo capturado hasta ese punto.
"""

from __future__ import annotations

import argparse
import csv
import json
import socket
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Captura datagramas UDP crudos de telemetría de Forza Motorsport (2023)."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Interfaz local donde escuchar (por defecto 0.0.0.0, todas las interfaces).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto UDP de escucha. Debe coincidir con el configurado en el juego (por defecto 5300).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Carpeta de salida. Por defecto ./captura_<timestamp>/",
    )
    parser.add_argument(
        "--max-packets",
        type=int,
        default=None,
        help="Detener automáticamente tras capturar N datagramas.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Detener automáticamente tras N segundos.",
    )
    parser.add_argument(
        "--note",
        default="",
        help="Nota libre para el manifest (ej. 'Car Dash, Circuito de Spa, Aston Martin').",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    out_dir = Path(args.out) if args.out else Path(
        f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    out_dir.mkdir(parents=True, exist_ok=False)

    raw_path = out_dir / "raw.bin"
    index_path = out_dir / "index.csv"
    manifest_path = out_dir / "manifest.json"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    sock.settimeout(1.0)  # permite revisar duración/Ctrl+C sin bloquear para siempre

    print(f"Escuchando UDP en {args.host}:{args.port}")
    print(f"Guardando en: {out_dir.resolve()}")
    print("Configura el juego para enviar telemetría a este puerto.")
    print("Presiona Ctrl+C para detener la captura.\n")

    packet_count = 0
    size_counter: Counter[int] = Counter()
    first_ts: float | None = None
    last_ts: float | None = None
    start_wall_clock = datetime.now(timezone.utc)
    offset = 0

    try:
        with raw_path.open("wb") as raw_file, index_path.open(
            "w", newline=""
        ) as index_file:
            writer = csv.writer(index_file)
            writer.writerow(["packet_index", "offset_bytes", "size_bytes", "t_ms"])

            while True:
                if args.max_packets is not None and packet_count >= args.max_packets:
                    print(f"\nLímite de {args.max_packets} paquetes alcanzado.")
                    break
                if args.duration is not None and first_ts is not None:
                    if (time.monotonic() - first_ts) >= args.duration:
                        print(f"\nDuración de {args.duration}s alcanzada.")
                        break

                try:
                    data, addr = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError as exc:
                    print(f"\nError de socket: {exc}", file=sys.stderr)
                    break

                now = time.monotonic()
                if first_ts is None:
                    first_ts = now
                    print(f"Primer datagrama recibido desde {addr[0]}:{addr[1]}")
                last_ts = now
                t_ms = int((now - first_ts) * 1000)

                raw_file.write(data)
                writer.writerow([packet_count, offset, len(data), t_ms])

                offset += len(data)
                size_counter[len(data)] += 1
                packet_count += 1

                if packet_count % 100 == 0:
                    sizes = ", ".join(f"{s}B x{c}" for s, c in size_counter.most_common(3))
                    print(f"  {packet_count} paquetes capturados ({sizes})", end="\r")

    except KeyboardInterrupt:
        print("\nCaptura detenida por el usuario (Ctrl+C).")
    finally:
        sock.close()

    duration_s = (last_ts - first_ts) if (first_ts and last_ts) else 0.0

    manifest = {
        "captured_at_utc": start_wall_clock.isoformat(),
        "host": args.host,
        "port": args.port,
        "packet_count": packet_count,
        "duration_seconds": round(duration_s, 3),
        "packet_sizes_seen": dict(size_counter),
        "note": args.note,
        "raw_file": raw_path.name,
        "index_file": index_path.name,
        "warning": (
            "Captura cruda, no interpretada. No asumir formato ni offsets sin "
            "contrastar contra docs/PROTOCOL.md y sin documentar la fuente en "
            "docs/DECISIONS.md o docs/LEGACY_FINDINGS.md."
        ),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n\nResumen de captura:")
    print(f"  Paquetes: {packet_count}")
    print(f"  Duración: {duration_s:.2f} s")
    print(f"  Tamaños vistos: {dict(size_counter)}")
    print(f"  Manifest: {manifest_path}")

    if packet_count == 0:
        print(
            "\nNo se recibió ningún datagrama. Verifica que:\n"
            "  1) El juego tenga la telemetría activada (Data Out).\n"
            "  2) La IP de destino en el juego apunte a esta máquina.\n"
            "  3) El puerto coincida con --port.\n"
            "  4) El firewall no esté bloqueando el puerto UDP."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())