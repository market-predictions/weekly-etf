"""Runtime-wide safety patches for ETF delivery rendering.

Python imports ``sitecustomize`` automatically at interpreter start when the
repository root is on ``sys.path``. Keep these patches narrow and defensive:
- localize the known Dutch ETF equity-curve labels for the Dutch companion PNG
- add missing Dutch replacement-duel phrase variants created by the runtime
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


def _install_replacement_duel_localization_patch() -> None:
    try:
        from runtime import nl_localization as nl
    except Exception:
        return

    decision_updates = {
        "Not fundable - close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
        "Not fundable - close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig",
        "Not fundable - valuation-grade challenger pricing required.": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist.",
        "Not fundable - valuation-grade challenger pricing required": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist",
        "Priced valuation-grade, but direct RS duel incomplete.": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
        "Priced valuation-grade, but direct RS duel incomplete": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
        "Replacement trigger watch - challenger leading over 3m.": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
        "Replacement trigger watch - challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
    }
    trigger_updates = {
        "Upgrade challenger to valuation-grade pricing before any funding decision.": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit.",
        "Upgrade challenger to valuation-grade pricing before any funding decision": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit",
    }

    nl.DECISION_TRANSLATIONS.update(decision_updates)
    nl.TRIGGER_TRANSLATIONS.update(trigger_updates)


_install_dutch_equity_curve_label_patch()
_install_replacement_duel_localization_patch()
