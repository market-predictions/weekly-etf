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
        check(r["pages"] <= 4 and not r["problems"], f"report {lang.upper()} ≤ 4 pages, no layout problems ({r['pages']} pages{'; ' + '; '.join(r['problems']) if r['problems'] else ''})")


def rules_hold() -> None:
    """Prevents: a rule change that silently breaks the agreed limits."""
    from v2 import simulate as sim
    from v2.engine import Prices
    pol = yaml.safe_load((ROOT / "policy.yml").read_text())
    uni = [i for i in yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"] if i.get("status") == "verified"]
    prices = Prices(list(csv.DictReader((ROOT / "state" / "prices.csv").open())))
    port = json.loads((ROOT / "state" / "portfolio.json").read_text())
    hold = {"L0CK": 934, "DFEN": 207, "VWCE": 151, "EUNA": 1526, "SXR8": 10, "IQQQ": 149}
    last = date.fromisoformat(port["as_of"])
    with contextlib.redirect_stdout(io.StringIO()), tempfile.TemporaryDirectory() as tmp:
        sim.ROOT = Path(tmp)
        s = sim.run("acceptance", hold, 28101.01, "2026-08-14", sim.wednesdays(date(2026, 8, 19), last), prices, uni, pol)
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
    for step in (history_reconciles, fresh_state, rules_hold, report_renders, size_budget):
        try:
            step()
        except Exception as exc:  # a crashing check is a failing check
            check(False, f"{step.__name__} crashed: {type(exc).__name__}: {exc}")
    print(f"\nACCEPTANCE {'OK' if not failures else 'FAILED'} ({len(failures)} failing)")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
