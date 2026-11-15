"""Assemble every fact the report may state, for one report date.

The report (and the AI commentary) may only use numbers that appear here.
Numbers are rounded to how they are displayed, so the number check can match
the text exactly.
"""
from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2 import macro as M
from v2.engine import Prices, apply, benchmark_index, benchmark_return, decide, scan

ROOT = Path(__file__).resolve().parent
MARKET_PANEL = [  # asset-class barometer shown in the report
    ("VWCE", "World equity", "Wereldwijde aandelen"),
    ("SXR8", "US equity (S&P 500)", "Amerikaanse aandelen (S&P 500)"),
    ("EUNK", "European equity", "Europese aandelen"),
    ("IJPA", "Japanese equity", "Japanse aandelen"),
    ("EMIM", "Emerging-market equity", "Aandelen opkomende markten"),
    ("EUNH", "Euro government bonds", "Euro-staatsobligaties"),
    ("EUN5", "Euro corporate bonds", "Euro-bedrijfsobligaties"),
    ("4GLD", "Gold", "Goud"),
]


def pct(x: float | None, nd: int = 2) -> float | None:
    if x is None:
        return None
    v = round(x * 100, nd)
    return 0.0 if v == 0 else v  # no "-0.0"


def ret(prices: Prices, iid: str, d: str, days_back: int) -> float | None:
    end = prices.close(iid, d)
    start = prices.close(iid, (date.fromisoformat(d) - timedelta(days=days_back)).isoformat())
    return (end / start - 1) if end and start else None


def attribution(hist: list[dict], d: str, names: dict, prices: Prices, pol: dict) -> dict:
    """Explain the gap with the benchmark, per holding and cash, chained weekly.

    For each week: holding i contributes w_i × (r_i − r_bench), cash contributes
    w_cash × (0 − r_bench), with weights at the start of the week. Summed over
    weeks this equals the arithmetic gap up to a small compounding residual,
    which is reported rather than hidden.
    """
    vals = list(csv.DictReader((ROOT / "state" / "valuations.csv").open()))
    by: dict[str, dict[str, dict]] = {}
    for r in vals:
        by.setdefault(r["date"], {})[r["id"]] = r
    H = {h["date"]: h for h in hist if h["date"] <= d}
    dates = sorted(H)

    def period(pairs):
        comp: dict[str, float] = {}
        for a, b in pairs:
            nav = float(H[a]["nav_eur"])
            rb = benchmark_return(prices, pol, a, b) or 0.0
            for i, r in by.get(a, {}).items():
                pa, pb = prices.close(i, a), prices.close(i, b)
                if not pa or not pb:
                    continue
                w = float(r["value_eur"]) / nav
                ri = pb / pa - 1
                comp[i] = comp.get(i, 0.0) + w * (ri - rb)
            comp["CASH"] = comp.get("CASH", 0.0) + float(H[a]["cash_eur"]) / nav * (0 - rb)
        return comp

    def own_return(i, first, last):
        pa, pb = prices.close(i, first), prices.close(i, last)
        return round((pb / pa - 1) * 100, 2) if pa and pb else None

    def start_weight(i, first):
        r = by.get(first, {}).get(i)
        nav = float(H[first]["nav_eur"])
        return round((float(r["value_eur"]) if r else float(H[first]["cash_eur"]) if i == "CASH" else 0) / nav * 100, 1)

    def pack(comp, first, last):
        span = [x for x in dates if first <= x <= last]
        bi = benchmark_index(prices, pol, span)
        bret = bi[last] / bi[first] - 1
        gap = (float(H[last]["nav_eur"]) / float(H[first]["nav_eur"]) - 1) - bret
        items = [{"id": k, "name": "Cash" if k == "CASH" else names.get(k, k), "pts": round(v * 100, 2),
                  "own_return_pct": 0.0 if k == "CASH" else own_return(k, first, last), "start_weight_pct": start_weight(k, first)} for k, v in comp.items()]
        items.sort(key=lambda x: x["pts"])
        resid = round(gap * 100 - sum(x["pts"] for x in items), 2)
        bench = round(bret * 100, 2)
        return {"from": first, "to": last, "gap_pts": round(gap * 100, 2), "benchmark_return_pct": bench, "items": items, "residual_pts": resid}

    pairs = list(zip(dates, dates[1:]))
    return {"since_start": pack(period(pairs), dates[0], dates[-1]) if pairs else None,
            "week": pack(period(pairs[-1:]), pairs[-1][0], pairs[-1][1]) if pairs else None}


def build(d: str, with_macro: bool = True, applied: dict | None = None) -> dict:
    """Facts for report date d.

    Preview (applied=None): decide from the saved state without saving anything.
    Live run: pass applied={"hold_before", "cash_before", "decision", "hold_after", "cash_after"}
    after run_weekly has saved the new state, so nothing is decided twice.
    """
    uni_all = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    uni = [i for i in uni_all if i.get("status") == "verified"]
    names = {i["id"]: i["name"] for i in uni_all}
    sleeves = {i["id"]: i["sleeve"] for i in uni_all}
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    prices = Prices(list(csv.DictReader((ROOT / "state" / "prices.csv").open())))
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    hist = list(csv.DictReader((ROOT / "state" / "history.csv").open()))
    sc = scan(prices, uni, pol, d)
    prev_d = (date.fromisoformat(d) - timedelta(days=7)).isoformat()
    sc_prev = scan(prices, uni, pol, prev_d)
    macro_now = M.fetch(date.fromisoformat(d)) if with_macro else {}
    if applied is None:
        pol["_runtime"] = M.runtime(macro_now)
        hold = {p["id"]: p["shares"] for p in port["positions"]}
        cash = float(port["cash_eur"])
        dec = decide(d, hold, cash, prices, uni, pol, sc)
        hold_after, cash_after = apply(hold, cash, dec)
    else:
        hold, cash = applied["hold_before"], applied["cash_before"]
        dec, hold_after, cash_after = applied["decision"], applied["hold_after"], applied["cash_after"]

    nav = round(cash_after + sum(sh * prices.close(i, d) for i, sh in hold_after.items()), 2)
    start = hist[0]
    prev_rows = [h for h in hist if h["date"] < d]
    prev_nav = float(prev_rows[-1]["nav_eur"]) if prev_rows else float(start["nav_eur"])
    bdates = sorted({h["date"] for h in hist if h["date"] <= d} | {d})
    bidx = benchmark_index(prices, pol, bdates)
    b_now, b_start = bidx[d], bidx[start["date"]]
    b_prev = bidx[prev_rows[-1]["date"]] if prev_rows else b_start
    nav_before = dec.nav_before

    positions = []
    for iid, sh in sorted(hold_after.items(), key=lambda kv: -kv[1] * prices.close(kv[0], d)):
        p = prices.close(iid, d)
        r = next((x for x in sc["rows"] if x["id"] == iid), {})
        rk = next((x for x in sc["ranked"] if x["id"] == iid), {})
        positions.append({
            "id": iid, "name": names.get(iid, iid),
            "role": "core" if iid == (pol.get("inflation_regime") or {}).get("alt_bonds") else sleeves.get(iid),
            "shares": sh, "price_eur": round(p, 2), "value_eur": round(sh * p, 2), "weight_pct": pct(sh * p / nav, 1),
            "week_return_pct": pct(ret(prices, iid, d, 7)), "return_3m_pct": pct(r.get("r63")),
            "trend": "up" if r.get("trend_up") else "down" if r.get("trend_up") is False else None,
            "rank": rk.get("rank"), "score": round(rk["score"]) if rk.get("score") is not None else None,
        })

    trades = [{
        "side": t["side"], "id": t["id"], "name": names.get(t["id"], t["id"]), "shares": t["shares"],
        "price_eur": round(t["price"], 2), "amount_eur": round(t["amount"]), "kind": t["kind"],
        "why": t["reason"].get("why"), "detail": t["reason"].get("detail"),
        "rank": t["reason"].get("rank"), "score": round(t["reason"]["score"]) if t["reason"].get("score") is not None else None,
        "replaced_by": t["reason"].get("replaced_by"), "params": t["reason"].get("params", {}),
    } for t in dec.trades]
    deferred = [{"id": x["id"], "name": names.get(x["id"], x["id"]), "kind": x["kind"], "why": x.get("why"), "detail": x.get("detail"), "params": x.get("params", {})} for x in dec.deferred]

    def scan_row(r):
        return {"rank": r["rank"], "id": r["id"], "name": names.get(r["id"], r["id"]), "score": round(r["score"]),
                "return_3m_pct": pct(r["r63"], 1), "return_6m_pct": pct(r["r126"], 1), "return_12m_pct": pct(r["r252"], 1),
                "trend": "up" if r["trend_up"] else "down", "held": r["id"] in hold_after}
    top_prev = {r["id"] for r in sc_prev["ranked"][:10]}
    top = [scan_row(r) for r in sc["ranked"][:10]]
    for r in top:
        r["new_in_top10"] = r["id"] not in top_prev

    market = []
    for iid, en, nl in MARKET_PANEL:
        market.append({"id": iid, "label_en": en, "label_nl": nl, "week_pct": pct(ret(prices, iid, d, 7)),
                       "return_3m_pct": pct(ret(prices, iid, d, 91), 1), "return_12m_pct": pct(ret(prices, iid, d, 365), 1)})

    chart = [{"date": h["date"], "portfolio_index": round(float(h["nav_eur"]) / float(start["nav_eur"]) * 100, 2),
              "benchmark_index": round(bidx[h["date"]] / b_start * 100, 2)} for h in hist if h["date"] <= d]
    if not chart or chart[-1]["date"] != d:
        chart.append({"date": d, "portfolio_index": round(nav / float(start["nav_eur"]) * 100, 2), "benchmark_index": round(b_now / b_start * 100, 2)})

    facts = {
        "report_date": d,
        "data_through": d,
        "track_record_start": start["date"],
        "benchmark": {"label": pol["benchmark"]["label"], "weights": pol["benchmark"]["weights"]},
        "portfolio": {
            "value_eur": nav, "value_before_trades_eur": nav_before, "cash_eur": round(cash_after, 2), "cash_pct": pct(cash_after / nav, 1),
            "week_return_pct": pct(nav_before / prev_nav - 1), "since_start_return_pct": pct(nav_before / float(start["nav_eur"]) - 1),
            "benchmark_week_return_pct": pct(b_now / b_prev - 1), "benchmark_since_start_return_pct": pct(b_now / b_start - 1),
            "difference_vs_benchmark_pts": round((nav_before / float(start["nav_eur"]) - 1 - (b_now / b_start - 1)) * 100, 2),
            "n_positions": len(hold_after), "start_value_eur": float(start["nav_eur"]),
        },
        "regime": {"state": sc["regime"], "breadth_pct": sc["breadth_pct"], "world_equity_trend": "up" if sc["benchmark_trend_up"] else "down",
                   "breadth_threshold_pct": pol["defensive_switch"]["max_breadth_pct"], "n_ranked": sc["n_ranked"]},
        "attribution": attribution(hist, d, names, prices, pol),
        "trades": trades,
        "deferred": deferred,
        "decision_notes": dec.notes,
        "positions": positions,
        "scan_top10": top,
        "scan_bottom5": [scan_row(r) for r in sc["ranked"][-5:]],
        "market": market,
        "macro": macro_now,
        "chart": chart,
        "rules": {
            "satellites": pol["satellites"]["count"], "satellite_weight_pct": pct(pol["satellites"]["weight_each"], 0),
            "max_changes_per_week": pol["turnover"]["max_instrument_changes_per_week"],
            "replacement_margin_pts": pol["satellites"]["replacement_margin_pts"],
            "cash_target_pct": pct(pol["cash"]["target"], 0), "cost_bps": pol["execution"]["cost_bps"],
        },
    }
    return facts


def main() -> None:
    import os
    d = os.environ.get("V2_REPORT_DATE") or date.today().isoformat()
    f = build(d)
    out = ROOT / "evidence" / f"facts_{d.replace('-', '')}.json"
    out.write_text(json.dumps(f, indent=1, ensure_ascii=False))
    print(json.dumps({k: f[k] for k in ("portfolio", "regime", "trades", "deferred")}, indent=1, ensure_ascii=False))
    for k, v in f["macro"].items():
        print("MACRO", k, v.get("date"), v.get("value"), v.get("stale"), v.get("error"))
    print(f"FACTS_WRITTEN {out}")


if __name__ == "__main__":
    main()
