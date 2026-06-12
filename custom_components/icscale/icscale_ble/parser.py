"""Frame parser for ICOMON kitchen-scale notifications. Pure Python (no HA).

Notification frame layout:

    byte[0]        header / sync
    byte[1]        package_type  (0xCA stable, 0xCE unstable, 0xCC unit)
    byte[2]        flag: bit0 = sign (1 -> negative), bits1..3 = precision (0-7)
    byte[3..5]     weight magnitude, 24-bit BIG-ENDIAN, unsigned
    byte[6]        unit code / reserved (still covered by the checksum)
    byte[7]        checksum = (b[2]+b[3]+b[4]+b[5]+b[6]) & 0xFF

The measure payload is 4 bytes (flag + 3 weight bytes); the magnitude is read as
unsigned and the displayed value is ``magnitude / 10**precision`` with the sign
applied from ``flag`` bit 0.
"""

from __future__ import annotations

from .const import (
    PKG_UNIT,
    PKG_WEIGHT_STABLE,
    PKG_WEIGHT_UNSTABLE,
    KitchenScaleUnit,
)
from .models import WeightSample

MIN_FRAME_LEN = 8


def _checksum(data: bytes) -> int:
    """Native checksum: low byte of the sum of payload bytes [2..6]."""
    return (data[2] + data[3] + data[4] + data[5] + data[6]) & 0xFF


def checksum_ok(data: bytes) -> bool:
    """Return True when the frame's trailing checksum byte matches."""
    return len(data) >= MIN_FRAME_LEN and data[7] == _checksum(data)


def _as_unit(code: int) -> KitchenScaleUnit | None:
    try:
        return KitchenScaleUnit(code)
    except ValueError:
        return None


def parse_notification(data: bytes) -> WeightSample | None:
    """Decode a NOTIFY_CHAR frame into a :class:`WeightSample`.

    Returns ``None`` for frames that are too short or carry a package type we
    do not model. Checksum mismatches are *not* fatal (so a slightly different
    hardware variant still surfaces data); callers may use :func:`checksum_ok`
    to gate on integrity.
    """
    if len(data) < MIN_FRAME_LEN:
        return None

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

    unit = _as_unit(data[6])

    return WeightSample(
        grams=value,
        stable=(pkg == PKG_WEIGHT_STABLE),
        unit=unit,
        precision=precision,
    )
