"""Frame parser tests."""

from __future__ import annotations

from custom_components.icscale.icscale_ble import checksum_ok, parse_notification


def _kitchen(pkg: int, flag: int, magnitude: int, unit: int = 0) -> bytes:
    body = [flag, (magnitude >> 16) & 0xFF, (magnitude >> 8) & 0xFF, magnitude & 0xFF, unit]
    return bytes([0xAC, pkg, *body, sum(body) & 0xFF])


def test_kitchen_stable_frame() -> None:
    frame = _kitchen(0xCA, 0x02, 1234)  # precision 1 -> 123.4
    assert checksum_ok(frame)
    sample = parse_notification(frame)
    assert sample is not None
    assert sample.stable
    assert sample.grams == 123.4


def test_kitchen_negative_unstable_frame() -> None:
    sample = parse_notification(_kitchen(0xCE, 0x01, 50))
    assert sample is not None
    assert not sample.stable
    assert sample.grams == -50


def test_kitchen_bad_checksum() -> None:
    frame = bytearray(_kitchen(0xCA, 0x00, 10))
    frame[7] ^= 0xFF
    assert not checksum_ok(bytes(frame))


def test_short_frame_ignored() -> None:
    assert parse_notification(b"\x00\x01") is None


def test_unknown_package_ignored() -> None:
    assert parse_notification(_kitchen(0x11, 0x00, 10)) is None


def test_coffee_frame() -> None:
    frame = bytearray(16)
    frame[2] = 0x01  # positive, stable
    frame[5], frame[6] = 0x03, 0xE8  # 1000 -> 1.0 g
    sample = parse_notification(bytes(frame))
    assert sample is not None
    assert sample.stable
    assert sample.grams == 1.0


def test_is_unit_frame() -> None:
    from custom_components.icscale.icscale_ble.parser import is_unit_frame

    assert is_unit_frame(_kitchen(0xCC, 0x00, 0, unit=1))
    assert not is_unit_frame(_kitchen(0xCA, 0x00, 10))
