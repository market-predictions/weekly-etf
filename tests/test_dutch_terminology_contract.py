from __future__ import annotations

from pathlib import Path

from runtime import nl_terminology as term
from runtime import nl_terminology_contract as contract
from runtime.client_facing_sanitizer import localize_dutch_delivery_html, validate_dutch_delivery_language
from runtime.nl_localization import localize_text
from runtime.scrub_nl_client_language import scrub_text


def test_central_terminology_covers_dutch_enum_leak_regression() -> None:
    assert contract.DUTCH_STATUS_ALIASES["No / under review"] == "Nee / onder herbeoordeling"
    assert contract.DUTCH_STATUS_ALIASES["Smaller / under review"] == "Kleiner / onder herbeoordeling"
    assert contract.DUTCH_STATUS_ALIASES["Hold but replaceable"] == "Aanhouden, maar vervangbaar"
    assert localize_text("No / under review", language="nl") == "Nee / onder herbeoordeling"
    assert localize_text("Smaller / under review", language="nl") == "Kleiner / onder herbeoordeling"
    assert localize_text("Hold but replaceable", language="nl") == "Aanhouden, maar vervangbaar"


def test_native_guard_only_scrub_uses_narrow_centralized_runtime_aliases() -> None:
    text = "| Better Alternative Exists? | Fresh cash |\n| No / under review | Smaller / under review |"
    scrubbed = scrub_text(text, native_dutch=True)
    assert "No / under review" not in scrubbed
    assert "Nee / onder herbeoordeling" in scrubbed
    assert "Kleiner / onder herbeoordeling" in scrubbed


def test_delivery_html_uses_shared_terminology_contract() -> None:
    html = "<p>Weekly ETF Pro Review</p><p>No / under review</p><p>Keep the current allocation</p>"
    localized = localize_dutch_delivery_html(html)
    assert "Weekly ETF Pro Review" not in localized
    assert "No / under review" not in localized
    assert "Keep the current allocation" not in localized
    assert "Wekelijkse ETF-review" in localized
    assert "Nee / onder herbeoordeling" in localized
    assert "Houd de huidige allocatie" in localized
    validate_dutch_delivery_language(localized, "synthetic_nl_report.html")


def test_validators_import_shared_terminology_contract() -> None:
    assert "Review huidige posities" in term.REQUIRED_DUTCH_MARKERS
    assert "Executive Summary" in term.FORBIDDEN_CLIENT_LABELS
    assert "No" in contract.ACTION_REPLACEMENTS
    assert contract.ACTION_REPLACEMENTS["Under review"] == "Onder herbeoordeling"
    assert "No / under review" in contract.NATIVE_STATE_LABEL_REPLACEMENTS
    assert "No / under review" in contract.NATIVE_STATE_LABEL_FORBIDDEN


def test_sitecustomize_does_not_own_client_surface_aliases() -> None:
    sitecustomize = Path("sitecustomize.py").read_text(encoding="utf-8")
    assert "Dutch client-facing enum/status terminology belongs" in sitecustomize
    assert "No / under review" not in sitecustomize
    assert "Nee / onder herbeoordeling" not in sitecustomize
