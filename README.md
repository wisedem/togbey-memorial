# In Memory of Dr. TOGBEY Kwamy Maoussi Félix

*20 novembre 1948 – 24 mai 2026*

This repository hosts the memorial flyer online so it can be shared via a link or QR code.

## Landing page

**https://drtogbeyfelix.com/** — shows the French flyer with a download button.
This is the address the QR code on the printed flyer points to, so the link stays valid even
if the content changes later (e.g. a future custom domain or expanded website).

## Files

| File | Description | Direct link |
| --- | --- | --- |
| [`flyer_single.png`](flyer_single.png) | French flyer (primary) | `https://drtogbeyfelix.com/flyer_single.png` |
| [`flyer_single_en.png`](flyer_single_en.png) | English flyer | `https://drtogbeyfelix.com/flyer_single_en.png` |
| [`qr_landing.png`](qr_landing.png) | Standalone QR → landing page | — |

The QR code embedded in both flyers points to the landing page above.

## Source (generators)

The [`src/`](src/) folder holds the Python (Pillow) scripts that generate every print piece,
plus the input assets (`oval.png`, `crop_clean_v7.png`, `fonts/`) and the design-system reference
in [`src/README.md`](src/README.md). Generated PNGs are git-ignored — rebuild them with:

```bash
cd src
pip install Pillow qrcode
python3 flyer_single.py      # French single flyer
python3 flyer_single_en.py   # English single flyer
python3 flyer_qr.py          # portrait + large scan-me QR
python3 generate_web_assets.py   # web assets -> ../img/ (oval, floral corner, share card)
```
