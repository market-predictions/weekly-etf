from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import polish_runtime_reports as polish


def test_preferred_takeaways_are_defined_as_parallel_messages() -> None:
    assert "SMH remains the best-supported core exposure" in polish.MAIN_TAKEAWAY_EN
    assert "SMH blijft de best onderbouwde kernblootstelling" in polish.MAIN_TAKEAWAY_NL
    assert "fresh capital and replacement decisions" in polish.MAIN_TAKEAWAY_EN
    assert "nieuw kapitaal en vervangingsbeslissingen" in polish.MAIN_TAKEAWAY_NL
    assert "relative-strength" in polish.MAIN_TAKEAWAY_EN
    assert "relatieve-sterkte" in polish.MAIN_TAKEAWAY_NL


def test_english_takeaway_replaces_static_review_label_message_when_macro_surface_applies() -> None:
    state = {"macro_policy_pack": {"regime": {"primary_regime": "Risk-on growth"}}}
    source = "# Weekly ETF Review\n\n## 1. Executive Summary\n\nOld.\n\n## 2. Portfolio Action Snapshot\n\nNone."
    result = polish.polish_english(source, runtime_state=state)
    assert polish.MAIN_TAKEAWAY_EN in result
    assert "static review labels" not in result


def test_dutch_takeaway_replaces_legacy_wording_when_macro_surface_applies() -> None:
    state = {"macro_policy_pack": {"regime": {"primary_regime": "Risk-on growth"}}}
    source = (
        "# Wekelijkse ETF-review\n\n"
        "## 1. Kernsamenvatting\n\n"
        "- **Primair regime:** Oud\n"
        "- **Belangrijkste conclusie:** Oude tekst\n\n"
        "## 2. Portefeuille-acties\n\nGeen.\n\n"
        "## 3. Regime-dashboard\n\nOud.\n\n"
        "## 4. Structurele kansenradar\n\nOud.\n\n"
        "## 10. Review huidige posities\n\nOud.\n\n"
        "## 15. Huidige posities en cash\n\nOud."
    )
    result = polish.polish_dutch(source, runtime_state=state)
    assert polish.MAIN_TAKEAWAY_NL in result
    assert "best onderbouwde kernpositie" not in result
