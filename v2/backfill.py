"""Backfill weekly valuations from the 14 Aug 2026 portfolio to the latest Wednesday.

No trades happened after 14 Aug, so the honest track record is the unchanged
portfolio revalued at each Wednesday close. Every valuation uses the primary
source and is checked against a verifier; disagreement > tolerance stops the run.

Writes:
  v2/state/portfolio.json   current holdings + cash + as-of date
  v2/state/trades.csv       trade ledger (opening balances only, so far)
  v2/state/history.csv      one row per valuation date
  v2/state/valuations.csv   one row per position per valuation date
  v2/evidence/backfill_<date>.json  per-price source evidence
"""
from __future__ import annotations

import csv
import json
import os
from datetime import date, timedelta
from pathlib import Path

from v2 import sources as S

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
EVID = ROOT / "evidence"

START = date(2026, 8, 14)
START_CASH = 28101.01
# Holdings of the 14 Aug 2026 report (output/etf_eu_portfolio_state.json).
START_POSITIONS = [
    {"id": "L0CK", "isin": "IE00BG0J4C88", "exchange": "Xetra", "shares": 934},
    {"id": "DFEN", "isin": "IE000YYE6WK5", "exchange": "Xetra", "shares": 207},
    {"id": "VWCE", "isin": "IE00BK5BQT80", "exchange": "Xetra", "shares": 151},
    {"id": "EUNA", "isin": "IE00BDBRDM35", "exchange": "Xetra", "shares": 1526},
    {"id": "SXR8", "isin": "IE00B5BMR087", "exchange": "Xetra", "shares": 10},
    {"id": "IQQQ", "isin": "IE00B1TXK627", "exchange": "Xetra", "shares": 149},
]
BENCHMARK = {"id": "VWCE", "exchange": "Xetra"}
TOLERANCE_PCT = 1.0
PRIMARY = os.environ.get("V2_PRIMARY", "yahoo")
VERIFIER = os.environ.get("V2_VERIFIER", "stooq")


def fetch(source: str, ticker: str, exchange: str, start: date, end: date) -> S.SourceResult:
    if source == "yahoo":
        return S.yahoo(ticker, exchange, start, end)
    if source == "stooq":
        return S.stooq(ticker, exchange, start)
    if source == "alpha_vantage":
        r = S.alpha_vantage(ticker, exchange)
        S.pause(13)
        return r
    if source == "eodhd":
        return S.eodhd(ticker, exchange, start)
    if source == "twelve_data":
        r = S.twelve_data(ticker, exchange, start)
        S.pause(8)
        return r
    raise ValueError(source)


def valuation_dates(end: date) -> list[date]:
    days = [START]
    d = START + timedelta(days=(2 - START.weekday()) % 7 or 7)  # first Wednesday after start
    while d <= end:
        days.append(d)
        d += timedelta(days=7)
    return days


def close_on_or_before(closes: dict[str, float], d: date) -> tuple[str | None, float | None]:
    eligible = [k for k in closes if k <= d.isoformat() and k >= (d - timedelta(days=5)).isoformat()]
    if not eligible:
        return None, None
    k = max(eligible)
    return k, closes[k]


def main() -> None:
    end = date.today()
    # Latest completed Wednesday close (run is never before Wednesday evening in production).
    last_wed = end - timedelta(days=(end.weekday() - 2) % 7)
    dates = valuation_dates(last_wed)
    fetch_start = START - timedelta(days=7)

    series: dict[str, dict[str, S.SourceResult]] = {}
    for pos in START_POSITIONS:
        series[pos["id"]] = {
            "primary": fetch(PRIMARY, pos["id"], pos["exchange"], fetch_start, end),
            "verifier": fetch(VERIFIER, pos["id"], pos["exchange"], fetch_start, end),
        }
        p, v = series[pos["id"]]["primary"], series[pos["id"]]["verifier"]
        print(f"{pos['id']}: primary {p.source} {len(p.closes)} closes err={p.error} | verifier {v.source} {len(v.closes)} closes err={v.error}", flush=True)

    evidence, history, valuations, problems = [], [], [], []
    for d in dates:
        invested = 0.0
        for pos in START_POSITIONS:
            p = series[pos["id"]]["primary"]
            v = series[pos["id"]]["verifier"]
            pd_, px = close_on_or_before(p.closes, d)
            px = round(px, 4) if px is not None else None
            vd_, vx = close_on_or_before(v.closes, d)
            vx = round(vx, 4) if vx is not None else None
            status = "verified"
            spread = None
            if px is None:
                status = "missing_primary"
                problems.append(f"{d} {pos['id']}: no primary close")
            elif vx is None or vd_ != pd_:
                status = "unverified"
            else:
                spread = abs(px - vx) / px * 100
                if spread > TOLERANCE_PCT:
                    status = "disagreement"
                    problems.append(f"{d} {pos['id']}: {p.source} {px} vs {v.source} {vx} ({spread:.2f}%)")
            value = round(pos["shares"] * px, 2) if px is not None else None
            invested += value or 0.0
            evidence.append({"valuation_date": d.isoformat(), "id": pos["id"], "isin": pos["isin"],
                             "close_date": pd_, "primary": p.source, "primary_close": px,
                             "verifier": v.source, "verifier_close_date": vd_, "verifier_close": vx,
                             "spread_pct": round(spread, 4) if spread is not None else None, "status": status})
            valuations.append({"date": d.isoformat(), "id": pos["id"], "isin": pos["isin"], "shares": pos["shares"],
                               "close_date": pd_, "close": px, "value_eur": value, "price_status": status})
        nav = round(START_CASH + invested, 2)
        bdate, bclose = close_on_or_before(series["VWCE"]["primary"].closes, d)
        history.append({"date": d.isoformat(), "nav_eur": nav, "cash_eur": START_CASH, "invested_eur": round(invested, 2),
                        "benchmark_close": bclose, "source": "backfill_unchanged_holdings"})

    base_nav, base_bm = history[0]["nav_eur"], history[0]["benchmark_close"]
    for i, h in enumerate(history):
        h["cum_return_pct"] = round((h["nav_eur"] / base_nav - 1) * 100, 4)
        h["week_return_pct"] = round((h["nav_eur"] / history[i - 1]["nav_eur"] - 1) * 100, 4) if i else 0.0
        h["benchmark_cum_return_pct"] = round((h["benchmark_close"] / base_bm - 1) * 100, 4) if base_bm and h["benchmark_close"] else None

    STATE.mkdir(exist_ok=True)
    EVID.mkdir(exist_ok=True)
    _write_csv(STATE / "history.csv", history)
    _write_csv(STATE / "valuations.csv", valuations)
    _write_csv(STATE / "trades.csv", [
        {"date": START.isoformat(), "type": "opening_balance", "id": p["id"], "isin": p["isin"], "shares": p["shares"],
         "price_eur": "", "amount_eur": "", "reason": "Holdings carried over from the 14 Aug 2026 report"}
        for p in START_POSITIONS
    ] + [{"date": START.isoformat(), "type": "opening_cash", "id": "CASH", "isin": "", "shares": "",
          "price_eur": "", "amount_eur": START_CASH, "reason": "Cash carried over from the 14 Aug 2026 report"}])
    last = history[-1]
    (STATE / "portfolio.json").write_text(json.dumps({
        "as_of": last["date"],
        "cash_eur": START_CASH,
        "nav_eur": last["nav_eur"],
        "track_record_start": START.isoformat(),
        "positions": [{k: p[k] for k in ("id", "isin", "exchange", "shares")} for p in START_POSITIONS],
    }, indent=1) + "\n")
    (EVID / f"backfill_{date.today():%Y%m%d}.json").write_text(json.dumps(
        {"primary": PRIMARY, "verifier": VERIFIER, "tolerance_pct": TOLERANCE_PCT, "problems": problems, "prices": evidence}, indent=1))

    counts = {}
    for e in evidence:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print("\n| date | NAV | week % | cum % | VWCE cum % |\n|---|---|---|---|---|")
    for h in history:
        print(f"| {h['date']} | {h['nav_eur']:,.2f} | {h['week_return_pct']} | {h['cum_return_pct']} | {h['benchmark_cum_return_pct']} |")
    print(f"\nprice status counts: {counts}")
    print("problems:", problems or "none")
    if any(e["status"] in ("missing_primary", "disagreement") for e in evidence):
        raise SystemExit("BACKFILL_BLOCKED: missing or disagreeing prices (see evidence)")
    print("BACKFILL_OK")


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
