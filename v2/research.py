"""Alpha research: do four pre-registered improvements beat a passive mix of equal risk?

Design (fixed before looking at results, 2026-11-15):
  * One continuous weekly run 2016-01-06 → latest Wednesday, from €100k cash.
    Metrics are split into a design period (2016–2021) and a test period (2022–2026).
    Parameters are not tuned; the values below were set a priori.
  * Long-history stand-ins: core equity / trend reference IWDA, core bonds EUNH
    (VWCE and EUNA do not exist before 2017–2019).
  * Yardstick: a weekly-rebalanced IWDA/EUNH mix with the SAME volatility as the
    variant over the same period. Alpha = variant return − that mix's return.
  * HICP is used only after publication: month m becomes known on the 20th of m+1.
  * Criterion: an improvement is kept only if it adds alpha in BOTH periods.

Variants:
  base  – current rules
  V1    – core equity share scaled to 15% world-equity volatility (30–100% of core)
  V2    – momentum skips the latest month (21 trading days)
  V3    – inflation ≥ 3% and rising → core bonds in short euro govt (IBGS)
  V4    – a theme may enter only if its 12-month return beats world equity
  ALL   – V1+V2+V3+V4
"""
from __future__ import annotations

import copy
import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2.engine import Prices, apply, decide, scan

ROOT = Path(__file__).resolve().parent
SPLIT = "2022-01-01"


def wednesdays(start: date, end: date) -> list[str]:
    d = start + timedelta(days=(2 - start.weekday()) % 7)
    out = []
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=7)
    return out


def hicp_known(hicp: list[tuple[str, float]], d: str) -> tuple[float | None, float | None]:
    """Latest HICP y/y published by date d (month m known from the 20th of m+1), and 3 months earlier."""
    dd = date.fromisoformat(d)
    known = []
    for m, v in hicp:
        y, mo = int(m[:4]), int(m[5:7])
        pub = date(y + (mo == 12), mo % 12 + 1, 20)
        if pub <= dd:
            known.append(v)
    return (known[-1] if known else None, known[-4] if len(known) >= 4 else None)


def run(pol: dict, prices: Prices, uni: list[dict], hicp, dates: list[str]) -> list[dict]:
    hold, cash, weeks, changes = {}, 100000.0, [], 0
    for d in dates:
        p = copy.deepcopy(pol)
        h, h3 = hicp_known(hicp, d)
        p["_runtime"] = {"hicp": h, "hicp_3m_ago": h3}
        sc = scan(prices, uni, p, d)
        dec = decide(d, hold, cash, prices, uni, p, sc)
        before = set(hold)
        hold, cash = apply(hold, cash, dec)
        changes += len(set(hold) ^ before)
        nav = cash + sum(sh * prices.close(i, d) for i, sh in hold.items())
        weeks.append({"date": d, "nav": nav, "changes": changes, "notes": dec.notes})
    return weeks


def stats(series: list[float], dates: list[str]) -> dict:
    rets = [series[i] / series[i - 1] - 1 for i in range(1, len(series))]
    m = sum(rets) / len(rets)
    vol = math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) * math.sqrt(52)
    yrs = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / 365.25
    ann = (series[-1] / series[0]) ** (1 / yrs) - 1
    peak, mdd = series[0], 0.0
    for v in series:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return {"ann": ann, "vol": vol, "mdd": mdd, "yrs": yrs}


def mix_series(prices: Prices, dates: list[str], eq: float) -> list[float]:
    v = [1.0]
    for a, b in zip(dates, dates[1:]):
        r = eq * (prices.close("IWDA", b) / prices.close("IWDA", a) - 1) + (1 - eq) * (prices.close("EUNH", b) / prices.close("EUNH", a) - 1)
        v.append(v[-1] * (1 + r))
    return v


def equal_risk_mix(prices: Prices, dates: list[str], target_vol: float) -> dict:
    lo, hi = 0.0, 1.0
    for _ in range(40):  # bisection on equity weight (vol rises with equity weight here)
        mid = (lo + hi) / 2
        if stats(mix_series(prices, dates, mid), dates)["vol"] < target_vol:
            lo = mid
        else:
            hi = mid
    eq = (lo + hi) / 2
    s = stats(mix_series(prices, dates, eq), dates)
    return {"eq": eq, **s}


def main() -> None:
    prices = Prices(list(csv.DictReader((ROOT / "state" / "prices_long.csv").open())))
    hicp = [(r["month"], float(r["hicp_yoy"])) for r in csv.DictReader((ROOT / "state" / "hicp_long.csv").open())]
    uni = [i for i in yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"] if i.get("status") == "verified"]
    base = yaml.safe_load((ROOT / "policy.yml").read_text())
    base["trend_reference"] = "IWDA"
    base["core"]["equity"], base["core"]["bonds"] = "IWDA", "EUNH"
    for i in uni:  # long-history stand-ins take the core role; the real core funds become satellites-in-waiting
        if i["id"] in ("IWDA", "EUNH"):  # core stand-ins: not also satellites
            i["sleeve"] = "reference"
        if i["id"] in ("VWCE", "EUNA"):
            i["sleeve"] = "reference"
    v = {
        "base": {},
        "V1 vol-target": {"core.vol_target": {"target_vol": 0.15, "min_share": 0.30, "max_share": 1.00}},
        "V2 skip-month": {"scoring.skip_days": 21},
        "V3 inflation": {"inflation_regime": {"threshold": 3.0, "alt_bonds": "IBGS"}},
        "V4 theme filter": {"satellites.theme_must_beat_reference": True},
    }
    v["ALL"] = {k: val for d in list(v.values())[1:] for k, val in d.items()}
    dates = wednesdays(date(2016, 1, 6), date.today())
    results = {}
    for name, changes in v.items():
        pol = copy.deepcopy(base)
        for k, val in changes.items():
            node = pol
            parts = k.split(".")
            for part in parts[:-1]:
                node = node[part]
            node[parts[-1]] = val
        weeks = run(pol, prices, uni, hicp, dates)
        out = {}
        for per, sel in (("design 2016-21", [w for w in weeks if w["date"] < SPLIT]), ("test 2022-26", [w for w in weeks if w["date"] >= SPLIT])):
            ds = [w["date"] for w in sel]
            s = stats([w["nav"] for w in sel], ds)
            mix = equal_risk_mix(prices, ds, s["vol"])
            ch = (sel[-1]["changes"] - sel[0]["changes"]) / s["yrs"]
            out[per] = {"ann": round(s["ann"] * 100, 2), "vol": round(s["vol"] * 100, 2), "mdd": round(s["mdd"] * 100, 1),
                        "mix_eq": round(mix["eq"] * 100), "mix_ann": round(mix["ann"] * 100, 2), "mix_mdd": round(mix["mdd"] * 100, 1),
                        "alpha": round((s["ann"] - mix["ann"]) * 100, 2), "changes_per_year": round(ch, 1)}
        results[name] = out
        print("RES " + name + " " + json.dumps(out), flush=True)
    (ROOT / "evidence" / "research_alpha_20261115.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
