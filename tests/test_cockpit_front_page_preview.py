from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.render_cockpit_front_page import render_cockpit_front_page


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    (output / "runtime").mkdir(parents=True)
    (output / "macro").mkdir(parents=True)
    (output / "pricing").mkdir(parents=True)
    state = {
        "report_date": "2026-06-18",
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 111413.22},
        "fx_basis": {"rate": 1.1458},
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
        "positions": [
            {"ticker": "SMH", "previous_weight_pct": 30.46, "previous_market_value_eur": 33934.09, "fresh_cash_test": "Smaller / under review", "better_alternative_exists": "Yes", "shares_delta_this_run": 0, "action_executed_this_run": "None"},
            {"ticker": "GSG", "previous_weight_pct": 8.66, "previous_market_value_eur": 9643.33, "fresh_cash_test": "Hold / monitor", "better_alternative_exists": "No", "shares_delta_this_run": 0, "action_executed_this_run": "None"},
        ],
    }
    (output / "runtime" / "fixture_state.json").write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text("output/runtime/fixture_state.json", encoding="utf-8")
    (output / "macro" / "latest.json").write_text(json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}), encoding="utf-8")
    with (output / "etf_valuation_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "nav_eur"])
        writer.writerow(["2026-03-28", "100000.00"])
        writer.writerow(["2026-04-29", "101854.68"])
        writer.writerow(["2026-06-18", "111413.22"])
    (output / "etf_portfolio_state.json").write_text("{}", encoding="utf-8")
    (output / "etf_trade_ledger.csv").write_text("date,ticker,action\n", encoding="utf-8")
    (output / "weekly_analysis_pro_260618_03.html").write_text("classic report", encoding="utf-8")
    return output


def test_cockpit_preview_renders_separate_html_without_mutating_core_files(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    protected = [output / "etf_portfolio_state.json", output / "etf_trade_ledger.csv", output / "etf_valuation_history.csv", output / "weekly_analysis_pro_260618_03.html"]
    before = {path: path.read_bytes() for path in protected}

    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)

    assert {item.language for item in rendered} == {"en", "nl"}
    for item in rendered:
        assert item.html_path.parent == output / "cockpit_preview"
        assert item.html_path.exists()
        html = item.html_path.read_text(encoding="utf-8")
        assert "data-cockpit-front-page" in html
        assert "SMH" in html
        assert "release score" not in html.lower()
        assert "system override" not in html.lower()
        assert "runtime valuation" not in html.lower()

    assert "In brief" in next(item.html_path for item in rendered if item.language == "en").read_text(encoding="utf-8")
    assert "In het kort" in next(item.html_path for item in rendered if item.language == "nl").read_text(encoding="utf-8")
    assert {path: path.read_bytes() for path in protected} == before


def test_cockpit_preview_sequences_do_not_overwrite_existing_preview(tmp_path: Path) -> None:
    output = _fixture_output(tmp_path)
    first = render_cockpit_front_page(output_dir=output, language="en", html_only=True)[0]
    second = render_cockpit_front_page(output_dir=output, language="en", html_only=True)[0]
    assert first.html_path != second.html_path
    assert first.html_path.name.endswith("_01.html")
    assert second.html_path.name.endswith("_02.html")
