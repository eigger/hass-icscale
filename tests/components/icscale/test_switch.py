"""Automatic measurement can be controlled through HA services."""

from homeassistant.helpers import entity_registry as er
from .conftest import ADDRESS


async def test_automatic_measurement_switch(hass, loaded_entry):
    entity_id = er.async_get(hass).async_get_entity_id(
        "switch", "icscale", f"{ADDRESS}_auto_measure"
    )
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()
    assert not loaded_entry.runtime_data.enabled
    assert hass.states.get(entity_id).state == "off"
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()
    assert loaded_entry.runtime_data.enabled
    assert hass.states.get(entity_id).state == "on"
