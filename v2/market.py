"""Download daily EUR closes for every verified universe instrument (Yahoo).

Writes v2/state/prices.csv in long format: date,id,close. Keeps ~3 years so the
12-month momentum and 200-day trend can be computed for historical tests.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2 import sources as S

ROOT = Path(__file__).resolve().parent
YEARS = 3


def verified_instruments() -> list[dict]:
    uni = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    return [i for i in uni if i.get("status") == "verified"]


def main() -> None:
    end = date.today()
    start = end - timedelta(days=365 * YEARS + 30)
    rows, report = [], []
    for inst in verified_instruments():
        r = S.yahoo(inst["id"], inst["exchange"], start, end)
        if r.currency not in (None, "EUR"):
            report.append(f"{inst['id']}: skipped, currency {r.currency}")
            continue
        for d, c in sorted(r.closes.items()):
            rows.append({"date": d, "id": inst["id"], "close": round(c, 4)})
        first = min(r.closes) if r.closes else None
        report.append(f"{inst['id']}: {len(r.closes)} closes from {first} err={r.error}")
        print(report[-1], flush=True)
        S.pause(0.5)
    out = ROOT / "state" / "prices.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "id", "close"])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: (x["date"], x["id"])))
    print(f"PRICES_WRITTEN {out} rows={len(rows)}")


if __name__ == "__main__":
    main()
