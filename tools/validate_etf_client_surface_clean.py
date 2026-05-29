from __future__ import annotations

import argparse
import re
from pathlib import Path

SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
DOUBLE_NEGATIVE_RE = [
    re.compile(r"\breduce\s+[A-Z][A-Z0-9.-]*\s+by\s+-\d+(?:\.\d+)?%", re.IGNORECASE),
    re.compile(r"\bverlaag\s+[A-Z][A-Z0-9.-]*\s+met\s+-\d+(?:\.\d+)?%", re.IGNORECASE),
]
ALLOWLIST = {
    "https",
}


def _scan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits: list[str] = []
    for match in SNAKE_CASE_RE.finditer(text):
        token = match.group(0)
        if token not in ALLOWLIST:
            hits.append(token)
    for regex in DOUBLE_NEGATIVE_RE:
        if regex.search(text):
            hits.append(regex.pattern)
    return sorted(set(hits))


def validate(output_dir: Path) -> None:
    failures: list[str] = []
    for pattern in ("weekly_analysis_pro*.md", "weekly_analysis_pro*delivery.html"):
        for path in sorted(output_dir.glob(pattern)):
            hits = _scan(path)
            if hits:
                failures.append(f"{path.name}: {', '.join(hits[:12])}")
    if failures:
        raise RuntimeError("ETF client-facing surface contains internal labels: " + " | ".join(failures))
    print("ETF_CLIENT_SURFACE_CLEAN_OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
