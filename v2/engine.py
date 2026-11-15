"""Scan + decision engine for Weekly ETF EU v2. Pure functions, no network.

scan()   ranks the universe on momentum and trend at a given date.
decide() turns the scan + current holdings into target weights and trades,
         applying every rule in policy.yml. Each trade carries a structured
         reason so the report can explain it without inventing anything.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field

TAG_KEYS = ("theme", "segment", "region", "factor")


# ── Price access ─────────────────────────────────────────────────────────────
class Prices:
    """Daily closes per instrument with as-of lookups (no look-ahead)."""

    def __init__(self, rows: list[dict]):
        self.dates: dict[str, list[str]] = {}
        self.closes: dict[str, list[float]] = {}
        for r in sorted(rows, key=lambda x: (x["id"], x["date"])):
            self.dates.setdefault(r["id"], []).append(r["date"])
            self.closes.setdefault(r["id"], []).append(float(r["close"]))

    def upto(self, iid: str, d: str) -> list[float]:
        ds = self.dates.get(iid, [])
        return self.closes.get(iid, [])[: bisect.bisect_right(ds, d)]

    def close(self, iid: str, d: str, max_stale_days: int = 5) -> float | None:
        ds = self.dates.get(iid, [])
        i = bisect.bisect_right(ds, d) - 1
        if i < 0:
            return None
        from datetime import date as _d
        gap = (_d.fromisoformat(d) - _d.fromisoformat(ds[i])).days
        return self.closes[iid][i] if gap <= max_stale_days else None


# ── Benchmark ────────────────────────────────────────────────────────────────
def benchmark_return(prices: Prices, policy: dict, a: str, b: str) -> float | None:
    """Return of the blended benchmark from close a to close b (weights reset at a)."""
    tot = 0.0
    for iid, w in policy["benchmark"]["weights"].items():
        pa, pb = prices.close(iid, a), prices.close(iid, b)
        if not pa or not pb:
            return None
        tot += w * (pb / pa - 1)
    return tot


def benchmark_index(prices: Prices, policy: dict, dates: list[str], base: float = 100.0) -> dict[str, float]:
    """Index of the benchmark over the given (weekly) dates, rebalanced at each date."""
    idx = {dates[0]: base}
    for a, b in zip(dates, dates[1:]):
        r = benchmark_return(prices, policy, a, b)
        idx[b] = idx[a] * (1 + (r or 0.0))
    return idx


# ── Scan ─────────────────────────────────────────────────────────────────────
def _ret(series: list[float], days: int) -> float | None:
    if len(series) <= days:
        return None
    return series[-1] / series[-1 - days] - 1


def _vol(series: list[float], days: int) -> float | None:
    if len(series) <= days:
        return None
    rets = [series[i] / series[i - 1] - 1 for i in range(len(series) - days, len(series))]
    m = sum(rets) / len(rets)
    return math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) * math.sqrt(252)


def tags(inst: dict) -> set[tuple[str, str]]:
    return {(k, inst[k]) for k in TAG_KEYS if inst.get(k)}


def scan(prices: Prices, universe: list[dict], policy: dict, d: str) -> dict:
    sc = policy["scoring"]
    wins = sc["momentum_windows_days"]
    min_hist = policy["satellites"]["min_history_days"]
    rows = []
    for inst in universe:
        s = prices.upto(inst["id"], d)
        if not s or prices.close(inst["id"], d) is None:
            continue
        sma = sum(s[-sc["trend_sma_days"]:]) / sc["trend_sma_days"] if len(s) >= sc["trend_sma_days"] else None
        row = {
            "id": inst["id"], "name": inst["name"], "sleeve": inst["sleeve"], "asset_class": inst["asset_class"],
            "tags": sorted(f"{k}:{v}" for k, v in tags(inst)),
            "close": s[-1], "sma200": round(sma, 4) if sma else None,
            "trend_up": (s[-1] > sma) if sma else None,
            # Trend one week (5 trading days) earlier, for exit confirmation.
            "trend_up_prev": (s[-6] > sum(s[-205:-5]) / sc["trend_sma_days"]) if len(s) >= sc["trend_sma_days"] + 5 else None,
            "vol": round(_vol(s, sc["volatility_days"]) or 0, 4) if len(s) > sc["volatility_days"] else None,
        }
        skip = int(sc.get("skip_days", 0))
        base = s[:-skip] if skip else s
        for w in wins:
            r = _ret(base, w)
            row[f"r{w}"] = round(r, 6) if r is not None else None
        row["rankable"] = inst["sleeve"] == "satellite" and len(s) > min_hist and all(row[f"r{w}"] is not None for w in wins) and sma is not None
        rows.append(row)

    ranked = [r for r in rows if r["rankable"]]
    n = len(ranked)
    for w in wins:
        order = sorted(ranked, key=lambda r: r[f"r{w}"])
        for i, r in enumerate(order):
            r[f"pct{w}"] = 100.0 * i / (n - 1) if n > 1 else 50.0
    for r in ranked:
        r["score"] = round(sum(r[f"pct{w}"] for w in wins) / len(wins), 2)
    ranked.sort(key=lambda r: -r["score"])
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    breadth = 100.0 * sum(1 for r in ranked if r["trend_up"]) / n if n else 0.0
    bench = next((r for r in rows if r["id"] == policy["trend_reference"]), None)
    ds = policy["defensive_switch"]
    risk_off = bool(bench and bench["trend_up"] is False and breadth < ds["max_breadth_pct"])
    return {"date": d, "rows": rows, "ranked": ranked, "n_ranked": n, "breadth_pct": round(breadth, 1),
            "benchmark_trend_up": bench["trend_up"] if bench else None, "regime": "risk_off" if risk_off else "risk_on"}


# ── Decide ───────────────────────────────────────────────────────────────────
@dataclass
class Decision:
    date: str
    regime: str
    nav_before: float
    targets: dict[str, float]
    trades: list[dict] = field(default_factory=list)
    deferred: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    selected_satellites: list[str] = field(default_factory=list)


def _select_satellites(sc: dict, held: set[str], uni: dict[str, dict], pol: dict) -> tuple[list[dict], list[dict]]:
    """Return (selected rows, exit explanations for held satellites not kept)."""
    sat = pol["satellites"]
    n = sat["count"][sc["regime"]]
    keep_limit = n * sat["hold_buffer_rank_multiple"]
    by_id = {r["id"]: r for r in sc["ranked"]}
    exits = []
    kept = []
    for iid in sorted(held):
        if uni.get(iid, {}).get("sleeve") != "satellite":
            continue
        r = by_id.get(iid)
        if r is None:
            exits.append({"id": iid, "why": "not_rankable", "detail": "insufficient price history to rank"})
        elif not r["trend_up"] and (sat.get("trend_exit_confirm_weeks", 1) < 2 or r["trend_up_prev"] is False):
            exits.append({"id": iid, "why": "trend_down", "detail": f"close {r['close']:.2f} below 200-day average {r['sma200']:.2f} for 2 consecutive weeks", "rank": r["rank"], "score": r["score"],
                          "params": {"close": round(r["close"], 2), "sma200": round(r["sma200"], 2)}})
        elif r["rank"] > keep_limit:
            exits.append({"id": iid, "why": "rank_dropped", "detail": f"rank {r['rank']} of {sc['n_ranked']} (keep while ≤ {keep_limit})", "rank": r["rank"], "score": r["score"],
                          "params": {"rank": r["rank"], "n": sc["n_ranked"], "keep_limit": keep_limit}})
        else:
            kept.append(r)
    kept.sort(key=lambda r: r["rank"])
    while len(kept) > n:  # risk-off can shrink the slot count
        r = kept.pop()
        exits.append({"id": r["id"], "why": "slots_reduced", "detail": f"{sc['regime']} allows {n} satellites; rank {r['rank']} is the weakest held", "rank": r["rank"], "score": r["score"],
                      "params": {"slots": n, "rank": r["rank"]}})

    def conflicts(r, chosen):
        t = set(r["tags"])
        return any(t & set(c["tags"]) for c in chosen)

    ref = next((x for x in sc["rows"] if x["id"] == pol.get("trend_reference")), None)
    long_w = max(pol["scoring"]["momentum_windows_days"])

    def theme_ok(r):
        if not sat.get("theme_must_beat_reference") or not any(t.startswith("theme:") for t in r["tags"]):
            return True
        return ref is not None and ref.get(f"r{long_w}") is not None and r[f"r{long_w}"] > ref[f"r{long_w}"]

    selected = list(kept)
    for r in sc["ranked"]:
        if len(selected) >= n:
            break
        if r["id"] in held or not r["trend_up"] or conflicts(r, selected) or not theme_ok(r):
            continue
        selected.append(r)

    # Replacement: full book, best outsider vs weakest keeper.
    if len(kept) == n and kept:
        weakest = max(kept, key=lambda r: r["rank"])
        others = [k for k in kept if k is not weakest]
        for r in sc["ranked"]:
            if r["id"] in held or not r["trend_up"] or conflicts(r, others) or not theme_ok(r):
                continue
            if r["score"] >= weakest["score"] + sat["replacement_margin_pts"]:
                selected = others + [r]
                exits.append({"id": weakest["id"], "why": "replaced", "detail": f"{r['id']} scores {r['score']:.0f} vs {weakest['score']:.0f} (margin ≥ {sat['replacement_margin_pts']})", "rank": weakest["rank"], "score": weakest["score"], "replaced_by": r["id"],
                              "params": {"new_id": r["id"], "new_score": round(r["score"]), "old_score": round(weakest["score"]), "margin": sat["replacement_margin_pts"]}})
            break
    return selected, exits


def decide(d: str, holdings: dict[str, int], cash: float, prices: Prices, universe: list[dict], policy: dict, sc: dict) -> Decision:
    uni = {i["id"]: i for i in universe}
    px = {iid: prices.close(iid, d) for iid in set(holdings) | set(uni)}
    nav = cash + sum(sh * px[i] for i, sh in holdings.items() if px.get(i))
    regime = sc["regime"]
    held = {i for i, sh in holdings.items() if sh > 0}

    # 1. Target weights ---------------------------------------------------------
    sat = policy["satellites"]
    n = sat["count"][regime]
    selected, sat_exits = _select_satellites(sc, held, uni, policy)
    w_sat = sat["weight_each"]
    targets: dict[str, float] = {r["id"]: w_sat for r in selected}
    cash_t = policy["cash"]["target"]
    defensive = (n - len(selected)) * w_sat
    core_w = 1 - cash_t - w_sat * len(selected) - defensive
    lo, hi = policy["core"]["weight_band"]
    if core_w > hi:
        defensive += core_w - hi
        core_w = hi
    eq_share = policy["core"]["equity_share"][regime]
    dec_notes: list[str] = []
    vt = policy["core"].get("vol_target")
    if vt:  # scale core equity to a fixed risk level using world-equity volatility
        ref = next((x for x in sc["rows"] if x["id"] == policy["trend_reference"]), None)
        if ref and ref.get("vol"):
            eq_share = min(vt["max_share"], max(vt["min_share"], eq_share * vt["target_vol"] / ref["vol"]))
            dec_notes.append(f"core equity share {eq_share:.0%} (world-equity volatility {ref['vol']:.1%} vs target {vt['target_vol']:.0%})")
    bonds = policy["core"]["bonds"]
    infl_info: dict = {}
    inf, rt = policy.get("inflation_regime"), policy.get("_runtime", {})
    if inf and rt.get("hicp") is None and inf["alt_bonds"] in held:
        bonds = inf["alt_bonds"]  # no current inflation data: keep the bond fund we hold, no switch on missing data
        dec_notes.append("inflation data unavailable: bond core unchanged")
    elif inf and rt.get("hicp") is not None and rt["hicp"] >= inf["threshold"] and rt["hicp"] >= (rt.get("hicp_3m_ago") or rt["hicp"]):
        bonds = inf["alt_bonds"]
        infl_info = {"hicp": rt["hicp"], "hicp_3m_ago": rt.get("hicp_3m_ago"), "threshold": inf["threshold"]}
        dec_notes.append(f"inflation {rt['hicp']:.1f}% ≥ {inf['threshold']}% and rising: core bonds held in {bonds}")
    targets[policy["core"]["equity"]] = core_w * eq_share
    targets[bonds] = targets.get(bonds, 0) + core_w * (1 - eq_share)
    if defensive > 1e-9:
        targets[policy["defensive_switch"]["instrument"]] = targets.get(policy["defensive_switch"]["instrument"], 0) + defensive
    dec = Decision(d, regime, round(nav, 2), {k: round(v, 4) for k, v in targets.items()}, selected_satellites=[r["id"] for r in selected])
    dec.notes.extend(dec_notes)
    if defensive > 1e-9:
        dec.notes.append(f"{defensive:.0%} parked in {policy['defensive_switch']['instrument']}: "
                         f"{n - len(selected)} of {n} satellite slots unfilled" + (" (risk-off)" if regime == "risk_off" else ""))

    # 2. Instrument changes (entries / full exits), limited per week -------------
    by_id = {r["id"]: r for r in sc["ranked"]}
    exit_info = {e["id"]: e for e in sat_exits}
    changes = []
    for iid in sorted(held):
        if targets.get(iid, 0) <= 0:
            info = exit_info.get(iid) or {"id": iid, "why": "not_in_target", "detail": "not part of the target portfolio (core is " + policy["core"]["equity"] + " + " + policy["core"]["bonds"] + ")",
                                          "params": {"core_equity": policy["core"]["equity"], "core_bonds": policy["core"]["bonds"]}}
            prio = {"trend_down": 0, "not_rankable": 0, "slots_reduced": 1, "replaced": 2, "rank_dropped": 2}.get(info["why"], 3)
            changes.append((prio, "exit", iid, info))
    for iid, w in targets.items():
        if iid not in held and w > 0:
            r = by_id.get(iid)
            info = ({"why": "selected", "detail": f"rank {r['rank']} of {sc['n_ranked']}, score {r['score']:.0f}, uptrend", "rank": r["rank"], "score": r["score"],
                     "params": {"rank": r["rank"], "n": sc["n_ranked"], "score": round(r["score"])}}
                    if r else {"why": "core_or_defensive", "detail": "core/defensive allocation", "params": {"target_pct": round(w * 100, 1)}})
            changes.append((4 + (r["rank"] / 1000 if r else 0), "entry", iid, info))
    # A switch between the normal and the inflation-regime core bond fund is one
    # decision (sell one, buy the other) and is executed together as one change.
    bond_pair = {policy["core"]["bonds"], (inf or {}).get("alt_bonds")} - {None}
    switch = [c for c in changes if c[2] in bond_pair]
    if switch:
        changes = [c for c in changes if c[2] not in bond_pair]
        new_bonds = bonds
        for k, (prio, kind, iid, info) in enumerate(switch):
            info = {"why": "inflation_regime" if new_bonds != policy["core"]["bonds"] else "inflation_regime_end",
                    "detail": (f"core bonds from {iid if kind == 'exit' else policy['core']['bonds']} to {new_bonds}"),
                    "params": {"from": policy["core"]["bonds"] if new_bonds != policy["core"]["bonds"] else (inf or {}).get("alt_bonds"),
                               "to": new_bonds, **infl_info, "threshold": (inf or {}).get("threshold")}}
            switch[k] = (-1, kind, iid, info)
    changes.sort(key=lambda c: c[0])
    limit = policy["turnover"]["max_instrument_changes_per_week"]
    limit_left = limit - (1 if switch else 0)
    allowed, deferred = switch + changes[:limit_left], changes[limit_left:]
    targets_before_defer = dict(targets)
    for _, kind, iid, info in deferred:
        dec.deferred.append({"id": iid, "kind": kind, **info, "deferred_reason": f"max {limit} instrument changes per week"})
        if kind == "exit":
            targets[iid] = holdings[iid] * px[iid] / nav  # hold as-is this week
        else:
            targets[iid] = 0.0
            # Weight waiting for a deferred entry is parked in the benchmark (core equity)
            # instead of cash, so waiting does not create a gap with the benchmark.
            park = policy.get("cash", {}).get("park_pending_entries_in")
            if park:
                targets[park] = targets.get(park, 0.0) + targets_before_defer.get(iid, 0.0)
    change_info = {iid: (kind, info) for _, kind, iid, info in allowed}

    # 3. Orders: sells first, then buys within the cash/deployment budget --------
    bps = policy["execution"]["cost_bps"] / 10_000
    band = policy["turnover"]["rebalance_band_pts"] / 100
    sells, buys = [], []
    # Cash above its band is deployed into underweight holdings even when each
    # holding is individually inside its rebalance band.
    cash_excess = cash / nav > policy["cash"]["band"][1]
    for iid in sorted(set(holdings) | set(targets)):
        p = px.get(iid)
        if not p:
            continue
        cur_w = holdings.get(iid, 0) * p / nav
        tgt_w = targets.get(iid, 0.0)
        diff = tgt_w - cur_w
        kind, info = change_info.get(iid, (None, None))
        if kind is None and abs(diff) <= band and not (diff > 0 and cash_excess and iid in held):
            continue
        if kind is None and iid not in held and tgt_w <= 0:
            continue
        if diff < 0:
            sh = holdings[iid] if tgt_w <= 0 else min(holdings[iid], round(-diff * nav / p))
            if sh > 0:
                sells.append({"id": iid, "side": "sell", "shares": sh, "price": p, "kind": kind or "resize",
                              "reason": info or {"why": "resize", "detail": f"weight {cur_w:.1%} vs target {tgt_w:.1%} (band {band:.0%})",
                                                 "params": {"weight_pct": round(cur_w * 100, 1), "target_pct": round(tgt_w * 100, 1), "band_pts": round(band * 100)}}})
        elif diff > 0:
            buys.append({"id": iid, "side": "buy", "want": diff * nav, "price": p, "kind": kind or "resize",
                         "reason": info or ({"why": "deploy_cash", "detail": f"cash {cash / nav:.1%} above {policy['cash']['band'][1]:.0%} ceiling; topping up toward target {tgt_w:.1%}",
                                             "params": {"cash_pct": round(cash / nav * 100, 1), "ceiling_pct": round(policy["cash"]["band"][1] * 100), "target_pct": round(tgt_w * 100, 1), "weight_pct": round(cur_w * 100, 1)}}
                                            if abs(diff) <= band else {"why": "resize", "detail": f"weight {cur_w:.1%} vs target {tgt_w:.1%} (band {band:.0%})",
                                                                       "params": {"weight_pct": round(cur_w * 100, 1), "target_pct": round(tgt_w * 100, 1), "band_pts": round(band * 100)}})})
    proceeds = 0.0
    for s in sells:
        amt = s["shares"] * s["price"]
        s["amount"] = round(amt, 2)
        s["cost"] = round(amt * bps, 2)
        proceeds += amt - s["cost"]
        dec.trades.append(s)
    cash_after_sells = cash + proceeds
    budget = min(cash_after_sells - cash_t * nav, proceeds + policy["cash"]["max_net_deployment_per_week_pct_nav"] / 100 * nav)
    want = sum(b["want"] for b in buys)
    scale = min(1.0, max(0.0, budget) / want) if want > 0 else 0.0
    if buys and scale < 1:
        dec.notes.append(f"buys scaled to {scale:.0%} of target by the cash/deployment limit")
    for b in sorted(buys, key=lambda b: b["kind"] != "entry"):
        sh = math.floor(b["want"] * scale / (b["price"] * (1 + bps)))
        if sh <= 0:
            continue
        amt = sh * b["price"]
        dec.trades.append({"id": b["id"], "side": "buy", "shares": sh, "price": b["price"], "kind": b["kind"],
                           "amount": round(amt, 2), "cost": round(amt * bps, 2), "reason": b["reason"]})
    dec.targets = {k: round(v, 4) for k, v in targets.items() if v > 0}
    return dec


def apply(holdings: dict[str, int], cash: float, dec: Decision) -> tuple[dict[str, int], float]:
    h = dict(holdings)
    c = cash
    for t in dec.trades:
        if t["side"] == "sell":
            h[t["id"]] -= t["shares"]
            c += t["amount"] - t["cost"]
        else:
            h[t["id"]] = h.get(t["id"], 0) + t["shares"]
            c -= t["amount"] + t["cost"]
    return {k: v for k, v in h.items() if v > 0}, round(c, 2)
