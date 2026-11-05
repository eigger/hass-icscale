<!-- hass-standards:header:start -->
# ICOMON Kitchen Scale for Home Assistant

A Home Assistant custom integration that reads weight directly from ICOMON Bluetooth Low Energy kitchen and coffee scales.

**English** | [한국어](README.ko.md)

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-icscale?style=flat)](https://github.com/eigger/hass-icscale/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#installation)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.2.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-icscale/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-icscale/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-icscale/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-icscale/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-icscale?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-icscale/latest/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-icscale/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

![ICScale](custom_components/icscale/brand/logo.png)

## Supported devices

ICOMON BLE kitchen and coffee scales that advertise service `0000ffb0-…` (local name `MY_SCALE*`). Two firmware variants are handled; see [protocol notes](docs/protocol.md). Only the automated tests (mocked BLE transport) are claimed; physical models and firmware are not individually verified.

## Features

- **Live Weight Sensor**: Real-time grams, streamed over the connection while the scale is in use
- **Stability Status**: Binary sensor indicating whether the weight has settled
- **Stable Weight Sensor**: Keeps the last weight read while the stable flag was on, updating on every stable frame and holding it afterwards (restored after restarts)
- **Display Unit Sensor**: Diagnostic sensor showing the current unit configured on the scale
- **Last error / Error count Sensors**: Diagnostic sensors with the most recent failed session (connect, command or unexpected link loss, with the likely cause and the radio used) and how many have failed; they survive restarts (Error count is disabled by default)
- **Automatic measurement Switch**: When on, HA auto-connects and streams weight while the scale is awake; turn it off to free the scale's Bluetooth for the phone app (single-connection devices)
- **Idle auto-disconnect**: Releases the scale after a configurable idle period so it can power off; reconnects automatically when used again
- **Measure now**: Button that forces an immediate connection and reading, for deterministic on-demand measurement regardless of the automatic connection state
- **Auto-discovery**: Instantly discovered via the Home Assistant Bluetooth integration

## Requirements

- **Home Assistant:** 2025.2.0 or later.
- **Bluetooth:** A Bluetooth adapter or preferably an ESPHome Bluetooth proxy. See [Important limitations](#important-limitations).

## Installation

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-icscale&category=integration)
<!-- hass-standards:installation:end -->

1. Click the badge above to open the repository in Marketplace.
2. If you need to add it yourself, go to **Settings → Marketplace → Add from link** and enter <https://github.com/eigger/hass-icscale>. Connect GitHub if prompted.
3. Select **Install**. Restart Home Assistant if prompted, then continue to [Configuration](#configuration).

## Configuration

Turn the scale on and configure it under **Settings → Devices & services**, or choose **Add integration → ICOMON Kitchen Scale**.

Under **Configure** on the integration page you can set the **Idle disconnect timeout (minutes)**: how long without a weight change before Home Assistant releases the connection (default 3). More in [How it works](docs/how-it-works.md).

## Quick start

Turn the scale on, wait for the weight sensor to become available, then place an item on it. Press **Measure now** to force a connection if the scale is still advertising after an idle disconnect.

## Important limitations

To remove it, delete the entry under **Devices & services**, then uninstall it from Marketplace.

- Use a **Bluetooth proxy rather than a built-in adapter** whenever possible, with `active: true`:

  ```yaml
  esp32_ble_tracker:
    scan_parameters:
      active: true

  bluetooth_proxy:
    active: true
  ```

  Recommended hardware and setup: [Bluetooth proxy setup](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md) and the [community board thread](https://community.home-assistant.io/t/great-esp32-board-for-an-esphome-bluetooth-proxy/916767/31).
- The scale allows a single connection; the phone app and Home Assistant cannot use it at the same time.
- Seeing the scale in discovery does not prove a GATT connection will succeed.

## Documentation

- [How it works](docs/how-it-works.md)
- [Protocol notes](docs/protocol.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development and testing](docs/development.md)

<!-- hass-standards:support:start -->
## Support

- [Issues](https://github.com/eigger/hass-icscale/issues): Report bugs or request features.
- [Discussions](https://github.com/eigger/hass-icscale/discussions): Ask questions and share your experience.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## License

Released under the [MIT License](LICENSE).
<!-- hass-standards:license:end -->
