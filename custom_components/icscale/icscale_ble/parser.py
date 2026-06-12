"""Frame parser for ICOMON-family kitchen/coffee scale notifications.

Two notification frame variants are supported and auto-detected by length.

Coffee-scale variant (long frame, more than 14 bytes):
    byte[2]      status: high nibble selects sign, low nibble == 1 -> stable
    byte[3..6]   weight magnitude = (b3 & 0x0F)<<24 | b4<<16 | b5<<8 | b6
    grams = (+/-) magnitude / 1000

Kitchen-scale variant (8-byte frame):
    byte[1]      package_type: 0xCA stable, 0xCE unstable, 0xCC unit
    byte[2]      flag: bit0 = sign (1 -> negative), bits1..3 = precision (0-7)
    byte[3..5]   weight magnitude, 24-bit big-endian
    byte[6]      unit code (covered by the checksum)
    byte[7]      checksum = (b[2]+b[3]+b[4]+b[5]+b[6]) & 0xFF
    grams = (+/-) magnitude / 10**precision
"""

from __future__ import annotations

from .const import (
    PKG_UNIT,
    PKG_WEIGHT_STABLE,
    PKG_WEIGHT_UNSTABLE,
    KitchenScaleUnit,
)
from .models import WeightSample

# A coffee-scale frame is longer than this; a kitchen-scale frame is shorter.
COFFEE_MIN_LEN = 14
KITCHEN_FRAME_LEN = 8


def _checksum(data: bytes) -> int:
    """Kitchen-scale checksum: low byte of the sum of payload bytes [2..6]."""
    return (data[2] + data[3] + data[4] + data[5] + data[6]) & 0xFF


def checksum_ok(data: bytes) -> bool:
    """Return True for a kitchen-scale frame whose trailing checksum matches.

    Always True for coffee-scale frames (that variant carries no checksum).
    """
    if len(data) > COFFEE_MIN_LEN:
        return True
    return len(data) >= KITCHEN_FRAME_LEN and data[7] == _checksum(data)


def _as_unit(code: int) -> KitchenScaleUnit | None:
    try:
        return KitchenScaleUnit(code)
    except ValueError:
        return None


def _parse_coffee(data: bytes) -> WeightSample:
    """Decode the long coffee-scale frame."""
    status = data[2]
    negative = (status >> 4) in (0x8, 0xC)
    stable = (status & 0x0F) == 0x01
    magnitude = (
        ((data[3] & 0x0F) << 24) | (data[4] << 16) | (data[5] << 8) | data[6]
    )
    grams = magnitude / 1000.0
    if negative:
        grams = -grams
    return WeightSample(grams=grams, stable=stable, unit=None, precision=0)


def _parse_kitchen(data: bytes) -> WeightSample | None:
    """Decode the 8-byte kitchen-scale frame."""
    pkg = data[1]
    if pkg not in (PKG_WEIGHT_STABLE, PKG_WEIGHT_UNSTABLE, PKG_UNIT):
        return None

    flag = data[2]
    negative = bool(flag & 0x01)
    precision = (flag >> 1) & 0x07

    magnitude = (data[3] << 16) | (data[4] << 8) | data[5]
    value = magnitude / (10**precision)
    if negative:
        value = -value

    return WeightSample(
        grams=value,
        stable=(pkg == PKG_WEIGHT_STABLE),
        unit=_as_unit(data[6]),
        precision=precision,
    )


def parse_notification(data: bytes) -> WeightSample | None:
    """Decode a NOTIFY_CHAR frame into a :class:`WeightSample`.

    Auto-detects the frame variant by length: long frames use the coffee-scale
    layout, 8..14-byte frames use the kitchen-scale layout. Returns ``None`` for
    frames that are too short or carry an unmodelled package type.
    """
    if len(data) > COFFEE_MIN_LEN:
        return _parse_coffee(data)
    if len(data) >= KITCHEN_FRAME_LEN:
        return _parse_kitchen(data)
    return None
