"""Actual entry setup, platform registration and cleanup."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er


async def test_setup_and_unload(hass, loaded_entry):
    assert loaded_entry.state is ConfigEntryState.LOADED
    registered = er.async_entries_for_config_entry(
        er.async_get(hass), loaded_entry.entry_id
    )
    assert {entity.domain for entity in registered} == {
        "binary_sensor",
        "button",
        "sensor",
        "switch",
    }
    coordinator = loaded_entry.runtime_data
    assert await hass.config_entries.async_unload(loaded_entry.entry_id)
    await hass.async_block_till_done()
    assert loaded_entry.state is ConfigEntryState.NOT_LOADED
    assert not coordinator._unsub_link_checks


async def test_entry_reload_preserves_registered_entities(hass, loaded_entry):
    registry = er.async_get(hass)
    before = {
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, loaded_entry.entry_id)
    }
    assert await hass.config_entries.async_reload(loaded_entry.entry_id)
    await hass.async_block_till_done()
    after = {
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, loaded_entry.entry_id)
    }
    assert before == after
