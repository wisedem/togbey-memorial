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

## Tribute wall (public condolences)

Visitors leave messages through the embedded Cognito forms (FR form #8, EN form #7). After
submitting, a thank-you pop-up appears. Messages the author agreed to share publicly can be shown
on the **Tribute Wall** / **Mur d'hommages** section of each page.

**How public messages appear — curated, moderated:**
The wall reads from [`tributes.json`](tributes.json). Nothing is published automatically — the family
adds approved messages by hand. The wall section stays hidden until the file contains at least one
matching entry.

To add an approved message, add an object to the array in `tributes.json`:

```json
[
  {"name":"Akossiwa M.","message":"Un homme bon et juste.","lang":"fr","place":"Lomé, Togo","date":"2026-05-29"},
  {"name":"James O.","message":"A gentle, brilliant man. Rest well.","lang":"en"}
]
```

- `name`, `message` — required. **Every approved message shows on BOTH the French and English pages**
  (the wall is kept in sync across languages). `lang` is optional metadata and no longer filters.
- `place`, `date` (ISO `YYYY-MM-DD`) — optional. Entries display in file order.
- Keep it valid JSON: comma between objects, **no** trailing comma after the last one
  (check at jsonlint.com). Commit + push and it appears within a few minutes.
- Message text is rendered safely as plain text (no HTML/script execution).

**Cognito setup (one-time, per form #7 and #8):** add a Yes/No field named **`Share`**
("Share my message publicly?" / "Partager mon message publiquement ?", default *No*). Its value is
what tells you which messages you may copy into `tributes.json`, and it drives the pop-up's
"will appear after review" note. The rendering logic lives in [`js/tributes.js`](js/tributes.js).

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
