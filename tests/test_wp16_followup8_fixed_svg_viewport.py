from __future__ import annotations

from runtime.equity_curve_svg_contract import render_equity_curve_svg


def test_dutch_equity_svg_uses_fixed_viewport_not_auto_height() -> None:
    svg = render_equity_curve_svg(
        [
            ("2026-03-28", 100000.0),
            ("2026-04-16", 100671.75),
            ("2026-06-12", 108251.42),
        ],
        language="nl",
    )

    assert "Portefeuillecurve (EUR)" in svg
    assert 'viewBox="0 0 900 420"' in svg
    assert 'width="900"' in svg
    assert 'height="420"' in svg
    assert 'height="auto"' not in svg
