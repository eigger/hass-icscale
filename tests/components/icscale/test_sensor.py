"""Weight readings are propagated to the actual HA state machine."""

from homeassistant.helpers import entity_registry as er
from custom_components.icscale.icscale_ble import WeightSample
from .conftest import ADDRESS


async def test_weight_sensor_updates(hass, loaded_entry):
    coordinator = loaded_entry.runtime_data
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", "icscale", f"{ADDRESS}_weight"
    )
    coordinator.state.weight = WeightSample(grams=42.5, stable=False)
    coordinator._async_notify_listeners()
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state.state == "42.5"
    assert state.attributes["unit_of_measurement"] == "g"
