from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

REVIEW_DIR_NAME = "cockpit_review"
SCHEMA_VERSION = "cockpit_side_by_side_review_v1"
REVIEW_TYPE = "side_by_side_preview_only"
PREVIOUS_PACKAGE = "WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE"
NEXT_PACKAGE = "WP_COCKPIT_SURFACE_09_PROMOTION_REVIEW_OR_FURTHER_ITERATION_DECISION"
REVIEW_DIMENSIONS = [
    "readability",
    "density",
    "visual_hierarchy",
    "decision_clarity",
    "trust_provenance_clarity",
    "premium_look_and_feel",
    "audit_evidence_preservation",
]


@dataclass(frozen=True)
class BuiltSideBySideReview:
    token: str
    metadata_path: Path
    english_markdown_path: Path
    english_html_path: Path
    dutch_markdown_path: Path
    dutch_html_path: Path


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _resolve_output_relative(path: Path, output_dir: Path) -> Path:
    if path.is_absolute():
        return path
    if str(path).startswith("output/"):
        return output_dir.parent / path
    return output_dir / path


def _load_runtime_state(output_dir: Path) -> dict[str, Any]:
    pointer = output_dir / "runtime" / "latest_etf_report_state_path.txt"
    if not pointer.exists():
        return {}
    target = pointer.read_text(encoding="utf-8").strip()
    if not target:
        return {}
    return _read_json(_resolve_output_relative(Path(target), output_dir))


def _token_from_state(state: dict[str, Any]) -> str | None:
    for key in ("report_date", "requested_close_date"):
        value = str(state.get(key) or "").strip()
        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value):
            return value.replace("-", "")[2:]
    return None


def _token_from_reports(output_dir: Path) -> str | None:
    tokens: list[str] = []
    pattern = re.compile(r"^weekly_analysis_pro(?:_nl)?_(\d{6})(?:_\d{2})?(?:_delivery)?\.(?:md|html)$")
    for path in output_dir.glob("weekly_analysis_pro*"):
        name = path.name
        if "cockpit" in name or "_clean" in name:
            continue
        match = pattern.match(name)
        if match:
            tokens.append(match.group(1))
    return sorted(tokens)[-1] if tokens else None


def _report_token(output_dir: Path, explicit_token: str | None = None) -> str:
    if explicit_token:
        return explicit_token
    state_token = _token_from_state(_load_runtime_state(output_dir))
    if state_token:
        return state_token
    report_token = _token_from_reports(output_dir)
    if report_token:
        return report_token
    return "unknown"


def _relative(path: Path, output_dir: Path) -> str:
    try:
        return str(path.relative_to(output_dir.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _sort_paths(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda item: item.name)


def _classic_report_sources(output_dir: Path, token: str) -> list[Path]:
    candidates: list[Path] = []
    for path in output_dir.glob(f"weekly_analysis_pro*_{token}*"):
        name = path.name
        if "cockpit" in name or "_clean" in name:
            continue
        if path.suffix not in {".md", ".html"}:
            continue
        if not (name.endswith(".md") or name.endswith("_delivery.html")):
            continue
        candidates.append(path)
    if candidates:
        return _sort_paths(candidates)

    fallback: list[Path] = []
    for path in output_dir.glob("weekly_analysis_pro*"):
        name = path.name
        if "cockpit" in name or "_clean" in name:
            continue
        if path.suffix in {".md", ".html"} and (name.endswith(".md") or name.endswith("_delivery.html")):
            fallback.append(path)
    return _sort_paths(fallback)


def _cockpit_preview_sources(output_dir: Path, token: str) -> list[Path]:
    preview_dir = output_dir / "cockpit_preview"
    if not preview_dir.exists():
        return []
    matches = list(preview_dir.glob(f"*cockpit*_{token}_*.html"))
    if matches:
        return _sort_paths(matches)
    return _sort_paths(list(preview_dir.glob("*cockpit*.html")))


def _metadata(output_dir: Path, token: str) -> dict[str, Any]:
    classic = _classic_report_sources(output_dir, token)
    preview = _cockpit_preview_sources(output_dir, token)
    return {
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "token": token,
        "classic_report_sources": [_relative(path, output_dir) for path in classic],
        "cockpit_preview_sources": [_relative(path, output_dir) for path in preview],
        "review_dimensions": REVIEW_DIMENSIONS,
        "promotion_status": "not_promoted",
        "production_report_change": "none",
        "delivery_change": "none",
        "state_change": "none",
        "state_mutation": "not_allowed",
        "delivery_mutation": "not_allowed",
        "provenance_iteration_review": True,
        "source_provenance_improvement": "present",
        "previous_package": PREVIOUS_PACKAGE,
        "next_package": NEXT_PACKAGE,
    }


def _source_lines(values: list[str], empty_text: str) -> str:
    if not values:
        return f"- {empty_text}"
    return "\n".join(f"- `{value}`" for value in values)


def _dimension_table(language: str) -> str:
    if language == "nl":
        rows = {
            "readability": ("Volledig en vertrouwd, maar vraagt meer leestijd.", "Sneller te scannen door één cockpitlaag."),
            "density": ("Rijk aan context en bewijs.", "Lager in dichtheid; geschikt als ingang, niet als vervanger van bewijs."),
            "visual_hierarchy": ("Sterk na recente besliscockpit-patches, maar nog rapportgericht.", "Sterkere eerste indruk door kaarten, grafiek en disciplinepunt."),
            "decision_clarity": ("Beslissingen blijven compleet onderbouwd.", "Beslissing wordt sneller zichtbaar, met minder uitleg."),
            "trust_provenance_clarity": ("Auditspoor blijft het sterkst in de klassieke rapportlaag.", "Verbeterd door Bronnen en bewijs: runtime-state, waarderingshistorie, pricing-audit, macro-pack en run-manifest zijn nu explicieter zichtbaar."),
            "premium_look_and_feel": ("Client-grade, maar tekstzwaar.", "Premium cockpitgevoel, mits bewijslaag behouden blijft."),
            "audit_evidence_preservation": ("Bewijs en controles blijven volledig zichtbaar.", "Kan als startlaag functioneren naast de bestaande bewijslaag; productie blijft klassiek."),
        }
    else:
        rows = {
            "readability": ("Complete and familiar, but requires more reading time.", "Faster to scan through a single cockpit layer."),
            "density": ("Rich in context and evidence.", "Lower density; suitable as an entry surface, not a replacement for evidence."),
            "visual_hierarchy": ("Improved by recent decision-cockpit patches, but still report-led.", "Stronger first impression through cards, chart, and discipline point."),
            "decision_clarity": ("Decisions remain fully supported.", "Decision state becomes visible faster, with less explanation."),
            "trust_provenance_clarity": ("Audit trail is strongest in the classic report layer.", "Improved by Source & evidence: runtime state, valuation history, pricing audit, macro pack, and run-manifest references are now more explicit."),
            "premium_look_and_feel": ("Client-grade, but text-heavy.", "Premium cockpit feel if the evidence layer remains preserved."),
            "audit_evidence_preservation": ("Evidence and controls remain fully visible.", "Can operate as a starting surface beside the existing evidence layer; production remains classic."),
        }
    lines = ["| Dimension | Classic report | Cockpit preview |", "|---|---|---|"]
    for dimension in REVIEW_DIMENSIONS:
        classic, cockpit = rows[dimension]
        lines.append(f"| `{dimension}` | {classic} | {cockpit} |")
    return "\n".join(lines)


def _provenance_iteration_section(language: str) -> str:
    if language == "nl":
        return "\n".join(
            [
                "## WP07 bron/provenance-iteratie",
                "",
                "- Bron/provenance clarity improved: de cockpit toont nu een zichtbare sectie Bronnen en bewijs.",
                "- De cockpit toont nu de runtime-state bron.",
                "- De cockpit toont nu de waarderingshistoriebron.",
                "- De cockpit toont nu een pricing-audit referentie wanneer beschikbaar.",
                "- De cockpit toont nu een macro-pack referentie wanneer beschikbaar.",
                "- De cockpit toont nu een run-manifest referentie wanneer beschikbaar.",
                "- De cockpit blijft preview-only en niet gepromoveerd.",
                "- Er wordt geen deliveryclaim gemaakt.",
                "- Het klassieke productierapport blijft de autoriteit.",
            ]
        )
    return "\n".join(
        [
            "## WP07 source/provenance iteration",
            "",
            "- Source/provenance clarity improved: the cockpit now exposes a visible Source & evidence section.",
            "- The cockpit now exposes the runtime-state source.",
            "- The cockpit now exposes the valuation-history source.",
            "- The cockpit now exposes the pricing-audit reference when available.",
            "- The cockpit now exposes the macro-pack reference when available.",
            "- The cockpit now exposes the run-manifest reference when available.",
            "- The cockpit remains preview-only and not promoted.",
            "- No delivery claim is made.",
            "- The classic production report remains authoritative.",
        ]
    )


def _markdown(metadata: dict[str, Any], language: str) -> str:
    classic_sources = metadata["classic_report_sources"]
    cockpit_sources = metadata["cockpit_preview_sources"]
    token = metadata["token"]
    if language == "nl":
        title = "# Weekly ETF cockpit side-by-side review — NL"
        intro = "Deze review vergelijkt de klassieke rapportlaag met de cockpitpreview na de WP07 provenance-iteratie. Het is een reviewlaag, geen promotiebesluit."
        classic_empty = "geen klassieke rapportbron gevonden in deze lokale outputmap"
        cockpit_empty = "geen cockpitpreviewbron gevonden in deze lokale outputmap"
        classic_strengths = [
            "De klassieke rapportlaag behoudt volledige context, uitleg en controleerbare onderbouwing.",
            "De bestaande audit- en bewijsstructuur blijft het beste zichtbaar in de klassieke rapportvorm.",
            "De Nederlandse companion blijft gekoppeld aan dezelfde rapportbron en wordt niet als aparte researchpass behandeld.",
        ]
        cockpit_strengths = [
            "De cockpitpreview maakt marktklimaat, actie, prestatie/risico en disciplinepunt sneller scanbaar.",
            "De visuele hiërarchie voelt meer als een premium startpagina voor een drukke lezer.",
            "De preview blijft gescheiden van de productie-output en toont nu expliciet Bronnen en bewijs.",
        ]
        risks = [
            "De cockpit blijft een samenvattende startlaag en mag niet de volledige bewijslaag vervangen.",
            "Promotie zonder expliciete beslissing kan de huidige rapportautoriteit onduidelijk maken.",
            "De cockpit mag geen nieuwe portefeuille- of leveringsautoriteit krijgen.",
        ]
        fixes = [
            "Voer na deze review een apart promotie-of-iteratiebesluit uit.",
            "Bepaal of de cockpit later bijlage, voorblad, vervanging of experiment blijft.",
            "Houd klassieke rapport- en delivery-validatie verplicht tijdens elke promotiestap.",
        ]
        no_promotion = "promotion_status: not_promoted — de cockpit blijft preview-only; deze review promoot niets naar productie."
        evidence = "## Evidence / Bewijs"
    else:
        title = "# Weekly ETF cockpit side-by-side review"
        intro = "This review compares the classic report layer with the cockpit preview after the WP07 provenance iteration. It is a review layer, not a promotion decision."
        classic_empty = "no classic report source found in this local output directory"
        cockpit_empty = "no cockpit preview source found in this local output directory"
        classic_strengths = [
            "The classic report keeps the full context, explanation, and reviewable evidence structure.",
            "The existing audit and proof layer remains clearest in the classic report form.",
            "The Dutch companion remains tied to the same report source instead of becoming a separate research pass.",
        ]
        cockpit_strengths = [
            "The cockpit preview makes market climate, action, performance/risk, and discipline point faster to scan.",
            "The visual hierarchy feels more like a premium starting page for a time-limited reader.",
            "The preview remains separate from production output and now exposes Source & evidence explicitly.",
        ]
        risks = [
            "The cockpit remains a summary starting layer and must not replace the full evidence layer.",
            "Promotion without an explicit decision could blur the current report authority.",
            "The cockpit must not gain new portfolio or delivery authority.",
        ]
        fixes = [
            "Run a separate promotion-or-iteration decision after this review.",
            "Decide later whether the cockpit becomes an attachment, first page, replacement, or experiment.",
            "Keep classic report and delivery validation mandatory through every promotion step.",
        ]
        no_promotion = "promotion_status: not_promoted — the cockpit remains preview-only; this review promotes nothing into production."
        evidence = "## Evidence"

    def bullets(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values)

    return "\n\n".join(
        [
            title,
            f"token: `{token}`",
            f"schema_version: `{SCHEMA_VERSION}`",
            f"review_type: `{REVIEW_TYPE}`",
            f"previous_package: `{metadata['previous_package']}`",
            f"next_package: `{metadata['next_package']}`",
            "provenance_iteration_review: `true`",
            "source_provenance_improvement: `present`",
            no_promotion,
            intro,
            _provenance_iteration_section(language),
            "## Classic report strengths / Sterktes klassiek rapport\n\n" + bullets(classic_strengths),
            "## Cockpit preview strengths / Sterktes cockpitpreview\n\n" + bullets(cockpit_strengths),
            "## Cockpit preview risks / Risico's cockpitpreview\n\n" + bullets(risks),
            "## Required fixes before promotion / Vereiste fixes vóór promotie\n\n" + bullets(fixes),
            "## Review dimensions / Reviewdimensies\n\n" + _dimension_table(language),
            "## Explicit no-promotion statement / Expliciete niet-promotieverklaring\n\n" + no_promotion,
            evidence
            + "\n\n### Classic report sources\n"
            + _source_lines(classic_sources, classic_empty)
            + "\n\n### Cockpit preview sources\n"
            + _source_lines(cockpit_sources, cockpit_empty),
        ]
    ) + "\n"


def _html_from_markdown(markdown: str, language: str) -> str:
    title = "Cockpit side-by-side review" if language == "en" else "Cockpit side-by-side review NL"
    return f"""<!DOCTYPE html>
<html lang=\"{language}\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>{escape(title)}</title>
<style>
  body {{ margin:0; padding:32px 18px; background:#F6F1E7; color:#211C16; font-family:Arial, Helvetica, sans-serif; }}
  article {{ max-width:980px; margin:0 auto; border:1px solid #D8CDB8; background:#fffaf0; padding:30px 36px; }}
  pre {{ white-space:pre-wrap; word-break:break-word; font-family:Arial, Helvetica, sans-serif; font-size:14px; line-height:1.55; }}
</style>
</head>
<body>
<article data-cockpit-side-by-side-review=\"true\" data-preview-only=\"true\" data-provenance-iteration-review=\"true\">
<pre>{escape(markdown)}</pre>
</article>
</body>
</html>
"""


def build_cockpit_side_by_side_review(output_dir: Path | str = Path("output"), token: str | None = None) -> BuiltSideBySideReview:
    output = Path(output_dir)
    review_dir = output / REVIEW_DIR_NAME
    review_dir.mkdir(parents=True, exist_ok=True)

    resolved_token = _report_token(output, token)
    metadata = _metadata(output, resolved_token)

    metadata_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.json"
    en_md_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.md"
    en_html_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_{resolved_token}.html"
    nl_md_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_nl_{resolved_token}.md"
    nl_html_path = review_dir / f"weekly_etf_cockpit_side_by_side_review_nl_{resolved_token}.html"

    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    en_markdown = _markdown(metadata, "en")
    nl_markdown = _markdown(metadata, "nl")
    en_md_path.write_text(en_markdown, encoding="utf-8")
    nl_md_path.write_text(nl_markdown, encoding="utf-8")
    en_html_path.write_text(_html_from_markdown(en_markdown, "en"), encoding="utf-8")
    nl_html_path.write_text(_html_from_markdown(nl_markdown, "nl"), encoding="utf-8")

    return BuiltSideBySideReview(
        token=resolved_token,
        metadata_path=metadata_path,
        english_markdown_path=en_md_path,
        english_html_path=en_html_path,
        dutch_markdown_path=nl_md_path,
        dutch_html_path=nl_html_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build preview-only cockpit side-by-side review artifacts.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--token", default=None)
    args = parser.parse_args(argv)

    result = build_cockpit_side_by_side_review(output_dir=Path(args.output_dir), token=args.token)
    print(
        "COCKPIT_SIDE_BY_SIDE_REVIEW_OK"
        f" | token={result.token}"
        f" | json={result.metadata_path}"
        f" | en={result.english_markdown_path}"
        f" | nl={result.dutch_markdown_path}"
        " | promotion_status=not_promoted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
