<!-- hass-standards:header:start -->
# ICOMON Kitchen Scale (hass-icscale)

A HACS custom integration for Home Assistant that connects directly over Bluetooth Low Energy (BLE) to ICOMON kitchen / coffee scales and reads weight data. It is not part of Home Assistant Core.

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
- **Tare and Power Off**: Interactive buttons to zero out the weight or turn off the scale
- **Auto-discovery**: Instantly discovered via the Home Assistant Bluetooth integration

## Requirements

- Home Assistant 2025.2.0 or newer
- A Bluetooth adapter or, strongly recommended, an ESPHome Bluetooth proxy (see [Important limitations](#important-limitations))

## Installation

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-icscale&category=integration)
<!-- hass-standards:installation:end -->

1. **HACS**: add `eigger/hass-icscale` as a custom repository (type *Integration*) and install it, or copy `custom_components/icscale` into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Turn the scale on. It should be discovered automatically under **Settings** > **Devices & Services**; click **Configure**. Otherwise choose **Add Integration** and search for "ICOMON Kitchen Scale".

To remove it, delete the integration entry in **Devices & Services**, then uninstall it from HACS (or delete the folder).

## Configuration

Under **Configure** on the integration page you can set the **Idle disconnect timeout (minutes)**: how long without a weight change before Home Assistant releases the connection (default 3). More in [How it works](docs/how-it-works.md).

## Quick start

Turn the scale on, wait for the weight sensor to become available, then place an item on it. Press **Measure now** to force a connection if the scale is still advertising after an idle disconnect.

## Important limitations

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
