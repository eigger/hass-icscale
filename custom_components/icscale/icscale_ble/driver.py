"""Active BLE client for ICOMON-protocol kitchen/coffee scales.

Pure Python: depends only on ``bleak`` / ``bleak-retry-connector`` and the
sibling modules. No Home Assistant imports — the HA coordinator wraps this.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from .const import (
    CMD_POWER_OFF,
    CMD_TARE,
    FIRMWARE_REV_CHAR,
    MANUFACTURER_NAME_CHAR,
    MODEL_NUMBER_CHAR,
    NOTIFY_CHAR,
    SERIAL_NUMBER_CHAR,
    WRITE_CHAR,
)
from .models import DeviceInfo, ScaleState
from .parser import parse_notification

_LOGGER = logging.getLogger(__name__)

UpdateCallback = Callable[[ScaleState], None]
DisconnectCallback = Callable[[], None]


class IcScaleClient:
    """Manage a GATT link to a single scale and decode its notifications.

    The same instance is reused across reconnects. Register an update callback
    with :meth:`set_update_callback`; it fires on every decoded frame with the
    accumulated :class:`ScaleState`.
    """

    def __init__(self, name: str = "Scale") -> None:
        """Initialize an idle client."""
        self._name = name
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()
        self._state = ScaleState()
        self._on_update: UpdateCallback | None = None
        self._on_disconnect: DisconnectCallback | None = None

    # --- public state -----------------------------------------------------

    @property
    def state(self) -> ScaleState:
        """Return the latest accumulated scale state."""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Return True while the underlying GATT link is up."""
        return self._client is not None and self._client.is_connected

    def set_update_callback(self, callback: UpdateCallback | None) -> None:
        """Register the callback fired on each decoded frame."""
        self._on_update = callback

    # --- connection -------------------------------------------------------

    async def connect(
        self,
        device: BLEDevice,
        disconnected_callback: DisconnectCallback | None = None,
    ) -> None:
        """Establish a link and subscribe to weight notifications."""
        async with self._lock:
            if self.is_connected:
                return
            self._on_disconnect = disconnected_callback

            def _disconnected(_client: BleakClient) -> None:
                _LOGGER.debug("%s disconnected", self._name)
                self._client = None
                if self._on_disconnect is not None:
                    self._on_disconnect()

            client = await establish_connection(
                BleakClient,
                device,
                self._name,
                disconnected_callback=_disconnected,
            )
            self._client = client
            _LOGGER.debug("%s connected", self._name)

            try:
                await self._read_device_info()
                await client.start_notify(NOTIFY_CHAR, self._handle_notification)
            except Exception:
                self._client = None
                try:
                    await client.disconnect()
                except Exception:
                    pass
                raise


    async def disconnect(self) -> None:
        """Tear down the GATT link if connected."""
        async with self._lock:
            self._on_disconnect = None
            client = self._client
            self._client = None
            if client is not None and client.is_connected:
                try:
                    await client.disconnect()
                except BleakError as err:  # pragma: no cover - best effort
                    _LOGGER.debug("%s disconnect error: %s", self._name, err)

    # --- commands ---------------------------------------------------------

    async def tare(self) -> None:
        """Zero the scale."""
        await self._write(CMD_TARE)

    async def power_off(self) -> None:
        """Power the scale off."""
        await self._write(CMD_POWER_OFF)

    # --- internals --------------------------------------------------------

    async def _write(self, packet: bytes) -> None:
        client = self._client
        if client is None or not client.is_connected:
            raise BleakError("Scale not connected")
        # Commands are written without expecting a response.
        await client.write_gatt_char(WRITE_CHAR, packet, response=False)

    async def _read_device_info(self) -> None:
        client = self._client
        if client is None:
            return
        info = DeviceInfo()
        for char, attr in (
            (MANUFACTURER_NAME_CHAR, "manufacturer"),
            (MODEL_NUMBER_CHAR, "model"),
            (SERIAL_NUMBER_CHAR, "serial"),
            (FIRMWARE_REV_CHAR, "firmware"),
        ):
            try:
                raw = await client.read_gatt_char(char)
            except BleakError:
                continue
            value = raw.decode("utf-8", "replace").strip("\x00").strip() or None
            setattr(info, attr, value)
        self._state.info = info

    def _handle_notification(self, _sender: int, data: bytearray) -> None:
        raw = bytes(data)
        sample = parse_notification(raw)
        if sample is None:
            _LOGGER.debug("%s: unrecognised frame %s", self._name, raw.hex(" "))
            return
        _LOGGER.debug(
            "%s: %s -> %.3f g (stable=%s)",
            self._name,
            raw.hex(" "),
            sample.grams,
            sample.stable,
        )
        self._state.weight = sample
        if sample.unit is not None:
            self._state.unit = sample.unit
        self._notify()

    def _notify(self) -> None:
        if self._on_update is not None:
            self._on_update(self._state)
