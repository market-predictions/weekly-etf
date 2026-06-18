from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import link_runtime_report_tickers as linkify
from runtime import polish_runtime_reports as polish


def test_english_final_markdown_places_cockpit_between_action_snapshot_and_regime() -> None:
    source = (
        "# Weekly ETF Review\n\n"
        "## 1. Executive Summary\n\n"
        "Old.\n\n"
        "## 2. Portfolio Action Snapshot\n\n"
        "None.\n\n"
        "## 3. Regime Dashboard\n\n"
        "Old."
    )

    polished = polish.polish_english(source, runtime_state={})
    result = linkify.linkify_report(polished)

    assert "## 2A. Decision cockpit" in result
    assert "### Decision cockpit" not in result
    assert result.index("## 2. Portfolio Action Snapshot") < result.index("## 2A. Decision cockpit")
    assert result.index("## 2A. Decision cockpit") < result.index("## 3. Regime Dashboard")
    assert "This week:** no portfolio action" in result


def test_dutch_final_markdown_places_besliscockpit_between_action_snapshot_and_regime() -> None:
    source = (
        "# Wekelijkse ETF-review\n\n"
        "## 1. Kernsamenvatting\n\n"
        "Oud.\n\n"
        "## 2. Portefeuille-acties\n\n"
        "Geen.\n\n"
        "## 3. Regime-dashboard\n\n"
        "Oud."
    )

    polished = polish.polish_dutch(source, runtime_state={})
    result = linkify.linkify_report(polished)

    assert "## 2A. Besliscockpit" in result
    assert "### Besliscockpit" not in result
    assert result.index("## 2. Portefeuille-acties") < result.index("## 2A. Besliscockpit")
    assert result.index("## 2A. Besliscockpit") < result.index("## 3. Regime-dashboard")
    assert "Deze week:** geen portefeuilleactie" in result
    assert "thesisfit" not in result
