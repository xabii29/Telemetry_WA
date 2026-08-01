"""Composition root; framework transport can be attached here without changing drivers."""
from backend.drivers.forza_motorsport import ForzaMotorsport2023Driver
from backend.telemetry.events import EventBus
from backend.telemetry.session import SessionTracker


class TelemetryApplication:
    def __init__(self) -> None:
        self.bus = EventBus()
        self.driver = ForzaMotorsport2023Driver()
        self.session = SessionTracker(self.bus)

    def ingest(self, datagram: bytes) -> None:
        packet = self.driver.decode(datagram)
        if packet is not None:
            self.session.accept(packet)
