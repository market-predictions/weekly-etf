from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

EquityPoint = tuple[str, float]


def _as_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def render_equity_curve_png(points: Iterable[EquityPoint], chart_path: Path, *, language: str = "en") -> Path:
    rows = list(points)
    if not rows:
        raise RuntimeError("Equity curve PNG render failed: no points supplied.")

    is_dutch = language.lower().startswith("nl")
    dates = [_as_datetime(date_str) for date_str, _ in rows]
    values = [float(value) for _, value in rows]

    fig, ax = plt.subplots(figsize=(8.8, 3.7), facecolor="white", constrained_layout=False)
    ax.set_facecolor("white")
    ax.plot(dates, values, marker="o", linewidth=2.2)
    ax.set_title("Portefeuillecurve (EUR)" if is_dutch else "Equity Curve (EUR)", pad=10)
    ax.set_xlabel("Datum" if is_dutch else "Date")
    ax.set_ylabel("Portefeuillewaarde (EUR)" if is_dutch else "Portfolio value (EUR)")
    ax.grid(True, alpha=0.28)
    ax.set_axisbelow(True)

    # Use explicit subplot margins instead of tight_layout. The previous Dutch
    # path could be squeezed into a tiny top band with the rest of the PNG
    # transparent. Fixed margins make the rendered image deterministic across
    # English and Dutch labels.
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.18, top=0.86)
    fig.savefig(chart_path, dpi=180, facecolor="white", edgecolor="white", transparent=False)
    plt.close(fig)

    validate_equity_curve_png(chart_path)
    return chart_path


def validate_equity_curve_png(chart_path: Path) -> None:
    if not chart_path.exists() or chart_path.stat().st_size <= 0:
        raise RuntimeError(f"Equity curve PNG render failed: missing or empty file: {chart_path}")

    image = mpimg.imread(chart_path)
    if image.ndim != 3 or image.shape[0] < 240 or image.shape[1] < 800:
        raise RuntimeError(f"Equity curve PNG render failed: unexpected image shape: {getattr(image, 'shape', None)}")

    if image.max() > 1.0:
        image = image / 255.0

    height = image.shape[0]
    lower = image[height // 3 :, :, :]

    if image.shape[2] >= 4:
        alpha_mean = float(lower[:, :, 3].mean())
        if alpha_mean < 0.98:
            raise RuntimeError(f"Equity curve PNG render failed: lower image area is transparent/blank (alpha_mean={alpha_mean:.3f}).")
        rgb = lower[:, :, :3]
    else:
        rgb = lower[:, :, :3]

    brightness = float(rgb.mean())
    if brightness < 0.65:
        raise RuntimeError(f"Equity curve PNG render failed: lower image area is too dark/blank (brightness={brightness:.3f}).")

    # The lower two-thirds should contain at least some grid/axis/line pixels.
    non_white = ((rgb < 0.96).any(axis=2)).mean()
    if float(non_white) < 0.005:
        raise RuntimeError(f"Equity curve PNG render failed: lower image area has too little visible chart content (non_white={float(non_white):.4f}).")
