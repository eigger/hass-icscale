"""Driver tests: the connect flow runs through blesession's ``ble_session``."""

from __future__ import annotations

import pytest
from bleak.exc import BleakError
from blesession import ConnectFailed, SessionTrace
from blesession import session as session_mod
from blesession.testing import FakeClient, FakeDevice, fake_connect

from custom_components.icscale.icscale_ble import IcScaleClient
from custom_components.icscale.icscale_ble.const import NOTIFY_CHAR


class ScaleFakeClient(FakeClient):
    """FakeClient plus the Device Information reads the driver performs."""

    async def read_gatt_char(self, characteristic):
        raise BleakError("no such characteristic")


KITCHEN_FRAME = bytes([0xAC, 0xCA, 0x00, 0x00, 0x03, 0xE8, 0x00, 0xEB])


def _patch(monkeypatch, client: FakeClient | None = None, fail=None) -> None:
    monkeypatch.setattr(session_mod, "establish_connection", fake_connect(client, fail=fail))


async def test_connect_keeps_the_link_and_streams(monkeypatch) -> None:
    fake = ScaleFakeClient()
    _patch(monkeypatch, fake)
    scale = IcScaleClient("Scale")
    updates = []
    scale.set_update_callback(updates.append)

    await scale.connect(FakeDevice(), None, SessionTrace())

    assert scale.is_connected
    assert fake.disconnects == 0
    assert NOTIFY_CHAR in fake.subscribed
    fake.reply(KITCHEN_FRAME)
    assert updates and updates[-1].weight.grams == 1000.0


async def test_connect_records_the_trace(monkeypatch) -> None:
    _patch(monkeypatch, ScaleFakeClient())
    trace = SessionTrace()
    await IcScaleClient("Scale").connect(FakeDevice(), None, trace)
    assert "connect" in trace.timings


async def test_failed_subscribe_closes_the_link(monkeypatch) -> None:
    fake = ScaleFakeClient()
    fake.fail_start_notify = BleakError("boom")
    _patch(monkeypatch, fake)
    scale = IcScaleClient("Scale")

    with pytest.raises(BleakError):
        await scale.connect(FakeDevice(), None, SessionTrace())

    assert not scale.is_connected
    assert not fake.is_connected
    assert fake.disconnects == 1


async def test_connect_failure_is_a_connect_failed(monkeypatch) -> None:
    _patch(monkeypatch, fail=BleakError("no route"))
    scale = IcScaleClient("Scale")
    with pytest.raises(ConnectFailed):
        await scale.connect(FakeDevice(), None, SessionTrace())
    assert not scale.is_connected


async def test_link_drop_notifies_and_clears_the_client(monkeypatch) -> None:
    fake = ScaleFakeClient()
    _patch(monkeypatch, fake)
    scale = IcScaleClient("Scale")
    dropped = []
    await scale.connect(FakeDevice(), lambda: dropped.append(True), SessionTrace())

    fake.drop()

    assert dropped == [True]
    assert not scale.is_connected


async def test_disconnect_closes_the_link(monkeypatch) -> None:
    fake = ScaleFakeClient()
    _patch(monkeypatch, fake)
    scale = IcScaleClient("Scale")
    await scale.connect(FakeDevice(), None, SessionTrace())

    await scale.disconnect()

    assert fake.disconnects == 1
    assert not scale.is_connected
