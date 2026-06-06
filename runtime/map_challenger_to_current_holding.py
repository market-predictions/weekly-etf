from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

EXPLICIT_TARGET_KEYS = (
    "current_holding",
    "replacement_target",
    "replacement_target_ticker",
    "target_holding",
    "incumbent_ticker",
    "may_replace",
    "replaceable_holding",
)

TEXT_MATCH_KEYS = (
    "taxonomy_tag",
    "bucket",
    "lane_name",
    "portfolio_role",
    "role",
    "theme",
    "sleeve",
    "asset_class",
    "exposure",
    "category",
)

STOPWORDS = {
    "etf",
    "fund",
    "lane",
    "current",
    "holding",
    "candidate",
    "challenger",
    "broad",
    "core",
    "the",
    "and",
    "for",
    "with",
}


@dataclass(frozen=True)
class ReplacementMapping:
    current_holding: str
    challenger: str
    mapping_confidence: str
    mapping_reason: str


def _norm_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _tokenize(value: Any) -> set[str]:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return {token for token in text.split() if len(token) > 2 and token not in STOPWORDS}


def _portfolio_positions(portfolio_state: dict[str, Any]) -> list[dict[str, Any]]:
    positions = portfolio_state.get("positions") or portfolio_state.get("holdings") or []
    output: list[dict[str, Any]] = []
    for item in positions:
        if not isinstance(item, dict):
            continue
        ticker = _norm_symbol(item.get("ticker") or item.get("symbol"))
        if not ticker or ticker == "CASH":
            continue
        normalized = dict(item)
        normalized["ticker"] = ticker
        output.append(normalized)
    return output


def _held_tickers(portfolio_state: dict[str, Any]) -> set[str]:
    return {position["ticker"] for position in _portfolio_positions(portfolio_state)}


def _lane_text_tokens(lane: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in TEXT_MATCH_KEYS:
        tokens |= _tokenize(lane.get(key))
    return tokens


def _holding_text_tokens(holding: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in TEXT_MATCH_KEYS + ("name", "description"):
        tokens |= _tokenize(holding.get(key))
    tokens |= _tokenize(holding.get("ticker"))
    return tokens


def _explicit_target(lane: dict[str, Any], held_tickers: set[str]) -> str | None:
    for key in EXPLICIT_TARGET_KEYS:
        target = _norm_symbol(lane.get(key))
        if target and target in held_tickers:
            return target
    return None


def _primary_challenger_symbol(lane: dict[str, Any]) -> str:
    return _norm_symbol(lane.get("primary_etf") or lane.get("challenger") or lane.get("ticker"))


def _score_holding_match(lane: dict[str, Any], holding: dict[str, Any]) -> tuple[float, str]:
    score = 0.0
    reasons: list[str] = []

    for key in ("taxonomy_tag", "bucket", "portfolio_role", "role", "sleeve", "asset_class", "category"):
        lane_value = str(lane.get(key) or "").strip().lower()
        holding_value = str(holding.get(key) or "").strip().lower()
        if lane_value and holding_value and lane_value == holding_value:
            score += 0.45 if key in {"taxonomy_tag", "bucket"} else 0.25
            reasons.append(f"matched {key}")

    lane_tokens = _lane_text_tokens(lane)
    holding_tokens = _holding_text_tokens(holding)
    shared = lane_tokens & holding_tokens
    if shared:
        overlap = len(shared) / max(len(lane_tokens), 1)
        score += min(overlap, 0.35)
        reasons.append("shared tokens: " + ", ".join(sorted(shared)[:5]))

    return score, "; ".join(reasons) if reasons else "no material metadata overlap"


def map_challenger_to_current_holding(
    lane: dict[str, Any],
    portfolio_state: dict[str, Any],
    *,
    minimum_confidence_score: float = 0.20,
) -> ReplacementMapping | None:
    """Return the current holding a challenger may replace, without creating trade authority."""

    challenger = _primary_challenger_symbol(lane)
    if not challenger:
        return None

    held = _held_tickers(portfolio_state)
    if challenger in held:
        return None

    explicit = _explicit_target(lane, held)
    if explicit:
        return ReplacementMapping(
            current_holding=explicit,
            challenger=challenger,
            mapping_confidence="explicit",
            mapping_reason="lane supplied explicit current-holding replacement target",
        )

    holdings = _portfolio_positions(portfolio_state)
    scored: list[tuple[float, str, str]] = []
    for holding in holdings:
        score, reason = _score_holding_match(lane, holding)
        scored.append((score, holding["ticker"], reason))

    if not scored:
        return None

    score, ticker, reason = sorted(scored, key=lambda item: item[0], reverse=True)[0]
    if score < minimum_confidence_score:
        return None

    if score >= 0.60:
        confidence = "high_metadata_match"
    elif score >= 0.35:
        confidence = "medium_metadata_match"
    else:
        confidence = "low_metadata_match"

    return ReplacementMapping(
        current_holding=ticker,
        challenger=challenger,
        mapping_confidence=confidence,
        mapping_reason=reason,
    )


def map_challenger_lanes_to_current_holdings(
    lane_assessment: dict[str, Any],
    portfolio_state: dict[str, Any],
) -> list[ReplacementMapping]:
    mappings: list[ReplacementMapping] = []
    for lane in lane_assessment.get("assessed_lanes", []) or []:
        if not isinstance(lane, dict):
            continue
        if lane.get("challenger") is not True and "challenger" not in str(lane.get("prior_run_status", "")):
            continue
        mapping = map_challenger_to_current_holding(lane, portfolio_state)
        if mapping:
            mappings.append(mapping)
    return mappings
