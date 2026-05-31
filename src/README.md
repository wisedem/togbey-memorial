# Togbey Funeral Materials — Source Bundle

Memorial materials for Dr. TOGBEY Kwamy Maoussi Félix
(20 novembre 1948 – 24 mai 2026).

## Contents

### Python scripts (the source code that generates each design)
- `build.py` — Marble plaque memorial. Run with `python3 build.py gold`
  or `python3 build.py black` to produce the two color variants.
  Outputs `memorial_redesign.png` (gold) or `memorial_redesign_black.png`.
- `flyer_spread.py` — French 2-page landscape spread (2400×1800).
  Outputs `flyer_spread.png`.
- `flyer_single.py` — French single-page portrait for WhatsApp sharing (1600×2530).
  Outputs `flyer_single.png`.
- `flyer_spread_en.py` — English version of the landscape spread.
- `flyer_single_en.py` — English version of the single-page (1600×2620).

### Images
- `crop_clean_v7.png` — Cleaned portrait with ivory-matched background
  (used by all four flyer files).
- `oval.png` — Gold-framed oval portrait (used by the marble plaque only).

### Fonts (in fonts/ subfolder)
- `EBGaramond.ttf` — variable font, supports weights 600 (SemiBold) and 700 (Bold).
- `EBGaramond-Italic.ttf` — variable italic.
- `PinyonScript-Regular.ttf` — script tribute font for the marble plaque.
- `GreatVibes-Regular.ttf` — alternative script (currently unused).

## How to rebuild from this bundle

```bash
# Unzip the bundle to a working directory
unzip togbey_funeral_source.zip
cd togbey_funeral_source

# Install Pillow if not already installed
pip install Pillow scipy

# Generate the marble plaque (both color variants)
python3 build.py gold
python3 build.py black

# Generate the four programme files
python3 flyer_spread.py
python3 flyer_single.py
python3 flyer_spread_en.py
python3 flyer_single_en.py
```

## Design system reference

- **Palette**: ivory paper (251,247,238), gold dark (158,121,56),
  gold pale (224,200,148), ink (44,42,42), ink soft (66,64,64).
- **Floral palette**: sage dark (96,116,86), sage (142,165,128),
  sage light (180,195,162), white petal (252,248,240),
  petal shadow (210,198,178), rose pink (210,168,158),
  rose pink dark (172,130,122).
- **Floral system**: white roses (3-tier petals: outer 60°×6, mid offset 30°,
  inner 72°×5, bud cup, colored center, gold pollen dot), sage eucalyptus
  leaves (alternating SAGE/SAGE_LIGHT colors), dusty rose accents,
  rendered at 3× scale then downsampled with LANCZOS.
- **Corner curve fix**: both horizontal and vertical stems use `sx*sy`
  as curve sign so all four corners mirror correctly.

## Wording rules (do not change)

- Tokoin-Solidarité (hyphenated)
- Agomé-Glozou (hyphenated; "(Bas-Mono)" stays as unbolded parenthetical)
- Veillée (not "Messe veillée")
- prières / remerciements (plural)
- "messe d'enterrement" lowercase
- "Église Baptiste Biblique" camel case
- "au domicile du défunt"
- Tagline: "En Mémoire de Notre Très Cher et Regretté"
- Dates as one sentence: "Rappelé à Dieu le 24 mai 2026 au CHU
  Sylvanus Olympio dans sa 78ᵉ année."
- Tribute: "Tu resteras à jamais dans nos cœurs." / "Repose en paix."
- Closing: "We love you!"
- Maison TOGBEY Félix — bolded in the LIEU section
- Agomé-Glozou — bolded in the event sentence
- Église Baptiste Biblique de Tokoin-Solidarité — bolded
- au domicile du défunt — bolded
