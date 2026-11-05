"""Only the verified Measure now button is exposed."""

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .conftest import ADDRESS


async def test_unverified_command_buttons_are_not_created(hass, loaded_entry):
    registry = er.async_get(hass)
    for key in ("tare", "power_off"):
        assert (
            registry.async_get_entity_id("button", "icscale", f"{ADDRESS}_{key}")
            is None
        )
    assert registry.async_get_entity_id("button", "icscale", f"{ADDRESS}_measure")


async def test_measure_out_of_range_has_no_fabricated_success(hass, loaded_entry):
    entity_id = er.async_get(hass).async_get_entity_id(
        "button", "icscale", f"{ADDRESS}_measure"
    )
    with pytest.raises(HomeAssistantError, match="not in range"):
        await hass.services.async_call(
            "button", "press", {"entity_id": entity_id}, blocking=True
        )
    assert loaded_entry.runtime_data.reports.failures == 0
