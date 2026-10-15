"""Session reports: the scale's own causes on top of blesession's."""

from __future__ import annotations

from blesession import ConnectFailed, Failure, SessionDropped, SessionTrace, stages

from custom_components.icscale import session_report
from custom_components.icscale.session_report import (
    OP_CONNECT,
    OP_LINK_LOST,
    OP_TARE,
    build_session_report,
    likely_cause,
)


def _failure(exc: BaseException, stage: str | None, facts=None) -> Failure:
    return Failure(stage, None, str(exc), exc, facts or {})


def test_connect_failure_hints_at_sleep_or_phone_app() -> None:
    exc = ConnectFailed("device did not answer")
    text = likely_cause(_failure(exc, stages.CONNECT), OP_CONNECT)
    assert text is not None
    assert "gone to sleep" in text
    assert "phone app" in text


def test_weak_signal_is_added_to_the_connect_hint() -> None:
    exc = ConnectFailed("device did not answer")
    facts = {"rssi": -92, "via": "proxy-1", "paths": 1}
    text = likely_cause(_failure(exc, stages.CONNECT, facts), OP_CONNECT)
    assert text is not None
    assert "-92" in text


def test_link_lost_has_its_own_sentence() -> None:
    exc = SessionDropped("The scale closed the connection")
    text = likely_cause(_failure(exc, stages.SESSION), OP_LINK_LOST)
    assert text is not None
    assert "dropped the connection" in text


def test_a_failed_command_names_the_command() -> None:
    exc = RuntimeError("write failed")
    text = likely_cause(_failure(exc, None), OP_TARE)
    assert text == "The scale did not accept the tare command."


def test_unknown_failure_falls_back_to_the_library() -> None:
    assert likely_cause(_failure(RuntimeError("x"), None), "measure") is None


def test_report_for_a_failed_connect(monkeypatch) -> None:
    monkeypatch.setattr(
        session_report, "radio_facts", lambda hass, address, link: {"via": "hci0"}
    )
    trace = SessionTrace()
    trace.note(consecutive_failures=2)

    report = build_session_report(
        None, "AA:BB", operation=OP_CONNECT, trace=trace, exc=ConnectFailed("nope")
    )

    assert report["success"] is False
    assert report["operation"] == OP_CONNECT
    assert report["error"]
    assert report["via"] == "hci0"
    assert report["consecutive_failures"] == 2
    assert "likely_cause" in report


def test_report_for_a_success(monkeypatch) -> None:
    monkeypatch.setattr(session_report, "radio_facts", lambda hass, address, link: {})
    report = build_session_report(
        None, "AA:BB", operation=OP_CONNECT, trace=SessionTrace(), exc=None
    )
    assert report["success"] is True
    assert "error" not in report
