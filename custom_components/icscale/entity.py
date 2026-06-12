"""Base entity for the ICOMON Kitchen Scale integration."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURER
from .coordinator import IcScaleCoordinator


class IcScaleEntity(Entity):
    """Common base wiring entities to the coordinator's push updates."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: IcScaleCoordinator, key: str) -> None:
        """Initialize the entity."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info tied to the BLE connection."""
        info = self.coordinator.state.info
        return DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, self.coordinator.address)},
            identifiers={(DOMAIN, self.coordinator.address)},
            manufacturer=info.manufacturer or MANUFACTURER,
            model=self.coordinator.model,
            name=self.coordinator.name,
            sw_version=info.firmware,
            serial_number=info.serial,
        )

    @property
    def available(self) -> bool:
        """Return entity availability from the coordinator."""
        return self.coordinator.available

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator updates."""
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_update))

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
