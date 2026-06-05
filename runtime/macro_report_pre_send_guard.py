from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.validate_etf_macro_thesis_surface_leakage import scan_text
from tools.validate_macro_compliance import _extract_report_macro_sections, validate_text
from tools.validate_macro_report_surface import validate_pack

DEFAULT_MACRO_PACK = Path("output/macro/latest.json")


def _load_macro_pack(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Macro report pre-send guard failed: macro pack missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Macro report pre-send guard failed: expected JSON object in {path}")
    return payload


def _compliance_scope(path: Path, text: str) -> str:
    """Limit macro-compliance figure checks to macro-sensitive report sections.

    Full-report leakage scanning remains active below. The macro-compliance
    orphan-figure rule is intentionally macro-specific, so it must not scan
    ordinary portfolio-performance sections such as Section 7A.
    """
    if path.suffix.lower() == ".md":
        return _extract_report_macro_sections(text)
    return text


def _validate_client_text(path: Path, text: str) -> tuple[int, int]:
    compliance = validate_text(_compliance_scope(path, text))
    leakage = scan_text(text, path)
    if compliance:
        for finding in compliance[:40]:
            print(
                "ETF_MACRO_PRE_SEND_COMPLIANCE_FINDING | "
                f"file={path.name} | code={finding.code} | line={finding.line} | excerpt={finding.excerpt}"
            )
    if leakage:
        for finding in leakage[:40]:
            print(
                "ETF_MACRO_PRE_SEND_LEAK_FINDING | "
                f"file={path.name} | code={finding.code} | line={finding.line} | excerpt={finding.excerpt}"
            )
    if compliance or leakage:
        raise RuntimeError(
            "ETF macro report pre-send guard failed: "
            f"file={path} | compliance_findings={len(compliance)} | leakage_findings={len(leakage)}"
        )
    return len(compliance), len(leakage)


def validate_macro_report_pre_send(bundle: dict[str, Any], macro_pack_path: Path = DEFAULT_MACRO_PACK) -> None:
    """Validate macro/regime client surface before SMTP delivery.

    This is intentionally a delivery-entrypoint guard, not a portfolio authority
    change. It blocks sending if the already-rendered report would leak internal
    shadow terms or violate macro compliance rules.
    """

    pack = _load_macro_pack(macro_pack_path)
    validate_pack(pack, str(macro_pack_path))

    files_checked: list[str] = []
    for key in ("en", "nl"):
        assets = bundle.get(key)
        if not isinstance(assets, dict):
            continue
        report_path = assets.get("report_path")
        md_text = assets.get("md_text_clean")
        html_path = assets.get("html_path")
        html_text = assets.get("html_email")
        if isinstance(report_path, Path) and isinstance(md_text, str):
            _validate_client_text(report_path, md_text)
            files_checked.append(report_path.name)
        if isinstance(html_path, Path) and isinstance(html_text, str):
            _validate_client_text(html_path, html_text)
            files_checked.append(html_path.name)

    if not files_checked:
        raise RuntimeError("ETF macro report pre-send guard failed: no report/html assets were checked")

    print(
        "ETF_MACRO_REPORT_PRE_SEND_GUARD_OK | "
        f"macro_pack={macro_pack_path} | files={','.join(files_checked)}"
    )
