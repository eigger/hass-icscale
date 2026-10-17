"""Active BLE client for ICOMON-protocol kitchen/coffee scales.

Pure Python: depends only on ``bleak`` / ``blesession`` and the sibling
modules. No Home Assistant imports — the HA coordinator wraps this.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from blesession import (
    DISCONNECT_TIMEOUT_S,
    SessionTrace,
    ble_session,
    start_notify_with_recovery,
)

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
from .parser import (
    COFFEE_MIN_LEN,
    KITCHEN_FRAME_LEN,
    checksum_ok,
    is_unit_frame,
    parse_notification,
)

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
        self._name = name
        self._warned_checksum = False
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
        trace: SessionTrace | None = None,
    ) -> None:
        """Establish a link and subscribe to weight notifications.

        The link outlives this call (``keep=True``): the scale streams weight
        for as long as it is held. ``trace`` times the connect and records
        which radio carried it. On any failure the link is closed again, so a
        half-set-up connection never holds a proxy slot.
        """
        async with self._lock:
            if self.is_connected:
                return
            # Whatever was held before is gone; its late callback must not
            # be taken for this link's.
            self._client = None
            self._on_disconnect = disconnected_callback

            def _disconnected(dropped: BleakClient) -> None:
                # A late callback from an earlier link must not clear the
                # client of a newer one.
                if dropped is not self._client:
                    return
                _LOGGER.debug("%s disconnected", self._name)
                self._client = None
                if self._on_disconnect is not None:
                    self._on_disconnect()

            async with ble_session(
                device,
                trace=trace,
                name=self._name,
                keep=True,
                disconnected_callback=_disconnected,
            ) as client:
                self._client = client
                _LOGGER.debug("%s connected", self._name)
                try:
                    await self._read_device_info()
                    await start_notify_with_recovery(
                        client, NOTIFY_CHAR, self._handle_notification
                    )
                except BaseException:
                    # keep=True hands the link to us, so a failed set-up must
                    # close it here.
                    # A drop during set-up already reached the owner through
                    # the disconnect callback (which cleared the client).
                    reported = self._client is not client
                    self._client = None
                    await self._close(client)
                    # The link was visible as up while setting up, so tell the
                    # owner it is gone, once.
                    if not reported and self._on_disconnect is not None:
                        self._on_disconnect()
                    raise

    async def disconnect(self) -> None:
        """Tear down the GATT link if connected."""
        async with self._lock:
            self._on_disconnect = None
            client = self._client
            self._client = None
            if client is not None and client.is_connected:
                await self._close(client)

    async def _close(self, client: BleakClient) -> None:
        """Disconnect ``client``, bounded and best effort."""
        try:
            async with asyncio.timeout(DISCONNECT_TIMEOUT_S):
                await client.disconnect()
        except Exception as err:  # noqa: BLE001 - never mask the caller's error
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
        if info.model and "coffee" in info.model.lower():
            self._state.is_coffee = True

    def _handle_notification(self, _sender: int, data: bytearray) -> None:
        raw = bytes(data)
        if len(raw) >= KITCHEN_FRAME_LEN and not checksum_ok(raw):
            # Warn once so a variant with another checksum is not silent.
            log = _LOGGER.debug if self._warned_checksum else _LOGGER.warning
            self._warned_checksum = True
            log("%s: bad checksum, dropping %s", self._name, raw.hex(" "))
            return
        sample = parse_notification(raw)
        if sample is None:
            _LOGGER.debug("%s: unrecognised frame %s", self._name, raw.hex(" "))
            return
        if len(raw) > COFFEE_MIN_LEN:
            self._state.is_coffee = True

        _LOGGER.debug(
            "%s: %s -> %.3f g (stable=%s)",
            self._name,
            raw.hex(" "),
            sample.grams,
            sample.stable,
        )
        if sample.unit is not None:
            self._state.unit = sample.unit
        # A unit-change frame carries no reading: keep weight/stable as-is.
        if not is_unit_frame(raw):
            self._state.weight = sample
        self._notify()

    def _notify(self) -> None:
        if self._on_update is not None:
            self._on_update(self._state)
