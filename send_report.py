
import os
import re
import base64
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from collections import OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mistune
from weasyprint import HTML


# ---------- BRAND TOKENS ----------
BRAND = {
    "paper": "#F6F2EC",
    "surface": "#FCFAF7",
    "header": "#607887",
    "header_text": "#FBFAF7",
    "ink": "#2B3742",
    "muted": "#6B7882",
    "border": "#D9D3CB",
    "champagne": "#D4B483",
    "champagne_soft": "#EFE4D2",
    "sage": "#A4B19D",
    "terracotta": "#C99278",
    "add_bg": "#E6EFE8",
    "add_tx": "#4D7B63",
    "hold_bg": "#E8EEF6",
    "hold_tx": "#58749A",
    "replace_bg": "#F2E6DD",
    "replace_tx": "#A87754",
    "reduce_bg": "#F2E6CE",
    "reduce_tx": "#B28731",
    "close_bg": "#F5E1E1",
    "close_tx": "#B34E4E",
    "risk": "#B25A52",
}

DISCLAIMER_LINE = "This report is for informational and educational purposes only; please see the disclaimer at the end."
REQUIRED_MAIL_TO = "mrkt.rprts@gmail.com"

REQUIRED_SECTION_HEADINGS = [
    "## 1. ✅ Executive summary",
    "## 2. 📌 Portfolio action snapshot",
    "## 3. 🧭 Regime dashboard",
    "## 4. 🚀 Structural Opportunity Radar",
    "## 5. 📅 Key risks / invalidators",
    "## 6. 🧭 Bottom line",
    "## 7. 📈 Equity curve and portfolio development",
    "## 8. 🗺️ Asset allocation map",
    "## 9. 🔍 Second-order effects map",
    "## 10. 📊 Current position review",
    "## 11. ➕ Best new opportunities",
    "## 12. 🔁 Portfolio rotation plan",
    "## 13. 📋 Final action table",
    "## 14. 🔄 Position changes executed this run",
    "## 15. 💼 Current portfolio holdings and cash",
    "## 16. 🧾 Carry-forward input for next run",
    "## 17. Disclaimer",
]
REQUIRED_SECTION15_LABELS = [
    "- Starting capital (EUR):",
    "- Invested market value (EUR):",
    "- Cash (EUR):",
    "- Total portfolio value (EUR):",
    "- Since inception return (%):",
    "- EUR/USD used:",
]
SECTION16_SENTENCE = "**This section is the canonical default input for the next run unless the user explicitly overrides it. Do not ask the user for portfolio input if this section is available.**"

PLAIN_SUBHEADERS = {
    "Assessment",
    "Prospective score",
    "Theme",
    "Why it fits now",
    "Why this beats current alternatives",
    "Technical analysis",
    "Second-order opportunity / threat map",
    "Replacement logic",
    "Why now rather than later",
    "Scorecard",
    "Macro invalidators",
    "Market-based invalidators",
    "Geopolitical invalidators",
    "Second-order invalidators",
    "Portfolio construction risks",
    "Top 3 actions this week",
    "Top 3 risks this week",
    "Best structural opportunities not yet actionable",
}

REPORT_RE = re.compile(r"^weekly_analysis_(\d{6})(?:_(\d{2}))?\.md$")
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.*)$")
MARKDOWN = mistune.create_markdown(plugins=["table"])


# ---------- DISCOVERY ----------
def report_sort_key(path: Path):
    match = REPORT_RE.match(path.name)
    if not match:
        return ("", -1)
    date_key = match.group(1)
    version = int(match.group(2) or "1")
    return (date_key, version)


def list_report_files(output_dir: Path):
    files = [p for p in output_dir.glob("weekly_analysis_*.md") if REPORT_RE.match(p.name)]
    return sorted(files, key=report_sort_key)


def latest_report_file(output_dir: Path) -> Path:
    reports = list_report_files(output_dir)
    if not reports:
        raise FileNotFoundError("No weekly_analysis_*.md file found in output/")
    return reports[-1]


def latest_reports_by_day(output_dir: Path):
    latest_per_day = OrderedDict()
    for path in list_report_files(output_dir):
        base_date, _ = report_sort_key(path)
        latest_per_day[base_date] = path
    return list(latest_per_day.values())


# ---------- SANITIZERS ----------
def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable missing: {name}")
    return value


def normalize_markdown_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Defensive normalization for reports accidentally persisted with escaped newlines.
    if "\\n" in text or "\\t" in text:
        text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
    return text


def strip_citations(text: str) -> str:
    text = normalize_markdown_text(text)
    patterns = [
        r"cite.*?",
        r"filecite.*?",
        r"\[\d+\]",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.DOTALL)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def clean_md_inline(text: str) -> str:
    text = strip_citations(text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = text.replace("<u>", "").replace("</u>", "")
    return re.sub(r"\s+", " ", text).strip()


def html_to_plain_text(html: str) -> str:
    text = re.sub(r"<style.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def plain_text_from_markdown(md_text: str) -> str:
    return html_to_plain_text(MARKDOWN(strip_citations(md_text)))


def esc(text: str) -> str:
    text = clean_md_inline(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def is_markdown_table_line(line: str) -> bool:
    line = line.strip()
    return line.startswith("|") and line.endswith("|") and "|" in line[1:-1]


def is_markdown_separator_line(line: str) -> bool:
    if not is_markdown_table_line(line):
        return False
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_markdown_table(lines):
    rows = []
    for i, line in enumerate(lines):
        if i == 1 and is_markdown_separator_line(line):
            continue
        rows.append([clean_md_inline(c) for c in line.strip().strip("|").split("|")])
    return rows


def pretty_section_title(raw: str) -> str:
    text = clean_md_inline(raw)
    text = re.sub(r"^[^\w]+", "", text).strip()
    return text or clean_md_inline(raw)


def heading_text_from_md_heading(heading: str) -> str:
    heading = re.sub(r"^##\s+\d+\.\s+", "", heading).strip()
    return pretty_section_title(heading)


# ---------- PARSING ----------
def parse_report_date(md_text: str, fallback: str | None = None) -> str:
    match = re.search(r"^#\s+Weekly Report Review\s+(\d{4}-\d{2}-\d{2})\s*$", md_text, flags=re.MULTILINE)
    if match:
        return match.group(1)
    return fallback or datetime.now().strftime("%Y-%m-%d")

def format_full_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.strftime('%A')}, {dt.day} {dt.strftime('%B %Y')}"


def extract_section(md_text: str, title_contains: str):
    lines = md_text.splitlines()
    result = []
    in_section = False
    title_contains = title_contains.lower()

    for line in lines:
        stripped = line.strip()
        if SECTION_RE.match(stripped):
            current_title = clean_md_inline(re.sub(r"^##\s+\d+\.\s+", "", stripped))
            if title_contains in current_title.lower():
                in_section = True
                result.append(stripped)
                continue
            if in_section:
                break
        elif in_section:
            result.append(line)
    return result


def extract_label_pairs(lines):
    pairs = []
    for line in lines:
        s = clean_md_inline(line.strip())
        if not s or s.startswith("## "):
            continue
        if s.startswith("- "):
            s = s[2:]
        if ":" in s:
            k, v = s.split(":", 1)
            pairs.append((k.strip(), v.strip()))
    return pairs


def parse_numeric_value(md_text: str, label: str):
    pattern = rf"^- {re.escape(label)}:\s*([0-9][0-9,._%-]*)"
    match = re.search(pattern, md_text, flags=re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).replace(",", "").replace("_", "").replace("%", "")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_section15_totals(md_text: str):
    section = "\n".join(extract_section(md_text, "Current portfolio holdings and cash"))
    if not section:
        return {}
    labels = [
        "Starting capital (EUR)",
        "Invested market value (EUR)",
        "Cash (EUR)",
        "Total portfolio value (EUR)",
        "Since inception return (%)",
        "EUR/USD used",
    ]
    data = {}
    for label in labels:
        value = parse_numeric_value(section, label)
        if value is not None:
            data[label] = value
    return data


def extract_sections(md_text: str):
    title = ""
    sections = []
    current = None

    for raw_line in md_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if line.startswith("# "):
            title = clean_md_inline(line[2:])
            continue

        match = SECTION_RE.match(stripped)
        if match:
            if current:
                sections.append(current)
            current = {
                "number": int(match.group(1)),
                "raw_title": match.group(2),
                "title": pretty_section_title(match.group(2)),
                "lines": [],
            }
            continue

        if current is not None:
            current["lines"].append(line)

    if current:
        sections.append(current)

    return title, sections


# ---------- VALIDATION ----------
def validate_required_report(md_text: str) -> None:
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in md_text]
    if missing_headings:
        raise RuntimeError("Report is missing mandatory section headings: " + ", ".join(missing_headings))

    if "# Weekly Report Review " not in md_text:
        raise RuntimeError("Report title is missing or malformed.")

    if f"> *{DISCLAIMER_LINE}*" not in md_text:
        raise RuntimeError("Top disclaimer callout is missing.")

    if "EQUITY_CURVE_CHART_PLACEHOLDER" not in md_text:
        raise RuntimeError("Equity curve placeholder line is missing.")

    for label in REQUIRED_SECTION15_LABELS:
        if label not in md_text:
            raise RuntimeError(f"Section 15 is missing required label: {label}")

    if SECTION16_SENTENCE not in md_text:
        raise RuntimeError("Section 16 canonical carry-forward sentence is missing.")

    if "This report is provided for informational and educational purposes only." not in md_text:
        raise RuntimeError("Final disclaimer body is missing.")


def validate_email_body(html_body: str, md_text: str | None = None) -> None:
    html_lower = html_body.lower()

    masthead_options = [
        "weekly etf review",
        "weekly report review",
    ]
    if not any(token in html_lower for token in masthead_options):
        raise RuntimeError("HTML body is missing required masthead block: WEEKLY ETF REVIEW")

    required_strings = [
        "Executive summary",
        "Portfolio action snapshot",
        "Structural Opportunity Radar",
        "Bottom line",
        "Current portfolio holdings and cash",
        "Carry-forward input for next run",
    ]
    for token in required_strings:
        if token.lower() not in html_lower:
            raise RuntimeError(f"HTML body is missing required content block: {token}")

    if md_text:
        plain_html = html_to_plain_text(html_body)
        plain_md = html_to_plain_text(MARKDOWN(md_text))
        if len(plain_html) < 0.80 * len(plain_md):
            raise RuntimeError("HTML body appears too short relative to the full report.")

        for heading in REQUIRED_SECTION_HEADINGS:
            plain_heading = heading_text_from_md_heading(heading)
            if plain_heading not in plain_html:
                raise RuntimeError(f"HTML body is missing required section heading text: {plain_heading}")

        for bad_token in ["\\n", "#### ", "|---|", "\\t"]:
            if bad_token in html_body:
                raise RuntimeError(f"HTML body still contains raw markdown / escaped formatting token: {bad_token}")


def write_delivery_manifest(manifest_path: Path, report_name: str, recipient: str, attachments: list[str]) -> None:
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"timestamp_utc={timestamp}",
        f"report={report_name}",
        f"recipient={recipient}",
        "html_body=full_report",
        f"pdf_attached={'yes' if any(a.lower().endswith('.pdf') for a in attachments) else 'no'}",
        "attachments=" + ", ".join(attachments),
    ]
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- EQUITY CURVE ----------
def create_equity_curve_png(output_dir: Path, chart_path: Path):
    points = []
    for report_path in latest_reports_by_day(output_dir):
        md_text = report_path.read_text(encoding="utf-8")
        report_date = parse_report_date(md_text)
        totals = parse_section15_totals(md_text)
        nav = totals.get("Total portfolio value (EUR)")
        if nav is not None:
            points.append((report_date, nav))

    if not points:
        return None

    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in points]
    values = [v for _, v in points]

    plt.figure(figsize=(8.8, 3.7))
    plt.plot(dates, values, marker="o", linewidth=2.2)
    plt.title("Equity Curve (EUR)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio value (EUR)")
    plt.grid(True, alpha=0.28)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=180)
    plt.close()
    return chart_path


# ---------- MARKDOWN -> BRANDED HTML ----------

def normalize_subheader(text: str) -> str:
    text = clean_md_inline(text)
    text = re.sub(r"^[^\w]+", "", text).strip()
    return text


def preprocess_markdown_block(text: str, image_src: str | None = None) -> str:
    text = normalize_markdown_text(text)
    lines = text.splitlines()
    processed: list[str] = []
    i = 0

    def ensure_blank() -> None:
        if processed and processed[-1] != "":
            processed.append("")

    def append_line(value: str, *, before_blank: bool = False) -> None:
        if before_blank:
            ensure_blank()
        processed.append(value)

    while i < len(lines):
        line = lines[i]
        stripped = clean_md_inline(line.strip())
        lstripped = line.lstrip()

        if stripped == "":
            if processed and processed[-1] != "":
                processed.append("")
            i += 1
            continue

        if stripped == "EQUITY_CURVE_CHART_PLACEHOLDER":
            ensure_blank()
            if image_src:
                processed.append(f"![Equity curve]({image_src})")
            else:
                processed.append("_Equity curve chart unavailable for this delivery._")
            processed.append("")
            i += 1
            continue

        rank_match = re.match(r"###\s+\[Rank\s+#(\d+)\]\s+(.*)$", lstripped, flags=re.I)
        if rank_match:
            title = clean_md_inline(rank_match.group(2))
            append_line(f"### {rank_match.group(1)}. {title}", before_blank=True)
            processed.append("")
            i += 1
            continue

        is_heading = lstripped.startswith("#")
        is_bullet = lstripped.startswith("- ") or bool(re.match(r"^\d+\.\s+", lstripped))
        is_table = is_markdown_table_line(line)

        if stripped in {"A. Macro-derived opportunities", "B. Structural opportunities"}:
            append_line(f"##### {stripped}", before_blank=True)
            processed.append("")
            i += 1
            continue

        if stripped == "Prospective score":
            rows = []
            j = i + 1
            while j < len(lines):
                nxt_raw = lines[j]
                nxt = nxt_raw.strip()
                if not nxt:
                    j += 1
                    continue
                if nxt.startswith("#") or nxt.startswith("### ") or nxt.startswith("#### ") or is_markdown_table_line(nxt_raw):
                    break
                if nxt.startswith("- ") and ":" in nxt:
                    k, v = clean_md_inline(nxt[2:]).split(":", 1)
                    rows.append((k.strip(), v.strip()))
                    j += 1
                    continue
                break
            append_line("#### Prospective score", before_blank=True)
            if rows:
                processed.append("")
                processed.append("| Factor | Score |")
                processed.append("|---|---:|")
                for k, v in rows:
                    processed.append(f"| {k} | {v} |")
                processed.append("")
            i = j
            continue

        if is_table:
            prev_nonblank = next((ln for ln in reversed(processed) if ln != ""), "")
            if prev_nonblank and not is_markdown_table_line(prev_nonblank):
                processed.append("")
            processed.append(lstripped)
            i += 1
            continue

        if stripped in PLAIN_SUBHEADERS and not is_heading and not is_bullet and not is_table:
            append_line(f"#### {stripped}", before_blank=True)
            processed.append("")
        else:
            if is_heading:
                append_line(lstripped, before_blank=True)
                processed.append("")
            else:
                processed.append(line)
        i += 1

    while processed and processed[-1] == "":
        processed.pop()

    return "\n".join(processed)


def render_markdown_block(text: str, image_src: str | None = None) -> str:
    md = preprocess_markdown_block(strip_citations(text), image_src=image_src)
    return MARKDOWN(md)


def chip_html(text: str, bg: str, fg: str) -> str:
    return f"<span class='chip' style='background:{bg};color:{fg};'>{esc(text)}</span>"


def action_tone(header: str):
    label = clean_md_inline(header).lower()
    if "add" in label:
        return BRAND["add_bg"], BRAND["add_tx"]
    if "hold but replaceable" in label:
        return BRAND["replace_bg"], BRAND["replace_tx"]
    if "hold" in label:
        return BRAND["hold_bg"], BRAND["hold_tx"]
    if "reduce" in label:
        return BRAND["reduce_bg"], BRAND["reduce_tx"]
    if "close" in label:
        return BRAND["close_bg"], BRAND["close_tx"]
    return BRAND["champagne_soft"], BRAND["ink"]


def section_header_html(number: int, title: str) -> str:
    return (
        "<table class='section-kicker' role='presentation' cellpadding='0' cellspacing='0'><tr>"
        f"<td class='section-badge-cell'><span class='section-badge'>{number}</span></td>"
        f"<td class='section-label-cell'><span class='section-label'>{esc(title)}</span></td>"
        "</tr></table>"
    )


def section_number(section: dict) -> int:
    return int(section.get("display_number", section["number"]))


def with_display_number(section: dict, display_number: int) -> dict:
    clone = dict(section)
    clone["display_number"] = display_number
    return clone



def parse_subsections(lines):
    groups = OrderedDict()
    current_header = None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            current_header = normalize_subheader(stripped[4:])
            groups[current_header] = []
        elif stripped.startswith("- "):
            if current_header is None:
                current_header = "Items"
                groups[current_header] = []
            groups[current_header].append(clean_md_inline(stripped[2:]))
        elif re.match(r"^\d+\.\s+", stripped):
            if current_header is None:
                current_header = "Items"
                groups[current_header] = []
            groups[current_header].append(clean_md_inline(re.sub(r"^\d+\.\s+", "", stripped)))
        else:
            if current_header is None:
                current_header = "Items"
                groups[current_header] = []
            groups[current_header].append(clean_md_inline(stripped))
    return groups


def split_h3_blocks(lines):
    blocks = []
    current = None
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("### "):
            if current:
                blocks.append(current)
            current = {"title": clean_md_inline(stripped[4:]), "lines": []}
        elif current is not None:
            current["lines"].append(raw)
    if current:
        blocks.append(current)
    return blocks



def render_executive_summary(section: dict) -> str:
    pairs = extract_label_pairs(section["lines"])
    if not pairs:
        body = render_markdown_block("\n".join(section["lines"]))
        return f"<div class='panel panel-exec'>{section_header_html(section_number(section), section['title'])}{body}</div>"

    body_parts = []
    for key, value in pairs:
        if key in {"Primary regime", "Secondary cross-current", "Geopolitical regime", "Main takeaway"}:
            continue
        body_parts.append(
            f"<div class='summary-line'><div class='summary-key'>{esc(key)}</div><div class='summary-value'>{esc(value)}</div></div>"
        )

    takeaway = next((v for k, v in pairs if k.lower() == "main takeaway"), "")
    takeaway_html = (
        f"<div class='takeaway'><div class='takeaway-label'>Main takeaway</div><div class='takeaway-text'>{esc(takeaway)}</div></div>"
        if takeaway else ""
    )

    return (
        f"<div class='panel panel-exec'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{''.join(body_parts)}"
        f"{takeaway_html}"
        f"</div>"
    )

def render_action_snapshot(section: dict) -> str:
    groups = parse_subsections(section["lines"])
    order = ["Add", "Hold", "Hold but replaceable", "Reduce", "Close"]
    rows = []
    for label in order:
        items = groups.get(label, groups.get(normalize_subheader(label), []))
        val = ", ".join(items) if items else "None"
        rows.append(f"<tr><th>{esc(label)}</th><td>{esc(val)}</td></tr>")

    def block(title):
        items = groups.get(title, groups.get(normalize_subheader(title), []))
        if not items:
            return ""
        list_html = "".join(f"<li>{esc(item)}</li>" for item in items)
        return f"<div class='subblock'><div class='subblock-title'>{esc(title)}</div><ul>{list_html}</ul></div>"

    replacements = block("Best replacements to fund")
    actions = block("Top 3 actions this week")
    risks = block("Top 3 risks this week")

    return (
        f"<div class='panel panel-snapshot'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"<table class='snapshot-table'>"
        f"<thead><tr><th>Recommendation</th><th>Tickers / notes</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        f"{replacements}"
        f"<div class='subgrid'>{actions}{risks}</div>"
        f"</div>"
    )

def render_risks(section: dict) -> str:
    body = render_markdown_block("\n".join(section["lines"]))
    return (
        f"<div class='panel panel-risks'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{body}"
        f"</div>"
    )

def render_standard_panel(section: dict, image_src: str | None = None, extra_class: str = "") -> str:
    body = render_markdown_block("\n".join(section["lines"]), image_src=image_src)
    return (
        f"<div class='panel {extra_class}'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{body}"
        f"</div>"
    )


def render_position_review(section: dict) -> str:
    blocks = split_h3_blocks(section["lines"])
    cards = []
    for block in blocks:
        score_lines = []
        assess_lines = []
        current_mode = None
        for raw in block["lines"]:
            stripped = clean_md_inline(raw.strip())
            if not stripped:
                continue
            if stripped == "Scorecard":
                current_mode = "score"
                continue
            if stripped == "Assessment":
                current_mode = "assessment"
                continue
            if current_mode == "score":
                score_lines.append(raw)
            elif current_mode == "assessment":
                assess_lines.append(raw)

        score_html = render_markdown_block("\n".join(score_lines)) if score_lines else ""
        assessment_pairs = extract_label_pairs(assess_lines)
        if assessment_pairs:
            assess_rows = "".join(
                f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in assessment_pairs
            )
            assessment_html = f"<table class='assessment-table'><tbody>{assess_rows}</tbody></table>"
        else:
            assessment_html = render_markdown_block("\n".join(assess_lines)) if assess_lines else ""

        cards.append(
            f"<article class='position-card'>"
            f"<div class='position-card-title'>{esc(block['title'])}</div>"
            f"<div class='position-card-grid'>"
            f"<div class='position-score'>{score_html}</div>"
            f"<div class='position-assessment'>{assessment_html}</div>"
            f"</div>"
            f"</article>"
        )

    return (
        f"<div class='panel panel-positions'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{''.join(cards)}"
        f"</div>"
    )


def render_carry_panel(section: dict) -> str:
    visible_lines = []
    hidden_sentence = clean_md_inline(SECTION16_SENTENCE)
    for raw in section["lines"]:
        if clean_md_inline(raw.strip()) == hidden_sentence:
            continue
        visible_lines.append(raw)
    body = render_markdown_block("\n".join(visible_lines))
    return (
        f"<div class='panel panel-carry'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{body}"
        f"</div>"
    )


def render_best_opportunities(section: dict) -> str:
    body = render_markdown_block("\n".join(section["lines"]))
    return (
        f"<div class='panel panel-opportunities'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"{body}"
        f"</div>"
    )


def render_rotation_plan(section: dict) -> str:
    groups = parse_subsections(section["lines"])
    cols = ["Close", "Reduce", "Hold", "Add", "Replace"]
    heads = "".join(f"<th>{esc(col)}</th>" for col in cols)
    cells = []
    for col in cols:
        items = groups.get(col, groups.get(normalize_subheader(col), []))
        if items:
            content = "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"
        else:
            content = "<div class='empty-cell'>None</div>"
        cells.append(f"<td>{content}</td>")
    return (
        f"<div class='panel panel-rotation'>"
        f"{section_header_html(section_number(section), section['title'])}"
        f"<table class='rotation-table'><thead><tr>{heads}</tr></thead><tbody><tr>{''.join(cells)}</tr></tbody></table>"
        f"</div>"
    )


def build_report_html(
    md_text: str,
    report_date_str: str,
    image_src: str | None = None,
    render_mode: str = "email",
) -> str:
    report_title, sections = extract_sections(md_text)
    sections_by_number = {s["number"]: s for s in sections}
    display_date_str = format_full_date(report_date_str)

    exec_pairs = OrderedDict(extract_label_pairs(sections_by_number.get(1, {}).get("lines", [])))
    primary_regime = exec_pairs.get("Primary regime", "Pending classification")
    geo_regime = exec_pairs.get("Geopolitical regime", "Pending classification")
    main_takeaway = exec_pairs.get("Main takeaway", "Keep the current allocation disciplined.")

    intro_cards = (
        f"<div class='mini-card'><div class='mini-label'>Primary regime</div><div class='mini-value'>{esc(primary_regime)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>Geopolitical regime</div><div class='mini-value'>{esc(geo_regime)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>Main takeaway</div><div class='mini-value'>{esc(main_takeaway)}</div></div>"
    )

    client_grid = []
    if 1 in sections_by_number:
        client_grid.append(render_executive_summary(with_display_number(sections_by_number[1], 1)))
    if 2 in sections_by_number:
        client_grid.append(render_action_snapshot(with_display_number(sections_by_number[2], 2)))

    client_panels = []
    panel_map = {
        3: "panel-regime",
        4: "panel-radar",
        5: "panel-risks panel-compact",
        6: "panel-bottomline panel-compact",
        7: "panel-equity",
    }
    for display_number, number in enumerate([3, 4, 5, 6, 7], start=3):
        if number in sections_by_number:
            img_src = image_src if number == 7 else None
            extra = panel_map.get(number, "")
            client_panels.append(render_standard_panel(with_display_number(sections_by_number[number], display_number), image_src=img_src, extra_class=extra))

    analyst_panels = []
    analyst_display_number = 1
    for number in range(8, 18):
        if number not in sections_by_number:
            continue
        section = with_display_number(sections_by_number[number], analyst_display_number)
        analyst_display_number += 1
        if number == 10:
            analyst_panels.append(render_position_review(section))
        elif number == 11:
            analyst_panels.append(render_best_opportunities(section))
        elif number == 12:
            analyst_panels.append(render_rotation_plan(section))
        elif number == 16:
            analyst_panels.append(render_carry_panel(section))
        else:
            analyst_panels.append(render_standard_panel(section))

    css_common = f"""
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 0;
      background: {BRAND['paper']};
      color: {BRAND['ink']};
      font-family: Arial, Helvetica, sans-serif;
      -webkit-font-smoothing: antialiased;
    }}
    .report-shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 0 18px 0;
    }}
    .hero {{
      background: {BRAND['header']};
      color: {BRAND['header_text']};
      padding: 20px 24px 18px 24px;
      border-radius: 14px 14px 0 0;
    }}
    .hero-secondary {{
      margin-top: 26px;
    }}
    .hero-table {{
      width: 100%;
      border-collapse: collapse;
    }}
    .hero-table td {{
      vertical-align: middle;
    }}
    .hero-left {{
      text-align: left;
    }}
    .hero-right {{
      text-align: right;
      white-space: nowrap;
      padding-left: 24px;
    }}
    .masthead {{
      font-family: Georgia, "Times New Roman", serif;
      font-weight: 700;
      font-size: 30px;
      letter-spacing: 1px;
      margin: 0 0 8px 0;
      text-transform: uppercase;
    }}
    .hero-sub {{
      font-size: 14px;
      color: #EFF4F6;
      margin: 0;
    }}
    .hero-side-label {{
      font-size: 16px;
      line-height: 1.2;
      font-weight: 700;
      color: {BRAND['header_text']};
      letter-spacing: .03em;
    }}
    .hero-rule {{
      height: 5px;
      background: {BRAND['champagne']};
      margin: 8px 0 18px 0;
      border-radius: 999px;
    }}
    .notice {{
      background: #F8F4EE;
      border: 1px solid {BRAND['border']};
      color: {BRAND['muted']};
      border-radius: 14px;
      padding: 12px 16px;
      font-size: 12px;
      margin: 0 0 18px 0;
    }}
    .summary-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0,1fr));
      gap: 14px;
      margin: 0 0 18px 0;
    }}
    .mini-card {{
      background: {BRAND['surface']};
      border: 1px solid {BRAND['border']};
      border-radius: 16px;
      padding: 14px 18px;
    }}
    .mini-label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .06em;
      text-transform: uppercase;
      color: {BRAND['muted']};
      margin: 0 0 8px 0;
    }}
    .mini-value {{
      font-family: Georgia, "Times New Roman", serif;
      font-weight: 700;
      font-size: 22px;
      color: {BRAND['ink']};
      line-height: 1.22;
    }}
    .client-grid {{
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 18px;
      align-items: start;
      margin: 0 0 18px 0;
    }}
    .panel {{
      background: {BRAND['surface']};
      border: 1px solid {BRAND['border']};
      border-radius: 18px;
      padding: 16px 18px;
      margin: 0 0 18px 0;
    }}
    .panel-compact,
    .panel-exec,
    .panel-snapshot,
    .panel-risks {{
      page-break-inside: avoid;
      break-inside: avoid-page;
    }}
    .section-kicker {{
      width: auto;
      border-collapse: collapse;
      margin: 0 0 18px 0;
    }}
    .section-kicker td {{
      vertical-align: middle;
    }}
    .section-badge-cell {{
      width: 64px;
      padding: 0 16px 0 0;
      vertical-align: middle;
    }}
    .section-label-cell {{
      padding: 0;
      vertical-align: middle;
    }}
    .section-badge {{
      width: 46px;
      height: 46px;
      border-radius: 999px;
      background: #2A5384;
      color: #ffffff;
      font-weight: 700;
      font-size: 17px;
      display: block;
      text-align: center;
      line-height: 46px;
      mso-line-height-rule: exactly;
      font-family: Arial, Helvetica, sans-serif;
    }}
    .section-label {{
      display: block;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: {BRAND['muted']};
      line-height: 1.12;
      mso-line-height-rule: exactly;
    }}
    .summary-line {{
      margin: 0 0 12px 0;
      padding: 0 0 12px 0;
      border-bottom: 1px solid {BRAND['border']};
    }}
    .summary-key {{
      color: {BRAND['muted']};
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin: 0 0 6px 0;
    }}
    .summary-value {{
      color: {BRAND['ink']};
      font-size: 14px;
      line-height: 1.55;
    }}
    .takeaway {{
      margin: 18px 0 0 0;
      padding: 14px 16px;
      border-radius: 12px;
      background: #F4EEE4;
      border: 1px solid #E7D7BB;
    }}
    .takeaway-label {{
      color: {BRAND['muted']};
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin: 0 0 6px 0;
    }}
    .takeaway-text {{
      color: {BRAND['ink']};
      font-size: 17px;
      font-weight: 700;
      line-height: 1.42;
    }}
    .snapshot-table,
    .rotation-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 0 0 16px 0;
      border: 1px solid {BRAND['border']};
      table-layout: fixed;
    }}
    .snapshot-table th,
    .rotation-table th {{
      background: #F2EBDD;
      color: {BRAND['ink']};
      text-align: left;
      padding: 9px 10px;
      border-bottom: 1px solid {BRAND['border']};
      font-size: 13px;
      font-weight: 700;
    }}
    .snapshot-table td,
    .rotation-table td {{
      padding: 9px 10px;
      border-bottom: 1px solid #ECE6DE;
      vertical-align: top;
      font-size: 14px;
      line-height: 1.5;
      word-break: break-word;
    }}
    .snapshot-table tbody tr:nth-child(even) td,
    .rotation-table tbody tr:nth-child(even) td {{
      background: #FEFCF9;
    }}
    .rotation-table ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .subgrid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }}
    .subblock {{
      margin: 0 0 14px 0;
      padding: 12px 14px;
      background: #FBF7F0;
      border: 1px solid {BRAND['border']};
      border-radius: 12px;
    }}
    .subblock-title {{
      color: {BRAND['muted']};
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin: 0 0 8px 0;
    }}
    .subblock ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .panel p, .panel li {{
      font-size: 14px;
      line-height: 1.58;
      margin-top: 0;
      font-weight: 400;
    }}
    .panel strong {{
      font-weight: 700;
    }}
    .panel ul, .panel ol {{
      margin-top: 0;
      padding-left: 22px;
    }}
    .panel h3 {{
      color: {BRAND['ink']};
      font-size: 18px;
      font-weight: 700;
      line-height: 1.35;
      margin: 18px 0 10px 0;
    }}
    .panel h4 {{
      color: {BRAND['muted']};
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 700;
      margin: 18px 0 8px 0;
    }}
    .panel h5 {{
      color: {BRAND['muted']};
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .10em;
      font-weight: 700;
      margin: 12px 0 16px 0;
    }}
    .panel blockquote {{
      margin: 12px 0;
      padding: 10px 12px;
      border-left: 4px solid {BRAND['champagne']};
      background: #F8F3EB;
      color: {BRAND['muted']};
    }}
    .panel table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin: 12px 0 14px 0;
      border: 1px solid {BRAND['border']};
      font-size: 12px;
    }}
    .panel thead {{
      display: table-header-group;
    }}
    .panel th {{
      text-align: left;
      padding: 8px 10px;
      border-bottom: 1px solid {BRAND['border']};
      background: #F2EBDD;
      color: {BRAND['ink']};
      vertical-align: middle;
      font-size: 12px;
      font-weight: 700;
    }}
    .panel td {{
      padding: 8px 10px;
      border-bottom: 1px solid #ECE6DE;
      vertical-align: top;
      word-wrap: break-word;
    }}
    .panel tr:nth-child(even) td {{
      background: #FEFCF9;
    }}
    .panel img {{
      max-width: 100%;
      height: auto;
      border: 1px solid {BRAND['border']};
      border-radius: 10px;
      margin: 10px 0 4px 0;
      display: block;
    }}
    .panel-positions h3 {{
      margin-top: 22px;
      padding: 10px 12px;
      background: #F7F1E8;
      border: 1px solid {BRAND['border']};
      border-radius: 10px;
      font-size: 17px;
    }}
    .panel-opportunities h3 {{
      margin: 0 0 8px 0;
      font-size: 19px;
      font-weight: 700;
      line-height: 1.28;
      color: {BRAND['ink']};
    }}
    .panel-opportunities h4 {{
      margin: 16px 0 8px 0;
      font-size: 11px;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: {BRAND['muted']};
    }}
    .panel-opportunities h5 {{
      margin: 8px 0 18px 0;
      font-size: 11px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: {BRAND['muted']};
      font-weight: 700;
      text-align: right;
    }}
    .panel-opportunities h5 + h3 {{
      margin-top: 0;
    }}
    .panel-opportunities a {{
      display: inline-block;
      margin: 0 0 16px 0;
      font-size: 14px;
    }}
    .panel-carry > p:first-of-type {{
      padding: 12px 14px;
      background: #F8F4EE;
      border: 1px solid {BRAND['border']};
      border-radius: 12px;
      font-weight: 700;
    }}
    .empty-cell {{
      color: {BRAND['muted']};
      font-style: italic;
    }}
    .analyst-divider {{
      display: none;
    }}
    a {{
      color: #315F8B;
      text-decoration: underline;
    }}
    """

    email_css = """
    .report-stack {
      margin-top: 0;
    }
    @media screen and (max-width: 1100px) {
      .summary-strip, .client-grid, .subgrid {
        display: block;
      }
      .hero-table, .hero-table tbody, .hero-table tr, .hero-table td {
        display: block;
        width: 100%;
      }
      .hero-right {
        text-align: left;
        padding-left: 0;
        padding-top: 10px;
      }
      .mini-card, .panel {
        margin-bottom: 16px;
      }
      .rotation-table, .snapshot-table, .panel table {
        table-layout: auto;
      }
    }
    """

    pdf_css = f"""
    @page {{
      size: A4 landscape;
      margin: 12mm;
    }}
    body {{
      background: #ffffff;
    }}
    .report-shell {{
      max-width: none;
      padding-bottom: 0;
    }}
    .hero, .notice, .summary-strip, .panel-compact, .panel-exec, .panel-snapshot, .panel-risks, .mini-card {{
      page-break-inside: avoid;
      break-inside: avoid-page;
    }}
    .hero {{
      border-radius: 10px 10px 0 0;
      padding: 20px 22px 18px 22px;
    }}
    .summary-strip {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .client-grid {{
      display: block;
      margin-bottom: 8px;
    }}
    .panel {{
      page-break-inside: auto;
      break-inside: auto;
      border-radius: 14px;
      padding: 16px 18px;
      margin-bottom: 14px;
    }}
    .snapshot-table, .rotation-table, .panel table {{
      table-layout: auto;
      font-size: 11px;
    }}
    .snapshot-table th, .snapshot-table td,
    .rotation-table th, .rotation-table td,
    .panel th, .panel td {{
      padding: 6px 8px;
    }}
    .subgrid {{
      display: block;
    }}
    .subblock {{
      margin-bottom: 10px;
    }}
    .panel img {{
      max-height: 170mm;
      object-fit: contain;
    }}
    .analyst-divider {{
      display: none;
      page-break-before: always;
      break-before: page;
      margin-top: 4px;
    }}
    """

    pdf_fallback_css = """
    @page {
      size: A4 landscape;
      margin: 12mm;
    }
    body {
      background: #ffffff;
      color: #222222;
      font-family: Arial, Helvetica, sans-serif;
    }
    .report-shell { max-width: none; }
    .summary-strip, .client-grid, .subgrid { display: block; }
    .hero { padding: 16px 18px; border-radius: 6px 6px 0 0; }
    .hero-rule { margin-bottom: 12px; }
    .mini-card, .panel, .subblock { margin-bottom: 10px; }
    .panel { page-break-inside: auto; break-inside: auto; border-radius: 8px; padding: 14px 16px; }
    .snapshot-table, .rotation-table, .panel table { table-layout: auto; font-size: 10.5px; }
    .snapshot-table th, .snapshot-table td,
    .rotation-table th, .rotation-table td,
    .panel th, .panel td { padding: 5px 7px; }
    .analyst-divider { page-break-before: always; break-before: page; margin-top: 6px; }
    """

    mode_css = email_css
    if render_mode == "pdf":
        mode_css = pdf_css
    elif render_mode == "pdf_fallback":
        mode_css = pdf_fallback_css

    analyst_appendix = ""
    if analyst_panels:
        analyst_appendix = (
            f"<div class='hero hero-secondary'>"
            f"<table class='hero-table' role='presentation' cellpadding='0' cellspacing='0'><tr>"
            f"<td class='hero-left'><div class='masthead'>WEEKLY ETF REVIEW</div><p class='hero-sub'>{esc(display_date_str)}</p></td>"
            f"<td class='hero-right'><div class='hero-side-label'>Analyst Report</div></td>"
            f"</tr></table>"
            f"</div><div class='hero-rule'></div>"
            + "".join(analyst_panels)
        )

    html = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <style>{css_common}{mode_css}</style>
      </head>
      <body>
        <div class="report-shell">
          <div class="hero">
            <table class="hero-table" role="presentation" cellpadding="0" cellspacing="0"><tr>
              <td class="hero-left"><div class="masthead">WEEKLY ETF REVIEW</div><p class="hero-sub">{esc(display_date_str)}</p></td>
              <td class="hero-right"><div class="hero-side-label">Investor Report</div></td>
            </tr></table>
          </div>
          <div class="hero-rule"></div>
          <div class="notice">{esc(DISCLAIMER_LINE)}</div>
          <div class="summary-strip">{intro_cards}</div>
          <div class="client-grid">{''.join(client_grid)}</div>
          <div class="report-stack">{''.join(client_panels)}{analyst_appendix}</div>
        </div>
      </body>
    </html>
    """
    return html.strip()

def create_pdf_from_html(html: str, output_path: Path, fallback_html: str | None = None) -> None:
    try:
        HTML(string=html, base_url=str(output_path.parent)).write_pdf(str(output_path))
    except AssertionError:
        if not fallback_html:
            raise
        HTML(string=fallback_html, base_url=str(output_path.parent)).write_pdf(str(output_path))


# ---------- DELIVERY ASSETS ----------
def generate_delivery_assets(output_dir: Path, report_path: Path):
    original_md_text = normalize_markdown_text(report_path.read_text(encoding="utf-8"))
    md_text_clean = strip_citations(original_md_text)
    validate_required_report(md_text_clean)

    report_date_str = parse_report_date(md_text_clean)
    safe_stem = report_path.stem

    clean_md_path = report_path.with_name(f"{safe_stem}_clean.md")
    clean_md_path.write_text(md_text_clean, encoding="utf-8")

    equity_curve_png = report_path.with_name(f"{safe_stem}_equity_curve.png")
    create_equity_curve_png(output_dir, equity_curve_png)

    image_src_pdf = equity_curve_png.resolve().as_uri() if equity_curve_png.exists() else None
    image_src_email = "cid:equitycurve" if equity_curve_png.exists() else None

    html_email = build_report_html(md_text_clean, report_date_str, image_src=image_src_email, render_mode="email")
    html_pdf = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf")
    html_pdf_fallback = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf_fallback")

    validate_email_body(html_email, md_text_clean)

    html_path = report_path.with_name(f"{safe_stem}_delivery.html")
    html_path.write_text(html_email, encoding="utf-8")

    pdf_path = report_path.with_name(f"{safe_stem}.pdf")
    create_pdf_from_html(html_pdf, pdf_path, fallback_html=html_pdf_fallback)

    if not pdf_path.exists() or pdf_path.stat().st_size <= 0:
        raise RuntimeError(f"PDF attachment was not created correctly: {pdf_path}")

    return {
        "report_date_str": report_date_str,
        "clean_md_path": clean_md_path,
        "equity_curve_png": equity_curve_png,
        "html_path": html_path,
        "pdf_path": pdf_path,
        "html_email": html_email,
        "safe_stem": safe_stem,
        "md_text_clean": md_text_clean,
    }


# ---------- EMAIL ----------
def send_email_with_attachments(assets: dict) -> tuple[list[str], Path, str]:
    subject = f"Weekly Report Review {assets['report_date_str']}"

    smtp_host = require_env("MRKT_RPRTS_SMTP_HOST")
    smtp_port = int(os.environ.get("MRKT_RPRTS_SMTP_PORT") or "587")
    smtp_user = require_env("MRKT_RPRTS_SMTP_USER")
    smtp_pass = require_env("MRKT_RPRTS_SMTP_PASS")
    mail_from = require_env("MRKT_RPRTS_MAIL_FROM")

    mail_to_env = os.environ.get("MRKT_RPRTS_MAIL_TO", REQUIRED_MAIL_TO).strip()
    if mail_to_env != REQUIRED_MAIL_TO:
        raise RuntimeError(f"Recipient mismatch: expected {REQUIRED_MAIL_TO}, got {mail_to_env}")
    mail_to = REQUIRED_MAIL_TO

    root = MIMEMultipart("mixed")
    root["Subject"] = subject
    root["From"] = mail_from
    root["To"] = mail_to

    related = MIMEMultipart("related")
    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(plain_text_from_markdown(assets["md_text_clean"]), "plain", "utf-8"))
    alternative.attach(MIMEText(assets["html_email"], "html", "utf-8"))
    related.attach(alternative)

    attachments = [assets["pdf_path"].name, assets["clean_md_path"].name, assets["html_path"].name]

    if assets["equity_curve_png"].exists():
        png_bytes = assets["equity_curve_png"].read_bytes()

        inline_png = MIMEImage(png_bytes, _subtype="png")
        inline_png.add_header("Content-ID", "<equitycurve>")
        inline_png.add_header("Content-Disposition", "inline", filename=assets["equity_curve_png"].name)
        related.attach(inline_png)

        png_attachment = MIMEApplication(png_bytes, _subtype="png")
        png_attachment.add_header("Content-Disposition", "attachment", filename=assets["equity_curve_png"].name)
        root.attach(png_attachment)
        attachments.append(assets["equity_curve_png"].name)

    root.attach(related)

    with open(assets["pdf_path"], "rb") as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
        pdf_attachment.add_header("Content-Disposition", "attachment", filename=assets["pdf_path"].name)
        root.attach(pdf_attachment)

    with open(assets["clean_md_path"], "rb") as f:
        md_attachment = MIMEApplication(f.read(), _subtype="markdown")
        md_attachment.add_header("Content-Disposition", "attachment", filename=assets["clean_md_path"].name)
        root.attach(md_attachment)

    with open(assets["html_path"], "rb") as f:
        html_attachment = MIMEApplication(f.read(), _subtype="html")
        html_attachment.add_header("Content-Disposition", "attachment", filename=assets["html_path"].name)
        root.attach(html_attachment)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(mail_from, [mail_to], root.as_string())

    manifest_path = assets["pdf_path"].with_name(f"{assets['safe_stem']}_delivery_manifest.txt")
    write_delivery_manifest(manifest_path, assets["pdf_path"].name.replace(".pdf", ".md"), mail_to, attachments)
    return attachments, manifest_path, mail_to


# ---------- MAIN ----------
def main():
    output_dir = Path("output")
    latest_report = latest_report_file(output_dir)
    assets = generate_delivery_assets(output_dir, latest_report)
    attachments, manifest_path, mail_to = send_email_with_attachments(assets)

    receipt = (
        f"DELIVERY_OK | report={latest_report.name} | recipient={mail_to} | "
        f"html_body=full_report | pdf_attached=yes | manifest={manifest_path.name} | "
        f"attachments={', '.join(attachments)}"
    )
    print(receipt)


if __name__ == "__main__":
    main()
