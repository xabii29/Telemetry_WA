"""Session-level behaviour derived from normalized packets."""
from __future__ import annotations

from .events import EventBus, TelemetryEvent
from .model import TelemetryPacket


class SessionTracker:
    """Detects vehicle changes without making any UI or storage decision."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self._vehicle_ordinal: int | None = None

    def accept(self, packet: TelemetryPacket) -> None:
        ordinal = packet.vehicle.ordinal if packet.vehicle else None
        if ordinal is not None and self._vehicle_ordinal not in (None, ordinal):
            self._bus.publish(TelemetryEvent("car_changed", {
                "previous_ordinal": self._vehicle_ordinal,
                "current_ordinal": ordinal,
            }))
        self._vehicle_ordinal = ordinal
        self._bus.publish(TelemetryEvent("packet", {"packet": packet.as_dict()}))
