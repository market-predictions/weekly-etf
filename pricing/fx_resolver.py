from __future__ import annotations

from .clients import twelve_data
from .models import FXResult


def resolve_fx(requested_date: str) -> FXResult:
    return twelve_data.fetch_eurusd(requested_date)
