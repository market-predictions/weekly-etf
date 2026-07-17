from __future__ import annotations

import pytest

from tools.validate_etf_delivery_html_visible_language_contract import validate_visible_dutch_delivery_language


def test_css_class_identifier_does_not_trigger_dutch_language_failure() -> None:
    html = """
    <style>.etf-cockpit-confidence{display:flex}</style>
    <div class="etf-cockpit-confidence"><span>66% vertrouwen</span></div>
    """
    validate_visible_dutch_delivery_language(html, "synthetic_nl_delivery.html")


def test_visible_english_confidence_still_fails() -> None:
    html = "<div><span>66% confidence</span></div>"
    with pytest.raises(RuntimeError, match="confidence"):
        validate_visible_dutch_delivery_language(html, "synthetic_nl_delivery.html")
