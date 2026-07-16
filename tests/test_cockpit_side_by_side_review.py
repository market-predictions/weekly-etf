from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_cockpit_side_by_side_review import REVIEW_DIMENSIONS, build_cockpit_side_by_side_review


DELIVERY_CLAIM_TOKENS = (
    "smtp_sendmail_returned_no_exception",
    "delivery_manifest_path_ok",
    "inbox receipt",
    "email " + "sent",
)


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ["runtime", "pricing", "run_manifests", "delivery", "cockpit_preview"]:
        (output / relative).mkdir(parents=True, exist_ok=True)

    state = {
        "report_date": "2026-06-18",
        "requested_close_date": "2026-06-18",
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 111413.22},
        "positions": [
            {
                "ticker": "SMH",
                "current_weight_pct": 30.46,
                "previous_weight_pct": 30.46,
                "market_value_eur": 33934.09,
                "shares_delta_this_run": 0,
                "action_executed_this_run": "None",
            }
        ],
    }
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")

    (output / "weekly_analysis_pro_260618_03.md").write_text("# Older classic English report", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260618_03.md").write_text("# Ouder klassiek Nederlands rapport", encoding="utf-8")
    (output / "weekly_analysis_pro_260618_04.md").write_text(
        "# Classic English report\n\nDecision cockpit evidence. Next action trigger.\n" + "Context. " * 200,
        encoding="utf-8",
    )
    (output / "weekly_analysis_pro_nl_260618_04.md").write_text(
        "# Klassiek Nederlands rapport\n\nBesliscockpit bewijs. Trigger voor volgende actie.\n" + "Context. " * 200,
        encoding="utf-8",
    )
    (output / "weekly_analysis_pro_260618_04_delivery.html").write_text("<html><body>Classic delivery surface</body></html>", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260618_04_delivery.html").write_text("<html><body>Klassieke delivery surface</body></html>", encoding="utf-8")

    (output / "cockpit_preview" / "weekly_analysis_pro_cockpit_260618_01.html").write_text(
        "<html><body data-cockpit-front-page='true'><div class=\"card\">In brief</div><div class=\"metrics\">Performance &amp; risk €111,413 +11.4% SMH 30.5%</div><div class=\"discipline\">Discipline</div></body></html>",
        encoding="utf-8",
    )
    (output / "cockpit_preview" / "weekly_analysis_pro_nl_cockpit_260618_01.html").write_text(
        "<html><body data-cockpit-front-page='true'><div class=\"card\">In het kort</div><div class=\"metrics\">Prestatie &amp; risico €111.413 +11,4% SMH 30,5%</div><div class=\"discipline\">Discipline</div></body></html>",
        encoding="utf-8",
    )

    (output / "etf_portfolio_state.json").write_text(json.dumps({"fixture": "portfolio"}), encoding="utf-8")
    (output / "etf_valuation_history.csv").write_text("date,nav_eur\n2026-03-28,100000.00\n2026-06-18,111413.22\n", encoding="utf-8")
    (output / "etf_trade_ledger.csv").write_text("date,ticker,action\n", encoding="utf-8")
    (output / "etf_recommendation_scorecard.csv").write_text("date,ticker,recommendation\n", encoding="utf-8")
    (output / "pricing" / "latest_price_audit_path.txt").write_text("output/pricing/price_audit_fixture.json", encoding="utf-8")
    (output / "pricing" / "price_audit_fixture.json").write_text(json.dumps({"fixture": "pricing"}), encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text("output/run_manifests/run_manifest_fixture.json", encoding="utf-8")
    (output / "run_manifests" / "run_manifest_fixture.json").write_text(json.dumps({"fixture": "run_manifest"}), encoding="utf-8")
    (output / "delivery" / "weekly_etf_delivery_manifest_fixture.json").write_text(json.dumps({"fixture": "delivery"}), encoding="utf-8")
    return output


def _files_under(path: Path) -> dict[str, bytes]:
    if not path.exists():
        return {}
    return {str(item.relative_to(path.parent)).replace("\\", "/"): item.read_bytes() for item in path.rglob("*") if item.is_file()}


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


def _production_report_paths(output: Path) -> list[Path]:
    return [
        output / "weekly_analysis_pro_260618_04.md",
        output / "weekly_analysis_pro_nl_260618_04.md",
        output / "weekly_analysis_pro_260618_04_delivery.html",
        output / "weekly_analysis_pro_nl_260618_04_delivery.html",
    ]


def test_side_by_side_review_writes_only_to_cockpit_review(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    before = {str(path.relative_to(output)).replace("\\", "/") for path in output.rglob("*") if path.is_file()}

    result = build_cockpit_side_by_side_review(output)

    after = {str(path.relative_to(output)).replace("\\", "/") for path in output.rglob("*") if path.is_file()}
    new_files = after - before
    assert new_files
    assert all(name.startswith("cockpit_review/") for name in new_files)
    assert result.metadata_path == output / "cockpit_review" / "weekly_etf_cockpit_side_by_side_review_260618.json"
    assert result.english_markdown_path.exists()
    assert result.english_html_path.exists()
    assert result.dutch_markdown_path.exists()
    assert result.dutch_html_path.exists()


def test_side_by_side_review_metadata_and_artifacts_include_required_contract(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)

    result = build_cockpit_side_by_side_review(output)

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["schema_version"] == "cockpit_side_by_side_review_v2"
    assert metadata["review_type"] == "evidence_based_side_by_side_preview_only"
    assert metadata["token"] == "260618"
    assert metadata["review_dimensions"] == REVIEW_DIMENSIONS
    assert [row["dimension"] for row in metadata["findings"]] == REVIEW_DIMENSIONS
    assert metadata["promotion_status"] == "not_promoted"
    assert metadata["state_mutation"] == "not_allowed"
    assert metadata["delivery_mutation"] == "not_allowed"
    assert metadata["review_conclusion"] in {"iteration_required", "ready_for_promotion_decision"}
    assert metadata["next_recommended_package"]
    assert metadata["selected_sources"]["classic"]["en"]["markdown"].endswith("_04.md")
    assert metadata["selected_sources"]["classic"]["nl"]["markdown"].endswith("_04.md")
    assert metadata["selected_sources"]["cockpit"]["en"].endswith("_01.html")
    assert metadata["input_sha256"]

    english_html = result.english_html_path.read_text(encoding="utf-8")
    dutch_html = result.dutch_html_path.read_text(encoding="utf-8")
    assert "<pre>" not in english_html
    assert "data-schema-version=\"cockpit_side_by_side_review_v2\"" in english_html
    assert "Selected evidence sources" in english_html
    assert "Geselecteerde bewijsbronnen" in dutch_html


def test_side_by_side_review_does_not_claim_delivery_success(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    result = build_cockpit_side_by_side_review(output)
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in [result.metadata_path, result.english_markdown_path, result.english_html_path, result.dutch_markdown_path, result.dutch_html_path]
    )
    for token in DELIVERY_CLAIM_TOKENS:
        assert token not in combined


def test_side_by_side_review_does_not_mutate_protected_state_or_delivery_files(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    protected = _protected_paths(output)
    before = _read_bytes(protected)
    build_cockpit_side_by_side_review(output)
    assert _read_bytes(protected) == before


def test_side_by_side_review_selects_only_current_classic_and_cockpit_sources(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    result = build_cockpit_side_by_side_review(output)
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))

    selected = metadata["selected_sources"]
    assert selected["classic"]["en"]["markdown"] == "output/weekly_analysis_pro_260618_04.md"
    assert selected["classic"]["nl"]["markdown"] == "output/weekly_analysis_pro_nl_260618_04.md"
    assert selected["classic"]["en"]["html"] == "output/weekly_analysis_pro_260618_04_delivery.html"
    assert selected["classic"]["nl"]["html"] == "output/weekly_analysis_pro_nl_260618_04_delivery.html"
    assert selected["cockpit"]["en"] == "output/cockpit_preview/weekly_analysis_pro_cockpit_260618_01.html"
    assert selected["cockpit"]["nl"] == "output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260618_01.html"
    assert "_03.md" not in json.dumps(selected)


def test_side_by_side_review_does_not_overwrite_cockpit_preview_or_production_reports(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    cockpit_before = _files_under(output / "cockpit_preview")
    reports = _production_report_paths(output)
    reports_before = _read_bytes(reports)
    build_cockpit_side_by_side_review(output)
    assert _files_under(output / "cockpit_preview") == cockpit_before
    assert _read_bytes(reports) == reports_before
