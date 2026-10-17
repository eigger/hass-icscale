"""Smoke imports for the integration's modules."""

from __future__ import annotations

import importlib

import pytest

MODULES = (
    "sensor",
    "binary_sensor",
    "button",
    "switch",
    "config_flow",
    "coordinator",
)


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name: str) -> None:
    importlib.import_module(f"custom_components.icscale.{name}")
