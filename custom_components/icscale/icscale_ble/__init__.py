"""Pure-Python BLE layer for ICOMON-protocol kitchen/coffee scales.

This subpackage has no Home Assistant dependencies and can be unit-tested or
reused standalone. The HA integration in the parent package wraps
:class:`IcScaleClient`.
"""

from __future__ import annotations

from .const import (
    NOTIFY_CHAR,
    SCALE_SERVICE,
    UNIT_LABELS,
    WRITE_CHAR,
    KitchenScaleUnit,
)
from .driver import IcScaleClient
from .models import DeviceInfo, ScaleState, WeightSample
from .parser import checksum_ok, parse_notification

__all__ = [
    "NOTIFY_CHAR",
    "SCALE_SERVICE",
    "UNIT_LABELS",
    "WRITE_CHAR",
    "KitchenScaleUnit",
    "DeviceInfo",
    "IcScaleClient",
    "ScaleState",
    "WeightSample",
    "checksum_ok",
    "parse_notification",
]
