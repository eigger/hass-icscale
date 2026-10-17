# Protocol notes

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
