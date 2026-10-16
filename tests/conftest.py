"""Test configuration.

Parser tests do not start Home Assistant. Integration tests request the
``hass`` fixture; custom integrations are enabled only for those.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(request: pytest.FixtureRequest) -> None:
    """Load custom_components/icscale only for tests that start Home Assistant."""
    if "hass" in request.fixturenames:
        request.getfixturevalue("enable_custom_integrations")


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
