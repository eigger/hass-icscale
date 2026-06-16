"""Binary sensor platform for the ICOMON kitchen scale."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity


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


class IcScaleStableSensor(IcScaleEntity, RestoreEntity, BinarySensorEntity):
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

    async def async_added_to_hass(self) -> None:
        """Handle entity about to be added to hass."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None and last_state.state not in (None, "unknown", "unavailable"):
            stable = last_state.state == "on"
            from .icscale_ble import WeightSample
            if self.coordinator.state.weight is None:
                self.coordinator.state.weight = WeightSample(
                    grams=0.0,
                    stable=stable,
                )
            else:
                w = self.coordinator.state.weight
                self.coordinator.state.weight = WeightSample(
                    grams=w.grams,
                    stable=stable,
                    unit=w.unit,
                    precision=w.precision,
                )

