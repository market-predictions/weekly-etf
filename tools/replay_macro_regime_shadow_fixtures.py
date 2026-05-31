from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml

from macro_regime.classify import classify_regime_shadow
from tools.validate_macro_regime_shadow import validate_shadow_payload

DEFAULT_FIXTURES = Path("fixtures/macro_regime_shadow/regime_shadow_fixtures.json")
DEFAULT_THRESHOLDS = Path("config/regime_thresholds.yml")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Fixture file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Threshold file not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _validate_fixture_result(fixture: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    fixture_id = str(fixture.get("id") or "unknown")
    expected_regime = fixture.get("expected_regime")
    _require(result.get("candidate_regime") == expected_regime, f"{fixture_id}: expected regime {expected_regime!r}, got {result.get('candidate_regime')!r}")

    expected_axes = fixture.get("expected_axes") or {}
    axes = result.get("axes") or {}
    for axis, expected_value in expected_axes.items():
        actual = axes.get(axis)
        _require(actual == expected_value, f"{fixture_id}: axis {axis} expected {expected_value!r}, got {actual!r}")

    confidence = float(result.get("candidate_confidence"))
    minimum = float(fixture.get("expected_confidence_min", 0.0))
    maximum = float(fixture.get("expected_confidence_max", 1.0))
    _require(minimum <= confidence <= maximum, f"{fixture_id}: confidence {confidence} outside expected range [{minimum}, {maximum}]")

    validate_shadow_payload(result)
    return {
        "id": fixture_id,
        "candidate_regime": result.get("candidate_regime"),
        "candidate_confidence": confidence,
        "axes": axes,
    }


def replay(fixtures_path: Path, thresholds_path: Path) -> list[dict[str, Any]]:
    payload = _load_json(fixtures_path)
    thresholds = _load_yaml(thresholds_path)
    _require(payload.get("status") == "shadow_only", "fixture payload must be shadow_only")
    _require(payload.get("client_facing_authority") is False, "fixtures must not be client-facing authority")
    results: list[dict[str, Any]] = []
    for fixture in payload.get("fixtures") or []:
        result = classify_regime_shadow(
            metrics=fixture.get("metrics") or {},
            macro_data_audit_summary={"present": False},
            thresholds=thresholds,
            legacy_regime="Legacy comparison placeholder",
            legacy_confidence=0.50,
        )
        results.append(_validate_fixture_result(fixture, result))
    _require(len(results) == 5, f"Expected 5 regime fixtures, got {len(results)}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay deterministic shadow macro regime fixtures with no network access.")
    parser.add_argument("--fixtures", default=str(DEFAULT_FIXTURES))
    parser.add_argument("--thresholds", default=str(DEFAULT_THRESHOLDS))
    args = parser.parse_args()
    results = replay(Path(args.fixtures), Path(args.thresholds))
    print(f"ETF_MACRO_REGIME_FIXTURE_REPLAY_OK | fixtures={len(results)}")
    for result in results:
        print(
            "ETF_MACRO_REGIME_FIXTURE_OK | "
            f"id={result['id']} | regime={result['candidate_regime']} | "
            f"confidence={result['candidate_confidence']} | axes={json.dumps(result['axes'], sort_keys=True)}"
        )


if __name__ == "__main__":
    main()
