#!/usr/bin/env python3
"""
apply_patch.py — Apply a JSON patch file to rates.json

Usage: python3 apply_patch.py <patch_file>

The patch file is a JSON object with:
{
  "date": "2026-04-18",
  "source": "HKET + moneyhk101",
  "banks": {
    "HSBC": {
      "rates": {"1M": 0.1, "3M": 0.125},
      "new_fund_rates": {"1M": 3.0, "3M": 2.2},
      "usd_rates": {...},
      "usd_new_fund_rates": {...},
      "cny_rates": {...},
      "cny_new_fund_rates": {...},
      "promo_rates": {...},
      "notes": "optional note"
    },
    ...
  }
}

Only provided fields are updated; missing fields are left unchanged.
"""

import json
import sys
import os
from datetime import date

RATES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "rates.json")

RATE_KEYS = [
    "rates", "new_fund_rates", "promo_rates",
    "usd_rates", "usd_new_fund_rates",
    "cny_rates", "cny_new_fund_rates",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apply_patch.py <patch_file>")
        sys.exit(1)

    patch_file = sys.argv[1]

    with open(patch_file, "r") as f:
        patch = json.load(f)

    with open(RATES_FILE, "r") as f:
        data = json.load(f)

    patch_banks = patch.get("banks", {})
    changes = 0
    matched = 0

    for bank in data["banks"]:
        name = bank["bank"]
        if name not in patch_banks:
            continue
        matched += 1
        upd = patch_banks[name]

        for key in RATE_KEYS:
            if key in upd:
                old = bank.get(key, {})
                new = upd[key]
                if old != new:
                    changes += 1
                bank[key] = new

        if "notes" in upd:
            bank["notes"] = upd["notes"]

    # Update metadata
    today = patch.get("date", date.today().isoformat())
    data["last_updated"] = today
    source = patch.get("source", "official bank websites + HKET + moneyhk101")
    data["data_source"] = f"Compiled from {source} ({today})"

    with open(RATES_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Patched rates.json — {matched} banks matched, {changes} field changes, date={today}")


if __name__ == "__main__":
    main()
