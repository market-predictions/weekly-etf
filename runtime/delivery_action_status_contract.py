from __future__ import annotations

from typing import Any


EXECUTION_NONE = {"", "none", "no", "n/a", "not_authorized", "not executed"}


def _num(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def has_actual_execution(state: dict[str, Any]) -> bool:
    changes = state.get("executed_model_changes") or []
    if isinstance(changes, list) and any(
        isinstance(row, dict) and str(row.get("ticker") or "").strip()
        for row in changes
    ):
        return True
    for position in state.get("positions", []) or []:
        if not isinstance(position, dict):
            continue
        if abs(_num(position.get("shares_delta_this_run"))) > 1e-9:
            return True
        action = str(
            position.get("action_executed_this_run") or ""
        ).strip().lower()
        if action not in EXECUTION_NONE:
            return True
    return False


def _no_change_note(language: str) -> str:
    if language == "nl":
        return (
            "Deze run is geen portefeuillewijziging voorgesteld of uitgevoerd; "
            "de officiële posities en gewichten blijven ongewijzigd."
        )
    return (
        "No portfolio change was proposed or executed this run; official "
        "positions and weights remain unchanged."
    )


def _no_replacement_note(language: str) -> str:
    if language == "nl":
        return (
            "Deze run is geen financierbare vervanging voorgesteld. Genoemde "
            "alternatieven blijven uitsluitend onder herbeoordeling."
        )
    return (
        "No fundable replacement was proposed this run. Named alternatives "
        "remain under review only."
    )


def install(module: Any) -> Any:
    if getattr(module, "_zero_execution_status_contract_installed", False):
        return module

    original_post_snapshot = module._post_execution_action_snapshot_html
    original_rotation_plan = module._rotation_plan_html
    original_post_replacement_note = (
        module._post_execution_best_replacements_note_html
    )

    def _post_replacement_note(
        base: Any, state: dict[str, Any], language: str
    ) -> str:
        if not has_actual_execution(state):
            return module.escape(_no_replacement_note(language))
        return original_post_replacement_note(base, state, language)

    def _post_snapshot(
        base: Any, state: dict[str, Any], language: str
    ) -> str:
        html = original_post_snapshot(base, state, language)
        if has_actual_execution(state):
            return html
        labels = module.LABELS[language]
        html = html.replace(
            labels["rotation_reflected_note"],
            _no_change_note(language),
        )
        html = html.replace(
            labels["post_execution_best_replacements_note"],
            _no_replacement_note(language),
        )
        html = html.replace(
            labels["rotation_status"],
            "Status portefeuillebesluit"
            if language == "nl"
            else "Portfolio decision status",
        )
        html = html.replace(
            labels["reflected_replace_reduce"],
            "Vervanging / verlaging"
            if language == "nl"
            else "Replace / reduce",
        )
        return html

    def _rotation_plan(
        base: Any, state: dict[str, Any], language: str
    ) -> str:
        html = original_rotation_plan(base, state, language)
        if has_actual_execution(state):
            return html
        labels = module.LABELS[language]
        return html.replace(
            labels["rotation_reflected_note"],
            _no_change_note(language),
        )

    module._post_execution_best_replacements_note_html = (
        _post_replacement_note
    )
    module._post_execution_action_snapshot_html = _post_snapshot
    module._rotation_plan_html = _rotation_plan
    module._zero_execution_status_contract_installed = True
    return module
