# ICScale brand assets

An original geometric digital kitchen scale icon drawn by
`scripts/generate_brand.py` on a dark navy rounded square, with a matching sky
blue `ICScale` wordmark for the landscape logo. No third-party artwork is used.

| File | Size | Purpose |
| --- | --- | --- |
| `icon.png` | 256 × 256 | Home Assistant and HACS icon |
| `icon@2x.png` | 512 × 512 | High-resolution icon |
| `logo.png` | 957 × 256 | Landscape integration logo; README artwork |
| `logo@2x.png` | 1914 × 512 | High-resolution landscape logo |

All images are RGBA PNGs with transparent outer corners and backgrounds. These
sizes follow the [HA brand image guidelines](https://contributors.home-assistant.io/core/integrations/brands/).
Home Assistant 2026.3 and later serves these assets from the integration's local
`brand/` directory. The sky blue wordmark works against light and dark
backgrounds, so separate dark variants are not required.

## Source and permission

The icon is drawn from geometric primitives in this repository's
`scripts/generate_brand.py` and is covered by the repository's MIT license
(Copyright (c) 2026 eigger). The wordmark is rendered with Pillow's bundled
Aileron Regular via
[`ImageFont.load_default`](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.load_default).
[Aileron](https://dotcolon.net/font/aileron/) permits commercial use and is
released with no rights reserved. No font file is redistributed or loaded from
the system.

## Reproduce

Use Python 3.10 or newer and Pillow 12.3.0 (also supplied by HA 2026.10.2):

```sh
python -m pip install Pillow==12.3.0
python scripts/generate_brand.py
```

The script needs no network access and produces the same PNG bytes on every
run with that Pillow version.

SHA256 (Pillow 12.3.0):

- `icon@2x.png`: `a2ede3a127cde1b4fcdeb6ff981bf68763e9345c21aa9d525a6ddf4fa8b979f4`
- `icon.png`: `af31a00d43a3b6ad366086ae675f98cd85b93c6e73f91194d5d834a7ab62f6a3`
- `logo@2x.png`: `447a86eabf24a2f4d3e3a8b591b3483f77c8b709330f037610c927113b6dbcca`
- `logo.png`: `852ea6aade5b1e42b23319ad07fcd9970f25d5261b776764000ecb348028d6d0`

The local `brand/icon.png` is used by the
[HACS brands check](https://hacs.xyz/docs/publish/include/#check-brands).
These files do not imply inclusion in the HACS default list or HA brands
repository. README pages use `custom_components/icscale/brand/logo.png`.
