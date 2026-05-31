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

API_BASE = "https://www.cognitoforms.com/api/1"
FORMS = [("7", "en"), ("8", "fr")]          # (Cognito form id, language tag)
OUT = "tributes.json"
PAGE_SIZE = 100

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
        v = _find(entry, r"\bname\b|nom")
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

def is_approved(entry):
    return _truthy_yes(_find(entry, r"approv|approuv"))   # EN "Approved" / FR "Approuvé"

def is_public(entry):
    return _truthy_yes(_find(entry, r"share|public|publi|partag"))

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
            it = {"name": get_name(e, lang), "message": msg, "lang": lang}
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

def fetch_entries(form_id, key):
    out, page = [], 1
    while True:
        batch = _api_get("/forms/%s/entries?page=%d&pageSize=%d" % (form_id, page, PAGE_SIZE), key)
        if isinstance(batch, dict):                           # tolerate a wrapped response
            batch = (batch.get("Entries") or batch.get("entries")
                     or next((v for v in batch.values() if isinstance(v, list)), []))
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < PAGE_SIZE or page > 100:
            break
        page += 1
    return out

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
        if entries:                                           # log keys to verify field mapping
            print("form %s (%s): %d entries; sample keys: %s"
                  % (form_id, lang, len(entries), list(entries[0].keys())))
        forms_entries.append((lang, entries))

    items = build_tributes(forms_entries)
    text = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print("sync_tributes: wrote %s with %d tribute(s)" % (OUT, len(items)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
