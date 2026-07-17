from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.additive_cockpit_front_page import (
    FEATURE_FLAG,
    FRONT_PAGE_MARKER,
    CockpitFrontPageInjectionResult,
    inject_additive_cockpit_front_page,
    parse_feature_value,
    render_delivery_cockpit_front_page_fragment,
)


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ["runtime", "macro", "pricing", "run_manifests"]:
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
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text(
        "output/runtime/fixture_state.json", encoding="utf-8"
    )
    (output / "macro" / "latest.json").write_text(
        json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}),
        encoding="utf-8",
    )
    (output / "etf_valuation_history.csv").write_text(
        "date,nav_eur\n2026-03-28,100000.00\n2026-07-14,110224.86\n",
        encoding="utf-8",
    )
    (output / "pricing" / "latest_price_audit_path.txt").write_text(
        "output/pricing/fixture.json", encoding="utf-8"
    )
    (output / "pricing" / "fixture.json").write_text("{}", encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text(
        "output/run_manifests/fixture.json", encoding="utf-8"
    )
    (output / "run_manifests" / "fixture.json").write_text("{}", encoding="utf-8")
    return output


def _classic_html() -> str:
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Classic</title></head>"
        "<body><main id='classic-report'><h1>Classic report body</h1>"
        "<div id='classic-evidence'>Evidence table remains</div>"
        "<div id='classic-tail'>Final disclaimer</div></main></body></html>"
    )


def test_feature_parser_accepts_only_explicit_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(FEATURE_FLAG, raising=False)
    assert parse_feature_value() == "disabled"
    assert parse_feature_value("disabled") == "disabled"
    assert parse_feature_value("enabled") == "enabled"
    for value in ["true", "false", "1", "0", "yes", "on", "", "preview"]:
        with pytest.raises(ValueError):
            parse_feature_value(value)


def test_disabled_mode_returns_byte_identical_classic_html(tmp_path: Path) -> None:
    classic = _classic_html()
    result = inject_additive_cockpit_front_page(
        classic,
        language="en",
        output_dir=_fixture_output(tmp_path),
        feature_value="disabled",
    )
    assert result.status == "disabled"
    assert result.html == classic
    assert result.front_page_count == 0


def test_enabled_mode_adds_one_front_page_before_complete_classic_body(tmp_path: Path) -> None:
    classic = _classic_html()
    result = inject_additive_cockpit_front_page(
        classic,
        language="en",
        output_dir=_fixture_output(tmp_path),
        feature_value="enabled",
    )
    assert result.status == "enabled"
    assert result.front_page_count == 1
    assert result.html.count(FRONT_PAGE_MARKER) == 1
    assert result.html.index(FRONT_PAGE_MARKER) < result.html.index("id='classic-report'")
    assert "Classic report body" in result.html
    assert "Evidence table remains" in result.html
    assert "Final disclaimer" in result.html
    assert "URNM reduced" in result.html
    assert "XBI added" in result.html
    assert "Next action trigger" in result.html


def test_delivery_fragment_uses_client_facing_english_and_dutch_wording(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    english = render_delivery_cockpit_front_page_fragment(
        output_dir=output, language="en", render_mode="email"
    ).html
    dutch = render_delivery_cockpit_front_page_fragment(
        output_dir=output, language="nl", render_mode="pdf"
    ).html

    assert "Report front page" in english
    assert "Complete analysis and evidence layer follow below" in english
    assert "Rapportvoorpagina" in dutch
    assert "Volledige analyse en bewijslaag volgen hierna" in dutch
    assert "URNM afgebouwd" in dutch
    assert "XBI toegevoegd" in dutch

    forbidden = [
        "preview lane",
        "preview-only cockpit",
        "no delivery claim",
        "not promoted to production",
        "voorbeeldcockpit",
        "geen leveringsclaim",
        "niet naar productie gepromoveerd",
    ]
    combined = (english + dutch).lower()
    assert not any(token in combined for token in forbidden)


def test_invalid_feature_value_fails_closed_with_diagnostic(tmp_path: Path) -> None:
    classic = _classic_html()
    result = inject_additive_cockpit_front_page(
        classic,
        language="en",
        output_dir=_fixture_output(tmp_path),
        feature_value="true",
    )
    assert result.status == "fallback"
    assert result.html == classic
    assert result.diagnostic.startswith("invalid_feature_value:")


def test_planted_renderer_failure_returns_unchanged_classic_html(tmp_path: Path) -> None:
    classic = _classic_html()

    def fail_renderer(**_: object) -> object:
        raise RuntimeError("planted cockpit render failure")

    result = inject_additive_cockpit_front_page(
        classic,
        language="en",
        output_dir=_fixture_output(tmp_path),
        feature_value="enabled",
        renderer=fail_renderer,  # type: ignore[arg-type]
    )
    assert result.status == "fallback"
    assert result.html == classic
    assert "planted cockpit render failure" in result.diagnostic
    assert result.front_page_count == 0


def test_existing_single_front_page_is_not_duplicated(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    first = inject_additive_cockpit_front_page(
        _classic_html(), language="en", output_dir=output, feature_value="enabled"
    )
    second = inject_additive_cockpit_front_page(
        first.html, language="en", output_dir=output, feature_value="enabled"
    )
    assert second.status == "enabled"
    assert second.front_page_count == 1
    assert second.html == first.html


def test_runtime_wrapper_suppresses_small_decision_cockpit_only_after_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import send_report_runtime_html as runtime_html

    output = _fixture_output(tmp_path)
    monkeypatch.setenv("MRKT_RPRTS_OUTPUT_DIR", str(output))
    markdown = (
        "## 2A. Decision cockpit\n"
        "- Keep concentration disciplined.\n"
        "## 3. Regime Dashboard\n"
    )
    classic = "<html><head></head><body><table class='action-table'><tr><td>Action</td></tr></table></body></html>"

    monkeypatch.setenv(FEATURE_FLAG, "disabled")
    disabled = runtime_html._apply_cockpit_front_page(
        classic, markdown, language="en", render_mode="email"
    )
    assert FRONT_PAGE_MARKER not in disabled
    assert "class='note-box decision-cockpit'" in disabled

    monkeypatch.setenv(FEATURE_FLAG, "enabled")
    enabled = runtime_html._apply_cockpit_front_page(
        classic, markdown, language="en", render_mode="email"
    )
    assert enabled.count(FRONT_PAGE_MARKER) == 1
    assert "class='note-box decision-cockpit'" not in enabled

    fallback = CockpitFrontPageInjectionResult(
        html=classic,
        status="fallback",
        diagnostic="planted_failure",
        feature_value="enabled",
        front_page_count=0,
    )
    monkeypatch.setattr(runtime_html, "inject_additive_cockpit_front_page", lambda *args, **kwargs: fallback)
    failed = runtime_html._apply_cockpit_front_page(
        classic, markdown, language="en", render_mode="email"
    )
    assert FRONT_PAGE_MARKER not in failed
    assert "class='note-box decision-cockpit'" in failed
