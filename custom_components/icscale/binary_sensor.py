"""Binary sensor platform for the ICOMON kitchen scale."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import IcScaleCoordinator
from .entity import IcScaleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up kitchen scale binary sensors."""
    coordinator: IcScaleCoordinator = entry.runtime_data
    async_add_entities(
        [
            IcScaleConnectivitySensor(coordinator),
            IcScaleStableSensor(coordinator),
        ]
    )


class IcScaleConnectivitySensor(IcScaleEntity, BinarySensorEntity):
    """Reports whether the BLE link to the scale is currently up."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, "connectivity")

    @property
    def is_on(self) -> bool:
        """Return True while the scale is connected."""
        return self.coordinator.connected

    @property
    def available(self) -> bool:
        """Always available so it can report the disconnected state too."""
        return True


class IcScaleStableSensor(IcScaleEntity, BinarySensorEntity):
    """Reports whether the latest weight reading is settled (stable)."""

    _attr_translation_key = "stable"
    _attr_icon = "mdi:scale-balance"

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the stability sensor."""
        super().__init__(coordinator, "stable")

    @property
    def is_on(self) -> bool | None:
        """Return True when the last weight frame was a stable reading."""
        weight = self.coordinator.state.weight
        return weight.stable if weight is not None else None
