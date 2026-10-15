"""The breakdown of one BLE session, as the diagnostic sensors publish it.

``SessionTrace`` records where the session spent its time and where it died.
``blesession`` turns that into the shared report: which radio the link went
over and one sentence on what a failure most likely means. The sentences that
are specific to the scale live here; the ones every BLE device shares (a proxy
with no free slot, a weak signal, a stack that stopped answering) come from
the library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from blesession import (
    Failure,
    SessionTrace,
    build_report,
    generic_cause,
    placement,
    stages,
)
from blesession.hass import radio_facts

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

OP_CONNECT = "connect"
OP_MEASURE = "measure"
OP_TARE = "tare"
OP_POWER_OFF = "power_off"
OP_LINK_LOST = "link_lost"

_SLEEP_HINT = (
    "The scale did not accept the connection. Most often it has gone to sleep "
    "or powered off, or the phone app is holding its single Bluetooth link: "
    "wake the scale, close the app and try again."
)
_LINK_LOST = (
    "The scale dropped the connection by itself. It has most likely powered "
    "itself off or gone out of range, or the phone app took over the link."
)
_COMMAND_FAILED = "The scale did not accept the {operation} command."


def likely_cause(failure: Failure, operation: str) -> str | None:
    """The scale's own reading of a failure, or ``None`` for the shared one.

    Where the library has a sentence for the failure (a proxy out of slots, a
    stack that stopped answering) it is more specific than anything said here,
    so ``None`` lets ``build_report`` word it and attach ``likely_cause_key``.
    """
    if operation == OP_LINK_LOST:
        return _LINK_LOST + placement(failure.facts, noun="scale")
    shared = generic_cause(
        failure.stage or failure.detail,
        failure.error,
        failure.facts,
        exc=failure.exc,
        noun="scale",
    )
    if shared is not None:
        return None
    if failure.stage == stages.CONNECT:
        return _SLEEP_HINT + placement(failure.facts, noun="scale")
    if operation in (OP_TARE, OP_POWER_OFF):
        return _COMMAND_FAILED.format(operation=operation.replace("_", " "))
    return None


def build_session_report(
    hass: HomeAssistant,
    address: str,
    *,
    operation: str,
    trace: SessionTrace | None,
    exc: BaseException | None,
) -> dict[str, Any]:
    """Assemble the attributes for one finished session.

    Outcome first, then the radio, then the stage timings, in the order
    ``blesession.build_report`` fixes so the same keys mean the same thing on
    every integration.
    """
    trace = trace if trace is not None else SessionTrace()
    return build_report(
        operation=operation,
        trace=trace,
        exc=exc,
        facts=radio_facts(hass, address, trace.link),
        cause=lambda failure: likely_cause(failure, operation),
        noun="scale",
    )
