from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.render_cockpit_front_page import render_cockpit_front_page


def _output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for dirname in ["runtime", "macro", "pricing", "run_manifests"]:
        (output / dirname).mkdir(parents=True, exist_ok=True)
    state = {
        "report_date": "2026-06-18",
        "portfolio": {"cash_eur": 1000, "total_portfolio_value_eur": 101000},
        "fx_basis": {"rate": 1.1},
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
        "positions": [{"ticker": "SMH", "previous_weight_pct": 20, "previous_market_value_eur": 20000, "shares_delta_this_run": 0, "action_executed_this_run": "None"}],
    }
    (output / "runtime" / "state.json").write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/state.json", encoding="utf-8")
    (output / "macro" / "latest.json").write_text(json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}), encoding="utf-8")
    (output / "pricing" / "latest_price_audit_path.txt").write_text("output/pricing/audit.json", encoding="utf-8")
    (output / "pricing" / "audit.json").write_text("{}", encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text("output/run_manifests/run.json", encoding="utf-8")
    (output / "run_manifests" / "run.json").write_text("{}", encoding="utf-8")
    with (output / "etf_valuation_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "nav_eur"])
        writer.writerow(["2026-03-28", "100000"])
        writer.writerow(["2026-06-18", "101000"])
    return output


def test_source_evidence_labels_are_bilingual(tmp_path: Path) -> None:
    rendered = render_cockpit_front_page(output_dir=_output(tmp_path), language="both", html_only=True)
    html = {item.language: item.html_path.read_text(encoding="utf-8") for item in rendered}

    assert "Source &amp; evidence" in html["en"] or "Source & evidence" in html["en"]
    assert "Built from runtime state" in html["en"]
    assert "Valuation history checked" in html["en"]
    assert "Pricing audit reference" in html["en"]
    assert "Macro pack reference" in html["en"]
    assert "Run-manifest reference" in html["en"]
    assert "No delivery claim" in html["en"]
    assert "Not promoted to production" in html["en"]
    assert "Bronnen en bewijs" in html["nl"]
    assert "Gebouwd vanuit runtime-state" in html["nl"]
    assert "Waarderingshistorie gecontroleerd" in html["nl"]
    assert "Pricing-audit referentie" in html["nl"]
    assert "Macro-pack referentie" in html["nl"]
    assert "Run-manifest referentie" in html["nl"]
    assert "Geen deliveryclaim" in html["nl"]
    assert "Niet gepromoveerd naar productie" in html["nl"]


def test_source_evidence_keeps_preview_boundary(tmp_path: Path) -> None:
    rendered = render_cockpit_front_page(output_dir=_output(tmp_path), language="en", html_only=True)
    page = rendered[0].html_path.read_text(encoding="utf-8")
    assert 'data-source-evidence="true"' in page
    assert 'data-promotion-status="not_promoted"' in page
    assert "shadow engine" not in page.lower()
    assert rendered[0].html_path.parent.name == "cockpit_preview"
