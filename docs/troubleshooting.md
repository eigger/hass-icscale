# Troubleshooting

See [Bluetooth proxy setup](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md) for setup and recommended hardware, and [Bluetooth connection troubleshooting](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md#troubleshooting) for connection checks.

## Model-specific conditions

- The scale only advertises while it is awake, and the advertisement carries **no weight**; weight is streamed over a GATT connection. Seeing the scale in Bluetooth discovery does not prove that connecting works.
- These scales allow **one connection at a time**. Close the phone app, or turn the **Automatic measurement** switch off, to let another client connect.
- For proxy GATT connections, enable `bluetooth_proxy.active: true` as described in [Bluetooth proxy setup](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md). The separate `esp32_ble_tracker.scan_parameters.active` setting requests scan responses; this integration listens for advertisements in passive mode. Discovery working does not prove a GATT connection or write will succeed.
- Tare and Power off are only supported by the 8-byte kitchen-scale firmware variant; coffee-scale firmware ignores them.
- Verified path: only what is covered by the automated tests (mocked BLE transport). No physical-device matrix (model, firmware, adapter/proxy) is claimed.

## Common problems

- **Sensor values not updating**: HA connects when the scale is awake and advertising. Make sure the scale is powered on, and confirm the **Automatic measurement** switch is on (or press **Measure now**). Place something on the scale to generate a weight change.
- **Tare / Power off command failed**: The scale must be turned on and in Bluetooth range. If the command fails, ensure the scale is awake.
- **Debug Logging**: If you face issues, enable debug logs:

```yaml
logger:
  logs:
    custom_components.icscale: debug
```



## Reporting an issue

Open an [Issue](https://github.com/eigger/hass-icscale/issues) with the debug log above and the **Last error** diagnostic sensor value. Remove MAC addresses and other personal data from logs before posting.
