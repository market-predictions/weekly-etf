from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "control" / "decisions" / "cockpit_promotion_decision_20260716.json"
DECISION_MD_PATH = REPO_ROOT / "control" / "decisions" / "COCKPIT_PROMOTION_DECISION_20260716.md"
PACKAGE_PATH = REPO_ROOT / "control" / "work_packages" / "WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW_20260716.md"


def _decision() -> dict:
    return json.loads(DECISION_PATH.read_text(encoding="utf-8"))


def test_promotion_decision_selects_additive_front_page_without_promoting() -> None:
    decision = _decision()
    assert decision["schema_version"] == "cockpit_promotion_decision_v1"
    assert decision["selected_option"] == "additive_delivery_front_page"
    assert decision["decision_status"] == "accepted_for_implementation_planning"
    assert decision["production_change_in_decision_package"] is False
    assert decision["promotion_status"] == "not_promoted"
    assert decision["next_package"] == "WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE"


def test_promotion_decision_preserves_delivery_and_evidence_contracts() -> None:
    decision = _decision()
    assert decision["classic_report_body"] == "preserved"
    assert decision["email_count_change"] is False
    assert decision["pdf_count_change"] is False
    assert decision["attachment_contract_change"] is False
    assert decision["manifest_contract_change"] is False
    assert decision["integration_layer"] == "delivery_html_and_pdf_render_pipeline"


def test_promotion_decision_requires_fail_closed_feature_gate() -> None:
    feature = _decision()["feature_gate"]
    assert feature["required"] is True
    assert feature["implementation_default"] == "disabled"
    assert feature["validation_enablement"] == "explicit"
    assert feature["production_enablement"] == "requires_separate_closeout"
    assert feature["failure_behavior"] == "return_unchanged_classic_output"
    assert feature["rollback"] == "disable_feature_flag"


def test_promotion_decision_suppresses_duplicate_decision_surface() -> None:
    decision = _decision()
    assert decision["duplicate_decision_surface_rule"] == "suppress_small_decision_cockpit_when_full_front_page_enabled"


def test_decision_package_changes_no_authority_or_delivery_action() -> None:
    boundary = _decision()["authority_boundaries"]
    assert boundary == {
        "portfolio_model_execution": False,
        "pricing_authority_change": False,
        "official_state_mutation": False,
        "official_trade_ledger_mutation": False,
        "email_send": False,
    }


def test_markdown_decision_and_package_contain_stable_contract_terms() -> None:
    combined = DECISION_MD_PATH.read_text(encoding="utf-8") + "\n" + PACKAGE_PATH.read_text(encoding="utf-8")
    for token in (
        "additive cockpit front page",
        "classic report body",
        "feature-gated",
        "fail closed",
        "WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE",
        "promotion_status: not_promoted",
    ):
        assert token.lower() in combined.lower()
