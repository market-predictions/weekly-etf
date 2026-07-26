"""Runtime synthesis and rendering helpers for ETF reports."""

from __future__ import annotations

import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    if name == "render_cockpit_front_page":
        module = importlib.import_module(
            ".render_cockpit_front_page", __name__
        )
        from runtime.cockpit_action_surface_contract import (
            install as install_cockpit_action_surface,
        )
        from runtime.delivery_action_status_contract import (
            install as install_delivery_action_status,
        )

        try:
            delivery_module = importlib.import_module(
                ".delivery_html_overrides", __name__
            )
            install_delivery_action_status(delivery_module)
        except Exception:
            pass
        return install_cockpit_action_surface(module)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
