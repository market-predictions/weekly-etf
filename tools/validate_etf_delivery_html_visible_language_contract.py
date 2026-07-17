from __future__ import annotations

import argparse
from pathlib import Path

import tools.validate_etf_delivery_html_contract as base
from runtime.client_facing_sanitizer import validate_dutch_delivery_language


def validate_visible_dutch_delivery_language(html: str, report_name: str) -> None:
    """Validate Dutch client language on rendered text, not CSS/class identifiers."""
    validate_dutch_delivery_language(base._visible_text(html), report_name)


def validate(output_dir: Path) -> None:
    original = base.validate_dutch_delivery_language
    base.validate_dutch_delivery_language = validate_visible_dutch_delivery_language
    try:
        base.validate(output_dir)
    finally:
        base.validate_dutch_delivery_language = original


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the complete ETF delivery HTML contract while evaluating Dutch language tokens on visible text."
    )
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
