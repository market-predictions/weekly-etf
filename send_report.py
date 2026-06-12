from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import smtplib
import ssl
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import etf
from runtime.execution_delivery_manifest import build_etf_delivery_manifest
from runtime.inject_etf_replacement_duel_v2 import inject_replacement_duel
from runtime.macro_report_pre_send_guard import validate_macro_report_pre_send
from tools.validate_etf_bilingual_pair import validate_bilingual_numeric_parity, validate_bilingual_pair
from tools.validate_etf_report_breadth_proof import validate_report_breadth_proof
from tools.validate_etf_report_content_contract import validate_required_report

try:
    import markdown as markdown_lib
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'markdown' package is required. Install with: pip install markdown") from exc
try:
    from weasyprint import HTML
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'weasyprint' package is required. Install with: pip install weasyprint") from exc

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "output"))
SMTP_HOST = os.environ.get("SMTP_HOST", "mail.smtp2go.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "2525"))
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@example.com")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
EMAIL_SUBJECT = os.environ.get("EMAIL_SUBJECT", "Weekly ETF Review")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
MARKDOWN = markdown_lib.Markdown(extensions=["tables", "fenced_code"])
PDF_REPORT_CSS = """
<style>
  @page { size: A4; margin: 12mm 11mm; }
  body { font-family: Arial, sans-serif; color: #111; font-size: 10.5px; line-height: 1.28; }
  h1 { font-size: 22px; margin: 0 0 8px 0; }
  h2 { font-size: 14px; margin: 14px 0 7px; page-break-after: avoid; }
  h3 { font-size: 12px; margin: 10px 0 5px; page-break-after: avoid; }
  p { margin: 4px 0; }
  ul, ol { margin: 4px 0 7px 17px; padding: 0; }
  li { margin: 2px 0; }
  table { border-collapse: collapse; width: 100%; margin: 6px 0 9px; page-break-inside: avoid; }
  th, td { border: 1px solid #d7d7d7; padding: 4px 5px; vertical-align: top; }
  th { background: #f1f3f5; }
  img { max-width: 100%; height: auto; margin: 8px 0 10px; }
  .small { color: #555; font-size: 9px; }
</style>
"""


def html_to_plain_text(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ")


def normalize_report_mode(mode: str | None) -> str:
    raw = (mode or os.environ.get("MRKT_RPRTS_REPORT_MODE") or "standard").strip().lower()
    if raw in {"pro", "professional"}:
        return "pro"
    return "standard"


def _latest_matching(pattern: str) -> list[Path]:
    return sorted(OUTPUT_DIR.glob(pattern))


def latest_report_file(output_dir: Path, mode: str = "standard") -> Path:
    mode = normalize_report_mode(mode)
    patterns = ["weekly_analysis_pro_*.md"] if mode == "pro" else ["weekly_analysis_*.md"]
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(p for p in sorted(output_dir.glob(pattern)) if "_nl_" not in p.name)
    if not candidates:
        raise RuntimeError(f"No report markdown files found in {output_dir} for mode={mode}.")
    return candidates[-1]


def latest_reports_by_day(output_dir: Path, mode: str = "standard") -> list[Path]:
    mode = normalize_report_mode(mode)
    pattern = "weekly_analysis_pro_*.md" if mode == "pro" else "weekly_analysis_*.md"
    by_day: dict[str, Path] = {}
    for path in sorted(output_dir.glob(pattern)):
        if "_nl_" in path.name or path.name.endswith("_clean.md"):
            continue
        match = re.search(r"_(\d{6})(?:_\d+)?\.md$", path.name)
        if not match:
            continue
        by_day[match.group(1)] = path
    return [by_day[key] for key in sorted(by_day)]


def parse_report_date(md_text: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", line)
            if match:
                return match.group(1)
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", md_text)
    if match:
        return match.group(1)
    raise RuntimeError("Could not determine report date from markdown title/body.")


def strip_citations(md_text: str) -> str:
    return re.sub(r"\[Source:[^\]]+\]", "", md_text)


def normalize_markdown_text(md_text: str) -> str:
    normalized = md_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip() + "\n"


def extract_sections(md_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "preamble"
    buffer: list[str] = []
    for line in md_text.splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    sections[current] = "\n".join(buffer).strip()
    return sections


def extract_section_by_number(md_text: str, number: int) -> str:
    pattern = re.compile(rf"^##\s+{number}(?:\.|\b).*", re.MULTILINE)
    match = pattern.search(md_text)
    if not match:
        return ""
    next_match = re.search(r"^##\s+\d+(?:\.|\b).*", md_text[match.end():], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(md_text)
    return md_text[match.start():end]


def parse_markdown_table(section: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == len(headers):
            rows.append(cells)
    return headers, rows


def _num(text: str) -> float | None:
    cleaned = re.sub(r"[^0-9,.-]", "", text).replace(",", "")
    if cleaned in {"", ".", "-", "--"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_section15_totals(md_text: str) -> dict[str, float]:
    section = extract_section_by_number(md_text, 15)
    totals: dict[str, float] = {}
    for line in section.splitlines():
        if ":" not in line:
            continue
        label, value = line.split(":", 1)
        val = _num(value)
        if val is not None:
            totals[label.strip(" -*")] = val
    return totals


def parse_section15_totals_generic(md_text: str) -> dict[str, float]:
    totals = parse_section15_totals(md_text)
    generic: dict[str, float] = {}
    for key, val in totals.items():
        lower = key.lower()
        for canonical, aliases in SECTION15_LABEL_ALIASES.items():
            if lower == canonical.lower() or lower in aliases:
                generic[canonical] = val
    return generic


def parse_section15_positions(md_text: str) -> list[dict[str, float | str]]:
    section = extract_section_by_number(md_text, 15)
    headers, rows = parse_markdown_table(section)
    if not headers:
        return []
    out = []
    for row in rows:
        item = {headers[i]: row[i] for i in range(len(headers))}
        out.append(item)
    return out


def parse_section15_positions_generic(md_text: str) -> list[dict[str, float | str]]:
    section = extract_section_by_number(md_text, 15)
    headers, rows = parse_markdown_table(section)
    if not headers:
        return []
    normalized_headers = []
    for header in headers:
        lower = header.strip().lower()
        canonical = next((name for name, aliases in SECTION15_HEADER_ALIASES.items() if lower == name.lower() or lower in aliases), header.strip())
        normalized_headers.append(canonical)
    return [{normalized_headers[i]: row[i] for i in range(len(normalized_headers))} for row in rows]


def parse_section7_equity_points(md_text: str) -> list[tuple[str, float]]:
    section = extract_section_by_number(md_text, 7)
    headers, rows = parse_markdown_table(section)
    if not headers:
        return []
    date_idx = 0
    value_idx = 1 if len(headers) > 1 else -1
    points = []
    for row in rows:
        date = row[date_idx]
        value = _num(row[value_idx]) if value_idx >= 0 else None
        if re.match(r"20\d{2}-\d{2}-\d{2}", date) and value is not None:
            points.append((date[:10], value))
    return points


def parse_section7_equity_points_generic(md_text: str) -> list[tuple[str, float]]:
    section = extract_section_by_number(md_text, 7)
    headers, rows = parse_markdown_table(section)
    if not headers:
        return []
    normalized_headers = []
    for header in headers:
        lower = header.strip().lower()
        canonical = next((name for name, aliases in SECTION7_HEADER_ALIASES.items() if lower == name.lower() or lower in aliases), header.strip())
        normalized_headers.append(canonical)
    date_idx = normalized_headers.index("date") if "date" in normalized_headers else 0
    value_idx = normalized_headers.index("portfolio value (eur)") if "portfolio value (eur)" in normalized_headers else (1 if len(normalized_headers) > 1 else -1)
    points = []
    for row in rows:
        date = row[date_idx]
        value = _num(row[value_idx]) if value_idx >= 0 else None
        if re.match(r"20\d{2}-\d{2}-\d{2}", date) and value is not None:
            points.append((date[:10], value))
    return points
