"""The European mirror portfolio: follows the US portfolio's decisions in UCITS lines.

Rules (policy.yml `mirror`, decided 2026-11-15):
- Each US fund maps to one EUR line (universe.yml `mirror.line`): twin, proxy ("benadering") or cash (XEON).
- Target weights = the US portfolio's weights after its trades, valued at the US Wednesday close in EUR.
  US cash maps to mirror cash. Two US funds on the same line add up.
- The mirror executes at the first European close after the US decision (the US closes later),
  in whole shares with cost. A line is traded only when it enters, leaves, or is off its target
  by more than the rebalance band.
Pure functions; no network.
"""
from __future__ import annotations

import bisect
import math
from datetime import date

from v2.engine import Prices


def implied_weights(us_hold: dict[str, int], us_cash: float, us_prices: Prices, d: str, line_of: dict[str, str]) -> dict[str, float]:
    vals = {i: sh * us_prices.close(i, d, max_stale_days=4) for i, sh in us_hold.items()}
    nav = us_cash + sum(vals.values())
    w: dict[str, float] = {}
    for i, v in vals.items():
        w[line_of[i]] = w.get(line_of[i], 0.0) + v / nav
    return w


def first_close_after(prices: Prices, line: str, d: str, max_days: int = 6) -> tuple[str | None, float | None]:
    ds = prices.dates.get(line, [])
    i = bisect.bisect_right(ds, d)
    if i >= len(ds) or (date.fromisoformat(ds[i]) - date.fromisoformat(d)).days > max_days:
        return None, None
    return ds[i], prices.closes[line][i]


def execute(hold: dict[str, int], cash: float, targets: dict[str, float], prices: Prices, decided: str,
            band_pts: float, cost_bps: float) -> tuple[dict[str, int], float, list[dict], list[str]]:
    """Move the mirror to `targets` at the first close after `decided`. Returns hold, cash, trades, problems."""
    lines = sorted(set(hold) | {k for k, v in targets.items() if v > 0})
    px, when, problems = {}, {}, []
    for ln in lines:
        dt, p = first_close_after(prices, ln, decided)
        if p is None:
            problems.append(f"{ln}: no European close after {decided}")
        when[ln], px[ln] = dt, p
    if problems:
        return dict(hold), cash, [], problems
    nav = cash + sum(sh * px[ln] for ln, sh in hold.items())
    cost = cost_bps / 10000
    new, trades = dict(hold), []
    sells, buys = [], []
    for ln in lines:
        w, cur = targets.get(ln, 0.0), hold.get(ln, 0) * px[ln] / nav if nav else 0.0
        if w <= 0:
            if hold.get(ln):
                sells.append((ln, hold[ln]))
            continue
        if ln in hold and abs(cur - w) * 100 <= band_pts:
            continue
        want = math.floor(w * nav / px[ln])
        delta = want - hold.get(ln, 0)
        if delta > 0:
            buys.append((ln, delta))
        elif delta < 0:
            sells.append((ln, -delta))
    for ln, n in sells:
        amt = n * px[ln]
        cash += amt * (1 - cost)
        new[ln] = new.get(ln, 0) - n
        trades.append({"date": when[ln], "side": "sell", "line": ln, "shares": n, "price": px[ln], "amount": round(amt, 2)})
    for ln, n in buys:
        n = min(n, math.floor(cash / (px[ln] * (1 + cost))))
        if n <= 0:
            continue
        amt = n * px[ln]
        cash -= amt * (1 + cost)
        new[ln] = new.get(ln, 0) + n
        trades.append({"date": when[ln], "side": "buy", "line": ln, "shares": n, "price": px[ln], "amount": round(amt, 2)})
    return {k: v for k, v in new.items() if v > 0}, round(cash, 2), trades, []


def value(hold: dict[str, int], cash: float, prices: Prices, d: str) -> tuple[float, dict[str, float]]:
    px = {ln: prices.close(ln, d, max_stale_days=4) for ln in hold}
    missing = [ln for ln, p in px.items() if p is None]
    if missing:
        raise SystemExit(f"MIRROR_BLOCKED: no close on/before {d} for {missing}")
    return round(cash + sum(sh * px[ln] for ln, sh in hold.items()), 2), px


def needs_trade(hold: dict[str, int], cash: float, targets: dict[str, float], prices: Prices, d: str, band_pts: float) -> bool:
    nav, px = value(hold, cash, prices, d)
    cur = {ln: sh * px[ln] / nav for ln, sh in hold.items()}
    held = {k for k, v in cur.items() if v > 0}
    want = {k for k, v in targets.items() if v > 0}
    if held != want:
        return True
    return any(abs(cur[k] - targets[k]) * 100 > band_pts for k in want)


def week(d: str, state: dict, line_of: dict[str, str], pol: dict, us_prices: Prices, mprices: Prices,
         us_hold_after: dict[str, int], us_cash_after: float) -> dict:
    """One weekly mirror step for report date d. Pure: returns the new state plus what happened.

    1. Execute the pending target (decided last week) at the first European close after that decision.
    2. Value the mirror at d.
    3. Set the new pending target from the US portfolio after this week's trades (if a trade is needed).
    """
    from v2.engine import benchmark_return
    band, cost = pol["mirror"]["rebalance_band_pts"], pol["mirror"]["cost_bps"]
    hold = {p["line"]: p["shares"] for p in state["positions"]}
    cash = float(state["cash_eur"])
    executed, pending = [], state.get("pending")
    if pending and pending["decided"] < d:
        hold, cash, executed, prob = execute(hold, cash, pending["targets"], mprices, pending["decided"], band, cost)
        if prob:
            raise SystemExit("MIRROR_BLOCKED: " + "; ".join(prob))
        executed = [dict(t, decided=pending["decided"]) for t in executed]
        pending = None
    nav, px = value(hold, cash, mprices, d)
    targets = implied_weights(us_hold_after, us_cash_after, us_prices, d, line_of)
    new_pending = {"decided": d, "targets": targets} if needs_trade(hold, cash, targets, mprices, d, band) else None
    b_ret = benchmark_return(mprices, {"benchmark": pol["mirror"]["benchmark"]}, state["as_of"], d)
    return {"state": {"as_of": d, "cash_eur": cash, "nav_eur": nav, "start": state["start"],
                      "positions": [{"line": ln, "shares": sh} for ln, sh in sorted(hold.items())], "pending": new_pending},
            "executed": executed, "prices": px, "targets": targets, "benchmark_week_return": b_ret}
