"""Stable boundary between a game's native datagram and the core."""
from __future__ import annotations

from typing import Protocol

from backend.telemetry.model import TelemetryPacket


class Driver(Protocol):
    game_id: str

    def probe(self, datagram: bytes) -> bool: ...

    def decode(self, datagram: bytes) -> TelemetryPacket | None: ...
