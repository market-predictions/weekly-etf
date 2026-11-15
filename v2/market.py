"""Download daily closes (Yahoo).

Writes three long-format files (date,id,close) in v2/state/:
  prices_usd.csv     US-listed ETFs in USD (raw; used for the cross-check)
  prices.csv         the same ETFs converted to EUR with that day's EURUSD close
                     (the engine scores and values the US portfolio on these)
  mirror_prices.csv  the European mirror lines in EUR, keyed by Yahoo symbol (e.g. SXR8.DE)

EURUSD=X is USD per EUR, so close_eur = close_usd / eurusd on the same date
(or the latest earlier FX close, at most 4 days back).
"""
from __future__ import annotations

import bisect
import csv
import os
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2 import sources as S

ROOT = Path(__file__).resolve().parent
YEARS = int(os.environ.get("V2_YEARS", "3"))
FX = "EURUSD=X"
BENCH_MIRROR = ["SXR8.DE", "EUNA.DE"]


def universe() -> list[dict]:
    return [i for i in yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"] if i.get("status") == "verified"]


def mirror_lines(uni: list[dict]) -> list[str]:
    return sorted({i["mirror"]["line"] for i in uni} | set(BENCH_MIRROR))


def fx_at(fx_dates: list[str], fx_vals: list[float], d: str) -> float | None:
    i = bisect.bisect_right(fx_dates, d) - 1
    if i < 0 or (date.fromisoformat(d) - date.fromisoformat(fx_dates[i])).days > 4:
        return None
    return fx_vals[i]


def _write(name: str, rows: list[dict]) -> Path:
    out = ROOT / "state" / name
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "id", "close"])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: (x["date"], x["id"])))
    return out


def main() -> None:
    end = date.today()
    start = end - timedelta(days=365 * YEARS + 30)
    fx = S.yahoo_symbol(FX, start, end)
    if not fx.closes:
        raise SystemExit(f"PRICES_BLOCKED: no {FX} data ({fx.error})")
    fx_dates = sorted(fx.closes)
    fx_vals = [fx.closes[k] for k in fx_dates]
    usd, eur, mir, report = [], [], [], []
    uni = universe()
    for inst in uni:
        r = S.yahoo_symbol(inst["id"], start, end)
        if r.currency not in (None, "USD"):
            report.append(f"{inst['id']}: skipped, currency {r.currency}")
            continue
        for d, c in sorted(r.closes.items()):
            usd.append({"date": d, "id": inst["id"], "close": round(c, 4)})
            rate = fx_at(fx_dates, fx_vals, d)
            if rate:
                eur.append({"date": d, "id": inst["id"], "close": round(c / rate, 4)})
        print(f"{inst['id']}: {len(r.closes)} closes from {min(r.closes) if r.closes else None} err={r.error}", flush=True)
        S.pause(0.4)
    for sym in mirror_lines(uni):
        r = S.yahoo_symbol(sym, start, end)
        if r.currency not in (None, "EUR"):
            print(f"{sym}: skipped, currency {r.currency}", flush=True)
            continue
        for d, c in sorted(r.closes.items()):
            mir.append({"date": d, "id": sym, "close": round(c, 4)})
        print(f"MIRROR {sym}: {len(r.closes)} closes from {min(r.closes) if r.closes else None} err={r.error}", flush=True)
        S.pause(0.4)
    _write("prices_usd.csv", usd)
    out = _write("prices.csv", eur)
    _write("mirror_prices.csv", mir)
    _write("fx.csv", [{"date": k, "id": FX, "close": round(v, 6)} for k, v in fx.closes.items()])
    print(f"PRICES_WRITTEN {out} rows={len(eur)} usd={len(usd)} mirror={len(mir)} fx={len(fx.closes)}")


if __name__ == "__main__":
    main()
