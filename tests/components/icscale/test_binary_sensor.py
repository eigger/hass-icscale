"""Stable status is exposed through the real HA platform."""

from homeassistant.helpers import entity_registry as er
from custom_components.icscale.icscale_ble import WeightSample
from .conftest import ADDRESS


async def test_stability_state_changes_with_measurements(hass, loaded_entry):
    coordinator = loaded_entry.runtime_data
    entity_id = er.async_get(hass).async_get_entity_id(
        "binary_sensor", "icscale", f"{ADDRESS}_stable"
    )
    coordinator.state.weight = WeightSample(grams=10.0, stable=True)
    coordinator._async_notify_listeners()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "on"
    coordinator.state.weight = WeightSample(grams=11.0, stable=False)
    coordinator._async_notify_listeners()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "off"
