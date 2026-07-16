from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_cockpit_side_by_side_review import build_cockpit_side_by_side_review
from runtime.render_cockpit_front_page import render_cockpit_front_page


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ["runtime", "macro", "pricing", "run_manifests", "delivery"]:
        (output / relative).mkdir(parents=True, exist_ok=True)

    state = {
        "report_date": "2026-07-14",
        "requested_close_date": "2026-07-14",
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 110224.86},
        "fx_basis": {"rate": 1.14211},
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
        "positions": [
            {
                "ticker": "SMH",
                "current_weight_pct": 28.13,
                "previous_weight_pct": 28.13,
                "market_value_eur": 31008.0,
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "fresh_cash_test": "Smaller / under review",
                "better_alternative_exists": "Yes",
            },
            {
                "ticker": "URNM",
                "current_weight_pct": 2.01,
                "previous_weight_pct": 7.01,
                "market_value_eur": 2215.0,
                "shares_delta_this_run": -122.008961,
                "action_executed_this_run": "Sell",
            },
            {
                "ticker": "XBI",
                "current_weight_pct": 5.00,
                "previous_weight_pct": 0.00,
                "market_value_eur": 5511.0,
                "shares_delta_this_run": 40.491749,
                "action_executed_this_run": "Buy",
            },
        ],
    }
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")
    (output / "macro" / "latest.json").write_text(json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}), encoding="utf-8")

    context = "Evidence context remains in the classic report. " * 1000
    (output / "weekly_analysis_pro_260714_03.md").write_text("# Older English report", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260714_03.md").write_text("# Ouder Nederlands rapport", encoding="utf-8")
    (output / "weekly_analysis_pro_260714_04.md").write_text(
        "# Weekly ETF Pro Review 2026-07-14\n\n"
        "URNM reduced from 7.01% to 2.01%; XBI added at 5.00%.\n"
        "Next action trigger: another mutation requires a confirmed edge and available churn budget.\n"
        "Current portfolio value (EUR): 110224.86\n" + context,
        encoding="utf-8",
    )
    (output / "weekly_analysis_pro_nl_260714_04.md").write_text(
        "# Wekelijkse ETF-review 2026-07-14\n\n"
        "URNM afgebouwd van 7,01% naar 2,01%; XBI toegevoegd op 5,00%.\n"
        "Trigger voor volgende actie: een volgende mutatie vereist bevestigde voorsprong en beschikbaar mutatiebudget.\n"
        "Huidige portefeuillewaarde (EUR): 110224.86\n" + context,
        encoding="utf-8",
    )
    (output / "weekly_analysis_pro_260714_04_delivery.html").write_text("<html><body>Current English delivery surface</body></html>", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260714_04_delivery.html").write_text("<html><body>Actuele Nederlandse delivery surface</body></html>", encoding="utf-8")

    (output / "etf_portfolio_state.json").write_text(json.dumps({"fixture": "portfolio"}), encoding="utf-8")
    (output / "etf_valuation_history.csv").write_text("date,nav_eur\n2026-03-28,100000.00\n2026-07-14,110224.86\n", encoding="utf-8")
    (output / "etf_trade_ledger.csv").write_text("date,ticker,action\n", encoding="utf-8")
    (output / "etf_recommendation_scorecard.csv").write_text("date,ticker,recommendation\n", encoding="utf-8")
    (output / "pricing" / "latest_price_audit_path.txt").write_text("output/pricing/price_audit_fixture.json", encoding="utf-8")
    (output / "pricing" / "price_audit_fixture.json").write_text(json.dumps({"fixture": "pricing"}), encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text("output/run_manifests/run_manifest_fixture.json", encoding="utf-8")
    (output / "run_manifests" / "run_manifest_fixture.json").write_text(json.dumps({"fixture": "manifest"}), encoding="utf-8")
    (output / "delivery" / "delivery_fixture.json").write_text(json.dumps({"fixture": "delivery"}), encoding="utf-8")
    return output


def _protected(output: Path) -> list[Path]:
    return [
        output / "etf_portfolio_state.json",
        output / "etf_valuation_history.csv",
        output / "etf_trade_ledger.csv",
        output / "etf_recommendation_scorecard.csv",
        output / "runtime" / "latest_etf_report_state_path.txt",
        output / "runtime" / "fixture_state.json",
        output / "pricing" / "latest_price_audit_path.txt",
        output / "pricing" / "price_audit_fixture.json",
        output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt",
        output / "run_manifests" / "run_manifest_fixture.json",
        output / "delivery" / "delivery_fixture.json",
    ]


def test_wp08_review_is_evidence_based_and_records_current_blockers(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    before = {path: path.read_bytes() for path in _protected(output)}

    render_cockpit_front_page(output_dir=output, language="both", html_only=True)
    result = build_cockpit_side_by_side_review(output)
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    findings = {row["dimension"]: row for row in metadata["findings"]}

    assert metadata["schema_version"] == "cockpit_side_by_side_review_v2"
    assert metadata["review_conclusion"] == "iteration_required"
    assert metadata["next_recommended_package"] == "WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT"
    assert metadata["promotion_status"] == "not_promoted"

    assert findings["executed_action_clarity"]["status"] == "pass"
    assert findings["current_weight_accuracy"]["status"] == "pass"
    assert findings["performance_risk_accuracy"]["status"] == "pass"
    assert findings["trust_provenance_clarity"]["status"] == "pass"
    assert findings["audit_evidence_preservation"]["status"] == "pass"

    assert findings["decision_clarity"]["status"] == "partial"
    assert findings["bilingual_semantic_parity"]["status"] == "partial"
    assert findings["premium_look_and_feel"]["status"] == "partial"
    assert {"decision_clarity", "bilingual_semantic_parity", "premium_look_and_feel"}.issubset(metadata["blocking_findings"])

    evidence = json.dumps(metadata, ensure_ascii=False)
    assert "URNM reduced" in evidence
    assert "XBI added" in evidence
    assert "URNM 7.0% → 2.0%" in evidence
    assert "XBI 0.0% → 5.0%" in evidence
    assert "summary_contradiction=True" in evidence
    assert "dutch_punctuation_bug=True" in evidence
    assert "hybrid_labels=" in evidence

    selected = metadata["selected_sources"]
    assert selected["classic"]["en"]["markdown"] == "output/weekly_analysis_pro_260714_04.md"
    assert selected["classic"]["nl"]["markdown"] == "output/weekly_analysis_pro_nl_260714_04.md"
    assert selected["cockpit"]["en"] == "output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html"
    assert selected["cockpit"]["nl"] == "output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html"

    english_html = result.english_html_path.read_text(encoding="utf-8")
    dutch_html = result.dutch_html_path.read_text(encoding="utf-8")
    assert "<pre>" not in english_html
    assert "Iteration required" in english_html
    assert "Iteratie vereist" in dutch_html
    assert "data-preview-only=\"true\"" in english_html
    assert "promotion_status: not_promoted" in english_html

    assert {path: path.read_bytes() for path in _protected(output)} == before
