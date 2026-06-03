#!/usr/bin/env python3
"""Validate the client-safe ETF macro report surface.

This is a narrow integration guard for the report-facing macro/regime text. It
proves that the shared macro surface can render English and Dutch text from the
macro policy pack without leaking internal shadow fields, driver IDs, or
predictive phrasing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.macro_report_surface import dashboard_en, dashboard_nl, executive_lines_en, executive_lines_nl
from tools.validate_etf_macro_thesis_surface_leakage import scan_text
from tools.validate_macro_compliance import validate_text


DEFAULT_PACK = Path("output/macro/latest.json")


def _load_pack(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Macro pack not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected macro pack JSON object: {path}")
    return payload


def _fixture_pack() -> dict[str, Any]:
    return {
        "regime": {
            "current": "Risk-on growth",
            "confidence": 0.66,
            "what_changed": [
                "AI and semiconductor leadership remains the dominant equity impulse.",
                "Gold hedge behavior remains under review rather than automatic ballast.",
            ],
        },
        "regime_memory": {
            "decision_rule": "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad.",
            "report_transfer": {
                "summary": "Risk-on growth has persisted for 3 runs; transition state is stable, breadth is mixed, and cross-asset confirmation is mixed."
            },
        },
        "central_banks": {
            "fed": {
                "stance": "Restrictive / data-dependent",
                "etf_implication": "Prefer quality, profitable growth and cash discipline over weak balance-sheet beta.",
            },
            "ecb": {
                "stance": "Neutral / transition",
                "etf_implication": "Non-U.S. developed exposure remains watchlist, not automatic add.",
            },
        },
        "policy_catalysts": [
            {
                "policy_area": "AI infrastructure and semiconductor supply chains",
                "latest_signal": "Capital spending and strategic supply-chain policy continue to support semiconductor and infrastructure lanes.",
                "transfer_to_report": True,
            },
            {
                "policy_area": "Defense and sovereign resilience",
                "latest_signal": "Defense-budget durability remains a structural support, but ETF vehicle choice still matters.",
                "transfer_to_report": True,
            },
        ],
        "portfolio_implications": [
            "Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation.",
            "Growth and infrastructure lanes can be considered if they do not worsen concentration.",
            "Defensive hedges should be reviewed for opportunity cost.",
        ],
        "lane_adjustments": {
            "AI compute infrastructure": {
                "reason": "Regime and price leadership still support AI compute exposure, but concentration discipline applies."
            }
        },
    }


def _render(pack: dict[str, Any]) -> dict[str, str]:
    state = {"macro_policy_pack": pack}
    en_lines = executive_lines_en(state)
    nl_lines = executive_lines_nl(state)
    return {
        "en": "\n".join(
            [
                en_lines["primary_regime"],
                en_lines["secondary_cross_current"],
                en_lines["geopolitical_regime"],
                en_lines["what_changed"],
                dashboard_en(state),
            ]
        ),
        "nl": "\n".join(
            [
                nl_lines["primary_regime"],
                nl_lines["geopolitical_regime"],
                nl_lines["what_changed"],
                dashboard_nl(state),
            ]
        ),
    }


def _validate_surface_text(name: str, text: str) -> None:
    compliance = validate_text(text)
    leakage = scan_text(text, Path(name))
    if compliance:
        for finding in compliance:
            print(f"MACRO_REPORT_SURFACE_COMPLIANCE_FINDING | {name} | {finding.code} | line={finding.line} | {finding.excerpt}")
        raise SystemExit(f"Macro report surface compliance failed for {name}: findings={len(compliance)}")
    if leakage:
        for finding in leakage:
            print(f"MACRO_REPORT_SURFACE_LEAK_FINDING | {name} | {finding.code} | line={finding.line} | {finding.excerpt}")
        raise SystemExit(f"Macro report surface leakage failed for {name}: findings={len(leakage)}")
    if "deterministic_regime_shadow" in text or "client_facing_authority" in text or "shadow_only" in text:
        raise SystemExit(f"Macro report surface leaked internal authority vocabulary in {name}")


def validate_pack(pack: dict[str, Any], label: str) -> None:
    rendered = _render(pack)
    for name, text in rendered.items():
        _validate_surface_text(f"{label}_{name}", text)
    print(
        "ETF_MACRO_REPORT_SURFACE_OK | "
        f"label={label} | en_chars={len(rendered['en'])} | nl_chars={len(rendered['nl'])}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--macro-pack", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test or args.macro_pack is None:
        validate_pack(_fixture_pack(), "fixture")
    if args.macro_pack is not None:
        validate_pack(_load_pack(args.macro_pack), str(args.macro_pack))


if __name__ == "__main__":
    main()
