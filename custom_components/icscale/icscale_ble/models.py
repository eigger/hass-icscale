"""Data models for parsed ICOMON kitchen-scale frames. Pure Python (no HA)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .const import KitchenScaleUnit


@dataclass(frozen=True)
class WeightSample:
    """A single weight reading decoded from a notification.

    ``grams`` is the signed weight converted to grams. ``unit`` is the unit the
    scale is currently displaying (the raw reading is always normalised to
    grams here for a stable Home Assistant sensor). ``stable`` is True for a
    settled reading (package type 0xCA) and False for a live one (0xCE).
    """

    grams: float
    stable: bool
    unit: KitchenScaleUnit | None = None
    precision: int = 0


@dataclass
class DeviceInfo:
    """Static GATT Device Information service values (best effort)."""

    manufacturer: str | None = None
    model: str | None = None
    serial: str | None = None
    firmware: str | None = None


@dataclass
class ScaleState:
    """Mutable, accumulated view of the scale shared with the HA layer."""

    weight: WeightSample | None = None
    unit: KitchenScaleUnit | None = None
    info: DeviceInfo = field(default_factory=DeviceInfo)
