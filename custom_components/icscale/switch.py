"""Switch platform for the ICOMON kitchen scale."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import IcScaleCoordinator
from .entity import IcScaleEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch platform."""
    coordinator: IcScaleCoordinator = entry.runtime_data
    async_add_entities([IcScaleAutoMeasureSwitch(coordinator)])


class IcScaleAutoMeasureSwitch(IcScaleEntity, SwitchEntity):
    """Switch for advertisement-driven automatic measurement.

    When on, HA automatically connects whenever the scale is seen advertising
    and streams weight (with idle auto-disconnect). When off, HA never
    auto-connects, leaving the scale's single BLE link free for the phone app;
    on-demand readings are still possible via the *Measure now* button.
    """

    _attr_translation_key = "auto_measure"
    _attr_icon = "mdi:auto-mode"

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "auto_measure")

    @property
    def is_on(self) -> bool:
        """Return True if automatic measurement is enabled."""
        return self.coordinator.enabled

    @property
    def available(self) -> bool:
        """Always available so the user can change modes at any time."""
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable automatic measurement."""
        await self.coordinator.async_set_enabled(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable automatic measurement (free the scale for the phone app)."""
        await self.coordinator.async_set_enabled(False)
        self.async_write_ha_state()
