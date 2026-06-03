#!/usr/bin/env python3
"""Sync approved + public condolences from Cognito Forms into tributes.json.

Source of truth = Cognito (once automated, do NOT hand-edit tributes.json).
Reads form 7 (English) and form 8 (French) via the Cognito API, keeps entries where an
"Approved"-like field AND a public-sharing field are Yes, and writes tributes.json:
  [ {"name": str, "message": str, "lang": "en"|"fr", "date": "YYYY-MM-DD"?}, ... ]

Both pages show all entries (the wall is language-synced), so `lang` is metadata only.

Env:
  COGNITO_API_KEY   (required)  Cognito read API key
Usage: run from the repo root -> writes ./tributes.json
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://www.cognitoforms.com/api"
FORMS = [("7", "en"), ("8", "fr")]          # (Cognito form id, language tag)
OUT = "tributes.json"
TRANSLATE_API = "https://api.mymemory.translated.net/get"   # free, keyless machine translation

# ---------- field extraction (name-agnostic; scans entry keys) ----------

def _truthy_yes(v):
    if v is True:
        return True
    if isinstance(v, str):
        return v.strip().lower() in ("yes", "oui", "true", "public", "publique")
    return False

def _find(entry, key_rx):
    rx = re.compile(key_rx, re.I)
    for k, v in entry.items():
        if rx.search(k):
            return v
    return None

def get_name(entry, lang):
    v = entry.get("Name")
    if v is None:
        v = _find(entry, r"name|nom")                         # e.g. "YourName" / "VotreNom"
    if isinstance(v, dict):                                   # Cognito Name field -> {First, Last}
        v = " ".join(p for p in (v.get("First"), v.get("Last")) if p).strip()
    if isinstance(v, str) and v.strip():
        return v.strip()
    return "Anonyme" if lang == "fr" else "Anonymous"

def get_message(entry):
    if isinstance(entry.get("Message"), str) and entry["Message"].strip():
        return entry["Message"].strip()
    v = _find(entry, r"message|msg|tribute|condol|t[ée]moign")
    if isinstance(v, str) and v.strip():
        return v.strip()
    best = ""                                                 # fallback: longest text value
    for k, val in entry.items():
        if isinstance(val, str) and k != "Email" and len(val) > len(best):
            best = val
    return best.strip()

def _meta(entry):
    return entry["Entry"] if isinstance(entry.get("Entry"), dict) else {}

def get_timestamp(entry):
    for src in (_meta(entry), entry):
        for k in ("DateSubmitted", "DateCreated", "DateUpdated"):
            v = src.get(k)
            if isinstance(v, str) and v:
                return v
    return ""

def _any_yes(entry, key_rx):
    rx = re.compile(key_rx, re.I)
    return any(rx.search(k) and _truthy_yes(v) for k, v in entry.items())

def is_approved(entry):
    return _any_yes(entry, r"approv|approuv")             # EN "Approved" / FR "Approuvé"

def is_public(entry):
    # match "Publicly"/"Publiquement" only — avoids the "...share/partager with us?" memories field
    return _any_yes(entry, r"publi")

def get_country(entry):
    v = _find(entry, r"country|pays")                     # "Country where you knew..." / "Pays où..."
    if isinstance(v, dict):
        v = v.get("Name") or v.get("Country") or v.get("Label") or v.get("Code") or ""
    return v.strip() if isinstance(v, str) else ""

# Detect a message's actual language (FR vs EN) from its text, so translation works even when
# someone writes French on the English page (or vice versa). Accents weigh heavily; common
# stop/tribute words break ties; the form's language is the fallback on a tie.
_FR_ACCENTS = set("àâäçéèêëîïôöùûüÿœæ")
_FR_WORDS = {
    "le", "la", "les", "un", "une", "des", "du", "et", "est", "ne", "pas", "vous", "nous", "tu",
    "te", "ton", "ta", "tes", "votre", "vos", "dans", "pour", "avec", "sur", "son", "sa", "ses",
    "aux", "que", "qui", "ce", "cette", "mon", "ma", "mes", "repose", "paix", "cher", "chere",
    "chers", "ame", "coeur", "coeurs", "jamais", "toujours", "merci", "famille", "dieu", "frere",
    "soeur", "bonne", "grand", "homme", "amour", "eternel", "eternelle", "adieu", "souvenir",
    "priere", "prieres", "tellement", "oncle", "tante", "ami", "amie", "gentil", "gentille",
    "aime", "manqueras", "manquera", "manques", "reste", "resteras", "tres", "etait", "nos",
    "notre", "ici", "bien", "sans", "tout", "toute", "ses", "elle", "il",
}
_EN_WORDS = {
    "the", "and", "you", "your", "we", "our", "he", "she", "his", "her", "they", "them", "for",
    "with", "on", "in", "of", "to", "at", "rest", "peace", "dear", "soul", "heart", "hearts",
    "never", "always", "thank", "thanks", "family", "god", "brother", "sister", "good", "great",
    "man", "love", "forever", "goodbye", "bye", "memory", "memories", "will", "was", "were",
    "have", "has", "had", "may", "miss", "missed", "beautiful", "kind", "gentle", "amazing",
    "wonderful", "uncle", "aunt", "friend", "laughter", "advice", "impact", "inspiration",
    "knew", "known", "father", "mother", "an", "as", "so", "from", "us",
}

def detect_lang(text, fallback="en"):
    t = (text or "").lower()
    fr = sum(3 for c in t if c in _FR_ACCENTS)
    words = re.findall(r"[a-zàâäçéèêëîïôöùûüÿœæ']+", t)
    fr += sum(1 for w in words if w in _FR_WORDS)
    en = sum(1 for w in words if w in _EN_WORDS)
    return "fr" if fr > en else ("en" if en > fr else fallback)

# ---------- pure build step (unit-testable without network) ----------

def build_tributes(forms_entries):
    """forms_entries: list of (lang, [entry, ...]) -> ordered list of tribute dicts."""
    items = []
    for lang, entries in forms_entries:
        for e in entries:
            if not (is_approved(e) and is_public(e)):
                continue
            msg = get_message(e)
            if not msg:
                continue
            it = {"name": get_name(e, lang), "message": msg, "lang": detect_lang(msg, lang)}
            country = get_country(e)
            if country:
                it["place"] = country                         # shown on the wall as "Country · date"
            ts = get_timestamp(e)
            if ts:
                it["date"] = ts[:10]
            it["_ts"] = ts
            items.append(it)
    items.sort(key=lambda x: x["_ts"])                        # chronological across both forms
    for it in items:
        it.pop("_ts", None)
    return items

# ---------- network + main ----------

def _api_get(path, key):
    req = urllib.request.Request(API_BASE + path,
                                 headers={"Authorization": "Bearer " + key,
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_entries(form_id, key, max_gap=20, hard_cap=5000):
    """Cognito has no list-entries endpoint; fetch one-by-one by number
    (/forms/{id}/entries/{n}) until a run of `max_gap` consecutive misses (tolerates
    gaps from deleted entries). Non-404 HTTP errors propagate so we never write on failure."""
    out, n, misses = [], 1, 0
    while misses < max_gap and n <= hard_cap:
        try:
            out.append(_api_get("/forms/%s/entries/%d" % (form_id, n), key))
            misses = 0
        except urllib.error.HTTPError as he:
            if he.code == 404:
                misses += 1
            else:
                raise
        n += 1
    return out

def _mymemory(text, src, tgt):
    url = "%s?q=%s&langpair=%s|%s" % (TRANSLATE_API, urllib.parse.quote(text), src, tgt)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    t = (data.get("responseData") or {}).get("translatedText")
    return t.strip() if isinstance(t, str) and t.strip() else None

def translate(text, src, tgt, maxlen=480):
    """Machine-translate text src->tgt (keyless). Chunks long text; returns None on any failure."""
    if not text or src == tgt:
        return None
    try:
        if len(text) <= maxlen:
            return _mymemory(text, src, tgt)
        chunks, cur = [], ""                                  # split on sentence boundaries
        for part in re.split(r"(?<=[.!?])\s+", text):
            if cur and len(cur) + len(part) + 1 > maxlen:
                chunks.append(cur); cur = part
            else:
                cur = (cur + " " + part).strip()
        if cur:
            chunks.append(cur)
        out = []
        for c in chunks:
            tr = _mymemory(c, src, tgt)
            if not tr:
                return None
            out.append(tr)
        return " ".join(out)
    except Exception:  # noqa: BLE001  (translation is best-effort; never break the sync)
        return None

def add_translations(items):
    """Add each tribute's message translated into the opposite language (cached by message)."""
    cache = {}
    try:                                                      # reuse prior translations for unchanged text
        for p in json.load(open(OUT, encoding="utf-8")):
            if p.get("message") and p.get("translation"):
                cache[(p.get("lang"), p["message"])] = p["translation"]
    except Exception:  # noqa: BLE001
        pass
    for it in items:
        tgt = "fr" if it["lang"] == "en" else "en"
        tr = cache.get((it["lang"], it["message"]))
        if tr is None:
            tr = translate(it["message"], it["lang"], tgt)
        if tr and tr.strip().lower() != it["message"].strip().lower():
            it["translation"] = tr

def main():
    key = os.environ.get("COGNITO_API_KEY")
    if not key:
        print("sync_tributes: COGNITO_API_KEY not set", file=sys.stderr)
        return 1
    forms_entries = []
    for form_id, lang in FORMS:
        try:
            entries = fetch_entries(form_id, key)
        except urllib.error.HTTPError as e:
            print("sync_tributes: API error form %s: HTTP %s %s" % (form_id, e.code, e.reason),
                  file=sys.stderr)
            return 2
        except Exception as e:  # noqa: BLE001
            print("sync_tributes: API error form %s: %s" % (form_id, e), file=sys.stderr)
            return 2
        ok = sum(1 for e in entries if is_approved(e) and is_public(e))
        # counts only — never log names/messages (this repo's Action logs are public)
        print("form %s (%s): %d entries, %d approved+public" % (form_id, lang, len(entries), ok))
        forms_entries.append((lang, entries))

    items = build_tributes(forms_entries)
    if os.environ.get("SYNC_DIAG"):                           # dry run: report only, write nothing
        print("DRY RUN: would write %d tribute(s); no file changes." % len(items))
        return 0
    add_translations(items)                                   # opposite-language translation per message
    print("sync_tributes: %d/%d tribute(s) have a translation"
          % (sum(1 for it in items if it.get("translation")), len(items)))
    text = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print("sync_tributes: wrote %s with %d tribute(s)" % (OUT, len(items)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
