from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.render_cockpit_front_page import render_cockpit_front_page


PRODUCTION_REPORT_NAMES = {
    "weekly_analysis_pro_260618.html",
    "weekly_analysis_pro_nl_260618.html",
    "weekly_analysis_pro_260618.pdf",
    "weekly_analysis_pro_nl_260618.pdf",
}

DELIVERY_CLAIM_TOKENS = (
    "smtp_sendmail_returned_no_exception",
    "delivery_manifest_path_ok",
    "inbox receipt",
    "email sent",
)


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ["runtime", "macro", "pricing", "run_manifests", "delivery"]:
        (output / relative).mkdir(parents=True, exist_ok=True)

    state = {
        "report_date": "2026-06-18",
        "requested_close_date": "2026-06-18",
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 111413.22},
        "fx_basis": {"rate": 1.1458},
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
        "positions": [
            {
                "ticker": "SMH",
                "previous_weight_pct": 30.46,
                "previous_market_value_eur": 33934.09,
                "fresh_cash_test": "Smaller / under review",
                "portfolio_role": "Core growth review",
                "better_alternative_exists": "Yes",
                "shares_delta_this_run": 0,
                "action_executed_this_run": "None",
            },
            {
                "ticker": "GSG",
                "previous_weight_pct": 8.66,
                "previous_market_value_eur": 9643.33,
                "fresh_cash_test": "Hold / monitor",
                "portfolio_role": "Diversifier",
                "better_alternative_exists": "No",
                "shares_delta_this_run": 0,
                "action_executed_this_run": "None",
            },
        ],
    }
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")

    macro = {"regime": {"current": "Risk-on growth", "confidence": 0.66}}
    (output / "macro" / "latest.json").write_text(json.dumps(macro, sort_keys=True), encoding="utf-8")

    with (output / "etf_valuation_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "nav_eur"])
        writer.writerow(["2026-03-28", "100000.00"])
        writer.writerow(["2026-04-29", "101854.68"])
        writer.writerow(["2026-06-18", "111413.22"])

    (output / "etf_portfolio_state.json").write_text(json.dumps({"fixture": "portfolio"}), encoding="utf-8")
    (output / "etf_trade_ledger.csv").write_text("date,ticker,action\n", encoding="utf-8")
    (output / "etf_recommendation_scorecard.csv").write_text("date,ticker,recommendation\n", encoding="utf-8")
    (output / "pricing" / "latest_price_audit_path.txt").write_text("output/pricing/price_audit_fixture.json", encoding="utf-8")
    (output / "pricing" / "price_audit_fixture.json").write_text(json.dumps({"fixture": "pricing"}), encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text("output/run_manifests/run_manifest_fixture.json", encoding="utf-8")
    (output / "run_manifests" / "run_manifest_fixture.json").write_text(json.dumps({"status": "fixture"}), encoding="utf-8")
    (output / "delivery" / "weekly_etf_delivery_manifest_fixture.json").write_text(json.dumps({"delivery_status": "fixture_only"}), encoding="utf-8")

    (output / "weekly_analysis_pro_260618_03.html").write_text("classic English report fixture", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260618_03.html").write_text("classic Dutch report fixture", encoding="utf-8")
    return output


def _read_bytes(paths: list[Path]) -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in paths}


def _protected_paths(output: Path) -> list[Path]:
    return [
        output / "etf_portfolio_state.json",
        output / "etf_valuation_history.csv",
        output / "etf_trade_ledger.csv",
        output / "etf_recommendation_scorecard.csv",
        output / "pricing" / "latest_price_audit_path.txt",
        output / "runtime" / "latest_etf_report_state_path.txt",
        output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt",
        output / "delivery" / "weekly_etf_delivery_manifest_fixture.json",
    ]


def test_cockpit_preview_contains_required_visual_contract_components(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)

    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    html_by_language = {item.language: item.html_path.read_text(encoding="utf-8") for item in rendered}
    assert set(html_by_language) == {"en", "nl"}

    english = html_by_language["en"]
    dutch = html_by_language["nl"]

    assert "data-cockpit-front-page" in english
    assert "In brief" in english
    assert "Market climate" in english
    assert "This week's action" in english
    assert "Performance & risk" in english
    assert "Discipline point" in english
    assert "Preview-only cockpit surface" in english
    assert "Preview-only cockpit surface; not investment advice." in english

    assert "data-cockpit-front-page" in dutch
    assert "In het kort" in dutch
    assert "Marktklimaat" in dutch
    assert "Actie deze week" in dutch
    assert "Prestatie &amp; risico" in dutch or "Prestatie & risico" in dutch
    assert "Disciplinepunt" in dutch
    assert "Preview-only cockpit surface" in dutch
    assert "Preview-only cockpit surface; geen beleggingsadvies." in dutch


def test_cockpit_preview_does_not_overwrite_classic_report_surfaces(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    classic_reports = [
        output / "weekly_analysis_pro_260618_03.html",
        output / "weekly_analysis_pro_nl_260618_03.html",
    ]
    before = _read_bytes(classic_reports)

    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    assert _read_bytes(classic_reports) == before
    for item in rendered:
        assert item.html_path.parent == output / "cockpit_preview"
        assert item.html_path.exists()


def test_cockpit_preview_does_not_mutate_state_pricing_runtime_or_delivery_files(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    protected = _protected_paths(output)
    before = _read_bytes(protected)

    render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    assert _read_bytes(protected) == before


def test_cockpit_preview_does_not_claim_delivery_or_email_success(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    delivery_dir = output / "delivery"
    before_manifests = {path.name: path.read_bytes() for path in delivery_dir.glob("*.json")}

    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    after_manifests = {path.name: path.read_bytes() for path in delivery_dir.glob("*.json")}
    assert after_manifests == before_manifests

    for item in rendered:
        html = item.html_path.read_text(encoding="utf-8").lower()
        for token in DELIVERY_CLAIM_TOKENS:
            assert token not in html


def test_cockpit_preview_uses_preview_only_names(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    before_root_names = {path.name for path in output.iterdir() if path.is_file()}

    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    after_root_names = {path.name for path in output.iterdir() if path.is_file()}
    assert after_root_names == before_root_names
    assert not (after_root_names & PRODUCTION_REPORT_NAMES)

    for item in rendered:
        assert item.html_path.parent == output / "cockpit_preview"
        assert "_cockpit_" in item.html_path.name
        assert item.html_path.name.endswith("_01.html")
        assert item.pdf_path is None
