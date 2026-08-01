import struct

from backend.drivers.forza_motorsport import ForzaMotorsport2023Driver


def packet() -> bytearray:
    data = bytearray(331)
    struct.pack_into("<iI", data, 0, 1, 1200)
    struct.pack_into("<fff", data, 8, 8000.0, 900.0, 4200.0)
    struct.pack_into("<fff", data, 32, 1.0, 2.0, 3.0)
    struct.pack_into("<iiiii", data, 212, 123, 4, 700, 1, 6)
    struct.pack_into("<fff", data, 232, 10.0, 20.0, 30.0)
    struct.pack_into("<ffffff", data, 244, 55.0, 100_000.0, 250.0, 0.5, 8.0, 900.0)
    struct.pack_into("<HB", data, 300, 3, 2)
    struct.pack_into("<BBBBBbbb", data, 303, 255, 128, 0, 0, 4, -64, 0, 0)
    struct.pack_into("<i", data, 311, 99)
    return data


def test_decodes_the_initial_forza_surface() -> None:
    decoded = ForzaMotorsport2023Driver().decode(packet())

    assert decoded is not None
    assert decoded.vehicle.ordinal == 123
    assert decoded.vehicle.drivetrain == "rwd"
    assert decoded.position_m.z == 30.0
    assert decoded.speed_mps == 55.0
    assert decoded.throttle == 1.0
    assert decoded.brake == 128 / 255
    assert decoded.gear == 4
    assert decoded.track_id == 99


def test_rejects_wrong_size_and_non_race_frame() -> None:
    driver = ForzaMotorsport2023Driver()
    assert driver.decode(b"not a packet") is None
    data = packet()
    struct.pack_into("<i", data, 0, 0)
    assert driver.decode(data) is None
