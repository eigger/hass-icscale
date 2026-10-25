"""Test configuration.

# <!-- hass-standards:domain-fixtures:start -->
# Use pytest_homeassistant_custom_component.common.MockConfigEntry for
# mock_config_entry when the integration uses config entries.
# Define mock_client only when an external communication client is present.
# Mock external communication boundaries, never Home Assistant core modules.
# Keep integration-specific fixtures below this managed block.
# <!-- hass-standards:domain-fixtures:end -->

Parser tests do not start Home Assistant. Integration tests request the
``hass`` fixture; custom integrations are enabled only for those.
"""

from __future__ import annotations

import pytest


ADDRESS = "AA:BB:CC:DD:EE:01"


async def setup_entry(hass, address: str = ADDRESS):
    """Create and load a config entry.

    No advertisement is required: the coordinator waits until the scale is seen.
    """
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.icscale.const import DOMAIN

    entry = MockConfigEntry(
        domain=DOMAIN, unique_id=address, title=f"Scale {address[-5:]}", data={}
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.fixture
def mock_config_entry(hass):
    """An actual config entry registered in the real HA manager."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(domain="icscale", unique_id=ADDRESS, title="Scale", data={})
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def loaded_entry(hass, enable_bluetooth, mock_config_entry):
    """Load all real platforms without a nearby physical scale."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
