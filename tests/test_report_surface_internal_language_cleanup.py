from __future__ import annotations

from runtime.client_facing_sanitizer import sanitize_client_facing_html
from runtime.report_surface_language_contract import (
    client_language_findings,
    markdown_link_multiset,
    normalize_client_language,
    numeric_multiset,
)
from runtime.wp16_followup3_cleanup import clean_text


def test_english_internal_language_is_rewritten_without_fact_drift() -> None:
    source = """## 3. Regime Dashboard
- Deterministic regime read — review-only: The shadow engine currently classifies the backdrop as Risk-on growth, broadly aligned with the legacy regime read. Confidence is high but review-only. This does not authorize portfolio changes. The normal discipline gates remain decisive.
### Rotation engine status
- Guarded model rotation executed and persisted: reduced [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) from 5.12% to 0.12%; added [XLV](https://www.tradingview.com/chart/?symbol=XLV) at 5.00%.
### [CIBR](https://www.tradingview.com/chart/?symbol=CIBR) — Hold with override — release score 10
Role: Rotation destination. Required next action: Monitor concentration..
"""
    cleaned = clean_text(source, language="en")

    assert client_language_findings(source, language="en")
    assert client_language_findings(cleaned, language="en") == []
    assert "Supplementary regime cross-check" in cleaned
    assert "secondary rules-based assessment" in cleaned
    assert "Implemented portfolio change" in cleaned
    assert "Portfolio rotation completed" in cleaned
    assert "Hold — no further change this review" in cleaned
    assert "review priority 10" in cleaned
    assert "Portfolio allocation" in cleaned
    assert "concentration.." not in cleaned
    assert numeric_multiset(cleaned) == numeric_multiset(source)
    assert markdown_link_multiset(cleaned) == markdown_link_multiset(source)
    assert clean_text(cleaned, language="en") == cleaned


def test_dutch_internal_language_is_rewritten_without_fact_drift() -> None:
    source = """## 3. Regime-dashboard
- Deterministische regime-inschatting — alleen ter review: De shadow-engine classificeert de marktomgeving momenteel als Risk-on groei, grotendeels in lijn met de bestaande regime-inschatting. De betrouwbaarheid is hoog maar alleen ter review. Dit geeft geen autoriteit voor portefeuillewijzigingen. De normale discipline blijft leidend.
- Bewaakte modelrotatie uitgevoerd en verwerkt: [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) verlaagd van 5.12% naar 0.12%; [XLV](https://www.tradingview.com/chart/?symbol=XLV) toegevoegd op 5.00%.
### [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) — Aanhouden met override — release score 75; override: rotation budget already used
Rol: Rotatiebestemming. Vereiste volgende actie: Herbeoordeel tegenover [GRID](https://www.tradingview.com/chart/?symbol=GRID)..
"""
    cleaned = clean_text(source, language="nl")

    assert client_language_findings(source, language="nl")
    assert client_language_findings(cleaned, language="nl") == []
    assert "Aanvullende regimecontrole" in cleaned
    assert "tweede regelgebaseerde beoordeling" in cleaned
    assert "Portefeuillerotatie voltooid" in cleaned
    assert "Aanhouden — geen verdere wijziging in deze review" in cleaned
    assert "reviewprioriteit 75" in cleaned
    assert "rotatielimiet bereikt voor deze review" in cleaned
    assert "Portefeuilleallocatie" in cleaned
    assert "GRID).." not in cleaned
    assert numeric_multiset(cleaned) == numeric_multiset(source)
    assert markdown_link_multiset(cleaned) == markdown_link_multiset(source)
    assert clean_text(cleaned, language="nl") == cleaned


def test_html_delivery_sanitizer_applies_same_contract() -> None:
    html = """<html><body><p>Rotation engine status</p><p>Guarded auto-execution: buy XLV at 5.00%.</p><p>Hold with override; release score 80..</p></body></html>"""
    cleaned = sanitize_client_facing_html(html, md_text="## 1. Executive Summary", language="en")

    assert client_language_findings(cleaned, language="en") == []
    assert "Implemented portfolio change" in cleaned
    assert "Implemented change" in cleaned
    assert "review priority 80" in cleaned
    assert "80.." not in cleaned
    assert "5.00%" in cleaned


def test_delivery_table_residuals_are_rewritten_without_numeric_drift() -> None:
    source = """- Holdings with high release scores require reduce/replace/override discipline.
| Ticker | Release score | Override status |
|---|---:|---|
| URNM | 90.00 | System override: Minimum trade size was not met |
"""
    cleaned = clean_text(source, language="en")

    assert set(client_language_findings(source, language="en")) == {"raw_override", "release_score"}
    assert client_language_findings(cleaned, language="en") == []
    assert "weakest capital-efficiency profile" in cleaned
    assert "review priority" in cleaned
    assert "Execution constraint status" in cleaned
    assert "Execution constraint: position too small for an efficient trade" in cleaned
    assert numeric_multiset(cleaned) == numeric_multiset(source)
    assert clean_text(cleaned, language="en") == cleaned


def test_generic_discipline_gate_language_is_cleaned_bilingually() -> None:
    english = "<html><body><p>All discipline gates must clear before allocation.</p></body></html>"
    dutch = "<html><body><p>Alle disciplinepoorten moeten vrijgeven vóór allocatie.</p></body></html>"

    cleaned_en = sanitize_client_facing_html(english, md_text="## 1. Executive Summary", language="en")
    cleaned_nl = sanitize_client_facing_html(dutch, md_text="## 1. Kernsamenvatting", language="nl")

    assert client_language_findings(cleaned_en, language="en") == []
    assert client_language_findings(cleaned_nl, language="nl") == []
    assert "decision conditions" in cleaned_en
    assert "beslisvoorwaarden" in cleaned_nl
    assert normalize_client_language(cleaned_en, language="en") == cleaned_en
    assert normalize_client_language(cleaned_nl, language="nl") == cleaned_nl


def test_normalizer_preserves_unrelated_authority_text() -> None:
    source = "Portfolio state is authoritative. Pricing authority remains unchanged."
    assert normalize_client_language(source, language="en") == source
