from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REVIEW_DIR_NAME = "cockpit_review"
SCHEMA_VERSION = "cockpit_side_by_side_review_v2"
REVIEW_TYPE = "evidence_based_side_by_side_preview_only"
REVIEW_DIMENSIONS = [
    "readability",
    "density",
    "visual_hierarchy",
    "decision_clarity",
    "executed_action_clarity",
    "current_weight_accuracy",
    "performance_risk_accuracy",
    "trust_provenance_clarity",
    "bilingual_semantic_parity",
    "premium_look_and_feel",
    "audit_evidence_preservation",
]
NEXT_PACKAGE = "WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT"


@dataclass(frozen=True)
class BuiltSideBySideReview:
    token: str
    metadata_path: Path
    english_markdown_path: Path
    english_html_path: Path
    dutch_markdown_path: Path
    dutch_html_path: Path


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self._parts.append(text)

    def text(self) -> str:
        return "\n".join(self._parts)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".html":
        parser = _TextExtractor()
        parser.feed(text)
        return parser.text()
    return text


def _resolve_output_relative(path: Path, output_dir: Path) -> Path:
    if path.is_absolute():
        return path
    if str(path).startswith("output/"):
        return output_dir.parent / path
    return output_dir / path


def _load_runtime_state(output_dir: Path) -> tuple[dict[str, Any], Path | None]:
    pointer = output_dir / "runtime" / "latest_etf_report_state_path.txt"
    if not pointer.exists():
        return {}, None
    target = pointer.read_text(encoding="utf-8").strip()
    if not target:
        return {}, None
    path = _resolve_output_relative(Path(target), output_dir)
    return _read_json(path), path


def _token_from_state(state: dict[str, Any]) -> str | None:
    for key in ("report_date", "requested_close_date"):
        value = str(state.get(key) or "").strip()
        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value):
            return value.replace("-", "")[2:]
    return None


def _token_from_reports(output_dir: Path) -> str | None:
    tokens: list[str] = []
    pattern = re.compile(r"^weekly_analysis_pro(?:_nl)?_(\d{6})(?:_\d{2})?(?:_delivery)?\.(?:md|html)$")
    for path in output_dir.glob("weekly_analysis_pro*"):
        if "cockpit" in path.name or "_clean" in path.name:
            continue
        match = pattern.match(path.name)
        if match:
            tokens.append(match.group(1))
    return sorted(tokens)[-1] if tokens else None


def _report_token(output_dir: Path, explicit_token: str | None = None) -> str:
    if explicit_token:
        return explicit_token
    state, _ = _load_runtime_state(output_dir)
    state_token = _token_from_state(state)
    if state_token:
        return state_token
    report_token = _token_from_reports(output_dir)
    return report_token or "unknown"


def _relative(path: Path | None, output_dir: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(output_dir.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _sha256(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _variant_sequence(name: str, token: str, language: str) -> int | None:
    prefix = "weekly_analysis_pro_nl" if language == "nl" else "weekly_analysis_pro"
    match = re.fullmatch(rf"{re.escape(prefix)}_{re.escape(token)}(?:_(\d{{2}}))?(?:_delivery)?\.(?:md|html)", name)
    if not match:
        return None
    return int(match.group(1) or 0)


def _select_classic_sources(output_dir: Path, token: str, language: str) -> dict[str, Path | None]:
    prefix = "weekly_analysis_pro_nl" if language == "nl" else "weekly_analysis_pro"
    candidates: list[tuple[int, Path]] = []
    for path in output_dir.glob(f"{prefix}_{token}*"):
        if "_clean" in path.name or "cockpit" in path.name:
            continue
        sequence = _variant_sequence(path.name, token, language)
        if sequence is not None:
            candidates.append((sequence, path))
    if not candidates:
        return {"markdown": None, "html": None}
    selected_sequence = max(sequence for sequence, _ in candidates)
    selected = [path for sequence, path in candidates if sequence == selected_sequence]
    markdown = next((path for path in selected if path.suffix == ".md"), None)
    html = next((path for path in selected if path.name.endswith("_delivery.html")), None)
    return {"markdown": markdown, "html": html}


def _preview_sequence(name: str, token: str, language: str) -> int | None:
    prefix = "weekly_analysis_pro_nl_cockpit" if language == "nl" else "weekly_analysis_pro_cockpit"
    match = re.fullmatch(rf"{re.escape(prefix)}_{re.escape(token)}_(\d{{2}})\.html", name)
    return int(match.group(1)) if match else None


def _select_cockpit_source(output_dir: Path, token: str, language: str) -> Path | None:
    preview_dir = output_dir / "cockpit_preview"
    if not preview_dir.exists():
        return None
    candidates: list[tuple[int, Path]] = []
    for path in preview_dir.glob("*.html"):
        sequence = _preview_sequence(path.name, token, language)
        if sequence is not None:
            candidates.append((sequence, path))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result


def _position_weight(position: dict[str, Any]) -> float:
    for key in ("current_weight_pct", "target_weight_pct", "previous_weight_pct", "weight_inherited_pct"):
        if key in position and position[key] not in (None, ""):
            return _float(position[key])
    return 0.0


def _previous_weight(position: dict[str, Any]) -> float:
    for key in ("previous_weight_pct", "weight_inherited_pct", "current_weight_pct"):
        if key in position and position[key] not in (None, ""):
            return _float(position[key])
    return 0.0


def _positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in state.get("positions", []) if str(row.get("ticker") or "").strip()]


def _executed_actions(state: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for position in _positions(state):
        delta = _float(position.get("shares_delta_this_run"))
        action = str(position.get("action_executed_this_run") or "").strip().lower()
        if abs(delta) <= 1e-9 and action in {"", "none", "no", "n/a"}:
            continue
        direction = "reduce" if delta < 0 or action in {"sell", "reduce", "reduced", "close", "closed"} else "add" if delta > 0 or action in {"buy", "add", "added", "open", "opened"} else "adjust"
        actions.append(
            {
                "ticker": str(position.get("ticker") or "-").upper(),
                "direction": direction,
                "previous_weight_pct": _previous_weight(position),
                "current_weight_pct": _position_weight(position),
            }
        )
    return actions


def _expected_action_labels(state: dict[str, Any], language: str) -> list[str]:
    verbs = {
        "en": {"reduce": "reduced", "add": "added", "adjust": "adjusted"},
        "nl": {"reduce": "afgebouwd", "add": "toegevoegd", "adjust": "aangepast"},
    }
    return [f"{row['ticker']} {verbs[language][row['direction']]}" for row in _executed_actions(state)]


def _format_pct(value: float, language: str) -> str:
    text = f"{value:.1f}%"
    return text.replace(".", ",") if language == "nl" else text


def _expected_weight_transitions(state: dict[str, Any], language: str) -> list[str]:
    return [
        f"{row['ticker']} {_format_pct(row['previous_weight_pct'], language)} → {_format_pct(row['current_weight_pct'], language)}"
        for row in _executed_actions(state)
    ]


def _largest_position(state: dict[str, Any]) -> tuple[str, float]:
    positions = _positions(state)
    if not positions:
        return "-", 0.0
    row = max(positions, key=_position_weight)
    return str(row.get("ticker") or "-").upper(), _position_weight(row)


def _total_nav(state: dict[str, Any]) -> float:
    portfolio = state.get("portfolio") or {}
    explicit = _float(portfolio.get("total_portfolio_value_eur"))
    if explicit:
        return explicit
    return _float(portfolio.get("cash_eur")) + sum(_float(row.get("market_value_eur")) for row in _positions(state))


def _valuation_start(output_dir: Path) -> float:
    path = output_dir / "etf_valuation_history.csv"
    if not path.exists():
        return 100000.0
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split(",")
        if len(parts) >= 2:
            value = _float(parts[1])
            if value > 0:
                return value
    return 100000.0


def _fmt_nav(nav: float, language: str) -> str:
    text = f"{nav:,.0f}"
    return f"€{text.replace(',', '.') if language == 'nl' else text}"


def _fmt_return(value: float, language: str) -> str:
    text = f"{value:+.1f}%"
    return text.replace(".", ",") if language == "nl" else text


def _pointer_target(output_dir: Path, relative_pointer: str) -> Path | None:
    pointer = output_dir / relative_pointer
    if not pointer.exists():
        return None
    target = pointer.read_text(encoding="utf-8").strip()
    return _resolve_output_relative(Path(target), output_dir) if target else None


def _contains_all(text: str, values: list[str]) -> bool:
    lower = text.lower()
    return all(value.lower() in lower for value in values)


def _finding(
    dimension: str,
    status: str,
    classic_observation: str,
    cockpit_observation: str,
    evidence: list[str],
    required_fix: str,
    blocking: bool = False,
) -> dict[str, Any]:
    return {
        "dimension": dimension,
        "status": status,
        "classic_observation": classic_observation,
        "cockpit_observation": cockpit_observation,
        "evidence": evidence,
        "required_fix": required_fix,
        "blocking": blocking,
    }


def _analyze(
    output_dir: Path,
    token: str,
    state: dict[str, Any],
    state_path: Path | None,
    selected: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    classic_en = _read_text(selected["classic"]["en"]["markdown"] or selected["classic"]["en"]["html"])
    classic_nl = _read_text(selected["classic"]["nl"]["markdown"] or selected["classic"]["nl"]["html"])
    cockpit_en = _read_text(selected["cockpit"]["en"])
    cockpit_nl = _read_text(selected["cockpit"]["nl"])

    action_en = _expected_action_labels(state, "en")
    action_nl = _expected_action_labels(state, "nl")
    transitions_en = _expected_weight_transitions(state, "en")
    transitions_nl = _expected_weight_transitions(state, "nl")
    largest_ticker, largest_weight = _largest_position(state)
    nav = _total_nav(state)
    start = _valuation_start(output_dir)
    since = (nav / start - 1.0) * 100.0 if start else 0.0

    findings: list[dict[str, Any]] = []

    classic_length = max(len(classic_en), 1)
    cockpit_length = len(cockpit_en)
    readability_pass = bool(classic_en and cockpit_en and cockpit_length < classic_length)
    findings.append(
        _finding(
            "readability",
            "pass" if readability_pass else "fail",
            f"The selected classic report contains {len(classic_en):,} review characters and preserves full context.",
            f"The cockpit contains {cockpit_length:,} review characters and is {'faster' if readability_pass else 'not demonstrably faster'} to scan.",
            [f"classic_en_chars={len(classic_en)}", f"cockpit_en_chars={cockpit_length}"],
            "Keep the cockpit concise while retaining the selected classic report as the evidence layer." if readability_pass else "Restore a materially more concise cockpit entry surface.",
            blocking=not readability_pass,
        )
    )

    density_ratio = cockpit_length / classic_length
    density_status = "pass" if density_ratio <= 0.35 else "partial" if density_ratio <= 0.55 else "fail"
    findings.append(
        _finding(
            "density",
            density_status,
            "The classic report is intentionally information-dense.",
            f"Cockpit-to-classic text ratio is {density_ratio:.2f}.",
            [f"density_ratio={density_ratio:.4f}"],
            "Preserve the lower-density front-page role; do not move audit tables into the cockpit.",
            blocking=density_status == "fail",
        )
    )

    hierarchy_markers = ["data-cockpit-front-page", "class=\"card\"", "class=\"metrics\"", "class=\"discipline\""]
    cockpit_html = selected["cockpit"]["en"].read_text(encoding="utf-8") if selected["cockpit"]["en"] else ""
    hierarchy_pass = all(marker in cockpit_html for marker in hierarchy_markers)
    findings.append(
        _finding(
            "visual_hierarchy",
            "pass" if hierarchy_pass else "fail",
            "The classic report remains report-led and section-dense.",
            "The cockpit uses a masthead, decision cards, performance metrics and a separate discipline block." if hierarchy_pass else "Required visual hierarchy markers are incomplete.",
            hierarchy_markers,
            "Preserve the existing cockpit hierarchy." if hierarchy_pass else "Restore the required masthead, cards, metrics and discipline hierarchy.",
            blocking=not hierarchy_pass,
        )
    )

    action_present = _contains_all(cockpit_en, action_en) and _contains_all(cockpit_nl, action_nl)
    classic_trigger = "next action trigger" in classic_en.lower() and "trigger voor volgende actie" in classic_nl.lower()
    cockpit_trigger = "next action trigger" in cockpit_en.lower() and "trigger voor volgende actie" in cockpit_nl.lower()
    summary_contradiction = bool(action_en) and (
        "discipline ahead of activity" in cockpit_en.lower() or "discipline boven activiteit" in cockpit_nl.lower()
    )
    decision_status = "pass" if action_present and cockpit_trigger and not summary_contradiction else "partial" if action_present else "fail"
    findings.append(
        _finding(
            "decision_clarity",
            decision_status,
            f"The classic decision cockpit includes the executed action and an explicit next-action trigger: {classic_trigger}.",
            "The cockpit shows the executed action, but its summary contradicts the presence of activity and it lacks a dedicated next-action trigger." if decision_status == "partial" else "The cockpit decision surface is aligned with the classic report." if decision_status == "pass" else "The cockpit does not expose the executed decision clearly.",
            [f"action_present={action_present}", f"classic_trigger={classic_trigger}", f"cockpit_trigger={cockpit_trigger}", f"summary_contradiction={summary_contradiction}"],
            "Replace the activity-contradicting summary and add a concise, explicit next-action trigger derived from current state." if decision_status != "pass" else "No change required.",
            blocking=decision_status != "pass",
        )
    )

    transitions_present = _contains_all(cockpit_en, transitions_en) and _contains_all(cockpit_nl, transitions_nl)
    classic_action_present = _contains_all(classic_en, [row["ticker"] for row in _executed_actions(state)]) and _contains_all(classic_nl, [row["ticker"] for row in _executed_actions(state)])
    action_status = "pass" if action_present and transitions_present and classic_action_present else "fail"
    findings.append(
        _finding(
            "executed_action_clarity",
            action_status,
            "The classic report names the guarded URNM-to-XBI rotation and the consumed rotation budget.",
            "The cockpit names each executed direction and shows the pre/post weights." if action_status == "pass" else "The cockpit action or weight transition does not match runtime authority.",
            action_en + transitions_en + action_nl + transitions_nl,
            "Keep the runtime-derived bilingual action contract." if action_status == "pass" else "Repair action wording and weight transitions from runtime state.",
            blocking=action_status != "pass",
        )
    )

    weight_terms_en = [largest_ticker, _format_pct(largest_weight, "en")]
    weight_terms_nl = [largest_ticker, _format_pct(largest_weight, "nl")]
    weight_pass = _contains_all(cockpit_en, weight_terms_en + transitions_en) and _contains_all(cockpit_nl, weight_terms_nl + transitions_nl)
    findings.append(
        _finding(
            "current_weight_accuracy",
            "pass" if weight_pass else "fail",
            f"The classic report and runtime state identify {largest_ticker} as the largest position and preserve current post-execution weights.",
            f"The cockpit shows {largest_ticker} at {_format_pct(largest_weight, 'en')} and the current executed transitions." if weight_pass else "The cockpit weight surface does not fully match runtime state.",
            weight_terms_en + transitions_en,
            "Continue using current-over-previous authority precedence." if weight_pass else "Correct the current weight presentation from runtime state.",
            blocking=not weight_pass,
        )
    )

    performance_terms_en = [_fmt_nav(nav, "en"), _fmt_return(since, "en")]
    performance_terms_nl = [_fmt_nav(nav, "nl"), _fmt_return(since, "nl")]
    performance_pass = _contains_all(cockpit_en, performance_terms_en) and _contains_all(cockpit_nl, performance_terms_nl) and f"{nav:.2f}" in classic_en
    findings.append(
        _finding(
            "performance_risk_accuracy",
            "pass" if performance_pass else "fail",
            f"The classic report records NAV {nav:.2f} EUR and since-inception return {since:.2f}%.",
            f"The cockpit displays {_fmt_nav(nav, 'en')} and {_fmt_return(since, 'en')} with the current largest-position risk." if performance_pass else "The cockpit performance summary does not reconcile to the current state and valuation history.",
            performance_terms_en + performance_terms_nl,
            "Keep NAV and return derived from runtime state plus valuation history." if performance_pass else "Reconcile performance metrics to runtime state and valuation history.",
            blocking=not performance_pass,
        )
    )

    pricing_path = _pointer_target(output_dir, "pricing/latest_price_audit_path.txt")
    manifest_path = _pointer_target(output_dir, "run_manifests/latest_weekly_etf_run_manifest_path.txt")
    provenance_terms_en = [
        _relative(state_path, output_dir) or "",
        _relative(pricing_path, output_dir) or "",
        _relative(manifest_path, output_dir) or "",
        "No delivery claim",
        "Not promoted to production",
    ]
    provenance_terms_nl = [
        _relative(state_path, output_dir) or "",
        _relative(pricing_path, output_dir) or "",
        _relative(manifest_path, output_dir) or "",
        "Geen deliveryclaim",
        "Niet gepromoveerd naar productie",
    ]
    provenance_pass = _contains_all(cockpit_en, provenance_terms_en) and _contains_all(cockpit_nl, provenance_terms_nl)
    findings.append(
        _finding(
            "trust_provenance_clarity",
            "pass" if provenance_pass else "fail",
            "The classic report keeps the full pricing, holdings and audit context.",
            "The WP07 provenance strip now exposes runtime state, pricing audit, run manifest, no-delivery and no-promotion status." if provenance_pass else "The cockpit provenance strip is incomplete.",
            provenance_terms_en,
            "Treat the WP07 provenance requirement as closed; preserve the visible evidence strip." if provenance_pass else "Restore complete visible source and status provenance.",
            blocking=not provenance_pass,
        )
    )

    dutch_punctuation_bug = "disciplinepoorten vrijgeven," in cockpit_nl.lower()
    hybrid_labels = [term for term in ("pricing-audit referentie", "macro-pack referentie", "run-manifest referentie", "deliveryclaim") if term in cockpit_nl.lower()]
    parity_core = action_present and transitions_present and _contains_all(cockpit_nl, performance_terms_nl)
    parity_status = "pass" if parity_core and not dutch_punctuation_bug and not hybrid_labels else "partial" if parity_core else "fail"
    findings.append(
        _finding(
            "bilingual_semantic_parity",
            parity_status,
            "The English and Dutch classic reports are companion surfaces from the same report state.",
            "Core action, weights and performance are parallel, but Dutch punctuation and hybrid provenance labels still require cleanup." if parity_status == "partial" else "English and Dutch cockpit surfaces are semantically parallel." if parity_status == "pass" else "The bilingual cockpit surfaces diverge on core facts.",
            [f"core_parity={parity_core}", f"dutch_punctuation_bug={dutch_punctuation_bug}", f"hybrid_labels={','.join(hybrid_labels) or 'none'}"],
            "Fix the Dutch sentence terminator and replace hybrid provenance labels with natural Dutch client-facing terms." if parity_status != "pass" else "No change required.",
            blocking=parity_status != "pass",
        )
    )

    premium_status = "pass" if hierarchy_pass and readability_pass and parity_status == "pass" else "partial" if hierarchy_pass else "fail"
    findings.append(
        _finding(
            "premium_look_and_feel",
            premium_status,
            "The classic report is client-grade but text-heavy.",
            "The cockpit has a strong premium front-page hierarchy, but copy and Dutch-language polish prevent a clean client-grade claim." if premium_status == "partial" else "The cockpit presents a coherent premium entry surface." if premium_status == "pass" else "The cockpit lacks the required premium hierarchy.",
            [f"hierarchy_pass={hierarchy_pass}", f"readability_pass={readability_pass}", f"parity_status={parity_status}"],
            "Complete the narrow copy and bilingual polish package, then rerun this evidence review." if premium_status != "pass" else "No change required.",
            blocking=premium_status != "pass",
        )
    )

    audit_pass = bool(selected["classic"]["en"]["markdown"] and selected["classic"]["nl"]["markdown"] and provenance_pass)
    findings.append(
        _finding(
            "audit_evidence_preservation",
            "pass" if audit_pass else "fail",
            "The selected current classic markdown remains the complete audit and rationale layer.",
            "The cockpit is additive, references the authority artifacts and does not replace the classic report." if audit_pass else "The selected evidence chain is incomplete.",
            [
                _relative(selected["classic"]["en"]["markdown"], output_dir) or "missing",
                _relative(selected["classic"]["nl"]["markdown"], output_dir) or "missing",
                _relative(state_path, output_dir) or "missing",
            ],
            "Preserve the classic report and current provenance references." if audit_pass else "Restore the selected classic and runtime evidence chain.",
            blocking=not audit_pass,
        )
    )

    blockers = [finding["dimension"] for finding in findings if finding["blocking"]]
    return findings, blockers


def _selected_sources(output_dir: Path, token: str) -> dict[str, Any]:
    return {
        "classic": {
            "en": _select_classic_sources(output_dir, token, "en"),
            "nl": _select_classic_sources(output_dir, token, "nl"),
        },
        "cockpit": {
            "en": _select_cockpit_source(output_dir, token, "en"),
            "nl": _select_cockpit_source(output_dir, token, "nl"),
        },
    }


def _serialize_selected(selected: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    return {
        "classic": {
            language: {kind: _relative(path, output_dir) for kind, path in sources.items()}
            for language, sources in selected["classic"].items()
        },
        "cockpit": {language: _relative(path, output_dir) for language, path in selected["cockpit"].items()},
    }


def _input_hashes(selected: dict[str, Any], output_dir: Path, state_path: Path | None) -> dict[str, str | None]:
    paths: list[Path | None] = [state_path]
    for language in ("en", "nl"):
        paths.extend(selected["classic"][language].values())
        paths.append(selected["cockpit"][language])
    pricing = _pointer_target(output_dir, "pricing/latest_price_audit_path.txt")
    manifest = _pointer_target(output_dir, "run_manifests/latest_weekly_etf_run_manifest_path.txt")
    paths.extend([output_dir / "etf_valuation_history.csv", pricing, manifest])
    return {(_relative(path, output_dir) or "missing"): _sha256(path) for path in paths}


def _metadata(output_dir: Path, token: str) -> dict[str, Any]:
    state, state_path = _load_runtime_state(output_dir)
    selected = _selected_sources(output_dir, token)
    findings, blockers = _analyze(output_dir, token, state, state_path, selected)
    conclusion = "iteration_required" if blockers else "ready_for_promotion_decision"
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "token": token,
        "report_date": report_date,
        "runtime_state_source": _relative(state_path, output_dir),
        "selected_sources": _serialize_selected(selected, output_dir),
        "input_sha256": _input_hashes(selected, output_dir, state_path),
        "review_dimensions": REVIEW_DIMENSIONS,
        "findings": findings,
        "blocking_findings": blockers,
        "review_conclusion": conclusion,
        "next_recommended_package": NEXT_PACKAGE if conclusion == "iteration_required" else "WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW",
        "promotion_status": "not_promoted",
        "state_mutation": "not_allowed",
        "delivery_mutation": "not_allowed",
        "email_send": False,
        "portfolio_model_execution": False,
    }


def _status_label(status: str, language: str) -> str:
    labels = {
        "en": {"pass": "PASS", "partial": "PARTIAL", "fail": "FAIL"},
        "nl": {"pass": "GOED", "partial": "DEELS", "fail": "ONVOLDOENDE"},
    }
    return labels[language][status]


def _markdown(metadata: dict[str, Any], language: str) -> str:
    is_nl = language == "nl"
    title = "# Weekly ETF cockpit side-by-side review — NL" if is_nl else "# Weekly ETF cockpit side-by-side review"
    intro = (
        "Deze review vergelijkt de geselecteerde actuele klassieke rapportlaag met de actuele cockpitpreview op basis van runtime-state en artifactinhoud."
        if is_nl
        else "This review compares the selected current classic report with the current cockpit preview using runtime state and artifact content."
    )
    conclusion_label = "Reviewconclusie" if is_nl else "Review conclusion"
    blockers_label = "Blokkerende bevindingen" if is_nl else "Blocking findings"
    sources_label = "Geselecteerde bronnen" if is_nl else "Selected sources"
    findings_label = "Evidence-based bevindingen" if is_nl else "Evidence-based findings"
    next_label = "Volgend pakket" if is_nl else "Next package"

    lines = [
        title,
        "",
        f"token: `{metadata['token']}`",
        f"report_date: `{metadata['report_date']}`",
        f"schema_version: `{metadata['schema_version']}`",
        f"review_type: `{metadata['review_type']}`",
        "promotion_status: `not_promoted`",
        "",
        intro,
        "",
        f"## {conclusion_label}",
        "",
        f"`{metadata['review_conclusion']}`",
        "",
        f"## {blockers_label}",
        "",
    ]
    blockers = metadata["blocking_findings"]
    lines.extend([f"- `{item}`" for item in blockers] if blockers else ["- none" if not is_nl else "- geen"])
    lines.extend(["", f"## {sources_label}", ""])
    selected = metadata["selected_sources"]
    for key, value in [
        ("Classic EN markdown", selected["classic"]["en"]["markdown"]),
        ("Classic EN HTML", selected["classic"]["en"]["html"]),
        ("Classic NL markdown", selected["classic"]["nl"]["markdown"]),
        ("Classic NL HTML", selected["classic"]["nl"]["html"]),
        ("Cockpit EN", selected["cockpit"]["en"]),
        ("Cockpit NL", selected["cockpit"]["nl"]),
        ("Runtime state", metadata["runtime_state_source"]),
    ]:
        lines.append(f"- **{key}:** `{value or 'missing'}`")

    lines.extend(["", f"## {findings_label}", ""])
    for finding in metadata["findings"]:
        lines.extend(
            [
                f"### `{finding['dimension']}` — {_status_label(finding['status'], language)}",
                "",
                f"- **{'Klassiek rapport' if is_nl else 'Classic report'}:** {finding['classic_observation']}",
                f"- **{'Cockpit' if is_nl else 'Cockpit'}:** {finding['cockpit_observation']}",
                f"- **{'Bewijs' if is_nl else 'Evidence'}:** " + "; ".join(f"`{item}`" for item in finding["evidence"]),
                f"- **{'Vereiste correctie' if is_nl else 'Required fix'}:** {finding['required_fix']}",
                "",
            ]
        )

    lines.extend(
        [
            f"## {next_label}",
            "",
            f"`{metadata['next_recommended_package']}`",
            "",
            "Deze review promoot of verzendt niets." if is_nl else "This review promotes and sends nothing.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(metadata: dict[str, Any], language: str) -> str:
    is_nl = language == "nl"
    title = "Cockpit side-by-side review — NL" if is_nl else "Cockpit side-by-side review"
    conclusion = metadata["review_conclusion"]
    conclusion_text = "Iteratie vereist" if is_nl and conclusion == "iteration_required" else "Iteration required" if conclusion == "iteration_required" else "Gereed voor promotiebesluit" if is_nl else "Ready for promotion decision"
    selected = metadata["selected_sources"]

    finding_cards = []
    for finding in metadata["findings"]:
        evidence = "".join(f"<li><code>{escape(str(item))}</code></li>" for item in finding["evidence"])
        finding_cards.append(
            f"""
            <section class="finding {escape(finding['status'])}">
              <div class="finding-head">
                <h3>{escape(finding['dimension'].replace('_', ' ').title())}</h3>
                <span class="status">{escape(_status_label(finding['status'], language))}</span>
              </div>
              <div class="compare">
                <div><h4>{'Klassiek rapport' if is_nl else 'Classic report'}</h4><p>{escape(finding['classic_observation'])}</p></div>
                <div><h4>Cockpit</h4><p>{escape(finding['cockpit_observation'])}</p></div>
              </div>
              <details><summary>{'Bewijs' if is_nl else 'Evidence'}</summary><ul>{evidence}</ul></details>
              <p class="fix"><strong>{'Vereiste correctie' if is_nl else 'Required fix'}:</strong> {escape(finding['required_fix'])}</p>
            </section>
            """
        )

    source_rows = [
        ("Classic EN markdown", selected["classic"]["en"]["markdown"]),
        ("Classic EN HTML", selected["classic"]["en"]["html"]),
        ("Classic NL markdown", selected["classic"]["nl"]["markdown"]),
        ("Classic NL HTML", selected["classic"]["nl"]["html"]),
        ("Cockpit EN", selected["cockpit"]["en"]),
        ("Cockpit NL", selected["cockpit"]["nl"]),
        ("Runtime state", metadata["runtime_state_source"]),
    ]
    sources_html = "".join(f"<tr><th>{escape(label)}</th><td><code>{escape(value or 'missing')}</code></td></tr>" for label, value in source_rows)
    blockers = "".join(f"<li><code>{escape(item)}</code></li>" for item in metadata["blocking_findings"]) or f"<li>{'Geen' if is_nl else 'None'}</li>"

    return f"""<!DOCTYPE html>
<html lang="{'nl' if is_nl else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<style>
:root{{--paper:#F6F1E7;--surface:#FFFCF5;--ink:#211C16;--muted:#665B4C;--line:#D8CDB8;--petrol:#0F4438;--brass:#B07D2B;--pass:#2F7A57;--partial:#A36B16;--fail:#A8452C}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.5;padding:28px 16px}}
main{{max-width:1100px;margin:0 auto}} header{{border:1px solid var(--line);background:var(--surface);padding:30px 34px;box-shadow:0 18px 44px -34px rgba(33,28,22,.55)}}
.kicker{{font-family:'Courier New',monospace;color:var(--brass);font-size:11px;letter-spacing:.16em;text-transform:uppercase}} h1{{font-family:Georgia,'Times New Roman',serif;font-size:36px;margin:8px 0 10px}} .lede{{color:var(--muted);max-width:820px}}
.summary{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px;margin-top:22px}} .summary div{{border-top:1px solid var(--line);padding-top:12px}} .label{{font-family:'Courier New',monospace;font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}} .big{{font-family:Georgia,'Times New Roman',serif;font-size:22px;margin-top:5px}}
.panel{{margin-top:18px;border:1px solid var(--line);background:var(--surface);padding:24px 28px}} .panel h2{{font-family:Georgia,'Times New Roman',serif;margin:0 0 14px}} table{{width:100%;border-collapse:collapse}} th,td{{padding:9px 8px;border-top:1px solid var(--line);text-align:left;vertical-align:top}} th{{width:190px;color:var(--muted)}} code{{font-family:'Courier New',monospace;font-size:12px;overflow-wrap:anywhere}}
.finding{{margin-top:14px;border:1px solid var(--line);background:var(--surface);padding:20px 22px;border-left-width:5px}} .finding.pass{{border-left-color:var(--pass)}} .finding.partial{{border-left-color:var(--partial)}} .finding.fail{{border-left-color:var(--fail)}} .finding-head{{display:flex;justify-content:space-between;gap:16px;align-items:center}} .finding h3{{margin:0;font-family:Georgia,'Times New Roman',serif}} .status{{font-family:'Courier New',monospace;font-size:10px;letter-spacing:.12em;border:1px solid currentColor;padding:4px 7px}} .compare{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:12px}} .compare h4{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:0 0 5px}} .compare p{{margin:0}} details{{margin-top:12px}} .fix{{margin:12px 0 0;background:#F2EADB;padding:10px 12px}}
footer{{margin-top:18px;color:var(--muted);font-family:'Courier New',monospace;font-size:11px}} @media(max-width:760px){{.summary,.compare{{grid-template-columns:1fr}} h1{{font-size:30px}}}}
</style>
</head>
<body>
<main data-cockpit-side-by-side-review="true" data-preview-only="true" data-schema-version="{SCHEMA_VERSION}">
<header>
<div class="kicker">Weekly ETF · evidence-based review · promotion_status: not_promoted</div>
<h1>{escape(title)}</h1>
<p class="lede">{'Deze review vergelijkt de actuele klassieke rapportlaag met de actuele cockpit op basis van runtime-state en artifactinhoud.' if is_nl else 'This review compares the current classic report with the current cockpit using runtime state and artifact content.'}</p>
<div class="summary">
<div><div class="label">{'Reviewconclusie' if is_nl else 'Review conclusion'}</div><div class="big">{escape(conclusion_text)}</div></div>
<div><div class="label">Token</div><div class="big">{escape(metadata['token'])}</div></div>
<div><div class="label">{'Blokkades' if is_nl else 'Blockers'}</div><div class="big">{len(metadata['blocking_findings'])}</div></div>
</div>
</header>
<section class="panel"><h2>{'Blokkerende bevindingen' if is_nl else 'Blocking findings'}</h2><ul>{blockers}</ul></section>
<section class="panel"><h2>{'Geselecteerde bewijsbronnen' if is_nl else 'Selected evidence sources'}</h2><table>{sources_html}</table></section>
{''.join(finding_cards)}
<section class="panel"><h2>{'Volgend pakket' if is_nl else 'Next package'}</h2><p><code>{escape(metadata['next_recommended_package'])}</code></p><p>{'Deze review promoot of verzendt niets.' if is_nl else 'This review promotes and sends nothing.'}</p></section>
<footer>schema={SCHEMA_VERSION} · review_type={REVIEW_TYPE} · promotion_status=not_promoted</footer>
</main>
</body>
</html>
"""


def build_cockpit_side_by_side_review(output_dir: Path | str = Path("output"), token: str | None = None) -> BuiltSideBySideReview:
    output = Path(output_dir)
    review_dir = output / REVIEW_DIR_NAME
    review_dir.mkdir(parents=True, exist_ok=True)

    resolved_token = _report_token(output, token)
    metadata = _metadata(output, resolved_token)

    metadata_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.json"
    en_md_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.md"
    en_html_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.html"
    nl_md_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_nl_{resolved_token}.md"
    nl_html_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_nl_{resolved_token}.html"

    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    en_md_path.write_text(_markdown(metadata, "en"), encoding="utf-8")
    nl_md_path.write_text(_markdown(metadata, "nl"), encoding="utf-8")
    en_html_path.write_text(_html(metadata, "en"), encoding="utf-8")
    nl_html_path.write_text(_html(metadata, "nl"), encoding="utf-8")

    return BuiltSideBySideReview(
        token=resolved_token,
        metadata_path=metadata_path,
        english_markdown_path=en_md_path,
        english_html_path=en_html_path,
        dutch_markdown_path=nl_md_path,
        dutch_html_path=nl_html_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build evidence-based preview-only cockpit side-by-side review artifacts.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--token", default=None)
    args = parser.parse_args(argv)

    result = build_cockpit_side_by_side_review(output_dir=Path(args.output_dir), token=args.token)
    metadata = _read_json(result.metadata_path)
    print(
        "COCKPIT_SIDE_BY_SIDE_REVIEW_OK"
        f" | token={result.token}"
        f" | schema={metadata.get('schema_version')}"
        f" | conclusion={metadata.get('review_conclusion')}"
        f" | blockers={len(metadata.get('blocking_findings') or [])}"
        f" | json={result.metadata_path}"
        " | promotion_status=not_promoted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
