"""The ICOMON Kitchen Scale Bluetooth integration."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_IDLE_TIMEOUT, DEFAULT_IDLE_TIMEOUT
from .coordinator import IcScaleCoordinator
from .types import IcScaleConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.SWITCH,
]

_LOGGER = logging.getLogger(__name__)


def _resolve_options(entry: IcScaleConfigEntry) -> int:
    """Read the idle timeout from options (falling back to data)."""
    idle_timeout = entry.options.get(
        CONF_IDLE_TIMEOUT, entry.data.get(CONF_IDLE_TIMEOUT, DEFAULT_IDLE_TIMEOUT)
    )
    return int(idle_timeout)


async def async_setup_entry(hass: HomeAssistant, entry: IcScaleConfigEntry) -> bool:
    """Set up the kitchen scale from a config entry."""
    address = entry.unique_id
    assert address is not None

    if not bluetooth.async_ble_device_from_address(hass, address, connectable=True):
        _LOGGER.debug(
            "Scale %s not currently in range; will connect when seen", address
        )

    idle_timeout = _resolve_options(entry)
    coordinator = IcScaleCoordinator(
        hass,
        address=address,
        name=entry.title or "Kitchen Scale",
        idle_timeout=idle_timeout,
    )
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await coordinator.async_start()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: IcScaleConfigEntry
) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: IcScaleConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_stop()
    return unload_ok
