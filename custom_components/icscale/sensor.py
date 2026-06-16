"""Sensor platform for the ICOMON kitchen scale."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfMass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import IcScaleCoordinator
from .entity import IcScaleEntity
from .icscale_ble import UNIT_LABELS, ScaleState

GRAMS = UnitOfMass.GRAMS


@dataclass(frozen=True, kw_only=True)
class IcScaleSensorDescription(SensorEntityDescription):
    """Sensor description with a value extractor over the scale state."""

    value_fn: Callable[[ScaleState], float | int | str | None]


SENSORS: tuple[IcScaleSensorDescription, ...] = (
    IcScaleSensorDescription(
        key="weight",
        translation_key="weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=GRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:scale",
        value_fn=lambda s: s.weight.grams if s.weight else None,
    ),
    IcScaleSensorDescription(
        key="unit",
        translation_key="unit",
        icon="mdi:format-letter-case",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: UNIT_LABELS.get(int(s.unit)) if s.unit is not None else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up kitchen scale sensors."""
    coordinator: IcScaleCoordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        IcScaleSensor(coordinator, description) for description in SENSORS
    ]
    entities.append(IcScaleRssiSensor(coordinator))
    async_add_entities(entities)


class IcScaleSensor(IcScaleEntity, SensorEntity):
    """A scale-state-backed sensor."""

    entity_description: IcScaleSensorDescription

    def __init__(
        self,
        coordinator: IcScaleCoordinator,
        description: IcScaleSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | str | None:
        """Return the current value from the coordinator state."""
        return self.entity_description.value_fn(self.coordinator.state)

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        if self.entity_description.key == "unit" and self.coordinator.state.is_coffee:
            return False
        return super().available



class IcScaleRssiSensor(IcScaleEntity, SensorEntity):
    """Signal strength sensor sourced from advertisements."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the RSSI sensor."""
        super().__init__(coordinator, "rssi")

    @property
    def native_value(self) -> int | None:
        """Return the last advertised RSSI."""
        return self.coordinator.rssi

    @property
    def available(self) -> bool:
        """RSSI is available whenever we have a reading."""
        return self.coordinator.rssi is not None
