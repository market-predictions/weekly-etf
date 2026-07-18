from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.additive_cockpit_front_page import (
    FRONT_PAGE_MARKER,
    STYLE_ID,
    inject_additive_cockpit_front_page,
    render_delivery_cockpit_front_page_fragment,
)


def _fixture_output(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    for relative in ("runtime", "macro", "pricing", "run_manifests"):
        (output / relative).mkdir(parents=True, exist_ok=True)
    state = {
        "report_date": "2026-07-16",
        "requested_close_date": "2026-07-16",
        "portfolio": {"cash_eur": 2534.36, "total_portfolio_value_eur": 107117.94},
        "fx_basis": {"rate": 1.1443},
        "positions": [
            {"ticker": "SMH", "current_weight_pct": 27.38, "market_value_eur": 29333.21},
            {"ticker": "IEFA", "current_weight_pct": 24.63, "market_value_eur": 26381.94},
            {"ticker": "CIBR", "current_weight_pct": 18.97, "market_value_eur": 20316.32},
        ],
        "source_files": {"macro_policy_pack": "output/macro/latest.json"},
    }
    state_path = output / "runtime" / "fixture_state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    (output / "runtime" / "latest_etf_report_state_path.txt").write_text(str(state_path), encoding="utf-8")
    (output / "macro" / "latest.json").write_text(
        json.dumps({"regime": {"current": "Risk-on growth", "confidence": 0.66}}),
        encoding="utf-8",
    )
    (output / "etf_valuation_history.csv").write_text(
        "date,nav_eur\n2026-03-28,100000.00\n2026-06-01,110321.58\n2026-07-16,107117.94\n",
        encoding="utf-8",
    )
    (output / "pricing" / "latest_price_audit_path.txt").write_text(
        "output/pricing/fixture.json", encoding="utf-8"
    )
    (output / "pricing" / "fixture.json").write_text("{}", encoding="utf-8")
    (output / "run_manifests" / "latest_weekly_etf_run_manifest_path.txt").write_text(
        "output/run_manifests/fixture.json", encoding="utf-8"
    )
    (output / "run_manifests" / "fixture.json").write_text("{}", encoding="utf-8")
    return output


def _required_inline_nodes(soup: BeautifulSoup) -> list[str]:
    selectors = [
        "section.etf-cockpit-page",
        ".etf-cockpit-inner",
        ".etf-cockpit-header",
        ".etf-cockpit-kicker",
        ".etf-cockpit-mast",
        ".etf-cockpit-strap",
        ".etf-cockpit-section-title",
        ".etf-cockpit-lede",
        ".etf-cockpit-card",
        ".etf-cockpit-performance",
        ".etf-cockpit-metric",
        ".etf-cockpit-discipline",
        ".etf-cockpit-trigger",
        ".etf-cockpit-evidence",
        ".etf-cockpit-footer",
    ]
    missing: list[str] = []
    for selector in selectors:
        node = soup.select_one(selector)
        if node is None or not str(node.get("style") or "").strip():
            missing.append(selector)
    return missing


def test_email_fragment_is_inline_and_table_based(tmp_path: Path) -> None:
    fragment = render_delivery_cockpit_front_page_fragment(
        output_dir=_fixture_output(tmp_path), language="en", render_mode="email"
    )
    soup = BeautifulSoup(fragment.html, "html.parser")
    assert fragment.css == ""
    assert FRONT_PAGE_MARKER in fragment.html
    assert not soup.find_all("style")
    assert not _required_inline_nodes(soup)
    assert len(soup.find_all("table", attrs={"role": "presentation"})) >= 8
    lowered = fragment.html.lower().replace(" ", "")
    assert "display:grid" not in lowered
    assert "display:flex" not in lowered
    assert "<svg" not in lowered
    assert "etf-cockpit-email-sparkline" in fragment.html


def test_email_front_page_survives_head_style_removal(tmp_path: Path) -> None:
    classic = (
        "<!doctype html><html><head><style>.classic{color:#123456}</style></head>"
        "<body><main class='classic'><h1>Classic report body</h1></main></body></html>"
    )
    result = inject_additive_cockpit_front_page(
        classic,
        language="en",
        output_dir=_fixture_output(tmp_path),
        render_mode="email",
        feature_value="enabled",
    )
    soup = BeautifulSoup(result.html, "html.parser")
    for node in soup.find_all("style"):
        node.decompose()
    assert not _required_inline_nodes(soup)
    assert soup.select_one('section[data-cockpit-front-page="delivery"]') is not None
    assert soup.select_one("main.classic") is not None
    assert "Classic report body" in soup.get_text(" ", strip=True)


def test_pdf_fragment_retains_current_class_based_surface(tmp_path: Path) -> None:
    fragment = render_delivery_cockpit_front_page_fragment(
        output_dir=_fixture_output(tmp_path), language="en", render_mode="pdf"
    )
    assert STYLE_ID in fragment.css
    assert "@media print" in fragment.css
    assert '<svg class="spark"' in fragment.html
    assert "etf-cockpit-email-sparkline" not in fragment.html


def test_dutch_email_fragment_is_inline_and_client_safe(tmp_path: Path) -> None:
    fragment = render_delivery_cockpit_front_page_fragment(
        output_dir=_fixture_output(tmp_path), language="nl", render_mode="email"
    )
    soup = BeautifulSoup(fragment.html, "html.parser")
    assert not _required_inline_nodes(soup)
    text = soup.get_text(" ", strip=True)
    assert "Rapportvoorpagina" in text
    assert "Bronnen en controle" in text
    assert "Volledige analyse en bewijslaag volgen hierna" in text
