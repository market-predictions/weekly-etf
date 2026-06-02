from __future__ import annotations

import argparse
import re
from pathlib import Path

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?_delivery\.html$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?_delivery\.html$")


def latest_delivery_html(output_dir: Path, *, language: str) -> Path:
    regex = NL_RE if language == "nl" else EN_RE
    files = sorted(path for path in output_dir.glob("weekly_analysis_pro*_delivery.html") if regex.match(path.name))
    if not files:
        raise RuntimeError(f"No {language} delivery HTML found in {output_dir}")
    return files[-1]


def plain(html: str) -> str:
    text = re.sub(r"<style.*?</style>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def validate_en(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    text = plain(html)
    failures: list[str] = []
    if "Executive Summary" not in text:
        failures.append(f"{path.name}: missing visible Executive Summary marker")
    if text.count("Replacement Duel Table") > 1:
        failures.append(f"{path.name}: duplicate Replacement Duel Table surface")
    if "11 Replacement Duel Table" in text:
        failures.append(f"{path.name}: stale replacement-duel section number 11 remains")
    if "Position Changes Executed This Run" in text:
        failures.append(f"{path.name}: idempotent execution heading still says executed this run")
    if "Position Changes Reflected in Official State" not in text:
        failures.append(f"{path.name}: missing reflected-position-change heading")
    return failures


def validate_nl(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    text = plain(html)
    failures: list[str] = []
    if "Kernsamenvatting" not in text:
        failures.append(f"{path.name}: missing visible Kernsamenvatting marker")
    if text.count("Vervangingsanalyse") > 1:
        failures.append(f"{path.name}: duplicate Vervangingsanalyse surface")
    if "11 Vervangingsanalyse" in text:
        failures.append(f"{path.name}: stale replacement-duel section number 11 remains")
    if "Positiewijzigingen in deze run" in text:
        failures.append(f"{path.name}: idempotent execution heading still says in deze run")
    if "Positiewijzigingen verwerkt in de officiële portefeuillestaat" not in text:
        failures.append(f"{path.name}: missing reflected-position-change heading")
    if "Guarded auto-execution" in text:
        failures.append(f"{path.name}: Dutch execution note still contains English Guarded auto-execution")
    if "reduce PPA to fund CIBR" in text or "buy CIBR funded by PPA" in text:
        failures.append(f"{path.name}: Dutch execution note still contains English funding sentence")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    failures = validate_en(latest_delivery_html(output_dir, language="en")) + validate_nl(latest_delivery_html(output_dir, language="nl"))
    if failures:
        raise SystemExit("FAIL: ETF PDF polish contract failed: " + "; ".join(failures))
    print("ETF_PDF_POLISH_CONTRACT_OK")


if __name__ == "__main__":
    main()
