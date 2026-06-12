"""BLE constants for ICOMON-protocol kitchen/coffee scales.

This module is pure Python and must not import Home Assistant.

Many rebranded kitchen/coffee scales share this same GATT profile.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Final


def _uuid16(short: str) -> str:
    """Expand a 16-bit Bluetooth SIG UUID into its 128-bit string form."""
    return f"0000{short}-0000-1000-8000-00805f9b34fb"


# --- GATT profile -----------------------------------------------------------
# Custom vendor service that identifies a kitchen scale in advertisements.
SCALE_SERVICE: Final = _uuid16("ffb0")
# Write-without-response: control commands (tare, unit, power off, ...).
WRITE_CHAR: Final = _uuid16("ffb1")
# Notifications: weight + unit frames.
NOTIFY_CHAR: Final = _uuid16("ffb2")

# Optional standard Device Information service (best effort).
DEVICE_INFO_SERVICE: Final = _uuid16("180a")
MANUFACTURER_NAME_CHAR: Final = _uuid16("2a29")
MODEL_NUMBER_CHAR: Final = _uuid16("2a24")
SERIAL_NUMBER_CHAR: Final = _uuid16("2a25")
FIRMWARE_REV_CHAR: Final = _uuid16("2a26")


# --- Notification frame package types (frame byte[1]) -----------------------
PKG_WEIGHT_STABLE: Final = 0xCA  # 202: stabilized weight
PKG_WEIGHT_UNSTABLE: Final = 0xCE  # 206: live/unstable weight
PKG_UNIT: Final = 0xCC  # 204: unit changed

# Device type byte embedded in every command frame (==4 for kitchen scale).
DEVICE_TYPE: Final = 0x04


class KitchenScaleUnit(IntEnum):
    """Weight unit codes."""

    G = 0
    ML = 1
    LB = 2
    OZ = 3
    MG = 4
    ML_MILK = 5
    FL_OZ_WATER = 6
    FL_OZ_MILK = 7


UNIT_LABELS: Final[dict[int, str]] = {
    KitchenScaleUnit.G: "g",
    KitchenScaleUnit.ML: "mL",
    KitchenScaleUnit.LB: "lb",
    KitchenScaleUnit.OZ: "oz",
    KitchenScaleUnit.MG: "mg",
    KitchenScaleUnit.ML_MILK: "mL (milk)",
    KitchenScaleUnit.FL_OZ_WATER: "fl oz",
    KitchenScaleUnit.FL_OZ_MILK: "fl oz (milk)",
}


# --- Command frames written to WRITE_CHAR (write-without-response) -----------
# These are the exact byte sequences emitted to control the scale.
# The last byte is a precomputed constant/checksum tail; emit literally.
# ``device_type`` (byte[1]) == 0x04.
#
# NOTE: verify these against real hardware on first use.
CMD_TARE: Final = bytes((0xAC, DEVICE_TYPE, 0xFE, 0x14, 0x01, 0x00, 0xCC))
CMD_POWER_OFF: Final = bytes((0xAC, DEVICE_TYPE, 0xFE, 0x00, 0x00, 0x00, 0xB0))
