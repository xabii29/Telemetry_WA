"""The small, explicit v1 packet model used between backend layers.

Fields are optional until a driver has supplied a verified value.  This avoids
the old convention of treating an unknown measurement as zero.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import time_ns
from typing import Any


@dataclass(frozen=True, slots=True)
class Vector3:
    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class VehicleIdentity:
    ordinal: int
    car_class: int | None = None
    performance_index: int | None = None
    drivetrain: str | None = None
    cylinders: int | None = None


@dataclass(frozen=True, slots=True)
class TelemetryPacket:
    """A normalized measurement frame, not a UI state or history buffer."""

    game_id: str
    source_timestamp_ms: int | None
    received_at_ns: int = field(default_factory=time_ns)
    vehicle: VehicleIdentity | None = None
    speed_mps: float | None = None
    position_m: Vector3 | None = None
    velocity_mps: Vector3 | None = None
    engine_rpm: float | None = None
    engine_idle_rpm: float | None = None
    engine_max_rpm: float | None = None
    power_w: float | None = None
    torque_nm: float | None = None
    boost: float | None = None
    fuel: float | None = None
    gear: int | None = None
    throttle: float | None = None
    brake: float | None = None
    clutch: float | None = None
    steering: float | None = None
    lap_number: int | None = None
    race_position: int | None = None
    track_id: int | None = None
    distance_m: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
