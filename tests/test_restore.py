"""State restore and coffee-type detection guards."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from custom_components.icscale.binary_sensor import IcScaleStableSensor
from custom_components.icscale.coordinator import IcScaleCoordinator
from custom_components.icscale.icscale_ble import ScaleState, WeightSample
from custom_components.icscale.sensor import SENSORS, IcScaleSensor


def _coordinator(state: ScaleState):
    return SimpleNamespace(
        state=state, address="AA:BB:CC:DD:EE:01", async_add_listener=lambda cb: lambda: None
    )


def _restore(entity, value: str) -> None:
    async def _last():
        return SimpleNamespace(state=value)

    entity.async_get_last_state = _last
    entity.async_on_remove = lambda *_: None


async def test_weight_restore_does_not_invent_a_sample() -> None:
    state = ScaleState()
    entity = IcScaleSensor(_coordinator(state), SENSORS[0])
    _restore(entity, "12.5")
    await entity.async_added_to_hass()
    assert state.weight is None
    assert entity.native_value == 12.5


async def test_weight_restore_never_overrides_a_live_reading() -> None:
    state = ScaleState(weight=WeightSample(grams=99.0, stable=False))
    entity = IcScaleSensor(_coordinator(state), SENSORS[0])
    _restore(entity, "12.5")
    await entity.async_added_to_hass()
    assert state.weight == WeightSample(grams=99.0, stable=False)
    assert entity.native_value == 99.0


async def test_stable_restore_does_not_touch_shared_state() -> None:
    state = ScaleState()
    entity = IcScaleStableSensor(_coordinator(state))
    _restore(entity, "on")
    await entity.async_added_to_hass()
    assert state.weight is None
    assert entity.is_on is True

    state.weight = WeightSample(grams=1.0, stable=False)
    assert entity.is_on is False


def test_coffee_type_is_saved_once() -> None:
    hass = MagicMock()
    coordinator = IcScaleCoordinator.__new__(IcScaleCoordinator)
    coordinator.hass = hass
    coordinator.entry = SimpleNamespace(data={})
    coordinator._coffee_type_saving = False
    coordinator._last_weight_value = None
    coordinator._last_weight_change = None
    coordinator._async_save_coffee_scale_type = MagicMock()

    state = ScaleState(is_coffee=True)
    coordinator._on_client_update(state)
    coordinator._on_client_update(state)

    assert hass.async_create_task.call_count == 1


def test_stable_weight_follows_stable_frames_and_holds() -> None:
    from custom_components.icscale.sensor import IcScaleStableWeightSensor

    state = ScaleState()
    entity = IcScaleStableWeightSensor(_coordinator(state))
    entity.async_write_ha_state = lambda: None
    assert entity.native_value is None

    state.weight = WeightSample(grams=10.0, stable=False)
    entity._handle_update()
    assert entity.native_value is None

    state.weight = WeightSample(grams=12.0, stable=True)
    entity._handle_update()
    state.weight = WeightSample(grams=12.5, stable=True)
    entity._handle_update()
    assert entity.native_value == 12.5

    state.weight = WeightSample(grams=30.0, stable=False)
    entity._handle_update()
    assert entity.native_value == 12.5


async def test_stable_weight_restore() -> None:
    from custom_components.icscale.sensor import IcScaleStableWeightSensor

    entity = IcScaleStableWeightSensor(_coordinator(ScaleState()))
    _restore(entity, "7.5")
    await entity.async_added_to_hass()
    assert entity.native_value == 7.5


async def test_coffee_save_failure_resets_guard() -> None:
    hass = MagicMock()
    hass.config_entries.async_update_entry.side_effect = RuntimeError("boom")
    coordinator = IcScaleCoordinator.__new__(IcScaleCoordinator)
    coordinator.hass = hass
    coordinator.entry = SimpleNamespace(data={}, entry_id="x")
    coordinator._coffee_type_saving = True
    try:
        await coordinator._async_save_coffee_scale_type()
    except RuntimeError:
        pass
    assert coordinator._coffee_type_saving is False
