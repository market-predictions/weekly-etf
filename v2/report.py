"""Build the weekly report for V2_REPORT_DATE: facts → commentary → PDF (NL + EN).

Outputs to v2/evidence/report_<YYYYMMDD>/: facts.json, commentary.json, the
HTML and PDF per language, and checks.json. Fails if a layout check fails.
"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from v2 import narrate as N
from v2 import render as R
from v2.facts import build

ROOT = Path(__file__).resolve().parent


def main() -> None:
    d = os.environ.get("V2_REPORT_DATE") or date.today().isoformat()
    out = ROOT / "evidence" / f"report_{d.replace('-', '')}"
    out.mkdir(parents=True, exist_ok=True)
    facts = build(d)
    (out / "facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False))
    commentary = N.narrate(facts)
    (out / "commentary.json").write_text(json.dumps(commentary, indent=1, ensure_ascii=False))
    rendered = R.render(facts, commentary, out)
    checks = {"commentary_source": commentary["source"], "commentary_problems": commentary["problems"], "render": rendered,
              "macro": {k: {"available": v.get("available"), "date": v.get("date"), "stale": v.get("stale"), "error": v.get("error")} for k, v in facts["macro"].items()}}
    (out / "checks.json").write_text(json.dumps(checks, indent=1, ensure_ascii=False))
    print("REPORT_CHECKS " + json.dumps(checks, ensure_ascii=False))
    if any(r["problems"] for r in rendered.values()):
        raise SystemExit("REPORT_BLOCKED: layout problems")
    print(f"REPORT_OK {out}")


if __name__ == "__main__":
    main()
