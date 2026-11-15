"""The weekly run: prices → checks → decision → new state → report → delivery.

Atomic by construction: this script only changes files in the checkout; the
workflow commits them only if the whole run (including delivery) succeeded. A
failed run therefore leaves the saved state untouched and can simply be rerun.

Environment:
  V2_REPORT_DATE   override the report date (YYYY-MM-DD, a Wednesday)
  V2_DRY_RUN=1     do everything except sending email
  V2_REHEARSAL=1   replay the latest saved week on a scratch copy of the state
                   (saved state is never touched; email only in trial mode, to the owner)
"""
from __future__ import annotations

import csv
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from v2 import market, mailer
from v2 import narrate as N
from v2 import render as R
from v2 import sources as S
from v2.engine import Prices, apply, benchmark_return, decide, scan
from v2.facts import build

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
TOLERANCE_PCT = 1.0


def report_date() -> str:
    if os.environ.get("V2_REPORT_DATE"):
        return os.environ["V2_REPORT_DATE"]
    now = datetime.now(timezone.utc)
    d = now.date() - timedelta(days=(now.weekday() - 2) % 7)  # latest Wednesday
    if d == now.date() and now.hour < 18:  # Wednesday close not complete yet
        d -= timedelta(days=7)
    return d.isoformat()


def read_csv(name: str) -> list[dict]:
    return list(csv.DictReader((STATE / name).open()))


def append_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    path = STATE / name
    fields = list(csv.DictReader(path.open()).fieldnames or rows[0].keys())
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writerows(rows)


def cross_check(held: dict[str, int], uni: dict[str, dict], prices: Prices, d: str) -> tuple[dict[str, str], list[str]]:
    """Primary (Yahoo) close vs Alpha Vantage for every held position."""
    status, blockers = {}, []
    for iid in sorted(held):
        p = prices.close(iid, d, max_stale_days=2)
        if p is None:
            blockers.append(f"{iid}: no current primary close for {d}")
            status[iid] = "missing_primary"
            continue
        av = S.alpha_vantage(iid, uni[iid]["exchange"])
        S.pause(13)
        v = av.closes.get(d)
        if v is None:
            status[iid] = "unverified"
        elif abs(p - v) / p * 100 > TOLERANCE_PCT:
            status[iid] = "disagreement"
            blockers.append(f"{iid}: primary {p:.4f} vs verifier {v:.4f}")
        else:
            status[iid] = "verified"
    return status, blockers


def _rehearsal_state() -> str:
    """Copy state to a scratch dir with the latest week removed; return that week's date."""
    import shutil
    import tempfile
    global STATE
    scratch = Path(tempfile.mkdtemp(prefix="v2_rehearsal_")) / "state"
    shutil.copytree(STATE, scratch)
    hist = list(csv.DictReader((scratch / "history.csv").open()))
    last = hist[-1]["date"]
    for name in ("history.csv", "valuations.csv"):
        rows = list(csv.DictReader((scratch / name).open()))
        fields = list(rows[0].keys())
        with (scratch / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(r for r in rows if r["date"] != last)
    trades = list(csv.DictReader((scratch / "trades.csv").open()))
    if any(t["date"] == last for t in trades):
        raise SystemExit("REHEARSAL_BLOCKED: latest week already has trades; rehearsal only replays a no-trade week")
    port = json.loads((scratch / "portfolio.json").read_text())
    port["as_of"] = hist[-2]["date"]
    (scratch / "portfolio.json").write_text(json.dumps(port, indent=1))
    STATE = scratch
    import v2.facts as F
    F.ROOT = scratch.parent  # facts reads state/ under ROOT
    (scratch.parent / "universe.yml").write_text((ROOT / "universe.yml").read_text())
    (scratch.parent / "policy.yml").write_text((ROOT / "policy.yml").read_text())
    return last


def main() -> None:
    rehearsal = os.environ.get("V2_REHEARSAL") == "1"
    d = _rehearsal_state() if rehearsal else report_date()
    dry = os.environ.get("V2_DRY_RUN") == "1"
    print(f"RUN report_date={d} dry_run={dry} rehearsal={rehearsal} delivery_mode={mailer.mode()}")
    if rehearsal and mailer.mode() != "trial":
        dry = True  # a rehearsal never reaches readers
    hist = read_csv("history.csv")
    if any(h["date"] == d for h in hist):
        print(f"ALREADY_DONE {d}: state already contains this week; nothing to do")
        return
    if hist and hist[-1]["date"] > d:
        raise SystemExit(f"RUN_BLOCKED: report date {d} is older than saved state {hist[-1]['date']}")

    # 1. Prices
    market.main()
    if rehearsal:  # market.main writes to the real state dir; copy fresh prices into scratch
        (STATE / "prices.csv").write_text((ROOT / "state" / "prices.csv").read_text())
    prices = Prices(read_csv("prices.csv"))
    uni_all = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    uni_by = {i["id"]: i for i in uni_all}
    uni = [i for i in uni_all if i.get("status") == "verified"]
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    port = json.loads((STATE / "portfolio.json").read_text())
    hold = {p["id"]: p["shares"] for p in port["positions"]}
    cash = float(port["cash_eur"])
    if any(prices.close(i, d, max_stale_days=2) is None for i in pol["benchmark"]["weights"]):
        raise SystemExit(f"RUN_BLOCKED: no benchmark close for {d} (market closed or data missing)")

    # 2. Cross-check held positions
    status, blockers = cross_check(hold, uni_by, prices, d)
    print("CROSS_CHECK " + json.dumps(status))
    if blockers:
        raise SystemExit("RUN_BLOCKED: " + "; ".join(blockers))

    # 3. Decide and apply (inflation rule gets the latest published HICP)
    from v2 import macro as M
    pol["_runtime"] = M.runtime(M.fetch(date.fromisoformat(d)))
    print("INFLATION_INPUT " + json.dumps(pol["_runtime"]))
    sc = scan(prices, uni, pol, d)
    dec = decide(d, hold, cash, prices, uni, pol, sc)
    hold_after, cash_after = apply(hold, cash, dec)
    if cash_after < 0:
        raise SystemExit(f"RUN_BLOCKED: negative cash {cash_after}")
    px = {i: prices.close(i, d, max_stale_days=2) for i in hold_after}
    invested = round(sum(sh * px[i] for i, sh in hold_after.items()), 2)
    nav = round(cash_after + invested, 2)

    # 4. Save new state (committed by the workflow only if the whole run succeeds)
    prev = hist[-1]
    bench = prices.close(pol["trend_reference"], d, max_stale_days=2)
    b_idx = round(float(prev["benchmark_index"]) * (1 + (benchmark_return(prices, pol, prev["date"], d) or 0.0)), 6)
    first = hist[0]
    append_csv("trades.csv", [{
        "date": d, "type": t["side"], "id": t["id"], "isin": uni_by[t["id"]]["isin"], "shares": t["shares"],
        "price_eur": round(t["price"], 4), "amount_eur": t["amount"], "reason": f"{t['reason'].get('why')}: {t['reason'].get('detail')}",
    } for t in dec.trades])
    append_csv("valuations.csv", [{
        "date": d, "id": i, "isin": uni_by[i]["isin"], "shares": sh, "close_date": d, "close": round(px[i], 4),
        "value_eur": round(sh * px[i], 2), "price_status": status.get(i, "unverified_new_position"),
    } for i, sh in sorted(hold_after.items())])
    append_csv("history.csv", [{
        "date": d, "nav_eur": nav, "cash_eur": round(cash_after, 2), "invested_eur": invested, "benchmark_close": bench,
        "source": "weekly_run", "cum_return_pct": round((nav / float(first["nav_eur"]) - 1) * 100, 4),
        "week_return_pct": round((nav / float(prev["nav_eur"]) - 1) * 100, 4),
        "benchmark_cum_return_pct": round((b_idx / float(first["benchmark_index"]) - 1) * 100, 4), "benchmark_index": b_idx,
    }])
    (STATE / "portfolio.json").write_text(json.dumps({
        "as_of": d, "cash_eur": round(cash_after, 2), "nav_eur": nav, "track_record_start": port.get("track_record_start", first["date"]),
        "positions": [{"id": i, "isin": uni_by[i]["isin"], "exchange": uni_by[i]["exchange"], "shares": sh} for i, sh in sorted(hold_after.items())],
    }, indent=1) + "\n")
    print(f"STATE_SAVED nav={nav} cash={cash_after:.2f} trades={len(dec.trades)} deferred={len(dec.deferred)}")

    # 5. Report
    out = (STATE.parent / "rehearsal" if rehearsal else ROOT / "evidence") / f"report_{d.replace('-', '')}"
    out.mkdir(parents=True, exist_ok=True)
    facts = build(d, applied={"hold_before": hold, "cash_before": cash, "decision": dec, "hold_after": hold_after, "cash_after": cash_after})
    facts["price_checks"] = status
    (out / "facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False))
    commentary = N.narrate(facts)
    (out / "commentary.json").write_text(json.dumps(commentary, indent=1, ensure_ascii=False))
    rendered = R.render(facts, commentary, out)
    problems = [p for r in rendered.values() for p in r["problems"]]
    if facts["portfolio"]["value_eur"] != nav:
        problems.append(f"facts value {facts['portfolio']['value_eur']} != saved nav {nav}")
    checks = {"report_date": d, "commentary_source": commentary["source"], "commentary_problems": commentary["problems"],
              "render": {k: {"pages": v["pages"], "problems": v["problems"]} for k, v in rendered.items()}, "price_checks": status,
              "macro": {k: {"available": v.get("available"), "date": v.get("date"), "stale": v.get("stale")} for k, v in facts["macro"].items()}}
    (out / "checks.json").write_text(json.dumps(checks, indent=1, ensure_ascii=False))
    if problems:
        raise SystemExit("RUN_BLOCKED: report checks failed: " + "; ".join(problems))

    # 6. Deliver
    delivery = mailer.deliver(facts, commentary, {k: Path(v["pdf"]) for k, v in rendered.items()}, dry_run=dry, label="REHEARSAL" if rehearsal else "TRIAL")
    (out / "delivery.json").write_text(json.dumps(delivery, indent=1))
    print(f"RUN_OK {d}")


if __name__ == "__main__":
    main()
