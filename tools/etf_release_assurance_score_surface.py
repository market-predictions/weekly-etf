from __future__ import annotations

"""Narrow score-heading parity repair for Weekly ETF release assurance.

The English current-position surface renders the recommendation score in a
Markdown heading and can also append operational review-priority metadata to the
same line. The Dutch surface renders the recommendation score in a compact
table. Only the score itself is a bilingual numeric parity field; review-priority
metadata is not. This helper preserves all table-number checks and only narrows
non-table score-heading extraction to the numeric token immediately after
``Score``.
"""

import re
from collections import Counter
from pathlib import Path

import tools.etf_release_assurance as _assurance

_SCORE_VALUE_RE = re.compile(r"\bscore\s+([-+]?\d[\d.,]*%?)", re.IGNORECASE)


def table_numeric_multiset(path: Path) -> Counter[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "|" in line:
            stripped = line.replace("|", "").replace("-", "").replace(":", "").strip()
            if not stripped:
                continue
            tokens = _assurance.NUMBER_RE.findall(line)
        else:
            score_match = _SCORE_VALUE_RE.search(line)
            if score_match is None:
                continue
            tokens = [score_match.group(1)]

        for token in tokens:
            normalized = _assurance.normalize_number(token)
            if normalized is not None:
                values.append(normalized)
    return Counter(values)


def install_score_heading_parity_fix() -> None:
    """Install the narrow parser into the existing assurance module in-process."""
    _assurance.table_numeric_multiset = table_numeric_multiset
