from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.additive_cockpit_front_page import FEATURE_FLAG, FRONT_PAGE_MARKER

REPORT_TOKEN = "260714"
EN_REPORT = f"weekly_analysis_pro_{REPORT_TOKEN}_04.md"
NL_REPORT = f"weekly_analysis_pro_nl_{REPORT_TOKEN}_04.md"
EN_HTML = f"weekly_analysis_pro_{REPORT_TOKEN}_04_delivery.html"
NL_HTML = f"weekly_analysis_pro_nl_{REPORT_TOKEN}_04_delivery.html"
EN_PDF = f"weekly_analysis_pro_{REPORT_TOKEN}_04.pdf"
NL_PDF = f"weekly_analysis_pro_nl_{REPORT_TOKEN}_04.pdf"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return digest.hexdigest()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(str(item.relative_to(path)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _copy_artifact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _normalized_classic_body(html: str, *, enabled: bool) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if enabled:
        for node in soup.select('[data-cockpit-front-page="delivery"]'):
            node.decompose()
    else:
        for node in soup.select(".decision-cockpit"):
            node.decompose()
    if soup.body is None:
        raise RuntimeError("Rendered report has no body element")
    return " ".join(str(soup.body).split())


def _pdf_text(path: Path) -> tuple[int, str]:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return len(reader.pages), text


def _assert_bundle_shape(bundle: dict[str, Any]) -> None:
    assert bundle.get("bilingual") is True
    assert set(bundle) == {"bilingual", "en", "nl"}
    for language in ("en", "nl"):
        assets = bundle[language]
        for key in (
            "report_date_str",
            "clean_md_path",
            "equity_curve_png",
            "html_path",
            "pdf_path",
            "html_email",
            "safe_stem",
            "md_text_clean",
            "language",
            "report_path",
        ):
            assert key in assets, (language, key)
        assert assets["language"] == language
        assert Path(assets["html_path"]).exists()
        assert Path(assets["pdf_path"]).exists()


def validate(*, repo_root: Path, work_root: Path, evidence_dir: Path) -> Path:
    source_output = repo_root / "output"
    work_output = work_root / "output"
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_output, work_output)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    report_en = work_output / EN_REPORT
    report_nl = work_output / NL_REPORT
    if not report_en.exists() or not report_nl.exists():
        raise RuntimeError("Exact current _04 bilingual report pair is missing")

    original_en_html = (work_output / EN_HTML).read_bytes()
    original_nl_html = (work_output / NL_HTML).read_bytes()
    delivery_digest_before = _tree_digest(work_output / "delivery")

    os.environ["MRKT_RPRTS_OUTPUT_DIR"] = str(work_output)
    os.environ["MRKT_RPRTS_EXPLICIT_REPORT_PATH"] = str(report_en)

    runtime_html = importlib.import_module("send_report_runtime_html")

    os.environ[FEATURE_FLAG] = "disabled"
    disabled_bundle = runtime_html.report_module.generate_delivery_assets_for_run(
        work_output, report_en, mode="pro"
    )
    _assert_bundle_shape(disabled_bundle)

    disabled_en_html = Path(disabled_bundle["en"]["html_path"]).read_text(encoding="utf-8")
    disabled_nl_html = Path(disabled_bundle["nl"]["html_path"]).read_text(encoding="utf-8")
    disabled_en_email = disabled_bundle["en"]["html_email"]
    disabled_nl_email = disabled_bundle["nl"]["html_email"]

    assert FRONT_PAGE_MARKER not in disabled_en_html
    assert FRONT_PAGE_MARKER not in disabled_nl_html
    assert FRONT_PAGE_MARKER not in disabled_en_email
    assert FRONT_PAGE_MARKER not in disabled_nl_email
    assert "decision-cockpit" in disabled_en_html
    assert "decision-cockpit" in disabled_nl_html
    assert Path(disabled_bundle["en"]["html_path"]).read_bytes() == original_en_html
    assert Path(disabled_bundle["nl"]["html_path"]).read_bytes() == original_nl_html

    disabled_en_pdf = Path(disabled_bundle["en"]["pdf_path"])
    disabled_nl_pdf = Path(disabled_bundle["nl"]["pdf_path"])
    disabled_en_pages, _ = _pdf_text(disabled_en_pdf)
    disabled_nl_pages, _ = _pdf_text(disabled_nl_pdf)

    _copy_artifact(Path(disabled_bundle["en"]["html_path"]), evidence_dir / "disabled" / EN_HTML)
    _copy_artifact(Path(disabled_bundle["nl"]["html_path"]), evidence_dir / "disabled" / NL_HTML)
    _copy_artifact(disabled_en_pdf, evidence_dir / "disabled" / EN_PDF)
    _copy_artifact(disabled_nl_pdf, evidence_dir / "disabled" / NL_PDF)

    os.environ[FEATURE_FLAG] = "enabled"
    enabled_bundle = runtime_html.report_module.generate_delivery_assets_for_run(
        work_output, report_en, mode="pro"
    )
    _assert_bundle_shape(enabled_bundle)

    enabled_en_html = Path(enabled_bundle["en"]["html_path"]).read_text(encoding="utf-8")
    enabled_nl_html = Path(enabled_bundle["nl"]["html_path"]).read_text(encoding="utf-8")
    enabled_en_email = enabled_bundle["en"]["html_email"]
    enabled_nl_email = enabled_bundle["nl"]["html_email"]

    for html in (enabled_en_html, enabled_nl_html, enabled_en_email, enabled_nl_email):
        assert html.count(FRONT_PAGE_MARKER) == 1
        assert "decision-cockpit" not in html
        assert "data-source-evidence" in html
        assert "data-next-action-trigger" in html

    assert "Report front page" in enabled_en_html
    assert "Rapportvoorpagina" in enabled_nl_html
    assert "URNM reduced" in enabled_en_html
    assert "XBI added" in enabled_en_html
    assert "URNM afgebouwd" in enabled_nl_html
    assert "XBI toegevoegd" in enabled_nl_html

    forbidden = (
        "preview lane",
        "preview-only cockpit",
        "no delivery claim",
        "not promoted to production",
        "voorbeeldcockpit",
        "geen leveringsclaim",
        "niet naar productie gepromoveerd",
    )
    enabled_combined = (enabled_en_html + enabled_nl_html).lower()
    assert not any(token in enabled_combined for token in forbidden)

    assert "data:image/png;base64," in enabled_en_html
    assert "data:image/png;base64," in enabled_nl_html
    assert "cid:equitycurve" not in enabled_en_html.lower()
    assert "cid:equitycurve" not in enabled_nl_html.lower()
    assert "cid:equitycurve" in enabled_en_email.lower()
    assert "cid:equitycurve" in enabled_nl_email.lower()

    assert _normalized_classic_body(disabled_en_html, enabled=False) == _normalized_classic_body(
        enabled_en_html, enabled=True
    )
    assert _normalized_classic_body(disabled_nl_html, enabled=False) == _normalized_classic_body(
        enabled_nl_html, enabled=True
    )

    enabled_en_pdf = Path(enabled_bundle["en"]["pdf_path"])
    enabled_nl_pdf = Path(enabled_bundle["nl"]["pdf_path"])
    enabled_en_pages, enabled_en_pdf_text = _pdf_text(enabled_en_pdf)
    enabled_nl_pages, enabled_nl_pdf_text = _pdf_text(enabled_nl_pdf)
    assert enabled_en_pages >= disabled_en_pages + 1
    assert enabled_nl_pages >= disabled_nl_pages + 1
    assert "Report front page" in enabled_en_pdf_text
    assert "Rapportvoorpagina" in enabled_nl_pdf_text

    _copy_artifact(Path(enabled_bundle["en"]["html_path"]), evidence_dir / "enabled" / EN_HTML)
    _copy_artifact(Path(enabled_bundle["nl"]["html_path"]), evidence_dir / "enabled" / NL_HTML)
    _copy_artifact(enabled_en_pdf, evidence_dir / "enabled" / EN_PDF)
    _copy_artifact(enabled_nl_pdf, evidence_dir / "enabled" / NL_PDF)

    delivery_digest_after = _tree_digest(work_output / "delivery")
    assert delivery_digest_after == delivery_digest_before

    evidence = {
        "schema_version": "cockpit_wp10_additive_delivery_front_page_v1",
        "report_token": REPORT_TOKEN,
        "implementation_status": "validated_ready_for_enablement_decision",
        "feature_default": "disabled",
        "disabled_html_byte_identical": {
            "en": _sha256_bytes(original_en_html) == _sha256_bytes(disabled_en_html.encode("utf-8")),
            "nl": _sha256_bytes(original_nl_html) == _sha256_bytes(disabled_nl_html.encode("utf-8")),
        },
        "enabled_front_page_count": {"en": 1, "nl": 1},
        "classic_report_body": "preserved",
        "small_decision_cockpit_duplicate": False,
        "standalone_equity_embed": "passed",
        "email_equity_cid": "passed",
        "pdf_generation": {
            "en_pages_disabled": disabled_en_pages,
            "en_pages_enabled": enabled_en_pages,
            "nl_pages_disabled": disabled_nl_pages,
            "nl_pages_enabled": enabled_nl_pages,
        },
        "email_count_change": False,
        "pdf_count_change": False,
        "attachment_contract_change": False,
        "manifest_contract_change": False,
        "delivery_directory_digest_unchanged": True,
        "email_sent": False,
        "promotion_status": "not_promoted",
        "artifact_sha256": {
            "disabled_en_html": _sha256_bytes((evidence_dir / "disabled" / EN_HTML).read_bytes()),
            "disabled_nl_html": _sha256_bytes((evidence_dir / "disabled" / NL_HTML).read_bytes()),
            "enabled_en_html": _sha256_bytes((evidence_dir / "enabled" / EN_HTML).read_bytes()),
            "enabled_nl_html": _sha256_bytes((evidence_dir / "enabled" / NL_HTML).read_bytes()),
            "enabled_en_pdf": _sha256_bytes((evidence_dir / "enabled" / EN_PDF).read_bytes()),
            "enabled_nl_pdf": _sha256_bytes((evidence_dir / "enabled" / NL_PDF).read_bytes()),
        },
    }
    assert all(evidence["disabled_html_byte_identical"].values())

    evidence_path = evidence_dir / "cockpit_wp10_additive_delivery_front_page_260714.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return evidence_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate WP10 additive cockpit delivery integration without sending email.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--work-root", default="/tmp/weekly-etf-wp10")
    parser.add_argument("--evidence-dir", default="output/wp10_validation")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    validate(
        repo_root=Path(args.repo_root).resolve(),
        work_root=Path(args.work_root).resolve(),
        evidence_dir=Path(args.evidence_dir).resolve(),
    )


if __name__ == "__main__":
    main()
