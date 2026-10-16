"""What the coordinator does and does not record as an error."""

from __future__ import annotations

from datetime import timedelta
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from conftest import ADDRESS, setup_entry
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    mock_restore_cache,
)
import pytest

from custom_components.icscale import coordinator as coordinator_module
from custom_components.icscale.const import DOMAIN
from custom_components.icscale.session_report import OP_LINK_LOST, OP_TARE


def _advertising(seconds_ago: float = 0.0):
    """A last-service-info stand-in whose advertisement is ``seconds_ago`` old."""
    return SimpleNamespace(time=time.monotonic() - seconds_ago)


def _awake(*_args, **_kwargs):
    """An advertisement that arrives after whatever just happened."""
    return _advertising(seconds_ago=-1)


async def _tick(hass: HomeAssistant, seconds: float) -> None:
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=seconds))
    await hass.async_block_till_done()


async def test_a_drop_while_still_advertising_is_an_error(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        side_effect=_awake,
    ):
        coordinator._on_disconnected()
        await hass.async_block_till_done()
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 1
    assert coordinator.reports.last_failure["operation"] == OP_LINK_LOST


async def test_a_drop_with_the_scale_asleep_is_not_an_error(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        return_value=_advertising(seconds_ago=120),
    ):
        coordinator._on_disconnected()
        await hass.async_block_till_done()
        assert coordinator._unsub_link_checks
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 0


async def test_a_drop_during_a_connect_is_left_to_that_connect(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        side_effect=_awake,
    ):
        async with coordinator._lock:
            coordinator._on_disconnected()
        await hass.async_block_till_done()
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 0


async def test_power_off_ending_the_link_is_not_an_error(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    coordinator._client = SimpleNamespace(
        state=coordinator.state,
        is_connected=True, power_off=AsyncMock(), disconnect=AsyncMock()
    )

    await coordinator.async_power_off()
    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        side_effect=_awake,
    ):
        coordinator._on_disconnected()
        await hass.async_block_till_done()
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 0


async def test_a_failed_command_is_recorded(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    coordinator._client = SimpleNamespace(
        state=coordinator.state,
        is_connected=True,
        tare=AsyncMock(side_effect=RuntimeError("write failed")),
        disconnect=AsyncMock(),
    )

    with pytest.raises(HomeAssistantError):
        await coordinator.async_tare()

    assert coordinator.reports.failures == 1
    report = coordinator.reports.last_failure
    assert report["operation"] == OP_TARE
    assert "write failed" in report["error"]
    assert report["likely_cause"] == "The scale did not accept the tare command."


async def test_a_scale_that_is_not_in_range_is_not_an_error(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    with pytest.raises(HomeAssistantError, match="not in range"):
        await coordinator.async_tare()

    assert coordinator.reports.failures == 0


async def test_no_advertisement_since_a_drop_means_asleep(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    device = object()
    coordinator._dropped_at = time.monotonic()

    with (
        patch.object(
            coordinator_module.bluetooth,
            "async_ble_device_from_address",
            return_value=device,
        ),
        patch.object(
            coordinator_module.bluetooth,
            "async_last_service_info",
            return_value=_advertising(seconds_ago=5),
        ),
    ):
        assert coordinator._async_awake_device() is None

    with (
        patch.object(
            coordinator_module.bluetooth,
            "async_ble_device_from_address",
            return_value=device,
        ),
        patch.object(
            coordinator_module.bluetooth,
            "async_last_service_info",
            return_value=_advertising(seconds_ago=-1),
        ),
    ):
        assert coordinator._async_awake_device() is device


async def test_error_count_is_restored_after_a_restart(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    registry = er.async_get(hass)
    entity_id = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{ADDRESS}_error_count",
        suggested_object_id="scale_error_count",
        disabled_by=None,
    ).entity_id
    mock_restore_cache(hass, [State(entity_id, "4")])

    entry = await setup_entry(hass)

    assert entry.runtime_data.reports.failures == 4
    assert hass.states.get(entity_id).state == "4"


async def test_unloading_cancels_a_pending_link_check(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    coordinator._on_disconnected()
    await hass.async_block_till_done()
    assert coordinator._unsub_link_checks

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not coordinator._unsub_link_checks


async def test_a_command_that_fails_on_a_dead_link_is_left_to_the_link_check(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    client = SimpleNamespace(
        state=coordinator.state, is_connected=True, disconnect=AsyncMock()
    )

    async def _tare() -> None:
        client.is_connected = False
        raise RuntimeError("Scale not connected")

    client.tare = _tare
    coordinator._client = client

    with pytest.raises(HomeAssistantError):
        await coordinator.async_tare()

    assert coordinator.reports.failures == 0


async def test_the_drop_a_failed_command_caused_is_not_counted_again(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    coordinator._client = SimpleNamespace(
        state=coordinator.state,
        is_connected=True,
        tare=AsyncMock(side_effect=RuntimeError("write failed")),
        disconnect=AsyncMock(),
    )

    with pytest.raises(HomeAssistantError):
        await coordinator.async_tare()
    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        side_effect=_awake,
    ):
        coordinator._on_disconnected()
        await hass.async_block_till_done()
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 1
    assert coordinator.reports.last_failure["operation"] == OP_TARE


async def test_an_expected_drop_still_needs_a_fresh_advertisement_to_reconnect(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    coordinator._client = SimpleNamespace(
        state=coordinator.state,
        is_connected=True,
        power_off=AsyncMock(),
        disconnect=AsyncMock(),
    )
    await coordinator.async_power_off()
    coordinator._on_disconnected()

    assert coordinator._dropped_at is not None
    assert not coordinator._unsub_link_checks


async def test_an_advertisement_from_before_the_drop_does_not_make_it_an_error(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    with patch.object(
        coordinator_module.bluetooth,
        "async_last_service_info",
        return_value=_advertising(),
    ):
        coordinator._on_disconnected()
        await hass.async_block_till_done()
        await _tick(hass, coordinator_module.LINK_LOST_CHECK_DELAY + 1)

    assert coordinator.reports.failures == 0


async def test_a_drop_after_the_expected_window_is_checked(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data
    coordinator._client = SimpleNamespace(
        state=coordinator.state,
        is_connected=True,
        power_off=AsyncMock(),
        disconnect=AsyncMock(),
    )
    await coordinator.async_power_off()
    assert coordinator._expect_drop_until > time.monotonic()

    coordinator._expect_drop_until = time.monotonic() - 1
    coordinator._on_disconnected()
    await hass.async_block_till_done()

    assert coordinator._unsub_link_checks


async def test_no_link_check_is_armed_while_closing(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    entry = await setup_entry(hass)
    coordinator = entry.runtime_data

    coordinator._closing = True
    coordinator._async_schedule_link_check(None, time.monotonic())

    assert not coordinator._unsub_link_checks
