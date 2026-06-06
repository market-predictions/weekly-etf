from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from runtime import nl_terminology as term
from runtime import nl_terminology_contract as contract
from runtime.nl_localization import localize_markdown_table_headers, localize_text, validate_dutch_text

DUTCH_DISCLAIMER = term.DUTCH_DISCLAIMER
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

SECTION_TITLE_REPLACEMENTS = term.SECTION_TITLE_REPLACEMENTS
CLIENT_PHRASES = {
    **term.REPORT_LABELS,
    **term.PHRASE_REPLACEMENTS,
    **term.EXACT_CLIENT_LANGUAGE_REPLACEMENTS,
}
ACTION_PHRASES = contract.ACTION_REPLACEMENTS
CLIENT_LANGUAGE_CLEANUPS = term.CLIENT_LANGUAGE_CLEANUPS

# Legacy safety overlays for reports that are not natively rendered in Dutch.
# Native Dutch reports remain guard-only; do not broaden this path into a new
# English-to-Dutch translation layer.
PARTIAL_MIXED_EXACT_CLEANUPS = contract.PARTIAL_MIXED_EXACT_CLEANUPS
REPLACEMENT_DUEL_PHRASE_CLEANUPS = contract.REPLACEMENT_DUEL_PHRASE_CLEANUPS


def is_native_dutch_report(text: str) -> bool:
    markers = [
        "# Wekelijkse ETF-review",
        "## 1. Kernsamenvatting",
        "## 2. Portefeuille-acties",
        "## 3. Regime-dashboard",
        "## 10. Review huidige posities",
        "## 15. Huidige posities en cash",
    ]
    return sum(marker in text for marker in markers) >= 5


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


def _replace_disclaimer(text: str) -> str:
    marker = "## 17. Disclaimer"
    idx = text.find(marker)
    if idx == -1:
        return text
    return text[: idx + len(marker)] + "\n\n" + DUTCH_DISCLAIMER + "\n"


def _replace_longest_first(text: str, replacements: dict[str, str]) -> str:
    for src, dst in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(src, dst)
    return text


def _localize_section_titles(text: str) -> str:
    return _replace_longest_first(text, SECTION_TITLE_REPLACEMENTS)


def _localize_phrases(text: str) -> str:
    return _replace_longest_first(text, {**CLIENT_PHRASES, **ACTION_PHRASES})


def _clean_runtime_artifacts(text: str) -> str:
    text = text.replace("portfolio_state_pricing_audit", "gevalideerde prijsbasis")
    text = text.replace("pricing_audit", "gevalideerde prijsbasis")
    text = text.replace("twelve_data", "externe slotkoersbron")
    return text


def _clean_client_language(text: str) -> str:
    text = _replace_longest_first(text, contract.CLIENT_SURFACE_EXACT_REPLACEMENTS)
    text = _replace_longest_first(text, CLIENT_LANGUAGE_CLEANUPS)
    for pattern, replacement in term.REGEX_CLIENT_LANGUAGE_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _localize_replacement_duel_phrases(text: str) -> str:
    return _replace_longest_first(text, REPLACEMENT_DUEL_PHRASE_CLEANUPS)


def _normalize_ticker_lists(text: str) -> str:
    return re.sub(
        r"\b([A-Z]{2,6}(?:,\s*[A-Z]{2,6})+)\s+and\s+([A-Z]{2,6})\b",
        lambda match: f"{match.group(1)} en {match.group(2)}",
        text,
    )


def _normalize_partial_mixed_language(text: str) -> str:
    text = _replace_longest_first(text, PARTIAL_MIXED_EXACT_CLEANUPS)
    text = _normalize_ticker_lists(text)
    text = re.sub(r"###\s*Aanhouden\s+maar\s+vervangbaar", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    text = re.sub(r"###\s*Aanhouden\s+but\s+replaceable", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    text = re.sub(r"###\s*Hold\s+but\s+replaceable", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    return text


def _localize_until_stable(text: str, passes: int = 3) -> str:
    previous = text
    for _ in range(passes):
        current = localize_text(previous, language="nl")
        current = localize_markdown_table_headers(current, language="nl")
        current = _clean_runtime_artifacts(current)
        current = _localize_replacement_duel_phrases(current)
        current = _clean_client_language(current)
        current = _normalize_partial_mixed_language(current)
        if current == previous:
            return current
        previous = current
    return previous


def localize_report(text: str) -> str:
    if is_native_dutch_report(text):
        # Native Dutch output is independently constructed from the same runtime
        # state/key figures as the English report. Do not run broad translation or
        # generic language-repair maps over it; that can mutate valid Dutch text.
        # Keep only deterministic artifact/disclaimer cleanup. Any remaining
        # English or malformed Dutch must fail validation downstream.
        text = _replace_disclaimer(text)
        text = _clean_runtime_artifacts(text)
        return text

    text = _replace_disclaimer(text)
    text = _localize_section_titles(text)
    text = _localize_phrases(text)
    text = _localize_until_stable(text, passes=4)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    localized = localize_report(text)
    failures = validate_dutch_text(localized)
    if failures:
        raise RuntimeError("Dutch localization failed before write: " + ", ".join(failures))
    report_path.write_text(localized, encoding="utf-8")
    print(f"ETF_NL_LOCALIZATION_OK | report={report_path.name} | native_dutch={is_native_dutch_report(localized)} | mode={'native_guard_only' if is_native_dutch_report(localized) else 'legacy_localization'}")


if __name__ == "__main__":
    main()
