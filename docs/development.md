# Development

This is an HACS custom integration whose structure follows Home Assistant Core conventions; it is not part of Core and makes no Core quality-tier claim. Shared rules: [hass-repo-standards](https://github.com/eigger/hass-repo-standards) (see [STANDARDS.md](../STANDARDS.md)).

## Tests

Tests live in `tests/components/icscale/` and run against a real Home Assistant through `pytest-homeassistant-custom-component`; only the BLE transport is mocked.

| Environment | Python | Home Assistant | Plugin | Requirements |
|---|---|---|---|---|
| Current | 3.14 | 2026.10.2 | 0.13.373 | `requirements_test.txt` |
| Minimum supported | 3.13 | 2025.2.0 (`hacs.json`) | 0.13.210 | `requirements_test_min.txt` |

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements_test.txt -r requirements_lint.txt "blesession>=0.9.0"
# Requirements of the HA components the tests load (bluetooth, bluetooth_adapters, recorder):
# reuse the shared CI installer from the pinned standards commit.
git clone https://github.com/eigger/hass-repo-standards /tmp/hass-repo-standards
git -C /tmp/hass-repo-standards checkout 78d242092eac732a1af48770e77e3f51e566c6c2
RUNNER_TEMP=/tmp INPUT_DOMAIN=icscale INPUT_REQUIREMENTS=requirements_test.txt \
  INPUT_HA_COMPONENTS="bluetooth bluetooth_adapters recorder" INPUT_TEST_PROFILE=ha \
  python /tmp/hass-repo-standards/actions/python-environment/install.py
python -m pytest tests/components/icscale/ -v
python -m ruff check . && python -m ruff format --check .
```

CI also installs the requirements of the HA `bluetooth`, `bluetooth_adapters` and `recorder` components and runs `blesession` at its declared minimum version.

## Dependencies

Runtime Python packages are declared only in `manifest.json` (`blesession>=0.9.0`). Test and lint requirements stay in separate files. The weekly *Update dependencies* workflow raises the `blesession` minimum through a single PR.
