from backend.telemetry.events import EventBus
from backend.telemetry.model import TelemetryPacket, VehicleIdentity
from backend.telemetry.session import SessionTracker


def test_vehicle_change_is_announced_before_its_packet() -> None:
    events = []
    bus = EventBus()
    bus.subscribe("car_changed", events.append)
    tracker = SessionTracker(bus)

    tracker.accept(TelemetryPacket(game_id="forza", source_timestamp_ms=1, vehicle=VehicleIdentity(1)))
    tracker.accept(TelemetryPacket(game_id="forza", source_timestamp_ms=2, vehicle=VehicleIdentity(2)))

    assert len(events) == 1
    assert events[0].payload == {"previous_ordinal": 1, "current_ordinal": 2}
