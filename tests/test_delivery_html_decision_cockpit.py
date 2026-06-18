from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report_runtime_html as runtime_html


def test_injects_english_decision_cockpit_into_delivery_html() -> None:
    md = "## 2A. Decision cockpit\n\n- This week: no portfolio action.\n"
    html = "<html><body><table class='action-table'><tr><td>Action</td></tr></table></body></html>"

    result = runtime_html._inject_decision_cockpit_html(html, md)

    assert "Decision cockpit" in result
    assert "This week: no portfolio action." in result
    assert result.index("Decision cockpit") < result.index("action-table")


def test_injects_dutch_besliscockpit_into_delivery_html() -> None:
    md = "## 2A. Besliscockpit\n\n- Deze week: geen portefeuilleactie.\n"
    html = "<html><body><table class='action-table'><tr><td>Actie</td></tr></table></body></html>"

    result = runtime_html._inject_decision_cockpit_html(html, md)

    assert "Besliscockpit" in result
    assert "Deze week: geen portefeuilleactie." in result
    assert "thesisfit" not in result
    assert result.index("Besliscockpit") < result.index("action-table")
