from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace

from runtime.report_freshness_contract import apply_report_freshness_contract, validate_report_freshness
from runtime.standalone_html_equity_embed import (
    validate_standalone_html_equity,
    with_standalone_html_equity_embed,
)


def state() -> dict:
    return {
        "report_date": "2026-07-14",
        "positions": [
            {"ticker": "IEFA", "current_weight_pct": 24.05},
            {"ticker": "DFEN", "current_weight_pct": 5.26},
        ],
        "macro_policy_pack": {
            "report_date": "2026-07-14",
            "regime": {"current": "Risk-on growth", "previous": "Risk-on growth"},
            "regime_memory": {
                "current_regime": "Risk-on growth",
                "prior_regime": "Risk-on growth",
                "regime_changed_this_run": False,
                "breadth_trend": "mixed",
                "cross_asset_confirmation": "mixed",
            },
            "policy_catalysts": [],
        },
    }


def test_plain_ticker_radar_and_actual_zero_allocation_wording_are_corrected() -> None:
    text = """# Weekly ETF Pro Review 2026-07-14

## 1. Executive Summary
- **What changed this week:** No update.

## 3. Regime Dashboard
### What changed
- Existing regime remains intact.

## 4. Structural Opportunity Radar
| Theme | Primary ETF | Why not promoted | What would change that |
|---|---|---|---|
| Non-U.S. developed market diversification | IEFA | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |

## 8. Asset Allocation Map
| Bucket | Stance | Reason |
|---|---|---|
| non-USD assets | Watchlist | Zero allocation is an explicit U.S. exceptionalism bet. |

## 9. Second-Order Effects Map
- Portfolio has limited non-U.S. exposure.
"""

    result = apply_report_freshness_contract(text, state(), "en")

    assert "Existing funded position; no additional lane promotion was granted this run." in result
    assert "Zero allocation is an explicit U.S. exceptionalism bet." not in result
    assert "Portfolio has limited non-U.S. exposure." not in result
    assert "24.05%" in result
    validate_report_freshness(result, state(), "en")


def test_dutch_plain_radar_and_no_exposure_wording_are_corrected() -> None:
    text = """# Wekelijkse ETF-review Dinsdag 14 juli 2026

## 1. Kernsamenvatting
- **Wat is er deze week veranderd:** Geen update.

## 3. Regime-dashboard
### Wat veranderde
- Het bestaande regime blijft intact.

## 4. Structurele kansenradar
| Thema | Primaire ETF | Waarom niet gepromoveerd | Wat zou veranderen |
|---|---|---|---|
| Ontwikkelde markten buiten de VS | IEFA | Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend. | Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase. |

## 8. Allocatiekaart
- De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.
"""

    result = apply_report_freshness_contract(text, state(), "nl")

    assert "Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend." in result
    assert "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS." not in result
    assert "24.05%" in result
    validate_report_freshness(result, state(), "nl")


def test_sanitized_equity_source_is_restored_for_email_and_standalone_html(tmp_path: Path) -> None:
    report = tmp_path / "weekly_analysis_pro_260714_04.md"
    chart = tmp_path / "weekly_analysis_pro_260714_04_equity_curve.png"
    html_path = tmp_path / "weekly_analysis_pro_260714_04_delivery.html"
    report.write_text("# Report\n\n`EQUITY_CURVE_CHART_PLACEHOLDER`\n", encoding="utf-8")
    chart.write_bytes(b"\x89PNG\r\n\x1a\npreview")
    harmful_html = '<html><img src="#harmful-link" alt="Equity curve" /></html>'
    html_path.write_text(harmful_html, encoding="utf-8")

    def png_to_data_uri(path: Path) -> str:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

    fake_module = SimpleNamespace(
        png_to_data_uri=png_to_data_uri,
        build_report_html=lambda *_args, **_kwargs: harmful_html,
    )

    def generate(_output_dir: Path, _report_path: Path, mode: str = "pro") -> dict:
        return {
            "bilingual": False,
            "en": {
                "report_path": report,
                "equity_curve_png": chart,
                "html_path": html_path,
                "html_email": harmful_html,
                "md_text_clean": report.read_text(encoding="utf-8"),
                "report_date_str": "2026-07-14",
            },
        }

    bundle = with_standalone_html_equity_embed(generate, fake_module)(tmp_path, report, mode="pro")

    assert "cid:equitycurve" in bundle["en"]["html_email"]
    assert "#harmful-link" not in bundle["en"]["html_email"]
    validate_standalone_html_equity(html_path)
    standalone = html_path.read_text(encoding="utf-8")
    assert "data:image/png;base64," in standalone
    assert "#harmful-link" not in standalone
