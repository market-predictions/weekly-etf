from __future__ import annotations

from runtime.equity_curve_svg_contract import render_equity_curve_svg, replace_pdf_equity_png_with_svg

POINTS = [
    ("2026-03-28", 100000.00),
    ("2026-04-16", 100671.75),
    ("2026-05-27", 109387.17),
    ("2026-06-11", 107747.59),
]


def test_wp16_followup7_renders_dutch_equity_curve_as_svg() -> None:
    svg = render_equity_curve_svg(POINTS, language="nl")

    assert "<svg" in svg
    assert "Portefeuillecurve (EUR)" in svg
    assert "Portefeuillewaarde (EUR)" in svg
    assert "path d=" in svg


def test_wp16_followup7_replaces_only_dutch_pdf_data_uri_image() -> None:
    html = '<div><img src="data:image/png;base64,abc123" alt="Equity curve" /></div>'

    replaced = replace_pdf_equity_png_with_svg(html, POINTS, language="nl")

    assert "data:image/png;base64" not in replaced
    assert "<svg" in replaced
    assert "Portefeuillecurve (EUR)" in replaced


def test_wp16_followup7_keeps_email_cid_image_unchanged() -> None:
    html = '<div><img src="cid:equitycurve" alt="Equity curve" /></div>'

    assert replace_pdf_equity_png_with_svg(html, POINTS, language="nl") == html


def test_wp16_followup7_keeps_english_pdf_image_unchanged() -> None:
    html = '<div><img src="data:image/png;base64,abc123" alt="Equity curve" /></div>'

    assert replace_pdf_equity_png_with_svg(html, POINTS, language="en") == html
