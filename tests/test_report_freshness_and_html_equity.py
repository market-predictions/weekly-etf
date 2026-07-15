from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace

import pytest

from runtime.report_freshness_contract import (
    ReportFreshnessError,
    apply_report_freshness_contract,
    validate_report_freshness,
)
from runtime.standalone_html_equity_embed import (
    validate_standalone_html_equity,
    with_standalone_html_equity_embed,
)

TV = "https://www.tradingview.com/chart/?symbol={}"


def link(ticker: str) -> str:
    return f"[{ticker}]({TV.format(ticker)})"


def runtime_state() -> dict:
    return {
        "report_date": "2026-07-14",
        "positions": [
            {"ticker": "IEFA", "current_weight_pct": 24.05},
            {"ticker": "DFEN", "current_weight_pct": 5.26},
            {"ticker": "SMH", "current_weight_pct": 28.13},
        ],
        "macro_policy_pack": {
            "report_date": "2026-07-14",
            "regime": {
                "current": "Risk-on growth",
                "previous": "Risk-on growth",
                "what_changed": [
                    "AI / semiconductor leadership remains the dominant equity impulse.",
                    "Gold hedge behavior remains under review rather than automatic ballast.",
                ],
            },
            "regime_memory": {
                "current_regime": "Risk-on growth",
                "prior_regime": "Risk-on growth",
                "regime_changed_this_run": False,
                "breadth_trend": "mixed",
                "cross_asset_confirmation": "mixed",
            },
            "macro_signals": {
                "equity_leadership": {
                    "signal": "narrow_ai_leadership",
                    "evidence": {
                        "SMH_return_3m_pct": 29.98,
                        "SPY_return_3m_pct": 8.89,
                    },
                }
            },
            "policy_catalysts": [
                {
                    "policy_area": "ECB rate-policy tightening",
                    "event_date": "2026-06-11",
                    "transfer_to_report": True,
                },
                {
                    "policy_area": "AI infrastructure and semiconductor supply chains",
                    "transfer_to_report": True,
                },
            ],
        },
    }


EN_STALE = f"""# Weekly ETF Pro Review 2026-07-14

## 1. Executive Summary
- **What changed this week:** AI / semiconductor leadership remains the dominant equity impulse.

## 3. Regime Dashboard
### What changed
- AI / semiconductor leadership remains the dominant equity impulse.
- Gold hedge behavior remains under review rather than automatic ballast.

### Policy catalysts included in this report
- ECB rate-policy tightening: The ECB raised rates this week in response to renewed inflation pressure.
- AI infrastructure and semiconductor supply chains: Current evidence remains relevant.

## 4. Structural Opportunity Radar
| Theme | Primary ETF | Why not promoted | What would change that |
|---|---|---|---|
| Defense innovation | {link('PPA')} | Candidate remains below cutoff. | The lane remains relevant, but {link('PPA')} must justify itself versus {link('ITA')}. |
| Non-U.S. developed market diversification | {link('IEFA')} | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |

## 5. Key Risks / Invalidators
- {link('PPA')} and {link('PAVE')} remain replaceable until their ETF implementation quality is proven.
- Non-U.S. equity exposure remains a diversification gap.

## 6. Bottom Line
- Current state remains under review.

## 7. Equity Curve and Portfolio Development
- placeholder

## 8. Asset Allocation Map
| Bucket | Stance | Reason |
|---|---|---|
| Europe equities | Neutral | Watchlist only; non-U.S. exposure remains a diversification gap. |
| non-USD assets | Watchlist | Zero allocation is an explicit U.S. exceptionalism bet. |

## 9. Second-Order Effects Map
| Driver | First-order effect | ETF implication |
|---|---|---|
| Factor concentration | {link('QUAL')}, {link('IEFA')} watchlist | Monitor |
| Defense thesis vs ETF implementation | {link('PPA')} must justify itself versus {link('ITA')} | Hold {link('PPA')} under review |

## 10. Current Position Review
- current
"""

NL_STALE = f"""# Wekelijkse ETF-review Dinsdag 14 juli 2026

## 1. Kernsamenvatting
- **Wat is er deze week veranderd:** AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.

## 3. Regime-dashboard
### Wat veranderde
- AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.
- Het gedrag van goud als hedge blijft onder herbeoordeling en is geen automatische stabilisator.

### Beleidscatalysatoren in dit rapport
- ECB-renteverkrapping: De ECB verhoogde deze week de rente vanwege hernieuwde inflatiedruk.
- AI-infrastructuur: Het signaal blijft relevant.

## 4. Structurele kansenradar
| Thema | Primaire ETF | Waarom niet gepromoveerd | Wat zou veranderen |
|---|---|---|---|
| Financial infrastructure and market plumbing | KCE | kandidaat | bewijs |
| Power infrastructure and utilities capex | XLU | kandidaat | bewijs |
| Defensie-innovatie | {link('PPA')} | kandidaat | PPA blijft een alternatief. |

## 5. Belangrijkste risico’s / invalidaties
- {link('PPA')} en {link('PAVE')} blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.
- Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.

## 6. Conclusie
- Voordat nieuw kapitaal naar alternatieven gaat, moeten {link('SPY')}, {link('PPA')} en {link('PAVE')} expliciet worden getoetst.
- {link('PPA')} moet zich bewijzen tegenover {link('ITA')}, {link('PAVE')} tegenover {link('GRID')}.

## 7. Portefeuillecurve en portefeuilleontwikkeling
- placeholder

## 8. Allocatiekaart
| Segment | Positionering | Toelichting |
|---|---|---|
| Europese aandelen | Neutraal | Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof. |
| Niet-USD activa | Volglijst | Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht. |

## 9. Tweede-orde-effectenkaart
| Drijver | Eerste-orde-effect | ETF-implicatie |
|---|---|---|
| Factorconcentratie | {link('QUAL')}, {link('IEFA')} op de volglijst | Monitor |
| Defensiethesis | {link('PPA')} moet zich bewijzen tegenover {link('ITA')} | Houd {link('PPA')} onder herbeoordeling |

## 10. Review huidige posities
> Diagnostisch-only: geen fundability-bevoegdheid.
"""


def test_unpatched_reports_fail_freshness_contract() -> None:
    with pytest.raises(ReportFreshnessError):
        validate_report_freshness(EN_STALE, runtime_state(), "en")
    with pytest.raises(ReportFreshnessError):
        validate_report_freshness(NL_STALE, runtime_state(), "nl")


def test_freshness_contract_patches_delta_events_and_current_holdings() -> None:
    state = runtime_state()
    en = apply_report_freshness_contract(EN_STALE, state, "en")
    nl = apply_report_freshness_contract(NL_STALE, state, "nl")

    assert "No material regime change was recorded versus the prior review." in en
    assert "Er is geen materiële regimeverandering vastgesteld ten opzichte van de vorige review." in nl
    assert "raised rates this week" not in en
    assert "verhoogde deze week de rente" not in nl
    assert "IEFA already represents 24.05% of the portfolio" in en
    assert "IEFA vertegenwoordigt al 24.05% van de portefeuille" in nl
    assert "DFEN" in en and "DFEN" in nl
    assert "Non-U.S. equity exposure remains a diversification gap" not in en
    assert "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof" not in nl

    # PPA remains valid as a candidate in Section 4, but no longer masquerades as a current holding.
    assert "The lane remains relevant, but" in en and link("PPA") in en
    section_five_en = en.split("## 5.", 1)[1].split("## 6.", 1)[0]
    section_five_nl = nl.split("## 5.", 1)[1].split("## 6.", 1)[0]
    assert "DFEN" in section_five_en and "PPA and PAVE remain replaceable" not in section_five_en
    assert "DFEN" in section_five_nl and "PPA en PAVE blijven vervangbaar" not in section_five_nl

    for phrase in (
        "Financial infrastructure and market plumbing",
        "Power infrastructure and utilities capex",
        "Diagnostisch-only",
        "fundability-bevoegdheid",
    ):
        assert phrase not in nl

    validate_report_freshness(en, state, "en")
    validate_report_freshness(nl, state, "nl")


def test_ecb_event_is_only_reported_in_its_actual_report_week() -> None:
    from runtime.build_macro_policy_pack import _event_is_in_report_week, policy_catalysts

    assert _event_is_in_report_week("2026-06-11", "2026-06-11")
    assert _event_is_in_report_week("2026-06-16", "2026-06-11")
    assert not _event_is_in_report_week("2026-07-14", "2026-06-11")

    july = policy_catalysts({}, "2026-07-14")
    june = policy_catalysts({}, "2026-06-11")
    assert all(item.get("policy_area") != "ECB rate-policy tightening" for item in july)
    assert any(item.get("policy_area") == "ECB rate-policy tightening" for item in june)


def test_standalone_html_embeds_graph_while_email_html_keeps_cid(tmp_path: Path) -> None:
    report = tmp_path / "weekly_analysis_pro_260714_04.md"
    chart = tmp_path / "weekly_analysis_pro_260714_04_equity_curve.png"
    html_path = tmp_path / "weekly_analysis_pro_260714_04_delivery.html"
    report.write_text("# Report\n\n`EQUITY_CURVE_CHART_PLACEHOLDER`\n", encoding="utf-8")
    chart.write_bytes(b"\x89PNG\r\n\x1a\npreview")
    html_path.write_text('<html><img src="cid:equitycurve"></html>', encoding="utf-8")

    def png_to_data_uri(path: Path) -> str:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

    def build_report_html(md_text: str, report_date: str, image_src: str | None = None, render_mode: str = "email") -> str:
        return f'<html data-mode="{render_mode}"><img alt="Equity curve" src="{image_src}"></html>'

    fake_module = SimpleNamespace(
        png_to_data_uri=png_to_data_uri,
        build_report_html=build_report_html,
    )

    def generate(_output_dir: Path, _report_path: Path, mode: str = "pro") -> dict:
        return {
            "bilingual": False,
            "en": {
                "report_path": report,
                "equity_curve_png": chart,
                "html_path": html_path,
                "html_email": '<html><img src="cid:equitycurve"></html>',
                "md_text_clean": report.read_text(encoding="utf-8"),
                "report_date_str": "2026-07-14",
            },
        }

    bundle = with_standalone_html_equity_embed(generate, fake_module)(tmp_path, report, mode="pro")
    validate_standalone_html_equity(html_path)
    assert "cid:equitycurve" in bundle["en"]["html_email"]
    assert "data:image/png;base64," in html_path.read_text(encoding="utf-8")
