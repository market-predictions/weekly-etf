from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from tools.validate_etf_pdf_visual_contract import _blue_pixel_count


def test_wp17_blue_pixel_count_detects_visible_chart_line(tmp_path) -> None:
    path = tmp_path / "chart.png"
    image = np.ones((120, 220, 3), dtype=float)
    image[60:64, 20:200, 2] = 0.85
    image[60:64, 20:200, 1] = 0.35
    image[60:64, 20:200, 0] = 0.10
    plt.imsave(path, image)

    assert _blue_pixel_count(path) > 500


def test_wp17_blue_pixel_count_rejects_blank_page(tmp_path) -> None:
    path = tmp_path / "blank.png"
    image = np.ones((120, 220, 3), dtype=float)
    plt.imsave(path, image)

    assert _blue_pixel_count(path) == 0
