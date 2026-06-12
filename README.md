# ICOMON BLE Home Assistant Integration (hass-icscale)

[![GitHub Release](https://img.shields.io/github/v/release/eigger/hass-icscale?style=flat-square)](https://github.com/eigger/hass-icscale/releases)
[![License](https://img.shields.io/github/license/eigger/hass-icscale?style=flat-square)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom integration for Home Assistant to connect and read weight data directly from ICOMON Bluetooth Low Energy (BLE) kitchen / coffee scales.

## 💬 Feedback & Support

🐞 Found a bug? Let us know via an [Issue](https://github.com/eigger/hass-icscale/issues).  
💡 Have a question or suggestion? Join the [Discussion](https://github.com/eigger/hass-icscale/discussions)!

## Features

- **Live Weight Sensor**: Real-time grams, streamed over the connection while the scale is in use
- **Stability Status**: Binary sensor indicating whether the weight has settled
- **Display Unit Sensor**: Diagnostic sensor showing the current unit configured on the scale
- **Automatic measurement Switch**: When on, HA auto-connects and streams weight while the scale is awake; turn it off to free the scale's Bluetooth for the phone app (single-connection devices)
- **Idle auto-disconnect**: Releases the scale after a configurable idle period so it can power off; reconnects automatically when used again
- **Measure now**: Button that forces an immediate connection and reading, for deterministic on-demand measurement regardless of the automatic connection state
- **Tare and Power Off**: Interactive buttons to zero out the weight or turn off the scale
- **Auto-discovery**: Instantly discovered via Home Assistant's Bluetooth integration

## Installation

1. **HACS**: Add this repository (`eigger/hass-icscale`) to HACS as a custom repository, or 
   **Manual**: Copy the `custom_components/icscale` directory into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.

## ⚠️ Important Notice

- It is **strongly recommended to use a Bluetooth proxy instead of a built-in Bluetooth adapter**.  
  Bluetooth proxies generally offer more stable connections and better range, especially in environments with multiple BLE devices.

> [!TIP]
> For hardware recommendations, refer to [Great ESP32 Board for an ESPHome Bluetooth Proxy](https://community.home-assistant.io/t/great-esp32-board-for-an-esphome-bluetooth-proxy/916767/31).  
- **bluetooth_proxy:** must always have **active: true**.

  Example (recommended configuration with default values):

  ```yaml
  esp32_ble_tracker:
    scan_parameters:
      active: true

  bluetooth_proxy:
    active: true
  ```

## Setup & Pairing

Device setup is done entirely through the Home Assistant UI.

1. **Power on the Scale**: Tap the scale's power button to turn it on.
2. **Add Integration**:
   - In Home Assistant, go to **Settings** > **Devices & Services**.
   - Home Assistant should automatically discover the "ICOMON Kitchen Scale" device via Bluetooth. Click **Configure**.
   - If it wasn't auto-discovered, click **Add Integration** and search for "ICOMON Kitchen Scale".
3. **Submit**: Click **Submit** in Home Assistant to finish setting up.

## How It Works

The scale only advertises over Bluetooth while it is awake, and it does **not**
put weight in the advertisement — weight is streamed over a connection. This
integration follows the scale's natural lifecycle:

- **Connect while awake**: As soon as the scale is seen advertising, Home
  Assistant connects and streams weight changes in real time.
- **Idle auto-disconnect**: If the weight does not change for the configured idle
  timeout (default 3 minutes), HA disconnects so the scale can power itself off
  and so the phone app can use Bluetooth (these scales allow only one connection
  at a time).
- **Automatic reconnect**: After an idle disconnect, HA reconnects when the scale
  genuinely wakes again (it stopped advertising and reappeared). A scale that
  keeps advertising is re-checked periodically as a fallback.
- **Automatic measurement switch**: Turn the **Automatic measurement** switch off
  to stop HA from auto-connecting entirely, freeing the scale for the phone app;
  turn it back on to resume automatic streaming. (The **Measure now** button still
  works while it is off.)
- **On-demand measurement**: Since the advertisement carries no weight, putting
  something on an already-connected scale streams instantly — but if HA has
  idle-disconnected and the scale never stopped advertising, press **Measure now**
  to force an immediate connection and reading. Turning the scale off and on (so
  it re-advertises) also triggers an automatic reconnect.
- **Interactive Commands**: The **Measure now**, **Tare**, and **Power off**
  buttons connect on demand to perform the action even if HA is currently
  disconnected.

## Configuration Options

You can adjust this under **Configure** on the integration page:
- **Idle disconnect timeout (minutes)**: How long with no weight change before HA
  releases the connection (default 3).

## Protocol Notes

GATT profile:

| Role | UUID |
| --- | --- |
| Service | `0000ffb0-0000-1000-8000-00805f9b34fb` |
| Notify (scale → app) | `0000ffb2-0000-1000-8000-00805f9b34fb` |
| Write (app → scale) | `0000ffb1-0000-1000-8000-00805f9b34fb` |

Two notification frame variants are supported and auto-detected by length.

**Coffee-scale variant** (long frame, > 14 bytes):

```
[2] status     high nibble -> sign, low nibble == 1 -> stable
[3..6] weight  magnitude = (b3 & 0x0F)<<24 | b4<<16 | b5<<8 | b6
```

`weight_grams = magnitude / 1000`, negated when the sign nibble is set.

**Kitchen-scale variant** (8-byte frame):

```
[1] package type (0xCA stable / 0xCE live / 0xCC unit)
[2] flag         bit0 = sign (1=negative), bits1-3 = precision (0-7)
[3..5] weight    24-bit big-endian magnitude
[6] unit         [7] checksum = (b2+b3+b4+b5+b6) & 0xFF
```

`weight_grams = magnitude / 10**precision`, negated when the sign bit is set.

Command frames written to `0xFFB1` (write-without-response, device type `0x04`),
used by the kitchen-scale variant (coffee-scale firmware ignores them):

- Tare: `AC 04 FE 14 01 00 CC`
- Power off: `AC 04 FE 00 00 00 B0`

## Troubleshooting

- **Sensor values not updating**: HA connects when the scale is awake and advertising. Make sure the scale is powered on, and confirm the **Automatic measurement** switch is on (or press **Measure now**). Place something on the scale to generate a weight change.
- **Tare / Power off command failed**: The scale must be turned on and in Bluetooth range. If the command fails, ensure the scale is awake.
- **Debug Logging**: If you face issues, enable debug logs:

```yaml
logger:
  logs:
    custom_components.icscale: debug
```


