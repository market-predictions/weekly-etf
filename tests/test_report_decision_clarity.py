from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import polish_runtime_reports as polish


def test_english_polish_adds_decision_cockpit() -> None:
    source = "# Weekly ETF Review\n\n## 1. Executive Summary\n\nOld summary.\n\n## 2. Portfolio Action Snapshot\n\nNone."
    result = polish.polish_english(source, runtime_state={})
    assert "### Decision cockpit" in result
    assert "This week:** no portfolio action" in result
    assert "SMH concentration remains above the soft position cap" in result
    assert "Next action trigger" in result


def test_dutch_polish_adds_besliscockpit() -> None:
    source = "# Wekelijkse ETF-review\n\n## 1. Kernsamenvatting\n\nOude samenvatting.\n\n## 2. Portefeuille-acties\n\nGeen."
    result = polish.polish_dutch(source, runtime_state={})
    assert "### Besliscockpit" in result
    assert "Deze week:** geen portefeuilleactie" in result
    assert "SMH-concentratie blijft boven de zachte positielimiet" in result
    assert "Trigger voor volgende actie" in result
    assert "aansluiting op de thesis" in result
    assert "thesisfit" not in result


def test_client_surface_cleanup_removes_harsh_role_language() -> None:
    en = polish.polish_english("Portfolio role is impaired", runtime_state={})
    nl = polish.polish_dutch("Portefeuillerol is verzwakt", runtime_state={})
    assert "Portfolio role is impaired" not in en
    assert "Role under review" in en
    assert "Portefeuillerol is verzwakt" not in nl
    assert "Rol onder herbeoordeling" in nl


def test_no_delivery_receipt_claim_added() -> None:
    result = polish.polish_english("# Weekly ETF Review", runtime_state={})
    assert "inbox receipt" not in result.lower()
    assert "email delivered" not in result.lower()
