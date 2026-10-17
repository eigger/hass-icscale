# Troubleshooting

See also the shared [Bluetooth troubleshooting order](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md#연결-문제-확인-순서) (Korean) and [proxy setup](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md).

## Model-specific conditions

- The scale only advertises while it is awake, and the advertisement carries **no weight**; weight is streamed over a GATT connection. Seeing the scale in Bluetooth discovery does not prove that connecting works.
- These scales allow **one connection at a time**. Close the phone app, or turn the **Automatic measurement** switch off, to let another client connect.
- Use a Bluetooth proxy configured as in the [shared guide](https://github.com/eigger/hass-repo-standards/blob/78d242092eac732a1af48770e77e3f51e566c6c2/docs/bluetooth.md) (`esp32_ble_tracker.scan_parameters.active: true` and `bluetooth_proxy.active: true`). Active scanning (scan responses) and GATT connection/write are separate steps: discovery working does not prove connecting works.
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
