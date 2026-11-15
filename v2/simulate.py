"""Historical test of the v2 rules.

A: from the real 14 Aug 2026 holdings, weekly decisions 19 Aug → last Wednesday.
B: from €100,000 cash, weekly decisions over ~2 years (sanity run of behaviour).

This does NOT rewrite the track record: the real holdings were unchanged since
14 Aug (v2/state/history.csv). It shows what the rules would have done.

Biases (disclosed): the universe was chosen in Nov 2026 (survivorship /
hindsight in fund selection); one price source family; costs are an estimate.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2.engine import Prices, apply, benchmark_index, decide, scan

ROOT = Path(__file__).resolve().parent


def wednesdays(start: date, end: date) -> list[str]:
    d = start + timedelta(days=(2 - start.weekday()) % 7)
    out = []
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=7)
    return out


def run(name: str, holdings: dict[str, int], cash: float, start: str, dates: list[str], prices: Prices, uni: list[dict], pol: dict) -> dict:
    """Value at `start`, then decide weekly on `dates` (all after start)."""
    weeks, trades_log, checks = [], [], []
    bidx = benchmark_index(prices, pol, [start] + dates)
    bench0 = bidx[start]
    start_value = round(cash + sum(sh * prices.close(i, start) for i, sh in holdings.items()), 2)
    for d in dates:
        sc = scan(prices, uni, pol, d)
        dec = decide(d, holdings, cash, prices, uni, pol, sc)
        holdings, cash = apply(holdings, cash, dec)
        if cash < -0.005:
            raise SystemExit(f"{name} {d}: negative cash {cash}")
        px = {i: prices.close(i, d) for i in holdings}
        nav = round(cash + sum(sh * px[i] for i, sh in holdings.items()), 2)
        w = {i: sh * px[i] / nav for i, sh in holdings.items()}
        sats = [i for i in holdings if next(u for u in uni if u["id"] == i)["sleeve"] == "satellite"]
        core = w.get(pol["core"]["equity"], 0) + w.get(pol["core"]["bonds"], 0)
        n_changes = sum(1 for t in dec.trades if t["kind"] in ("entry", "exit") or (t["side"] == "sell" and t["id"] not in holdings))
        checks.append({
            "date": d,
            "changes": n_changes,
            "max_sat_weight": round(max([w[i] for i in sats], default=0), 4),
            "n_sats": len(sats),
            "core_weight": round(core, 4),
            "cash_weight": round(cash / nav, 4),
        })
        for t in dec.trades:
            trades_log.append({"date": d, **{k: t[k] for k in ("id", "side", "shares", "price", "amount", "cost", "kind")},
                               "why": t["reason"].get("why"), "detail": t["reason"].get("detail")})
        weeks.append({"date": d, "nav": nav, "bench": round(bidx[d], 4), "regime": dec.regime,
                      "breadth": sc["breadth_pct"], "n_trades": len(dec.trades), "sats": ",".join(sorted(sats)),
                      "deferred": len(dec.deferred), "notes": " | ".join(dec.notes)})

    navs = [w["nav"] for w in weeks]
    total = navs[-1] / start_value - 1
    bench = weeks[-1]["bench"] / bench0 - 1
    peak, mdd = start_value, 0.0
    for v in navs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    rets = [navs[i] / navs[i - 1] - 1 for i in range(1, len(navs))]
    vol = (math.sqrt(sum((r - sum(rets) / len(rets)) ** 2 for r in rets) / (len(rets) - 1)) * math.sqrt(52)) if len(rets) > 2 else None
    traded = sum(t["amount"] for t in trades_log)
    years = max((date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / 365.25, 1 / 52)
    summary = {
        "run": name, "from": dates[0], "to": dates[-1], "weeks": len(dates),
        "start_value": start_value, "end_value": navs[-1],
        "return_pct": round(total * 100, 2), "benchmark_return_pct": round(bench * 100, 2),
        "max_drawdown_pct": round(mdd * 100, 2), "ann_vol_pct": round(vol * 100, 2) if vol else None,
        "instrument_changes": sum(c["changes"] for c in checks), "trades": len(trades_log),
        "turnover_per_year_pct": round(traded / (sum(navs) / len(navs)) / years * 100, 1),
        "costs_eur": round(sum(t["cost"] for t in trades_log), 2),
        "weeks_risk_off": sum(1 for w in weeks if w["regime"] == "risk_off"),
        "rule_checks": {
            "max_changes_in_a_week": max(c["changes"] for c in checks),
            "max_satellite_weight_pct": round(max(c["max_sat_weight"] for c in checks) * 100, 2),
            "max_satellites_held": max(c["n_sats"] for c in checks),
            "weeks_core_outside_40_60": sum(1 for c in checks if not 0.40 <= c["core_weight"] <= 0.60),
            "weeks_cash_above_5pct": sum(1 for c in checks if c["cash_weight"] > 0.05),
            "first_week_cash_at_or_below_5pct": next((c["date"] for c in checks if c["cash_weight"] <= 0.05), None),
        },
        "final_holdings": holdings, "final_cash": cash,
    }
    out = ROOT / "evidence"
    out.mkdir(exist_ok=True)
    (out / f"simulation_{name}.json").write_text(json.dumps({"summary": summary, "weeks": weeks, "checks": checks}, indent=1))
    with (out / f"simulation_{name}_trades.csv").open("w", newline="") as f:
        if trades_log:
            wr = csv.DictWriter(f, fieldnames=list(trades_log[0].keys()))
            wr.writeheader()
            wr.writerows(trades_log)
    print(f"\n=== {name}\n" + json.dumps(summary, indent=1))
    print("date | nav | regime | breadth | sats | trades | deferred | notes")
    for w in weeks:
        print(f"WEEK {name} {w['date']} | {w['nav']:,.0f} | {w['regime']} | {w['breadth']} | {w['sats']} | {w['n_trades']} | {w['deferred']} | {w['notes']}")
    return summary



def main() -> None:
    uni = [i for i in yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"] if i.get("status") == "verified"]
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    prices = Prices(list(csv.DictReader((ROOT / "state" / "prices.csv").open())))
    last = date.today()

    # A: real holdings from 14 Aug.
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    hold = {p["id"]: p["shares"] for p in port["positions"]}
    run("A_from_14aug_holdings", hold, 28101.01, "2026-08-14", wednesdays(date(2026, 8, 19), last), prices, uni, pol)

    # B: €100k cash, as far back as 12-month history allows for most of the universe.
    first_dates = sorted(prices.dates[i["id"]][0] for i in uni if i["id"] in prices.dates)
    median_first = date.fromisoformat(first_dates[len(first_dates) // 2])
    start_b = max(median_first + timedelta(days=400), last - timedelta(days=730))
    weeks_b = wednesdays(start_b, last)
    run("B_from_cash_2y", {}, 100000.0, weeks_b[0], weeks_b[1:], prices, uni, pol)


if __name__ == "__main__":
    main()
