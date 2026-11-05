"""Button platform for the ICOMON kitchen scale (measure now)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import IcScaleCoordinator
from .entity import IcScaleEntity


@dataclass(frozen=True, kw_only=True)
class IcScaleButtonDescription(ButtonEntityDescription):
    """Button description binding a press to a coordinator command."""

    press_fn: Callable[[IcScaleCoordinator], Awaitable[None]]


BUTTONS: tuple[IcScaleButtonDescription, ...] = (
    IcScaleButtonDescription(
        key="measure",
        translation_key="measure",
        icon="mdi:scale",
        press_fn=lambda c: c.async_measure_now(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up kitchen scale buttons."""
    coordinator: IcScaleCoordinator = entry.runtime_data

    # Tare and Power off were removed (unverified commands); drop their leftovers.
    registry = er.async_get(hass)
    for key in ("tare", "power_off"):
        if entity_id := registry.async_get_entity_id(
            "button", DOMAIN, f"{coordinator.address}_{key}"
        ):
            registry.async_remove(entity_id)

    async_add_entities(IcScaleButton(coordinator, d) for d in BUTTONS)


class IcScaleButton(IcScaleEntity, ButtonEntity):
    """A button that issues a control command to the scale."""

    entity_description: IcScaleButtonDescription

    def __init__(
        self,
        coordinator: IcScaleCoordinator,
        description: IcScaleButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Issue the bound command."""
        await self.entity_description.press_fn(self.coordinator)
