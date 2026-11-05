"""Button platform for the ICOMON kitchen scale (measure now)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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

    entities = []
    for description in BUTTONS:
        entities.append(IcScaleButton(coordinator, description))
    async_add_entities(entities)


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
