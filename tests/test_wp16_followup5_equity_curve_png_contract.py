from __future__ import annotations

from runtime.equity_curve_png_contract import render_equity_curve_png, validate_equity_curve_png

POINTS = [
    ("2026-03-28", 100000.00),
    ("2026-04-16", 100671.75),
    ("2026-04-20", 102026.08),
    ("2026-04-24", 104477.54),
    ("2026-04-29", 101854.68),
    ("2026-05-04", 102636.85),
    ("2026-05-05", 103536.96),
    ("2026-05-27", 109387.17),
    ("2026-05-28", 110032.93),
    ("2026-05-29", 109964.97),
    ("2026-06-01", 110321.58),
    ("2026-06-02", 112376.10),
    ("2026-06-03", 111596.95),
    ("2026-06-04", 111105.47),
    ("2026-06-09", 106246.36),
    ("2026-06-10", 103994.26),
    ("2026-06-11", 107747.59),
]


def test_wp16_followup5_renders_dutch_equity_curve_png_without_blank_lower_area(tmp_path) -> None:
    path = tmp_path / "nl_equity_curve.png"

    render_equity_curve_png(POINTS, path, language="nl")

    validate_equity_curve_png(path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_wp16_followup5_renders_english_equity_curve_png_without_blank_lower_area(tmp_path) -> None:
    path = tmp_path / "en_equity_curve.png"

    render_equity_curve_png(POINTS, path, language="en")

    validate_equity_curve_png(path)
    assert path.exists()
    assert path.stat().st_size > 0
