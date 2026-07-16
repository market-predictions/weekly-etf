from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.render_cockpit_front_page import (
    _discipline_surface,
    _next_action_trigger,
    _plain_summary,
    _source_evidence_html,
    render_cockpit_front_page,
)


def _executed_state() -> dict:
    return {
        "report_date": "2026-07-14",
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 110224.86},
        "fx_basis": {"rate": 1.14211},
        "positions": [
            {
                "ticker": "SMH",
                "current_weight_pct": 28.13,
                "previous_weight_pct": 28.13,
                "market_value_eur": 31008.0,
                "shares_delta_this_run": 0,
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
                "current_weight_pct": 5.0,
                "previous_weight_pct": 0.0,
                "market_value_eur": 5511.0,
                "shares_delta_this_run": 40.491749,
                "action_executed_this_run": "Buy",
            },
        ],
    }


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ["runtime", "macro", "pricing", "run_manifests"]:
        (output / relative).mkdir(parents=True, exist_ok=True)

    state = _executed_state()
    state["source_files"] = {"macro_policy_pack": "output/macro/latest.json"}
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")
    (output / "macro" / "latest.json").write_text(json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}), encoding="utf-8")
    (output / "pricing" / "price_audit.json").write_text("{}", encoding="utf-8")
    (output / "pricing" / "latest_price_audit_path.txt").write_text("output/pricing/price_audit.json", encoding="utf-8")
    (output / "run_manifests" / "run_manifest.json").write_text("{}", encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text("output/run_manifests/run_manifest.json", encoding="utf-8")
    (output / "etf_valuation_history.csv").write_text("date,nav_eur\n2026-03-28,100000.00\n2026-07-14,110224.86\n", encoding="utf-8")
    return output


def test_action_aware_summary_does_not_contradict_executed_rotation() -> None:
    state = _executed_state()
    macro = {"regime": {"current": "Risk-on growth", "confidence": 0.66}}
    points = [("2026-03-28", 100000.0), ("2026-07-14", 110224.86)]

    english = _plain_summary(state, macro, points, "en")
    dutch = _plain_summary(state, macro, points, "nl")

    assert "A controlled rotation was executed this week" in english
    assert "URNM reduced" in english and "XBI added" in english
    assert "discipline ahead of activity" not in english.lower()
    assert "Deze week is een gecontroleerde rotatie uitgevoerd" in dutch
    assert "URNM afgebouwd" in dutch and "XBI toegevoegd" in dutch
    assert "discipline boven activiteit" not in dutch.lower()


def test_no_action_summary_retains_disciplined_no_action_wording() -> None:
    state = _executed_state()
    for row in state["positions"]:
        row["shares_delta_this_run"] = 0
        row["action_executed_this_run"] = "None"
    macro = {"regime": {"current": "Risk-on growth", "confidence": 0.66}}
    points = [("2026-03-28", 100000.0), ("2026-07-14", 110224.86)]

    assert "discipline ahead of activity" in _plain_summary(state, macro, points, "en").lower()
    assert "discipline boven activiteit" in _plain_summary(state, macro, points, "nl").lower()


def test_next_action_trigger_is_bilingual_and_authority_derived() -> None:
    state = _executed_state()
    english = _next_action_trigger(state, "en")
    dutch = _next_action_trigger(state, "nl")

    assert english.startswith("Next action trigger:")
    assert "SMH" in english
    assert "relative strength" in english
    assert "pricing basis" in english
    assert dutch.startswith("Trigger voor volgende actie:")
    assert "SMH" in dutch
    assert "relatieve sterkte" in dutch
    assert "prijsbasis" in dutch


def test_dutch_discipline_sentence_has_valid_percentage_and_period() -> None:
    sentence = _discipline_surface(_executed_state(), "nl")
    assert "28,1%" in sentence
    assert sentence.endswith(".")
    assert not sentence.endswith(",")


def test_dutch_provenance_labels_are_natural_and_legacy_hybrids_are_absent(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    html = _source_evidence_html(
        output,
        output / "runtime" / "fixture_state.json",
        output / "macro" / "latest.json",
        "nl",
    )

    for expected in (
        "Bron prijscontrole",
        "Bron macrobeeld",
        "Bron uitvoerregistratie",
        "Geen leveringsclaim",
        "Niet naar productie gepromoveerd",
    ):
        assert expected in html

    for legacy in (
        "Pricing-audit referentie",
        "Macro-pack referentie",
        "Run-manifest referentie",
        "Geen deliveryclaim",
    ):
        assert legacy not in html


def test_rendered_wp09_surface_contains_trigger_and_preserves_preview_boundary(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)
    html_by_language = {item.language: item.html_path.read_text(encoding="utf-8") for item in rendered}

    assert "Next action trigger" in html_by_language["en"]
    assert "Trigger voor volgende actie" in html_by_language["nl"]
    assert "A controlled rotation was executed this week" in html_by_language["en"]
    assert "Deze week is een gecontroleerde rotatie uitgevoerd" in html_by_language["nl"]
    assert "disciplinepoorten vrijgeven," not in html_by_language["nl"]
    assert all(item.html_path.parent == output / "cockpit_preview" for item in rendered)
