"""Connection coordinator for an ICOMON kitchen scale.

Wraps :class:`icscale_ble.IcScaleClient` and bridges its callbacks to Home
Assistant entities. A single, device-faithful connection strategy:

* The scale only advertises (service ``0xFFB0``) while it is awake; it carries no
  weight in the advertisement. Weight is streamed over a GATT notification once
  connected.
* So: while the *connection* switch is enabled, connect as soon as the scale is
  seen advertising and stream weight in real time.
* If the weight does not change for ``idle_timeout`` minutes, disconnect so the
  scale can power itself off and so the phone app can take the link (BLE scales
  allow only one connection). After an idle disconnect we wait for the scale to
  genuinely re-wake (an advertisement gap, i.e. it slept and came back) before
  reconnecting, with a long fallback so a scale that never stops advertising is
  still re-checked periodically.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import timedelta

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothChange, BluetoothScanningMode
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval

from .icscale_ble import IcScaleClient, ScaleState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .types import IcScaleConfigEntry


_LOGGER = logging.getLogger(__name__)

# How often to check for connection idleness.
IDLE_CHECK_INTERVAL = timedelta(seconds=30)
# An advertisement gap longer than this means the scale slept and re-woken, so a
# fresh advertisement should trigger a reconnect even after an idle disconnect.
AWAY_THRESHOLD = 5.0

# Failsafe: re-check a scale that keeps advertising forever this long after an
# idle disconnect, even without an advertisement gap.
RECONNECT_FALLBACK = 120.0
# Minimum weight delta (grams) that counts as activity (resets the idle timer).
WEIGHT_CHANGE_THRESHOLD = 0.1


class IcScaleCoordinator:
    """Own the BLE client lifecycle and push updates to entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: IcScaleConfigEntry,
        address: str,
        name: str,
        *,
        idle_timeout: int,
    ) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self.address = address
        self.name = name
        self.idle_timeout = idle_timeout


        # User-facing "Connection" switch; when False we never hold the link.
        self.enabled = True

        self.rssi: int | None = None
        self._client = IcScaleClient(name=name)
        self._client.set_update_callback(self._on_client_update)
        self._listeners: list[CALLBACK_TYPE] = []
        self._lock = asyncio.Lock()
        self._unsub_advert: CALLBACK_TYPE | None = None
        self._unsub_idle: CALLBACK_TYPE | None = None
        self._closing = False

        # Idle / reconnect bookkeeping (monotonic seconds).
        self._last_weight_change: float | None = None
        self._last_weight_value: float | None = None
        self._last_adv_time: float | None = None
        self._idle_released = False
        self._idle_released_time: float | None = None

    # --- lifecycle --------------------------------------------------------

    async def async_start(self) -> None:
        """Track advertisements and start the idle watchdog."""
        self._closing = False
        self._unsub_advert = bluetooth.async_register_callback(
            self.hass,
            self._async_on_advertisement,
            {"address": self.address, "connectable": True},
            BluetoothScanningMode.ACTIVE,
        )
        self._unsub_idle = async_track_time_interval(
            self.hass, self._async_check_idle, IDLE_CHECK_INTERVAL
        )
        # If the scale is already in range, connect now rather than waiting for
        # the next advertisement.
        if self.enabled:
            self.hass.async_create_task(self._async_connect())

    async def async_stop(self) -> None:
        """Stop tracking and disconnect."""
        self._closing = True
        if self._unsub_advert is not None:
            self._unsub_advert()
            self._unsub_advert = None
        if self._unsub_idle is not None:
            self._unsub_idle()
            self._unsub_idle = None
        await self._client.disconnect()

    # --- entity plumbing --------------------------------------------------

    @property
    def state(self) -> ScaleState:
        """Latest decoded scale state."""
        return self._client.state

    @property
    def connected(self) -> bool:
        """True while the GATT link is up."""
        return self._client.is_connected

    @property
    def available(self) -> bool:
        """Entities are always available to display their last known state."""
        return True


    @property
    def model(self) -> str:
        """Best-known device model string."""
        if self.state.is_coffee or (self.state.info.model and "coffee" in self.state.info.model.lower()):
            return "Coffee Scale"
        return self.state.info.model or DEFAULT_MODEL


    async def async_set_enabled(self, enabled: bool) -> None:
        """Enable/disable HA holding the connection (the 'Connection' switch)."""
        if enabled == self.enabled:
            return
        self.enabled = enabled
        if enabled:
            self._idle_released = False
            await self._async_connect()
        else:
            await self._client.disconnect()
        self._async_notify_listeners()

    @callback
    def async_add_listener(self, update_callback: CALLBACK_TYPE) -> CALLBACK_TYPE:
        """Register an entity update callback; returns an unsubscribe handle."""
        self._listeners.append(update_callback)

        def _remove() -> None:
            if update_callback in self._listeners:
                self._listeners.remove(update_callback)

        return _remove

    @callback
    def _async_notify_listeners(self) -> None:
        for update_callback in list(self._listeners):
            update_callback()

    # --- BLE callbacks ----------------------------------------------------

    @callback
    def _on_client_update(self, state: ScaleState) -> None:
        # Called from the bleak notification loop; marshal to the HA loop.
        if state.is_coffee and not self.entry.data.get("is_coffee"):
            self.hass.async_create_task(self._async_save_coffee_scale_type())

        if state.weight is not None:
            current = state.weight.grams
            if (
                self._last_weight_value is None
                or abs(current - self._last_weight_value) > WEIGHT_CHANGE_THRESHOLD
            ):
                self._last_weight_change = time.monotonic()
                self._last_weight_value = current
        self.hass.loop.call_soon_threadsafe(self._async_notify_listeners)


    @callback
    def _async_on_advertisement(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        now = time.monotonic()
        gap = now - self._last_adv_time if self._last_adv_time is not None else None
        self._last_adv_time = now
        self.rssi = service_info.rssi

        # Clear an idle "released" state when the scale has genuinely re-woken
        # (advertised again after a gap) or after the failsafe interval.
        if self._idle_released:
            woke = gap is not None and gap > AWAY_THRESHOLD
            timed_out = (
                self._idle_released_time is not None
                and now - self._idle_released_time > RECONNECT_FALLBACK
            )
            _LOGGER.debug(
                "%s: idle_released is True. gap=%s, AWAY_THRESHOLD=%s, woke=%s, timed_out=%s",
                self.name,
                f"{gap:.1f}s" if gap is not None else "None",
                AWAY_THRESHOLD,
                woke,
                timed_out,
            )
            if woke or timed_out:
                self._idle_released = False

        _LOGGER.debug(
            "%s: advertisement received. enabled=%s, idle_released=%s, client_connected=%s, closing=%s, locked=%s",
            self.name,
            self.enabled,
            self._idle_released,
            self._client.is_connected,
            self._closing,
            self._lock.locked(),
        )

        if (
            self.enabled
            and not self._idle_released
            and not self._client.is_connected
            and not self._closing
            and not self._lock.locked()
        ):
            _LOGGER.debug("%s: triggering async_connect task", self.name)
            self.hass.async_create_task(self._async_connect())

        self._async_notify_listeners()

    @callback
    def _on_disconnected(self) -> None:
        self.hass.loop.call_soon_threadsafe(self._async_notify_listeners)

    # --- connection drivers ----------------------------------------------

    async def _async_connect(self) -> None:
        if self._closing or not self.enabled or self._client.is_connected:
            _LOGGER.debug(
                "%s: async_connect aborted early. closing=%s, enabled=%s, connected=%s",
                self.name,
                self._closing,
                self.enabled,
                self._client.is_connected,
            )
            return
        async with self._lock:
            if self._closing or not self.enabled or self._client.is_connected:
                _LOGGER.debug(
                    "%s: async_connect aborted under lock. closing=%s, enabled=%s, connected=%s",
                    self.name,
                    self._closing,
                    self.enabled,
                    self._client.is_connected,
                )
                return
            device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if device is None:
                _LOGGER.debug("%s not in range; deferring connect", self.name)
                return
            _LOGGER.debug("%s: initiating Bleak connection", self.name)
            try:
                await self._client.connect(device, self._on_disconnected)
                _LOGGER.debug("%s: Bleak connection successful", self.name)
            except Exception as err:  # noqa: BLE001 - log and retry on next advert
                _LOGGER.debug("%s connect failed: %s", self.name, err)
                return

            # Start the idle clock from the moment we connect.
            self._last_weight_change = time.monotonic()
            self._last_weight_value = (
                self.state.weight.grams if self.state.weight else None
            )
        self._async_notify_listeners()

    async def _async_check_idle(self, _now=None) -> None:
        """Disconnect a connection that has seen no weight change for too long."""
        if self._closing or not self._client.is_connected:
            return
        if self._last_weight_change is None:
            return
        elapsed = time.monotonic() - self._last_weight_change
        if elapsed >= self.idle_timeout * 60:
            _LOGGER.info(
                "%s: no weight change for %d min; disconnecting to allow sleep",
                self.name,
                self.idle_timeout,
            )
            self._idle_released = True
            self._idle_released_time = time.monotonic()
            await self._client.disconnect()
            self._async_notify_listeners()

    # --- commands ---------------------------------------------------------

    async def _async_ensure_connected(self, description: str) -> None:
        """Connect on demand for an explicit user action; raise if unreachable."""
        if self._client.is_connected:
            return
        device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if device is None:
            raise HomeAssistantError(f"{self.name} not in range (turn the scale on)")
        try:
            async with self._lock:
                await self._client.connect(device, self._on_disconnected)
            # An explicit action counts as activity (starts the idle clock).
            self._last_weight_change = time.monotonic()
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(
                f"{self.name} connect for {description} failed: {err}"
            ) from err

    async def _async_run_command(
        self, action: Callable[[], Awaitable[None]], description: str
    ) -> None:
        """Run a control command, connecting on demand if needed."""
        await self._async_ensure_connected(description)
        try:
            await action()
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"{description} failed: {err}") from err

    async def async_measure_now(self) -> None:
        """Force an immediate connect + stream, regardless of idle/standby state.

        Gives deterministic on-demand measurement: even if the scale keeps
        advertising (so the automatic 'fresh wake' reconnect would not fire) or
        the Connection switch is off, this connects now and resets the idle clock
        so a fresh reading streams in.
        """
        self._idle_released = False
        await self._async_ensure_connected("Measure")
        self._last_weight_change = time.monotonic()
        self._async_notify_listeners()

    async def async_tare(self) -> None:
        """Zero the scale."""
        await self._async_run_command(self._client.tare, "Tare")

    async def async_power_off(self) -> None:
        """Power the scale off."""
        await self._async_run_command(self._client.power_off, "Power off")

    async def _async_save_coffee_scale_type(self) -> None:
        """Save the scale type in config entry and reload to update entities."""
        new_data = {**self.entry.data, "is_coffee": True}
        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
        await self.hass.config_entries.async_reload(self.entry.entry_id)

