"""Acceptance: does the product meet OUTCOME.md? Offline, deterministic, a few minutes.

Each check names the concrete failure it prevents. Run: python -m v2.acceptance
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import tempfile
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
failures: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        failures.append(what)


def history_reconciles() -> None:
    """Prevents: a report whose portfolio value does not equal its holdings plus cash."""
    hist = list(csv.DictReader((ROOT / "state" / "history.csv").open()))
    vals = defaultdict(float)
    for v in csv.DictReader((ROOT / "state" / "valuations.csv").open()):
        vals[v["date"]] += round(float(v["shares"]) * float(v["close"]), 2)
    bad = [h["date"] for h in hist if abs(float(h["cash_eur"]) + vals[h["date"]] - float(h["nav_eur"])) > 0.02]
    check(not bad, f"every saved week reconciles to the cent ({len(hist)} weeks){' — off: ' + ', '.join(bad) if bad else ''}")


def mirror_reconciles() -> None:
    """Prevents: a mirror portfolio whose holdings, cash or value cannot be traced to its trades and prices."""
    from v2.engine import Prices
    m = json.loads((ROOT / "state" / "mirror.json").read_text())
    mh = list(csv.DictReader((ROOT / "state" / "mirror_history.csv").open()))
    cost = yaml.safe_load((ROOT / "policy.yml").read_text())["mirror"]["cost_bps"] / 10000
    hold, cash = defaultdict(int), float(mh[0]["nav_eur"])
    for t in csv.DictReader((ROOT / "state" / "mirror_trades.csv").open()):
        if not t["date"]:
            continue
        amt = float(t["shares"]) * float(t["price_eur"])
        if t["type"] == "buy":
            hold[t["line"]] += int(t["shares"]); cash -= amt * (1 + cost)
        else:
            hold[t["line"]] -= int(t["shares"]); cash += amt * (1 - cost)
    saved = {p["line"]: p["shares"] for p in m["positions"]}
    check({k: v for k, v in hold.items() if v} == saved and abs(cash - m["cash_eur"]) <= 0.05,
          f"mirror holdings and cash follow from its trade ledger (cash {cash:.2f} vs saved {m['cash_eur']:.2f})")
    px = Prices(list(csv.DictReader((ROOT / "state" / "mirror_prices.csv").open())))
    nav = m["cash_eur"] + sum(sh * px.close(ln, m["as_of"], max_stale_days=4) for ln, sh in saved.items())
    check(abs(nav - m["nav_eur"]) <= 0.05 and abs(float(mh[-1]["nav_eur"]) - m["nav_eur"]) <= 0.05,
          f"mirror value = holdings at closing prices + cash ({nav:.2f} vs saved {m['nav_eur']:.2f})")


def mirror_maps() -> None:
    """Prevents: a mirror holding a fund the US portfolio does not hold (outside the approved twin/approximation list)."""
    uni = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    line_of = {i["id"]: i["mirror"]["line"] for i in uni}
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    m = json.loads((ROOT / "state" / "mirror.json").read_text())
    us_lines = {line_of[p["id"]] for p in port["positions"]}
    stray = [p["line"] for p in m["positions"] if p["line"] not in us_lines]
    check(not stray or bool(m.get("pending")), f"every mirror line belongs to a US holding (or a planned trade is pending){' — stray: ' + ', '.join(stray) if stray else ''}")


def report_renders() -> None:
    """Prevents: a broken, too long or internally-worded report; invented numbers in the text."""
    from v2 import narrate as N
    from v2 import render as R
    from v2.facts import build
    d = json.loads((ROOT / "state" / "portfolio.json").read_text())["as_of"]
    facts = build(d, with_macro=False)
    commentary = N.narrate(facts)  # fallback text without a key; raises if it fails the number check
    check(commentary["source"]["nl"] in ("fallback",) or commentary["source"]["nl"].startswith("ai:"), "commentary produced (NL)")
    with tempfile.TemporaryDirectory() as tmp:
        res = R.render(facts, commentary, Path(tmp))
    for lang, r in res.items():
        check(r["pages"] <= 5 and not r["problems"], f"report {lang.upper()} ≤ 5 pages, no layout problems ({r['pages']} pages{'; ' + '; '.join(r['problems']) if r['problems'] else ''})")


def rules_hold() -> None:
    """Prevents: a rule change that silently breaks the agreed limits."""
    from v2 import simulate as sim
    from v2.engine import Prices
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    uni = [i for i in yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"] if i.get("status") == "verified"]
    prices = Prices(list(csv.DictReader((ROOT / "state" / "prices.csv").open())))
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    hold = {"CIBR": 253, "GSG": 374, "IEFA": 312, "PAVE": 107, "SMH": 59, "URNM": 48, "XBI": 40, "XLU": 14, "XLV": 37}
    last = date.fromisoformat(port["as_of"])
    with contextlib.redirect_stdout(io.StringIO()), tempfile.TemporaryDirectory() as tmp:
        sim.ROOT = Path(tmp)
        s = sim.run("acceptance", hold, 2534.36, "2026-08-07", sim.wednesdays(date(2026, 8, 12), last), prices, uni, pol)
        sim.ROOT = ROOT
    rc = s["rule_checks"]
    check(rc["max_changes_in_a_week"] <= pol["turnover"]["max_instrument_changes_per_week"] + 1,
          f"at most {pol['turnover']['max_instrument_changes_per_week']} fund changes a week (+1 for a bond-core switch): max {rc['max_changes_in_a_week']}")
    check(rc["max_satellite_weight_pct"] <= pol["satellites"]["max_weight_each"] * 100 + 0.5, f"satellite weight ≤ {pol['satellites']['max_weight_each']:.0%}: max {rc['max_satellite_weight_pct']}%")
    check(rc["max_satellites_held"] <= pol["satellites"]["count"]["risk_on"] + 1, f"satellites held ≤ {pol['satellites']['count']['risk_on']} (+1 in transition): max {rc['max_satellites_held']}")


def fresh_state() -> None:
    """Prevents: a report built on a portfolio that stopped being updated (the old 'frozen since August' failure)."""
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    age = (date.today() - date.fromisoformat(port["as_of"])).days
    check(age <= 15, f"saved portfolio is at most 15 days old ({age} days)")


def size_budget() -> None:
    """Prevents: the document and workflow growth that buried v1 (577 control documents, 58 workflows)."""
    docs = [p for p in REPO.rglob("*.md") if ".git" not in p.parts and "evidence" not in p.parts]
    flows = list((REPO / ".github" / "workflows").glob("*.yml"))
    check(len(docs) <= 5, f"≤ 5 documentation files ({len(docs)}: {', '.join(sorted(str(p.relative_to(REPO)) for p in docs))})")
    check(len(flows) <= 5, f"≤ 5 workflows ({len(flows)})")


def main() -> None:
    for step in (history_reconciles, mirror_reconciles, mirror_maps, fresh_state, rules_hold, report_renders, size_budget):
        try:
            step()
        except Exception as exc:  # a crashing check is a failing check
            check(False, f"{step.__name__} crashed: {type(exc).__name__}: {exc}")
    print(f"\nACCEPTANCE {'OK' if not failures else 'FAILED'} ({len(failures)} failing)")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
