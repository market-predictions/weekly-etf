"""Runtime-wide safety patches for ETF delivery rendering.

Python imports ``sitecustomize`` automatically at interpreter start when the
repository root is on ``sys.path``. Keep this layer narrow and defensive.
Dutch client-facing enum/status terminology belongs in ``runtime.nl_localization``
and ``runtime.nl_terminology``, not in startup mutation patches.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _install_dutch_equity_curve_label_patch() -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    if getattr(plt.savefig, "_etf_nl_chart_label_patch", False):
        return

    original_savefig = plt.savefig

    def _patched_savefig(*args: Any, **kwargs: Any):
        if args:
            target = args[0]
        else:
            target = kwargs.get("fname")

        try:
            name = Path(str(target)).name.lower()
        except Exception:
            name = ""

        if "weekly_analysis_pro_nl_" in name and "equity_curve" in name:
            ax = plt.gca()
            if ax.get_title() == "Equity Curve (EUR)":
                ax.set_title("Portefeuilleontwikkeling (EUR)")
            if ax.get_xlabel() == "Date":
                ax.set_xlabel("Datum")
            if ax.get_ylabel() == "Portfolio value (EUR)":
                ax.set_ylabel("Portefeuillewaarde (EUR)")

        return original_savefig(*args, **kwargs)

    _patched_savefig._etf_nl_chart_label_patch = True  # type: ignore[attr-defined]
    plt.savefig = _patched_savefig


_install_dutch_equity_curve_label_patch()
