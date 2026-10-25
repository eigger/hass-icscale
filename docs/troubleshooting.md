# Troubleshooting

[한국어](troubleshooting.ko.md) · [Home](../README.md)

## Common troubleshooting

See [common Bluetooth troubleshooting](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md).

See [Bluetooth proxy setup](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md) for setup and recommended hardware, and [Bluetooth connection troubleshooting](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md) for connection checks.

## Device-specific checks

- The scale only advertises while it is awake, and the advertisement carries **no weight**; weight is streamed over a GATT connection. Seeing the scale in Bluetooth discovery does not prove that connecting works.
- These scales allow **one connection at a time**. Close the phone app, or turn the **Automatic measurement** switch off, to let another client connect.
- For proxy GATT connections, enable `bluetooth_proxy.active: true` as described in [Bluetooth proxy setup](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md). The separate `esp32_ble_tracker.scan_parameters.active` setting requests scan responses; this integration listens for advertisements in passive mode. Discovery working does not prove a GATT connection or write will succeed.
- Tare and Power off are only supported by the 8-byte kitchen-scale firmware variant; coffee-scale firmware ignores them.
- Verified path: only what is covered by the automated tests (mocked BLE transport). No physical-device matrix (model, firmware, adapter/proxy) is claimed.

## Symptoms and actions

| Symptom | Failing stage | Checks | Action |
|---|---|---|---|
| No discovery | Advertisement | Power, awake state, MY_SCALE name and service | Wake the scale and check HA Bluetooth reception. |
| Found but cannot connect | Connect | Other apps, active proxy slots and network | Close the phone app and retry while the scale remains awake. |
| No weight update | Notify / measurement | Automatic measurement switch and received data | Enable the switch or press Measure now; place an item on the scale. |
| Tare / Power off rejected | Command | Firmware variant and awake state | Use the supported kitchen-scale firmware; coffee firmware ignores these commands. |
| Unexpected connection loss | Link | Battery, distance and proxy network | Restore the route, wake the scale and retry; distinguish normal sleeping. |

- **Sensor values not updating**: HA connects when the scale is awake and advertising. Make sure the scale is powered on, and confirm the **Automatic measurement** switch is on (or press **Measure now**). Place something on the scale to generate a weight change.
- **Tare / Power off command failed**: The scale must be turned on and in Bluetooth range. If the command fails, ensure the scale is awake.
## Diagnostics and logs

The Last error and Error count diagnostic sensors expose failed sessions. Expected sleep and an intentional Power off are not counted as unexpected link failures. Connection path facts are reported only when observed; discovery by a receiver does not prove it carried the connection.

If you face issues, enable debug logs for one reproduction and turn them off afterward:

```yaml
logger:
  logs:
    custom_components.icscale: debug
```



## If the problem persists

Open an [Issue](https://github.com/eigger/hass-icscale/issues) with the debug log above and the **Last error** diagnostic sensor value. Include HA/integration/blesession versions when known, scale model/firmware, adapter or proxy model/firmware, the local/proxy path, failure time and reproduction steps. Remove MAC addresses, internal addresses and other personal data from logs before posting. New physical-device validation is outside this change.
