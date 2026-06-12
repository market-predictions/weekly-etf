from __future__ import annotations

import html
import re
from datetime import datetime

EquityPoint = tuple[str, float]

DATA_URI_EQUITY_IMG_RE = re.compile(
    r"<img\b(?=[^>]*\bsrc=[\"']data:image/png;base64,)[^>]*(?:alt=[\"'](?:Equity curve|Portefeuillecurve)[\"'])[^>]*/?>",
    re.IGNORECASE,
)


def render_equity_curve_svg(points: list[EquityPoint], *, language: str = "en") -> str:
    if not points:
        return ""

    is_dutch = language.lower().startswith("nl")
    parsed = [(datetime.strptime(date_str, "%Y-%m-%d"), float(value)) for date_str, value in points]
    min_x = min(date.toordinal() for date, _ in parsed)
    max_x = max(date.toordinal() for date, _ in parsed)
    min_y = min(value for _, value in parsed)
    max_y = max(value for _, value in parsed)
    x_span = max(max_x - min_x, 1)
    y_span = max(max_y - min_y, 1.0)
    pad_y = y_span * 0.08
    min_y -= pad_y
    max_y += pad_y
    y_span = max(max_y - min_y, 1.0)

    width = 900
    height = 420
    left = 86
    right = 28
    top = 52
    bottom = 62
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(date: datetime) -> float:
        return left + ((date.toordinal() - min_x) / x_span) * plot_w

    def sy(value: float) -> float:
        return top + (1.0 - ((value - min_y) / y_span)) * plot_h

    coords = [(sx(date), sy(value)) for date, value in parsed]
    path_d = " ".join(("M" if idx == 0 else "L") + f" {x:.2f} {y:.2f}" for idx, (x, y) in enumerate(coords))

    title = "Portefeuillecurve (EUR)" if is_dutch else "Equity Curve (EUR)"
    y_label = "Portefeuillewaarde (EUR)" if is_dutch else "Portfolio value (EUR)"
    x_label = "Datum" if is_dutch else "Date"

    y_grid = []
    for idx in range(5):
        value = min_y + (y_span * idx / 4)
        y = sy(value)
        label = f"{value:,.0f}".replace(",", "")
        y_grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" stroke="#d9d9d9" stroke-width="1" />'
            f'<text x="{left-10}" y="{y+5:.2f}" text-anchor="end" class="tick">{html.escape(label)}</text>'
        )

    tick_indices = sorted({0, len(parsed) // 3, (2 * len(parsed)) // 3, len(parsed) - 1})
    x_ticks = []
    for idx in tick_indices:
        date, _ = parsed[idx]
        x = sx(date)
        label = date.strftime("%Y-%m-%d")
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{height-bottom}" stroke="#e5e5e5" stroke-width="1" />'
            f'<text x="{x:.2f}" y="{height-bottom+24}" text-anchor="middle" class="tick">{html.escape(label)}</text>'
        )

    circles = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.2" fill="#1f77b4" />' for x, y in coords)
    return f"""
<div class="equity-curve-svg-block" role="img" aria-label="{html.escape(title)}">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto">
<style>
.equity-title {{ font: 700 20px Arial, sans-serif; fill: #111; }}
.axis-label {{ font: 14px Arial, sans-serif; fill: #111; }}
.tick {{ font: 12px Arial, sans-serif; fill: #111; }}
</style>
<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" />
<text x="{width/2:.2f}" y="30" text-anchor="middle" class="equity-title">{html.escape(title)}</text>
{''.join(y_grid)}
{''.join(x_ticks)}
<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#111" stroke-width="1.4" />
<path d="{path_d}" fill="none" stroke="#1f77b4" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
{circles}
<text x="{width/2:.2f}" y="{height-12}" text-anchor="middle" class="axis-label">{html.escape(x_label)}</text>
<text transform="translate(18 {height/2:.2f}) rotate(-90)" text-anchor="middle" class="axis-label">{html.escape(y_label)}</text>
</svg>
</div>
""".strip()


def replace_pdf_equity_png_with_svg(html_text: str, points: list[EquityPoint], *, language: str) -> str:
    if not language.lower().startswith("nl"):
        return html_text
    if "data:image/png;base64," not in html_text:
        return html_text
    svg = render_equity_curve_svg(points, language=language)
    if not svg:
        return html_text
    updated, count = DATA_URI_EQUITY_IMG_RE.subn(svg, html_text, count=1)
    return updated if count else html_text
