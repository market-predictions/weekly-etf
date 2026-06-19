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
        "positions": [{"ticker": "SMH", "previous_weight_pct": 30.46}],
    }
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")

    (output / "weekly_analysis_pro_260618_04.md").write_text("# Classic English report\n\nDecision cockpit evidence.", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260618_04.md").write_text("# Klassiek Nederlands rapport\n\nBesliscockpit bewijs.", encoding="utf-8")
    (output / "weekly_analysis_pro_260618_04_delivery.html").write_text("<html><body>Classic delivery surface</body></html>", encoding="utf-8")
    (output / "weekly_analysis_pro_nl_260618_04_delivery.html").write_text("<html><body>Klassieke delivery surface</body></html>", encoding="utf-8")

    (output / "cockpit_preview" / "weekly_analysis_pro_cockpit_260618_01.html").write_text(
        "<html><body data-cockpit-front-page='true'>In brief Source &amp; evidence Performance &amp; risk</body></html>",
        encoding="utf-8",
    )
    (output / "cockpit_preview" / "weekly_analysis_pro_nl_cockpit_260618_01.html").write_text(
        "<html><body data-cockpit-front-page='true'>In het kort Bronnen en bewijs Prestatie &amp; risico</body></html>",
        encoding="utf-8",
    )

    (output / "etf_portfolio_state.json").write_text(json.dumps({"fixture": "portfolio"}), encoding="utf-8")
    (output / "etf_valuation_history.csv").write_text("date,nav_eur\n2026-06-18,111413.22\n", encoding="utf-8")
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
    assert metadata["schema_version"] == "cockpit_side_by_side_review_v1"
    assert metadata["review_type"] == "side_by_side_preview_only"
    assert metadata["token"] == "260618"
    assert metadata["review_dimensions"] == REVIEW_DIMENSIONS
    assert metadata["promotion_status"] == "not_promoted"
    assert metadata["production_report_change"] == "none"
    assert metadata["delivery_change"] == "none"
    assert metadata["state_change"] == "none"
    assert metadata["state_mutation"] == "not_allowed"
    assert metadata["delivery_mutation"] == "not_allowed"
    assert metadata["provenance_iteration_review"] is True
    assert metadata["source_provenance_improvement"] == "present"
    assert metadata["previous_package"] == "WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE"
    assert metadata["next_package"] == "WP_COCKPIT_SURFACE_09_PROMOTION_REVIEW_OR_FURTHER_ITERATION_DECISION"
    assert metadata["classic_report_sources"]
    assert metadata["cockpit_preview_sources"]

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [result.english_markdown_path, result.english_html_path, result.dutch_markdown_path, result.dutch_html_path]
    )
    for dimension in REVIEW_DIMENSIONS:
        assert dimension in combined
    for required in [
        "Classic report strengths",
        "Cockpit preview strengths",
        "Cockpit preview risks",
        "Required fixes before promotion",
        "Explicit no-promotion statement",
        "Evidence",
        "promotion_status: not_promoted",
        "WP07 source/provenance iteration",
        "Source/provenance clarity improved",
        "Source &amp; evidence",
        "runtime-state source",
        "valuation-history source",
        "pricing-audit reference",
        "macro-pack reference",
        "run-manifest reference",
        "classic production report remains authoritative",
        "WP07 bron/provenance-iteratie",
        "Bronnen en bewijs",
        "Geen deliveryclaim",
        "Niet gepromoveerd naar productie",
    ]:
        assert required in combined


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


def test_side_by_side_review_references_classic_and_cockpit_sources(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)

    result = build_cockpit_side_by_side_review(output)

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert "output/weekly_analysis_pro_260618_04.md" in metadata["classic_report_sources"]
    assert "output/weekly_analysis_pro_nl_260618_04.md" in metadata["classic_report_sources"]
    assert "output/cockpit_preview/weekly_analysis_pro_cockpit_260618_01.html" in metadata["cockpit_preview_sources"]
    assert "output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260618_01.html" in metadata["cockpit_preview_sources"]

    english = result.english_markdown_path.read_text(encoding="utf-8")
    dutch = result.dutch_markdown_path.read_text(encoding="utf-8")
    assert "output/weekly_analysis_pro_260618_04.md" in english
    assert "output/cockpit_preview/weekly_analysis_pro_cockpit_260618_01.html" in english
    assert "output/weekly_analysis_pro_nl_260618_04.md" in dutch
    assert "output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260618_01.html" in dutch


def test_side_by_side_review_does_not_overwrite_cockpit_preview_or_production_reports(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    cockpit_before = _files_under(output / "cockpit_preview")
    reports = _production_report_paths(output)
    reports_before = _read_bytes(reports)

    build_cockpit_side_by_side_review(output)

    assert _files_under(output / "cockpit_preview") == cockpit_before
    assert _read_bytes(reports) == reports_before
