"""Exercise the registered HA flow and options managers."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.icscale.const import CONF_IDLE_TIMEOUT


async def test_manual_flow_without_advertisements(hass, enable_bluetooth):
    result = await hass.config_entries.flow.async_init(
        "icscale", context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices_found"


async def test_options_idle_timeout(hass, loaded_entry):
    result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_IDLE_TIMEOUT: 5}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert loaded_entry.options[CONF_IDLE_TIMEOUT] == 5
