"""Backfill from the 7 Aug 2026 portfolio to the latest Wednesday: US portfolio + European mirror.

US portfolio: no trades happened after 7 Aug (the v1 system stopped), so the honest record is
the unchanged holdings revalued at each Wednesday close (USD close / EURUSD). Held prices are
checked against Alpha Vantage (USD); a disagreement > 1% stops the backfill.

Mirror: starts on 7 Aug with the same value, in cash; it converts to the US weights at the first
European close after 7 Aug and then follows the mirror rules (v2/mirror.py).

Writes v2/state/: portfolio.json, trades.csv, history.csv, valuations.csv, history_v1.csv,
mirror.json, mirror_trades.csv, mirror_history.csv; evidence/backfill_<date>.json.
"""
from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2 import market
from v2 import mirror as MR
from v2 import sources as S
from v2.engine import Prices, benchmark_return

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
EVID = ROOT / "evidence"
REPO = ROOT.parent

START = date(2026, 8, 7)
START_CASH = 2534.36
START_POSITIONS = {"CIBR": 253, "GSG": 374, "IEFA": 312, "PAVE": 107, "SMH": 59, "URNM": 48, "XBI": 40, "XLU": 14, "XLV": 37}
V1_NAV_AT_START = 110005.86  # output/etf_portfolio_state.json, last_valuation 2026-08-07
INCEPTION = ("2026-03-28", 100000.0)
TOLERANCE_PCT = 1.0


def wednesdays(end: date) -> list[str]:
    days = [START.isoformat()]
    d = START + timedelta(days=(2 - START.weekday()) % 7 or 7)
    while d <= end:
        days.append(d.isoformat())
        d += timedelta(days=7)
    return days


def read(name: str) -> list[dict]:
    return list(csv.DictReader((STATE / name).open()))


def write(name: str, rows: list[dict]) -> None:
    with (STATE / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    market.main()
    uni = {i["id"]: i for i in market.universe()}
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    prices = Prices(read("prices.csv"))
    usd = Prices(read("prices_usd.csv"))
    mpx = Prices(read("mirror_prices.csv"))
    end = date.today()
    dates = wednesdays(end - timedelta(days=(end.weekday() - 2) % 7))
    if (date.fromisoformat(dates[-1]) == end):
        dates = dates[:-1]

    # Verify held USD closes against Alpha Vantage (compact: ~100 trading days)
    problems, evidence = [], []
    for iid in START_POSITIONS:
        av = S.alpha_vantage(iid, "US")
        S.pause(13)
        for d in dates:
            p = usd.close(iid, d, max_stale_days=4)
            k = max((x for x in av.closes if x <= d), default=None)
            v = av.closes.get(k) if k else None
            status = "unverified" if v is None or p is None else ("verified" if abs(p - v) / p * 100 <= TOLERANCE_PCT else "disagreement")
            if p is None:
                status = "missing_primary"
            if status in ("missing_primary", "disagreement"):
                problems.append(f"{d} {iid}: yahoo {p} vs alpha_vantage {v}")
            evidence.append({"date": d, "id": iid, "yahoo_usd": p, "av_usd": v, "status": status})

    # US portfolio: unchanged holdings revalued
    history, valuations = [], []
    b_idx = 100.0
    for n, d in enumerate(dates):
        px = {i: prices.close(i, d, max_stale_days=4) for i in START_POSITIONS}
        if any(v is None for v in px.values()):
            raise SystemExit(f"BACKFILL_BLOCKED: missing EUR close on {d}: {[i for i, v in px.items() if v is None]}")
        inv = round(sum(sh * px[i] for i, sh in START_POSITIONS.items()), 2)
        nav = round(START_CASH + inv, 2)
        if n:
            b_idx = round(b_idx * (1 + (benchmark_return(prices, pol, dates[n - 1], d) or 0.0)), 6)
        history.append({"date": d, "nav_eur": nav, "cash_eur": START_CASH, "invested_eur": inv,
                        "benchmark_close": prices.close(pol["trend_reference"], d), "source": "backfill_unchanged_holdings",
                        "cum_return_pct": round((nav / history[0]["nav_eur"] - 1) * 100, 4) if history else 0.0,
                        "week_return_pct": round((nav / history[-1]["nav_eur"] - 1) * 100, 4) if history else 0.0,
                        "benchmark_cum_return_pct": round((b_idx / 100 - 1) * 100, 4), "benchmark_index": b_idx})
        st = {e["id"]: e["status"] for e in evidence if e["date"] == d}
        valuations += [{"date": d, "id": i, "isin": "", "shares": sh, "close_date": d, "close": round(px[i], 4),
                        "value_eur": round(sh * px[i], 2), "price_status": st.get(i, "unverified")} for i, sh in START_POSITIONS.items()]

    # Mirror portfolio
    line_of = {i: u["mirror"]["line"] for i, u in uni.items()}
    band, cost = pol["mirror"]["rebalance_band_pts"], pol["mirror"]["cost_bps"]
    mpol = {"benchmark": pol["mirror"]["benchmark"]}
    m_hold, m_cash = {}, history[0]["nav_eur"]
    pending = {"decided": dates[0], "targets": MR.implied_weights(START_POSITIONS, START_CASH, prices, dates[0], line_of)}
    m_hist, m_trades = [], []
    mb_idx = 100.0
    for n, d in enumerate(dates):
        if pending and pending["decided"] < d:
            m_hold, m_cash, tr, prob = MR.execute(m_hold, m_cash, pending["targets"], mpx, pending["decided"], band, cost)
            if prob:
                raise SystemExit("BACKFILL_BLOCKED: mirror " + "; ".join(prob))
            m_trades += [{"date": t["date"], "type": t["side"], "line": t["line"], "shares": t["shares"], "price_eur": round(t["price"], 4),
                          "amount_eur": t["amount"], "reason": f"follows US decision of {pending['decided']}"} for t in tr]
            pending = None
        if n:
            mb_idx = round(mb_idx * (1 + (benchmark_return(mpx, mpol, dates[n - 1], d) or 0.0)), 6)
        nav, _ = MR.value(m_hold, m_cash, mpx, d)
        us = history[n]
        m_hist.append({"date": d, "nav_eur": nav, "cash_eur": m_cash, "invested_eur": round(nav - m_cash, 2),
                       "cum_return_pct": round((nav / m_hist[0]["nav_eur"] - 1) * 100, 4) if m_hist else 0.0,
                       "week_return_pct": round((nav / m_hist[-1]["nav_eur"] - 1) * 100, 4) if m_hist else 0.0,
                       "benchmark_index": mb_idx, "benchmark_cum_return_pct": round((mb_idx / 100 - 1) * 100, 4),
                       "us_cum_return_pct": us["cum_return_pct"]})
        if n and pending is None:
            t = MR.implied_weights(START_POSITIONS, START_CASH, prices, d, line_of)
            if MR.needs_trade(m_hold, m_cash, t, mpx, d, band):
                pending = {"decided": d, "targets": t}

    STATE.mkdir(exist_ok=True)
    EVID.mkdir(exist_ok=True)
    write("history.csv", history)
    write("valuations.csv", valuations)
    write("trades.csv", [{"date": START.isoformat(), "type": "opening_balance", "id": i, "isin": "", "shares": sh, "price_eur": "",
                          "amount_eur": "", "reason": "Holdings carried over from the 7 Aug 2026 report"} for i, sh in START_POSITIONS.items()]
          + [{"date": START.isoformat(), "type": "opening_cash", "id": "CASH", "isin": "", "shares": "", "price_eur": "",
              "amount_eur": START_CASH, "reason": "Cash carried over from the 7 Aug 2026 report"}])
    v1 = [{"date": r["date"], "nav_eur": r["nav_eur"]} for r in csv.DictReader((REPO / "output" / "etf_valuation_history.csv").open())]
    write("history_v1.csv", v1)
    last = history[-1]
    (STATE / "portfolio.json").write_text(json.dumps({
        "as_of": last["date"], "cash_eur": START_CASH, "nav_eur": last["nav_eur"], "track_record_start": START.isoformat(),
        "inception": {"date": INCEPTION[0], "capital_eur": INCEPTION[1]},
        "positions": [{"id": i, "isin": None, "exchange": "US", "shares": sh} for i, sh in sorted(START_POSITIONS.items())],
    }, indent=1) + "\n")
    write("mirror_history.csv", m_hist)
    write("mirror_trades.csv", m_trades or [{"date": "", "type": "", "line": "", "shares": "", "price_eur": "", "amount_eur": "", "reason": ""}])
    (STATE / "mirror.json").write_text(json.dumps({
        "as_of": m_hist[-1]["date"], "cash_eur": m_cash, "nav_eur": m_hist[-1]["nav_eur"], "start": START.isoformat(),
        "positions": [{"line": ln, "shares": sh} for ln, sh in sorted(m_hold.items())], "pending": pending,
    }, indent=1) + "\n")
    (EVID / f"backfill_{date.today():%Y%m%d}.json").write_text(json.dumps({"problems": problems, "prices": evidence}, indent=1))

    print(f"\nv1 NAV on {START}: {V1_NAV_AT_START:,.2f} | v2 recomputed: {history[0]['nav_eur']:,.2f} "
          f"({(history[0]['nav_eur'] / V1_NAV_AT_START - 1) * 100:+.2f}%)")
    print("\n| date | US NAV | US cum % | bench cum % | mirror NAV | mirror cum % | mirror bench % |\n|---|---|---|---|---|---|---|")
    for h, m in zip(history, m_hist):
        print(f"| {h['date']} | {h['nav_eur']:,.2f} | {h['cum_return_pct']} | {h['benchmark_cum_return_pct']} | {m['nav_eur']:,.2f} | "
              f"{m['cum_return_pct']} | {m['benchmark_cum_return_pct']} |")
    print("\nMIRROR_TRADES")
    for t in m_trades:
        print(f"  {t['date']} {t['type']} {t['shares']} {t['line']} @ {t['price_eur']} = {t['amount_eur']}")
    print("mirror holdings:", m_hold, "cash", m_cash, "pending", pending)
    counts = {}
    for e in evidence:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print("price status counts:", counts, "| problems:", problems or "none")
    if problems:
        raise SystemExit("BACKFILL_BLOCKED: missing or disagreeing prices (see evidence)")
    print("BACKFILL_OK")


if __name__ == "__main__":
    main()
