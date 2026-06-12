"""Config flow for the ICOMON Kitchen Scale integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback

from .const import (
    CONF_IDLE_TIMEOUT,
    DEFAULT_IDLE_TIMEOUT,
    DOMAIN,
    MAX_IDLE_TIMEOUT,
    MIN_IDLE_TIMEOUT,
)
from .icscale_ble import SCALE_SERVICE


def _is_scale(service_info: BluetoothServiceInfoBleak) -> bool:
    """A device is a supported scale if it advertises the vendor service."""
    return SCALE_SERVICE.lower() in (
        uuid.lower() for uuid in service_info.service_uuids
    )


class IcScaleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the kitchen scale."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._discovery: BluetoothServiceInfoBleak | None = None
        self._discovered: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a Bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        if not _is_scale(discovery_info):
            return self.async_abort(reason="not_supported")
        self._discovery = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a discovered device."""
        assert self._discovery is not None
        if user_input is not None:
            return self.async_create_entry(title=self._discovery.name, data={})
        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery.name},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the manual pick-a-device step."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            discovery = self._discovered[address]
            return self.async_create_entry(title=discovery.name, data={})

        current = self._async_current_ids(include_ignore=False)
        for service_info in async_discovered_service_info(self.hass, False):
            address = service_info.address
            if address in current or address in self._discovered:
                continue
            if _is_scale(service_info):
                self._discovered[address] = service_info

        if not self._discovered:
            return self.async_abort(reason="no_devices_found")

        titles = {
            address: f"{info.name} ({address})"
            for address, info in self._discovered.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(titles)}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return IcScaleOptionsFlow()


class IcScaleOptionsFlow(OptionsFlow):
    """Handle options (connection mode and interval)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IDLE_TIMEOUT,
                        default=options.get(
                            CONF_IDLE_TIMEOUT,
                            data.get(CONF_IDLE_TIMEOUT, DEFAULT_IDLE_TIMEOUT),
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_IDLE_TIMEOUT, max=MAX_IDLE_TIMEOUT),
                    ),
                }
            ),
        )
