from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime.render_cockpit_front_page import render_cockpit_front_page


def _write_fixture(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ("runtime", "macro", "pricing", "run_manifests"):
        (output / relative).mkdir(parents=True, exist_ok=True)

    state = {
        "report_date": "2026-07-14",
        "requested_close_date": "2026-07-14",
        "portfolio": {"cash_eur": 100.0},
        "fx_basis": {"rate": 1.14211},
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
        "positions": [
            {
                "ticker": "URNM",
                "shares_delta_this_run": -122.008961,
                "action_executed_this_run": "Sell",
                "previous_weight_pct": 7.01,
                "current_weight_pct": 2.01,
                "previous_market_value_eur": 7000.0,
                "market_value_eur": 2000.0,
                "fresh_cash_test": "Hold",
            },
            {
                "ticker": "XBI",
                "shares_delta_this_run": 40.491749,
                "action_executed_this_run": "Buy",
                "previous_weight_pct": 0.0,
                "current_weight_pct": 5.0,
                "previous_market_value_eur": 0.0,
                "market_value_eur": 5000.0,
                "fresh_cash_test": "Hold / monitor",
            },
            {
                "ticker": "CURRENT",
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "previous_weight_pct": 5.0,
                "current_weight_pct": 30.0,
                "previous_market_value_eur": 500.0,
                "market_value_eur": 30000.0,
                "fresh_cash_test": "Hold / monitor",
            },
            {
                "ticker": "STALE",
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "previous_weight_pct": 60.0,
                "current_weight_pct": 10.0,
                "previous_market_value_eur": 60000.0,
                "market_value_eur": 10000.0,
                "fresh_cash_test": "Hold / monitor",
            },
        ],
    }
    (output / "runtime" / "executed.json").write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text(
        "output/runtime/executed.json", encoding="utf-8"
    )
    (output / "macro" / "latest.json").write_text(
        json.dumps({"regime": {"current": "Mixed risk-on", "confidence": 0.62}}),
        encoding="utf-8",
    )
    with (output / "etf_valuation_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "nav_eur"])
        writer.writerow(["2026-03-28", "100000.00"])
    return output


def test_executed_rotation_is_specific_and_bilingual(tmp_path: Path) -> None:
    output = _write_fixture(tmp_path)
    rendered = render_cockpit_front_page(output_dir=output, language="both", html_only=True)
    html = {item.language: item.html_path.read_text(encoding="utf-8") for item in rendered}

    assert "URNM reduced" in html["en"]
    assert "XBI added" in html["en"]
    assert "URNM 7.0% → 2.0%" in html["en"]
    assert "XBI 0.0% → 5.0%" in html["en"]
    assert "Action present in runtime state" not in html["en"]
    assert "No portfolio action" not in html["en"]

    assert "URNM afgebouwd" in html["nl"]
    assert "XBI toegevoegd" in html["nl"]
    assert "URNM 7,0% → 2,0%" in html["nl"]
    assert "XBI 0,0% → 5,0%" in html["nl"]
    assert "Actie aanwezig volgens runtime state" not in html["nl"]
    assert "Geen portefeuilleactie" not in html["nl"]


def test_current_weights_and_market_values_override_previous_values(tmp_path: Path) -> None:
    output = _write_fixture(tmp_path)
    rendered = render_cockpit_front_page(output_dir=output, language="en", html_only=True)[0]
    html = rendered.html_path.read_text(encoding="utf-8")

    assert "CURRENT" in html
    assert "30.0%" in html
    assert "STALE" not in html.split("Largest position", 1)[-1].split("EUR/USD", 1)[0]
    assert "€47,100" in html
    assert "€127,500" not in html
