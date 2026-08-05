from __future__ import annotations

"""Guarded ticker-link entrypoint with narrow historical replay cleanup.

Imported callers receive the preserved implementation. Direct execution applies
exact replay-state compatibility at the portfolio-integrity transformation
boundary, then invokes the unchanged linker and fail-closed validator.
"""

import os
import sys
from pathlib import Path

import runtime.link_runtime_report_tickers_legacy as _legacy


if __name__ != "__main__":
    sys.modules[__name__] = _legacy
else:
    import runtime.report_portfolio_integrity_contract as _integrity
    from runtime.executed_replay_state_contract import executed_model_change_present
    from runtime.nonheld_watchlist_replay_cleanup import (
        normalize_nonheld_watchlist_file,
        normalize_nonheld_watchlist_text,
    )

    original_normalize_radar_rows = _integrity._normalize_radar_rows
    original_current_execution_present = _integrity._current_execution_present

    def normalize_radar_rows_with_nonheld_boundary(
        text: str,
        state: dict,
        language: str,
    ) -> str:
        transformed = original_normalize_radar_rows(text, state, language)
        return normalize_nonheld_watchlist_text(transformed, language)

    def current_execution_present_with_replay_contract(state: dict) -> bool:
        return original_current_execution_present(state) or executed_model_change_present(state)

    _integrity._normalize_radar_rows = normalize_radar_rows_with_nonheld_boundary
    _integrity._current_execution_present = current_execution_present_with_replay_contract

    candidates: list[tuple[Path, str]] = []
    explicit_en = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "").strip()
    explicit_nl = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", "").strip()
    if explicit_en:
        candidates.append((Path(explicit_en), "en"))
    if explicit_nl:
        candidates.append((Path(explicit_nl), "nl"))

    if not candidates:
        output = Path("output")
        en_reports = sorted(output.glob("weekly_analysis_pro_[0-9]*.md"))
        nl_reports = sorted(output.glob("weekly_analysis_pro_nl_[0-9]*.md"))
        if en_reports:
            candidates.append((en_reports[-1], "en"))
        if nl_reports:
            candidates.append((nl_reports[-1], "nl"))

    for path, language in candidates:
        if path.is_file():
            normalize_nonheld_watchlist_file(path, language)

    _legacy.main()
