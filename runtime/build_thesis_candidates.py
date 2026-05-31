#!/usr/bin/env python3
"""Build internal Stage-1 ETF thesis candidates from macro drivers.

This is a shadow-only Phase 5 artifact. It must not feed client-facing reports,
lane scoring, fundability, portfolio actions, or recommendations.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


AUTHORITY = {
    "shadow_only": True,
    "client_facing_authority": False,
    "decision_impact": "none_stage1_thesis_candidates_only",
    "portfolio_action_authority": False,
    "fundability_authority": False,
    "report_surface_allowed": False,
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected YAML object in {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _flatten_strings(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            out.extend(_flatten_strings(nested))
    elif isinstance(value, list):
        for nested in value:
            out.extend(_flatten_strings(nested))
    return out


def _term_score(pack: dict[str, Any], terms: list[str]) -> tuple[int, list[str]]:
    haystack = "\n".join(_flatten_strings(pack)).lower()
    matched: list[str] = []
    for term in terms:
        if str(term).lower() in haystack:
            matched.append(str(term))
    return len(matched), matched


def _universe_by_tag(universe: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = universe.get("lanes") or []
    if not isinstance(lanes, list):
        raise SystemExit("config/etf_discovery_universe.yml has no lanes list")
    by_tag: dict[str, dict[str, Any]] = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        tag = lane.get("taxonomy_tag")
        if isinstance(tag, str):
            by_tag[tag] = lane
    return by_tag


def _validate_authority(config: dict[str, Any], path: Path) -> None:
    authority = config.get("authority") or {}
    if authority.get("shadow_only") is not True:
        raise SystemExit(f"{path} must set authority.shadow_only=true")
    if authority.get("client_facing_authority") is not False:
        raise SystemExit(f"{path} must set authority.client_facing_authority=false")
    if authority.get("decision_impact") != "none_stage1_thesis_candidates_only":
        raise SystemExit(f"{path} has unexpected decision_impact")


def build_candidates(
    macro_pack: dict[str, Any],
    driver_catalog: dict[str, Any],
    beneficiary_map: dict[str, Any],
    universe: dict[str, Any],
    *,
    reference_date: str,
    run_id: str,
) -> dict[str, Any]:
    _validate_authority(driver_catalog, Path("driver_catalog"))
    _validate_authority(beneficiary_map, Path("driver_beneficiary_map"))

    lane_by_tag = _universe_by_tag(universe)
    mappings = beneficiary_map.get("mappings") or {}
    if not isinstance(mappings, dict):
        raise SystemExit("driver_beneficiary_map.yml mappings must be an object")

    drivers_out: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for driver in driver_catalog.get("drivers") or []:
        if not isinstance(driver, dict):
            continue
        driver_id = driver.get("driver_id")
        if not isinstance(driver_id, str):
            raise SystemExit("Every driver must have driver_id")
        activation = driver.get("activation") or {}
        terms = activation.get("terms") or []
        if not isinstance(terms, list):
            raise SystemExit(f"Driver {driver_id} activation.terms must be a list")
        score, matched_terms = _term_score(macro_pack, [str(t) for t in terms])
        active = score > 0
        drivers_out.append(
            {
                "driver_id": driver_id,
                "label": driver.get("label"),
                "active": active,
                "activation_score": score,
                "matched_terms": matched_terms,
                "status": "active_stage_1_shadow_candidate_only" if active else "inactive",
            }
        )
        if not active:
            continue
        mapping = mappings.get(driver_id)
        if not isinstance(mapping, dict):
            raise SystemExit(f"Active driver {driver_id} has no beneficiary mapping")
        for beneficiary in mapping.get("beneficiaries") or []:
            tag = beneficiary.get("taxonomy_tag") if isinstance(beneficiary, dict) else None
            if not isinstance(tag, str):
                raise SystemExit(f"Beneficiary for {driver_id} missing taxonomy_tag")
            lane = lane_by_tag.get(tag)
            if not lane:
                raise SystemExit(f"Beneficiary taxonomy_tag not found in ETF universe: {tag}")
            candidates.append(
                {
                    "driver_id": driver_id,
                    "driver_label": driver.get("label"),
                    "taxonomy_tag": tag,
                    "lane_name": lane.get("lane_name"),
                    "primary_etf": lane.get("primary_etf"),
                    "alternative_etf": lane.get("alternative_etf"),
                    "driver_to_beneficiary_rationale": beneficiary.get("rationale"),
                    "stage": "stage_1_shadow_candidate_only",
                    "client_facing_authority": False,
                    "fundability_status": "not_fundable_stage_1_only",
                    "portfolio_action": "none",
                    "requires_stage_2_confirmation": True,
                }
            )

    candidates = sorted(candidates, key=lambda row: (str(row["driver_id"]), str(row["taxonomy_tag"])))
    active_driver_ids = sorted([d["driver_id"] for d in drivers_out if d["active"]])

    return {
        "schema_version": "1.0",
        "artifact_type": "stage_1_thesis_candidates_shadow",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "reference_date": reference_date,
        "run_id": run_id,
        "authority": AUTHORITY,
        "inputs": {
            "macro_pack": "provided",
            "driver_catalog_schema_version": driver_catalog.get("schema_version"),
            "beneficiary_map_schema_version": beneficiary_map.get("schema_version"),
        },
        "active_driver_ids": active_driver_ids,
        "drivers": drivers_out,
        "candidates": candidates,
        "guardrails": [
            "Stage-1 thesis candidates are internal only.",
            "No candidate is fundable without Stage-2 confirmation, valuation-grade pricing, and portfolio discipline gates.",
            "Do not surface this artifact in English or Dutch reports.",
        ],
    }


def validate_artifact(payload: dict[str, Any], universe: dict[str, Any]) -> None:
    authority = payload.get("authority") or {}
    required_false = ["client_facing_authority", "portfolio_action_authority", "fundability_authority", "report_surface_allowed"]
    if authority.get("shadow_only") is not True:
        raise SystemExit("Thesis artifact must be shadow_only=true")
    for field in required_false:
        if authority.get(field) is not False:
            raise SystemExit(f"Thesis artifact must set authority.{field}=false")
    if authority.get("decision_impact") != "none_stage1_thesis_candidates_only":
        raise SystemExit("Thesis artifact has unexpected decision_impact")

    lane_by_tag = _universe_by_tag(universe)
    for candidate in payload.get("candidates") or []:
        if candidate.get("taxonomy_tag") not in lane_by_tag:
            raise SystemExit(f"Candidate taxonomy_tag missing from universe: {candidate.get('taxonomy_tag')}")
        if candidate.get("client_facing_authority") is not False:
            raise SystemExit("Candidate has client-facing authority")
        if candidate.get("fundability_status") != "not_fundable_stage_1_only":
            raise SystemExit("Candidate has non-stage-1 fundability status")
        if candidate.get("portfolio_action") != "none":
            raise SystemExit("Candidate has portfolio action")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--macro-pack", type=Path, default=Path("output/macro/latest.json"))
    parser.add_argument("--driver-catalog", type=Path, default=Path("config/driver_catalog.yml"))
    parser.add_argument("--beneficiary-map", type=Path, default=Path("config/driver_beneficiary_map.yml"))
    parser.add_argument("--universe", type=Path, default=Path("config/etf_discovery_universe.yml"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro"))
    parser.add_argument("--reference-date", default="unknown")
    parser.add_argument("--run-id", default="shadow_thesis")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--expect-driver", action="append", default=[])
    args = parser.parse_args()

    macro_pack = _load_json(args.macro_pack)
    catalog = _load_yaml(args.driver_catalog)
    beneficiary_map = _load_yaml(args.beneficiary_map)
    universe = _load_yaml(args.universe)

    payload = build_candidates(
        macro_pack,
        catalog,
        beneficiary_map,
        universe,
        reference_date=args.reference_date,
        run_id=args.run_id,
    )
    validate_artifact(payload, universe)

    missing = [driver for driver in args.expect_driver if driver not in payload["active_driver_ids"]]
    if missing:
        raise SystemExit(f"Expected active drivers missing: {missing}")

    if not args.validate_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        safe_date = args.reference_date.replace("/", "-")
        out = args.output_dir / f"thesis_candidates_{safe_date}_{args.run_id}.json"
        latest = args.output_dir / "latest_thesis_candidates.json"
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        out.write_text(text, encoding="utf-8")
        latest.write_text(text, encoding="utf-8")
        print(f"ETF_THESIS_CANDIDATES_WRITTEN | path={out} | candidates={len(payload['candidates'])}")
    print(
        "ETF_THESIS_CANDIDATES_SHADOW_OK | "
        f"active_drivers={len(payload['active_driver_ids'])} | candidates={len(payload['candidates'])}"
    )


if __name__ == "__main__":
    main()
