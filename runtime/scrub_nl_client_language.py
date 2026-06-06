from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from runtime import nl_terminology as term
from runtime import nl_terminology_contract as contract
from runtime.apply_nl_localization import is_native_dutch_report
from runtime.nl_table_section_mappings import apply_table_section_mappings, TABLE_SECTION_FORBIDDEN_AFTER_SCRUB

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

# Client-facing Dutch scrub layer.
#
# Broad replacements are legacy-only. Native Dutch runtime reports are
# independently constructed from the same runtime state/key figures as the English
# report, so this module must not broadly rewrite them. For native reports it only
# validates/guards against leakage and malformed Dutch tokens.

EXACT_REPLACEMENTS = contract.CLIENT_SURFACE_EXACT_REPLACEMENTS

# Narrow structured-state labels that may still appear inside native Dutch tables
# when the runtime state carries English enum/display names. This is not a broad
# translation pass over prose; it is a deterministic runtime-label alias map.
NATIVE_STATE_LABEL_REPLACEMENTS = contract.NATIVE_STATE_LABEL_REPLACEMENTS

NATIVE_REGEX_REPLACEMENTS = contract.NATIVE_REGEX_REPLACEMENTS

REGEX_REPLACEMENTS = [
    *[(re.compile(pattern, re.I), replacement) for pattern, replacement in contract.REGEX_CLIENT_LANGUAGE_REPLACEMENTS],
    (re.compile(r"\bas\s+(posities|positie|thema’s|themas|kandidaten|alternatieven)\b", re.I), r"als \1"),
    (re.compile(r"\band\s+(GLD|PAVE|PPA|SPY|SMH|URNM|cash|koersbevestiging|vervangingsbeslissingen)\b", re.I), r"en \1"),
    (re.compile(r"\b([A-Z]{2,6}(?:,\s*[A-Z]{2,6})+)\s+and\s+([A-Z]{2,6})\b"), lambda match: f"{match.group(1)} en {match.group(2)}"),
    (re.compile(r"###\s*Aanhouden\s+(?:but|maar)\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
    (re.compile(r"###\s*Hold\s+but\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
]

FORBIDDEN_AFTER_SCRUB = sorted(set(term.FORBIDDEN_AFTER_SCRUB + contract.NATIVE_STATE_LABEL_FORBIDDEN + [
    "Healthcare quality and defensive growth",
    "fundable",
    "funding",
    "Aanhouden but replaceable",
    "passive holds",
    "active review items",
    "but treat",
    "PRIMARY REGIME",
    "GEOPOLITICAL REGIME",
    "MAIN TAKEAWAY",
    "confidence",
    "Mixed / not yet decisive",
    "Keep the current allocation",
    "THIS WEEK",
    "Capital spending",
    "AI compute infrastructure",
    "Neetable",
    "Neeg",
    "not promoted this week",
    "SPY plus SMH creates",
    "GLD remains",
    "GLD blijft een hedgepositie onder herbeoordeling",
    "GLD moet bewijzen dat het nog steeds een stabiliserende hedgefunctie heeft",
    "Herbeoordeling goudhedge",
    "No / under review",
    "Neen-U.S.",
    "Best verdiende",
    "Actiebias",
    "with full valuation history",
    "Inaugural model portfolio established",
    "Fresh per-ticker",
    "Latest 4 mei close basis",
    "Latest 4 May close basis",
    "Runtime valuation from immutable pricing audit",
    "Runtime valuation repriced from official portfolio-state shares",
    "Rotation destination",
    "Equity Curve (EUR)",
    "Portfolio value (EUR)",
    "US equities",
    "Investment Report",
    "Investor Report",
    "Analyst Report",
]))


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


def _normalize_native_state_labels(text: str) -> str:
    for source, target in sorted(NATIVE_STATE_LABEL_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    for pattern, target in NATIVE_REGEX_REPLACEMENTS:
        text = pattern.sub(target, text)
    return text


def scrub_text(text: str, *, native_dutch: bool | None = None) -> str:
    native = is_native_dutch_report(text) if native_dutch is None else native_dutch
    if native:
        # Guard-only mode: native Dutch reports must be generated correctly by the
        # runtime renderer. Broad replacement maps are legacy-only and may mutate
        # valid Dutch prose. Only narrow runtime-state display-label aliases are
        # normalized here before validation.
        return _normalize_native_state_labels(text)
    for source, target in sorted(EXACT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    for pattern, target in REGEX_REPLACEMENTS:
        text = pattern.sub(target, text)
    text = apply_table_section_mappings(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    native = is_native_dutch_report(text)
    scrubbed = scrub_text(text, native_dutch=native)
    forbidden = FORBIDDEN_AFTER_SCRUB + TABLE_SECTION_FORBIDDEN_AFTER_SCRUB
    failures = [token for token in forbidden if token.lower() in scrubbed.lower()]
    if failures:
        raise RuntimeError("Dutch client-language scrub failed: " + ", ".join(sorted(set(failures))))
    report_path.write_text(scrubbed, encoding="utf-8")
    print(f"ETF_NL_CLIENT_LANGUAGE_SCRUB_OK | report={report_path.name} | mode={'native_guard_only' if native else 'legacy_scrub'}")


if __name__ == "__main__":
    main()
