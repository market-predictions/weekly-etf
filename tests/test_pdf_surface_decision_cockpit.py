from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import polish_runtime_reports as polish


def test_english_final_markdown_contains_visible_decision_cockpit() -> None:
    source = "# Weekly ETF Review\n\n## 1. Executive Summary\n\nOld.\n\n## 2. Portfolio Action Snapshot\n\nNone.\n\n## 3. Regime Dashboard\n\nOld."
    result = polish.polish_english(source, runtime_state={})
    assert "Decision cockpit" in result
    assert "This week:** no portfolio action" in result


def test_dutch_final_markdown_contains_visible_besliscockpit() -> None:
    source = "# Wekelijkse ETF-review\n\n## 1. Kernsamenvatting\n\nOud.\n\n## 2. Portefeuille-acties\n\nGeen.\n\n## 3. Regime-dashboard\n\nOud."
    result = polish.polish_dutch(source, runtime_state={})
    assert "Besliscockpit" in result
    assert "Deze week:** geen portefeuilleactie" in result
    assert "thesisfit" not in result
