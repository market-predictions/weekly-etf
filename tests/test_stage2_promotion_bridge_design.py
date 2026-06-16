from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_bridge_design as validator


def _write_design(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "STAGE2_PROMOTION_BRIDGE_DESIGN.md"
    path.write_text(text, encoding="utf-8")
    return path


def _valid_design_text() -> str:
    return """
# Stage-2 Promotion Bridge Design

## Status

Design-only. No production wiring.

This bridge does not change production report output, lane scoring, fundability, portfolio actions, delivery behavior, execution behavior, or historical output files.

## Purpose

Stage-2 confirmation remains shadow-only until a later explicit promotion decision exists.

The bridge sequence is Stage-2 shadow confirmation → promotion-review eligibility → explicit control-layer promotion decision → separate future implementation package.

## Authority boundaries

client_facing_authority: false
production_report_narrative_authority: false
portfolio_action_authority: false
lane_scoring_authority: false
fundability_authority: false
portfolio_mutation: false
historical_output_mutation: false
delivery_authority: false
execution_authority: false

## Prerequisite artifacts

pricing-lineage validation is complete

## Eligible evidence fields

bilingual sanitized alias exists if client wording is proposed
leakage firewall passes
macro/report-surface compliance passes

## Forbidden direct-use fields

Raw driver IDs and internal Stage-2 fields must not be used directly.

## Bilingual alias dependency

config/macro_thesis_bilingual_aliases.yml

## Promotion-review checklist

The review checks evidence only.

## Explicit non-goals

No production integration.

## Future implementation gate

A separate later implementation package is required.
"""


def test_valid_design_document_passes(tmp_path: Path) -> None:
    validator.validate_design_file(_write_design(tmp_path, _valid_design_text()))


def test_missing_design_only_wording_fails(tmp_path: Path) -> None:
    text = _valid_design_text().replace("Design-only. No production wiring.", "No production wiring.")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_design_file(_write_design(tmp_path, text))


def test_missing_shadow_only_boundary_fails(tmp_path: Path) -> None:
    text = _valid_design_text().replace(
        "Stage-2 confirmation remains shadow-only until a later explicit promotion decision exists.",
        "Stage-2 confirmation remains under review.",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_design_file(_write_design(tmp_path, text))


def test_missing_false_authority_fields_fails(tmp_path: Path) -> None:
    text = _valid_design_text().replace("fundability_authority: false", "")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_design_file(_write_design(tmp_path, text))


def test_missing_bilingual_alias_dependency_fails(tmp_path: Path) -> None:
    text = _valid_design_text().replace("config/macro_thesis_bilingual_aliases.yml", "config/other_aliases.yml")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_design_file(_write_design(tmp_path, text))


def test_now_promoted_wording_fails(tmp_path: Path) -> None:
    text = _valid_design_text() + "\nStage-2 is now promoted.\n"

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_design_file(_write_design(tmp_path, text))


def test_production_design_document_validates() -> None:
    validator.validate_design_file(Path("control/STAGE2_PROMOTION_BRIDGE_DESIGN.md"))
