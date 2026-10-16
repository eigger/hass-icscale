"""The Last error / Error count diagnostics against a real Home Assistant."""

from __future__ import annotations

from datetime import UTC, datetime

from blesession import ConnectFailed, SessionTrace
from conftest import ADDRESS, setup_entry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import mock_restore_cache

from custom_components.icscale.const import DOMAIN
from custom_components.icscale.session_report import OP_CONNECT


def _entity_id(hass: HomeAssistant, key: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{ADDRESS}_{key}"
    )
    assert entity_id is not None, key
    return entity_id


async def test_diagnostics_start_empty_and_are_diagnostic(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    await setup_entry(hass)
    registry = er.async_get(hass)

    last_error = registry.async_get(_entity_id(hass, "last_error"))
    error_count = registry.async_get(_entity_id(hass, "error_count"))

    assert last_error.entity_category is EntityCategory.DIAGNOSTIC
    assert error_count.entity_category is EntityCategory.DIAGNOSTIC
    assert error_count.disabled_by is None
    assert hass.states.get(last_error.entity_id).state == "unknown"
    assert hass.states.get(error_count.entity_id).state == "0"


async def test_a_failure_is_published_and_kept_after_a_success(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    entity_id = _entity_id(hass, "last_error")

    coordinator._async_publish_report(
        OP_CONNECT, SessionTrace(), ConnectFailed("no route")
    )
    await hass.async_block_till_done()
    failed = hass.states.get(entity_id)
    assert failed.state != "unknown"
    assert failed.attributes["operation"] == OP_CONNECT
    assert failed.attributes["success"] is False
    assert "no route" in failed.attributes["error"]
    assert coordinator.reports.failures == 1

    coordinator._async_publish_report(OP_CONNECT, SessionTrace(), None)
    await hass.async_block_till_done()
    kept = hass.states.get(entity_id)
    assert kept.state == failed.state
    assert kept.attributes["success"] is False
    assert coordinator.reports.failures == 1


async def test_last_error_is_restored_after_a_restart(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    failed_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    registry = er.async_get(hass)
    entity_id = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{ADDRESS}_last_error",
        suggested_object_id="scale_last_error",
    ).entity_id
    mock_restore_cache(
        hass,
        [
            State(
                entity_id,
                failed_at.isoformat(),
                {
                    "operation": OP_CONNECT,
                    "success": False,
                    "error": "no route",
                    "friendly_name": "Scale Last error",
                    "icon": "mdi:clock-alert-outline",
                    "device_class": "timestamp",
                },
            )
        ],
    )

    entry = await setup_entry(hass)

    reports = entry.runtime_data.reports
    assert reports.last_failure_at == failed_at
    assert reports.last_failure == {
        "operation": OP_CONNECT,
        "success": False,
        "error": "no route",
    }
    assert hass.states.get(entity_id).attributes["error"] == "no route"
