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
