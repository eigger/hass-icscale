"""Shared typing helpers for the ICOMON Kitchen Scale integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import IcScaleCoordinator

IcScaleConfigEntry: TypeAlias = "ConfigEntry[IcScaleCoordinator]"
