from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_regime_shadow_narrative_v1"
DEFAULT_OUTPUT_DIR = Path("output/macro/shadow_narrative")
AUTHORITY_FALSE_FLAGS = {
    "client_facing": False,
    "production_report": False,
    "portfolio_action_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path | None) -> str:
    return "" if path is None or not path.exists() else path.read_text(encoding="utf-8")


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _text(value: Any, default: str = "not_available") -> str:
    if value is None:
        return default
    stripped = str(value).strip()
    return stripped or default


def _confidence(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return _text(value)
    if number <= 1.0:
        return f"{number * 100:.0f}%"
    return f"{number:.0f}%"


def _section(report_text: str, heading: str) -> str:
    lines = report_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            section = [line]
            for later in lines[index + 1 :]:
                if later.startswith("## "):
                    break
                section.append(later)
            return "\n".join(section).strip()
    return ""


def _extract_current_macro_narrative(report_text: str, *, language: str) -> dict[str, Any]:
    headings = (
        ["## 1. Kernsamenvatting", "## 3. Regime-dashboard", "## 3. Regime Dashboard"]
        if language == "nl"
        else ["## 1. Executive Summary", "## 3. Regime Dashboard", "## 3. Regime-dashboard"]
    )
    sections = [section for section in (_section(report_text, heading) for heading in headings) if section]
    if sections:
        return {"status": "found", "language": language, "text": "\n\n".join(sections)}
    return {
        "status": "not_found",
        "language": language,
        "text": "No current macro narrative section was found in the supplied report.",
    }


def _normalise_shadow_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("shadow_summary"), dict):
        shadow = dict(payload["shadow_summary"])
        shadow.setdefault("source_artifact_type", payload.get("artifact_type", "macro_regime_shadow_validation_evidence"))
        return shadow
    if isinstance(payload.get("deterministic_regime_shadow"), dict):
        shadow = dict(payload["deterministic_regime_shadow"])
        regime = payload.get("regime") if isinstance(payload.get("regime"), dict) else {}
        shadow.setdefault("legacy_regime", regime.get("current"))
        shadow.setdefault("legacy_confidence", regime.get("confidence"))
        return shadow
    if isinstance(payload.get("macro_regime"), dict):
        return dict(payload["macro_regime"])
    return dict(payload)


def _dict_lines(value: Any, *, max_items: int = 8) -> list[str]:
    if not isinstance(value, dict) or not value:
        return []
    return [f"{key}={_text(value[key])}" for key in sorted(value)[:max_items]]


def _evidence_lines(shadow: dict[str, Any], *, language: str) -> list[str]:
    lines: list[str] = []
    for label, key in (("axes", "axes"), ("macro_axes", "macro_axes"), ("macro_axis_scores", "macro_axis_scores")):
        values = _dict_lines(shadow.get(key))
        if values:
            lines.append(f"{label}: " + "; ".join(values))
    if isinstance(shadow.get("what_changed"), list):
        lines.extend(_text(item, "") for item in shadow["what_changed"][:3])
    if lines:
        return [f"- {line}" for line in lines if line]
    if language == "nl":
        return ["- Geen deterministische bewijsregels meegeleverd; kandidaat blijft uitsluitend shadow-only."]
    return ["- No deterministic evidence rows supplied; candidate remains shadow-only."]


def build_candidate_narrative(macro_regime_payload: dict[str, Any], *, language: str) -> str:
    shadow = _normalise_shadow_payload(macro_regime_payload)
    candidate = _text(
        shadow.get("candidate_regime")
        or shadow.get("deterministic_regime")
        or shadow.get("regime")
        or shadow.get("regime_label"),
        "unclassified",
    )
    candidate_confidence = _confidence(shadow.get("candidate_confidence") or shadow.get("confidence"))
    legacy_regime = _text(shadow.get("legacy_regime"), "not_available")
    legacy_confidence = _confidence(shadow.get("legacy_confidence"))
    method = _text(shadow.get("method"), "not_available")
    differs = _text(shadow.get("differs_from_legacy"), "not_available")
    evidence = "\n".join(_evidence_lines(shadow, language=language))

    if language == "nl":
        return (
            "## Deterministisch macroregime — shadow-kandidaat\n\n"
            "> **SHADOW-ONLY:** Deze tekst is geen client-facing rapporttekst, geen productieoutput, "
            "geen portefeuille-actie, geen lane-score en geen fundability-beslissing.\n\n"
            f"De deterministische shadow-kandidaat classificeert het regime als **{candidate}** met vertrouwen **{candidate_confidence}**. "
            f"De huidige legacy-regimebasis is **{legacy_regime}** met vertrouwen **{legacy_confidence}**. "
            f"Methode: **{method}**. Verschilt van legacy: **{differs}**. Deze tekst mag alleen worden gebruikt "
            "voor vergelijking en review, niet als productie-narratief.\n\n"
            "### Shadow-bewijsregels\n\n"
            f"{evidence}\n\n"
            "### Autoriteitsgrens\n\n"
            "client_facing=false; production_report=false; portfolio_action_authority=false; "
            "lane_scoring_authority=false; fundability_authority=false."
        )
    return (
        "## Deterministic macro regime — shadow candidate\n\n"
        "> **SHADOW-ONLY:** This text is not client-facing report text, not production output, "
        "not a portfolio action, not a lane score and not a fundability decision.\n\n"
        f"The deterministic shadow candidate classifies the regime as **{candidate}** with confidence **{candidate_confidence}**. "
        f"The current legacy regime basis is **{legacy_regime}** with confidence **{legacy_confidence}**. "
        f"Method: **{method}**. Differs from legacy: **{differs}**. This text may only be used "
        "for comparison and review, not as production narrative.\n\n"
        "### Shadow evidence rows\n\n"
        f"{evidence}\n\n"
        "### Authority boundary\n\n"
        "client_facing=false; production_report=false; portfolio_action_authority=false; "
        "lane_scoring_authority=false; fundability_authority=false."
    )


def _comparison_markdown(*, current_en: dict[str, Any], current_nl: dict[str, Any], candidate_en: str, candidate_nl: str) -> str:
    return (
        "# Macro regime shadow narrative comparison\n\n"
        "> **SHADOW-ONLY / NOT FOR PRODUCTION / NIET VOOR PRODUCTIE:** This artifact compares current report wording "
        "with a deterministic macro regime narrative candidate. It does not modify the production report.\n\n"
        "## Authority flags\n\n"
        "- client_facing=false\n- production_report=false\n- portfolio_action_authority=false\n"
        "- lane_scoring_authority=false\n- fundability_authority=false\n\n"
        "## Current macro narrative — English\n\n"
        f"Status: {current_en['status']}\n\n{current_en['text']}\n\n"
        "## Deterministic regime shadow narrative candidate — English\n\n"
        f"{candidate_en}\n\n"
        "## Current macro narrative — Dutch\n\n"
        f"Status: {current_nl['status']}\n\n{current_nl['text']}\n\n"
        "## Deterministisch regime shadow-narratief kandidaat — Nederlands\n\n"
        f"{candidate_nl}\n"
    )


def build_macro_regime_shadow_narrative(
    *,
    run_id: str,
    report_date: str,
    current_report_en_text: str = "",
    current_report_nl_text: str = "",
    macro_regime_payload: dict[str, Any] | None = None,
    current_report_en_path: str | None = None,
    current_report_nl_path: str | None = None,
    macro_regime_artifact_path: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    payload = macro_regime_payload or {}
    current_en = _extract_current_macro_narrative(current_report_en_text, language="en")
    current_nl = _extract_current_macro_narrative(current_report_nl_text, language="nl")
    candidate_en = build_candidate_narrative(payload, language="en")
    candidate_nl = build_candidate_narrative(payload, language="nl")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "macro_regime_shadow_narrative_comparison",
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": "shadow_candidate_only",
        "shadow_only": True,
        **AUTHORITY_FALSE_FLAGS,
        "authority": dict(AUTHORITY_FALSE_FLAGS),
        "inputs": {
            "current_report_en_path": current_report_en_path,
            "current_report_nl_path": current_report_nl_path,
            "macro_regime_artifact_path": macro_regime_artifact_path,
        },
        "current_macro_narrative": {"en": current_en, "nl": current_nl},
        "deterministic_regime_shadow_narrative_candidate": {"en": candidate_en, "nl": candidate_nl},
        "comparison_markdown": _comparison_markdown(
            current_en=current_en,
            current_nl=current_nl,
            candidate_en=candidate_en,
            candidate_nl=candidate_nl,
        ),
        "blockers": [
            "shadow-only comparison artifact",
            "client_facing=false",
            "production_report=false",
            "portfolio_action_authority=false",
            "lane_scoring_authority=false",
            "fundability_authority=false",
            "no production report mutation",
        ],
    }


def write_macro_regime_shadow_narrative(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    current_report_en_path: Path | None = None,
    current_report_nl_path: Path | None = None,
    macro_regime_artifact_path: Path | None = None,
    created_at_utc: str | None = None,
) -> Path:
    artifact = build_macro_regime_shadow_narrative(
        run_id=run_id,
        report_date=report_date,
        current_report_en_text=_read_text(current_report_en_path),
        current_report_nl_text=_read_text(current_report_nl_path),
        macro_regime_payload=_read_json(macro_regime_artifact_path),
        current_report_en_path=str(current_report_en_path) if current_report_en_path else None,
        current_report_nl_path=str(current_report_nl_path) if current_report_nl_path else None,
        macro_regime_artifact_path=str(macro_regime_artifact_path) if macro_regime_artifact_path else None,
        created_at_utc=created_at_utc,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"macro_regime_shadow_narrative_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--current-report-en")
    parser.add_argument("--current-report-nl")
    parser.add_argument("--macro-regime-artifact", default="output/macro/validation/latest_macro_regime_shadow_validation.json")
    args = parser.parse_args()
    path = write_macro_regime_shadow_narrative(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        current_report_en_path=Path(args.current_report_en) if args.current_report_en else None,
        current_report_nl_path=Path(args.current_report_nl) if args.current_report_nl else None,
        macro_regime_artifact_path=Path(args.macro_regime_artifact) if args.macro_regime_artifact else None,
    )
    print(
        "MACRO_REGIME_SHADOW_NARRATIVE_OK | "
        f"artifact={path} | client_facing=false | production_report=false | "
        "portfolio_action_authority=false | lane_scoring_authority=false | fundability_authority=false"
    )


if __name__ == "__main__":
    main()
