"""Sensor platform for the ICOMON kitchen scale."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util


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
    is_coffee = entry.data.get("is_coffee", False)

    entities: list[SensorEntity] = []
    for description in SENSORS:
        if description.key == "unit" and is_coffee:
            continue
        entities.append(IcScaleSensor(coordinator, description))

    entities.append(IcScaleRssiSensor(coordinator))
    entities.append(IcScaleLastErrorSensor(coordinator))
    entities.append(IcScaleErrorCountSensor(coordinator))
    async_add_entities(entities)



class IcScaleSensor(IcScaleEntity, RestoreEntity, SensorEntity):
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

    async def async_added_to_hass(self) -> None:
        """Handle entity about to be added to hass."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None and last_state.state not in (None, "unknown", "unavailable"):
            if self.entity_description.key == "weight":
                try:
                    val = float(last_state.state)
                    from .icscale_ble import WeightSample
                    if self.coordinator.state.weight is None:
                        self.coordinator.state.weight = WeightSample(
                            grams=val,
                            stable=True,
                        )
                    else:
                        w = self.coordinator.state.weight
                        self.coordinator.state.weight = WeightSample(
                            grams=val,
                            stable=w.stable,
                            unit=w.unit,
                            precision=w.precision,
                        )
                except (ValueError, TypeError):
                    pass
            elif self.entity_description.key == "unit":
                from .icscale_ble import UNIT_LABELS
                for unit_enum, label in UNIT_LABELS.items():
                    if label == last_state.state:
                        self.coordinator.state.unit = unit_enum
                        break


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


# Attributes Home Assistant adds to a state itself; they are not part of a report.
_HA_STATE_ATTRIBUTES = frozenset(
    {
        "friendly_name",
        "icon",
        "device_class",
        "entity_category",
        "entity_picture",
        "restored",
        "supported_features",
    }
)
_UNRESTORABLE = (None, "unknown", "unavailable")


class _IcScaleReportsEntity(IcScaleEntity, RestoreEntity, SensorEntity):
    """Base for diagnostics that read the coordinator's session reports.

    They survive a restart: a failure at 3 am is still readable after Home
    Assistant restarted, because a success never erases the evidence.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_added_to_hass(self) -> None:
        """Subscribe to new reports and restore what the last run recorded."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.reports.add_listener(self._handle_report)
        )
        if (last_state := await self.async_get_last_state()) is not None:
            self._restore(last_state.state, dict(last_state.attributes))

    def _restore(self, state: str, attributes: dict[str, Any]) -> None:
        """Seed the reports from the previous run, unless a new one has begun."""
        raise NotImplementedError

    @callback
    def _handle_report(self) -> None:
        self.async_write_ha_state()


class IcScaleLastErrorSensor(_IcScaleReportsEntity):
    """When a BLE session last failed, with that session's breakdown.

    The attributes say which stage failed, over which radio, and what it most
    likely means. They are kept until the next failure. A scale that is simply
    asleep is not an error: connect attempts skipped for it are not recorded.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-alert-outline"
    _attr_translation_key = "last_error"

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the last error sensor."""
        super().__init__(coordinator, "last_error")

    @property
    def native_value(self) -> datetime | None:
        """When the last failed session ended."""
        return self.coordinator.reports.last_failure_at

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """The breakdown of the session that failed at this time."""
        return self.coordinator.reports.last_failure

    def _restore(self, state: str, attributes: dict[str, Any]) -> None:
        reports = self.coordinator.reports
        if reports.last_failure is not None or state in _UNRESTORABLE:
            return
        failed_at = dt_util.parse_datetime(state)
        if failed_at is None:
            return
        reports.last_failure_at = dt_util.as_utc(failed_at)
        reports.last_failure = {
            key: value
            for key, value in attributes.items()
            if key not in _HA_STATE_ATTRIBUTES
        }


class IcScaleErrorCountSensor(_IcScaleReportsEntity):
    """How many BLE sessions have failed (connects and commands)."""

    _attr_icon = "mdi:alert-circle-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_translation_key = "error_count"

    def __init__(self, coordinator: IcScaleCoordinator) -> None:
        """Initialize the error count sensor."""
        super().__init__(coordinator, "error_count")

    @property
    def native_value(self) -> int:
        """Failed sessions so far."""
        return self.coordinator.reports.failures

    def _restore(self, state: str, attributes: dict[str, Any]) -> None:
        reports = self.coordinator.reports
        if reports.failures or state in _UNRESTORABLE:
            return
        try:
            reports.failures = int(float(state))
        except ValueError:
            return
