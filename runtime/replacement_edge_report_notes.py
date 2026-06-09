from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.score_replacement_edge import (
    PORTFOLIO_STATE_PATH,
    RS_PATH,
    build_replacement_edge_artifact,
)

MARKER = "ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED"
DEFAULT_LIMIT = 5


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _score_text(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}"


def _edge_text(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def _note(score: Any, language: str = "en") -> str:
    value = _num(score)
    if language == "nl":
        if value is None:
            return "Diagnostische score ontbreekt; reguliere prijs- en relatieve-sterktepoorten blijven leidend."
        if value >= 0.20:
            return "Diagnostisch voordeel zichtbaar; dit geeft geen allocatie-, fundability-, score-, aanbevelings- of uitvoeringsbevoegdheid."
        if value > 0:
            return "Bescheiden diagnostisch voordeel; herhaalbevestiging blijft nodig."
        if value < 0:
            return "Huidige positie blijft diagnostisch sterker; geen vervangingssignaal."
        return "Neutrale diagnostische score; reguliere vervangingspoorten blijven leidend."

    if value is None:
        return "Diagnostic score unavailable; standard pricing and relative-strength gates remain authoritative."
    if value >= 0.20:
        return "Diagnostic edge visible; this grants no allocation, fundability, scoring, recommendation or execution authority."
    if value > 0:
        return "Modest diagnostic edge; repeat confirmation remains required."
    if value < 0:
        return "Current holding remains stronger on the diagnostic edge; no replacement signal."
    return "Neutral diagnostic score; standard replacement gates remain authoritative."


def build_notes_payload_from_paths(
    lane_assessment_path: str | Path,
    relative_strength_path: str | Path = RS_PATH,
    portfolio_state_path: str | Path = PORTFOLIO_STATE_PATH,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Build the WP5 diagnostic payload without granting production authority."""
    payload = build_replacement_edge_artifact(
        Path(lane_assessment_path),
        Path(relative_strength_path),
        Path(portfolio_state_path),
        run_id=run_id,
    )
    payload["report_notes_surface"] = {
        "diagnostic_only": True,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "lane_scoring_authority": False,
        "production_recommendation_authority": False,
        "portfolio_mutation": False,
    }
    return payload


def replacement_edge_notes_markdown(payload: dict[str, Any], language: str = "en", limit: int = DEFAULT_LIMIT) -> str:
    edges = list(payload.get("edges", []) or [])[:limit]
    if language == "nl":
        lines = [
            f"<!-- {MARKER} -->",
            "> Diagnostisch-only: deze notities geven geen allocatie-, fundability-, score-, aanbevelings- of uitvoeringsbevoegdheid.",
            "",
            "| Huidige positie | Alternatief | Diagnostische score | 1m-edge | 3m-edge | Drawdown-edge | Volatiliteitsedge | Niet-autoritatieve notitie |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
        empty = "| Geen | Geen | n.v.t. | n.v.t. | n.v.t. | n.v.t. | n.v.t. | Geen vervangingsedge-diagnostiek beschikbaar deze run. |"
    else:
        lines = [
            f"<!-- {MARKER} -->",
            "> Diagnostic-only: these notes grant no allocation, fundability, scoring, recommendation or execution authority.",
            "",
            "| Current holding | Challenger | Diagnostic score | 1m edge | 3m edge | Drawdown edge | Volatility edge | Non-authoritative note |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
        empty = "| None | None | n/a | n/a | n/a | n/a | n/a | No replacement-edge diagnostics available this run. |"

    if not edges:
        lines.append(empty)
        return "\n".join(lines)

    for edge in edges:
        lines.append(
            f"| {edge.get('current_holding')} | {edge.get('challenger')} | "
            f"{_score_text(edge.get('replacement_edge_score'))} | "
            f"{_edge_text(edge.get('1m_relative_strength_edge'))} | "
            f"{_edge_text(edge.get('3m_relative_strength_edge'))} | "
            f"{_edge_text(edge.get('drawdown_edge'))} | "
            f"{_edge_text(edge.get('volatility_edge'))} | "
            f"{_note(edge.get('replacement_edge_score'), language)} |"
        )
    return "\n".join(lines)
