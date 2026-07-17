from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

DEFAULT_MAX_ACTIVE_POSITIONS = 8
SHARE_EPSILON = 1e-9


@dataclass(frozen=True)
class PositionCountAssessment:
    passed: bool
    status: str
    max_active_positions: int
    current_count: int
    projected_count: int
    current_tickers: tuple[str, ...]
    projected_tickers: tuple[str, ...]
    opened_tickers: tuple[str, ...]
    closed_tickers: tuple[str, ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in (
            "current_tickers",
            "projected_tickers",
            "opened_tickers",
            "closed_tickers",
            "errors",
            "warnings",
        ):
            payload[key] = list(payload[key])
        return payload


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _shares(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid share quantity: {value!r}") from exc


def _active_index(
    positions: Iterable[dict[str, Any]], *, context: str
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    active: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for row_number, raw in enumerate(positions, start=1):
        row = dict(raw)
        ticker = _ticker(row.get("ticker"))
        try:
            shares = _shares(row.get("shares"))
        except ValueError:
            errors.append(f"{context}:invalid_shares:row_{row_number}:{row.get('shares')!r}")
            continue
        if shares < -SHARE_EPSILON:
            errors.append(f"{context}:negative_shares:{ticker or 'row_' + str(row_number)}:{shares}")
            continue
        if shares <= SHARE_EPSILON:
            continue
        if not ticker:
            errors.append(f"{context}:active_position_missing_ticker:row_{row_number}")
            continue
        if ticker in active:
            errors.append(f"{context}:duplicate_active_ticker:{ticker}")
            continue
        active[ticker] = row
    return active, errors


def active_tickers(positions: Iterable[dict[str, Any]]) -> tuple[str, ...]:
    active, errors = _active_index(positions, context="positions")
    if errors:
        raise ValueError("; ".join(errors))
    return tuple(sorted(active))


def count_active_positions(positions: Iterable[dict[str, Any]]) -> int:
    return len(active_tickers(positions))


def resolve_max_active_positions(runtime_state: dict[str, Any] | None = None) -> int:
    state = runtime_state or {}
    policy = (state.get("rotation_plan") or {}).get("policy") or {}
    raw = policy.get("max_active_positions", DEFAULT_MAX_ACTIVE_POSITIONS)
    try:
        parsed = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"max_active_positions must be an integer, received {raw!r}") from exc
    maximum = int(parsed)
    if maximum <= 0 or abs(parsed - maximum) > SHARE_EPSILON:
        raise ValueError(f"max_active_positions must be a positive integer, received {raw!r}")
    return maximum


def assess_current_positions(
    positions: Iterable[dict[str, Any]], *, max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS
) -> PositionCountAssessment:
    active, errors = _active_index(positions, context="official_state")
    tickers = tuple(sorted(active))
    count = len(tickers)
    warnings: list[str] = []
    if count > max_active_positions:
        warnings.append(f"position_count_close_first:{count}>{max_active_positions}")
        status = "close_first"
    else:
        status = "compliant"
    if errors:
        status = "invalid"
    return PositionCountAssessment(
        passed=not errors,
        status=status,
        max_active_positions=max_active_positions,
        current_count=count,
        projected_count=count,
        current_tickers=tickers,
        projected_tickers=tickers,
        opened_tickers=(),
        closed_tickers=(),
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
    )


def assess_position_count_transition(
    current_positions: Iterable[dict[str, Any]],
    projected_positions: Iterable[dict[str, Any]],
    *,
    max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS,
    trade_intents_present: bool = True,
) -> PositionCountAssessment:
    current, current_errors = _active_index(current_positions, context="current_state")
    projected, projected_errors = _active_index(projected_positions, context="projected_state")
    current_tickers = tuple(sorted(current))
    projected_tickers = tuple(sorted(projected))
    opened = tuple(sorted(set(projected) - set(current)))
    closed = tuple(sorted(set(current) - set(projected)))
    current_count = len(current_tickers)
    projected_count = len(projected_tickers)
    errors = list(current_errors) + list(projected_errors)
    warnings: list[str] = []

    if current_count > max_active_positions:
        warnings.append(f"position_count_close_first:{current_count}>{max_active_positions}")
        if trade_intents_present:
            if opened:
                errors.append("close_first_new_ticker_blocked:" + ",".join(opened))
            if projected_count >= current_count:
                errors.append(
                    f"close_first_trade_must_reduce_active_count:{current_count}->{projected_count}"
                )
    elif projected_count > max_active_positions:
        errors.append(
            f"post_trade_active_position_count_exceeds_limit:{projected_count}>{max_active_positions}"
        )

    if current_count == max_active_positions and opened and not closed:
        errors.append("new_ticker_requires_full_source_close_at_limit:" + ",".join(opened))

    if errors:
        status = "blocked"
    elif projected_count > max_active_positions:
        status = "close_first_progress"
    else:
        status = "compliant"

    return PositionCountAssessment(
        passed=not errors,
        status=status,
        max_active_positions=max_active_positions,
        current_count=current_count,
        projected_count=projected_count,
        current_tickers=current_tickers,
        projected_tickers=projected_tickers,
        opened_tickers=opened,
        closed_tickers=closed,
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
    )


def client_breach_sentence(
    *, current_count: int, max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS, language: str
) -> str:
    if current_count <= max_active_positions:
        return ""
    if language == "nl":
        return (
            f"Maximaal aantal actieve posities: {max_active_positions}. "
            f"Huidig aantal actieve posities: {current_count}. "
            "Er mag geen nieuwe positie worden geopend totdat het aantal is hersteld."
        )
    return (
        f"Maximum active positions: {max_active_positions}. "
        f"Current active positions: {current_count}. "
        "No new position may be opened until the count is restored."
    )
