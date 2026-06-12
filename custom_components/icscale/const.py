"""Constants for the ICOMON Kitchen Scale integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "icscale"

# Disconnect after this many minutes without a weight change, so the scale can
# sleep and the phone app can take the (single-connection) link if needed.
CONF_IDLE_TIMEOUT: Final = "idle_timeout"
DEFAULT_IDLE_TIMEOUT: Final = 3  # minutes
MIN_IDLE_TIMEOUT: Final = 1
MAX_IDLE_TIMEOUT: Final = 60

MANUFACTURER: Final = "ICOMON"
DEFAULT_MODEL: Final = "Kitchen Scale"
