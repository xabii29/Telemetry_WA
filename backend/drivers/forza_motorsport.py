"""Forza Motorsport (2023) UDP adapter.

This is intentionally a narrow first implementation: it decodes only the
fields required by the first dashboard modules.  Its layout is traced to the
legacy validation reference and guarded by tests; new fields must be added
with an independently captured fixture.
"""
from __future__ import annotations

import struct

from backend.telemetry.model import TelemetryPacket, Vector3, VehicleIdentity


class ForzaMotorsport2023Driver:
    game_id = "forza_motorsport_2023"
    packet_size = 331
    # Offsets are explicit instead of mirroring the legacy field-list structure.
    _is_race_on = struct.Struct("<i")
    _timestamp = struct.Struct("<I")
    _f32 = struct.Struct("<f")
    _i32 = struct.Struct("<i")
    _u16 = struct.Struct("<H")
    _u8 = struct.Struct("<B")
    _i8 = struct.Struct("<b")

    def probe(self, datagram: bytes) -> bool:
        return len(datagram) == self.packet_size

    def decode(self, datagram: bytes) -> TelemetryPacket | None:
        if not self.probe(datagram) or self._is_race_on.unpack_from(datagram, 0)[0] != 1:
            return None

        f = lambda offset: self._f32.unpack_from(datagram, offset)[0]
        i = lambda offset: self._i32.unpack_from(datagram, offset)[0]
        return TelemetryPacket(
            game_id=self.game_id,
            source_timestamp_ms=self._timestamp.unpack_from(datagram, 4)[0],
            engine_max_rpm=f(8), engine_idle_rpm=f(12), engine_rpm=f(16),
            velocity_mps=Vector3(f(32), f(36), f(40)),
            vehicle=VehicleIdentity(
                ordinal=i(212), car_class=i(216), performance_index=i(220),
                drivetrain={0: "fwd", 1: "rwd", 2: "awd"}.get(i(224)),
                cylinders=i(228),
            ),
            position_m=Vector3(f(232), f(236), f(240)),
            speed_mps=f(244), power_w=f(248), torque_nm=f(252),
            boost=f(272), fuel=f(276), distance_m=f(280),
            lap_number=self._u16.unpack_from(datagram, 300)[0],
            race_position=self._u8.unpack_from(datagram, 302)[0],
            throttle=self._u8.unpack_from(datagram, 303)[0] / 255,
            brake=self._u8.unpack_from(datagram, 304)[0] / 255,
            clutch=self._u8.unpack_from(datagram, 305)[0] / 255,
            steering=self._i8.unpack_from(datagram, 308)[0] / 127,
            gear=self._u8.unpack_from(datagram, 307)[0], track_id=i(311),
        )
