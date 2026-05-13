from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

EXACT_REPLACEMENTS = {
    "Aanhouden but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden maar replaceable": "Aanhouden, maar vervangbaar",
    "Hold maar vervangbaar": "Aanhouden, maar vervangbaar",
    "active review items rather than passive holds": "posities onder actieve herbeoordeling in plaats van passieve aanhoudposities",
    "posities onder actieve herbeoordeling in plaats van passieve holds": "posities onder actieve herbeoordeling in plaats van passieve aanhoudposities",
    "actieve herbeoordeling in plaats van passieve holds": "actieve herbeoordeling in plaats van passieve aanhoudposities",
    "passive holds": "passieve aanhoudposities",
    "fresh capital and replacement decisions": "nieuw kapitaal en vervangingsbeslissingen",
    "replacement decisions": "vervangingsbeslissingen",
    "funding challengers": "allocatie naar alternatieven",
    "funding candidates": "allocatiekandidaten",
    "funding source": "financieringsbron",
    "Funding source": "Financieringsbron",
    "funding note": "allocatietoelichting",
    "Funding note": "Allocatietoelichting",
    "before funding": "vóór allocatie",
    "after funding": "na allocatie",
    "not fundable": "niet geschikt voor allocatie",
    "Not fundable": "Niet geschikt voor allocatie",
    "fundable": "geschikt voor allocatie",
    "Fundable": "Geschikt voor allocatie",
    "funding": "allocatie",
    "Funding": "Allocatie",
    "as posities": "als posities",
    "as positie": "als positie",
}

REGEX_REPLACEMENTS = [
    (re.compile(r"\bnot\s+fundable\b", re.I), "niet geschikt voor allocatie"),
    (re.compile(r"\bfunding\s+source\b", re.I), "financieringsbron"),
    (re.compile(r"\bfunding\s+note\b", re.I), "allocatietoelichting"),
    (re.compile(r"\bfunding\s+candidates\b", re.I), "allocatiekandidaten"),
    (re.compile(r"\bfunding\s+challengers\b", re.I), "allocatie naar alternatieven"),
    (re.compile(r"\bbefore\s+funding\b", re.I), "vóór allocatie"),
    (re.compile(r"\bafter\s+funding\b", re.I), "na allocatie"),
    (re.compile(r"\bfundable\b", re.I), "geschikt voor allocatie"),
    (re.compile(r"\bfunding\b", re.I), "allocatie"),
    (re.compile(r"\bbut\s+treat\b", re.I), "maar behandel"),
    (re.compile(r"\bbut\b", re.I), "maar"),
    (re.compile(r"\bas\s+(posities|positie|thema’s|themas|kandidaten|alternatieven)\b", re.I), r"als \1"),
    (re.compile(r"\band\s+(GLD|PAVE|PPA|SPY|SMH|URNM|cash|koersbevestiging|vervangingsbeslissingen)\b", re.I), r"en \1"),
    (re.compile(r"###\s*Aanhouden\s+(?:but|maar)\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
    (re.compile(r"###\s*Hold\s+but\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
]

FORBIDDEN_AFTER_SCRUB = [
    "fundable",
    "funding",
    "Aanhouden but replaceable",
    "passive holds",
    "active review items",
    "but treat",
]


def latest_nl_report(output_dir: Path) -> Path:
    explicit = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and NL_RE.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro_nl_*.md") if NL_RE.match(path.name))
    if not reports:
        raise RuntimeError(f"No Dutch ETF pro report found in {output_dir}")
    return reports[-1]


def scrub_text(text: str) -> str:
    for source, target in sorted(EXACT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    for pattern, target in REGEX_REPLACEMENTS:
        text = pattern.sub(target, text)
    text = re.sub(
        r"\b([A-Z]{2,6}(?:,\s*[A-Z]{2,6})+)\s+and\s+([A-Z]{2,6})\b",
        lambda match: f"{match.group(1)} en {match.group(2)}",
        text,
    )
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    scrubbed = scrub_text(text)
    failures = [token for token in FORBIDDEN_AFTER_SCRUB if token.lower() in scrubbed.lower()]
    if failures:
        raise RuntimeError("Dutch client-language scrub failed: " + ", ".join(sorted(set(failures))))
    report_path.write_text(scrubbed, encoding="utf-8")
    print(f"ETF_NL_CLIENT_LANGUAGE_SCRUB_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
