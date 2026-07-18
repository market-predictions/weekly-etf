from __future__ import annotations

import os
import subprocess
from pathlib import Path

DECISION_LOG = Path("control/DECISION_LOG.md")
CHANGELOG = Path("control/ETF_SESSION_CHANGELOG.md")
SELF = Path("tools/append_close_first_review_governance.py")
WORKFLOW = Path(".github/workflows/append-close-first-review-governance.yml")

DECISION_MARKER = "## 2026-07-18 — Close-first review selects URNM-to-cash as a review option"
DECISION_BLOCK = '''
---

## 2026-07-18 — Close-first review selects URNM-to-cash as a review option

### Decision

The no-mutation close-first review uses fresh completed-close data, current lane quality, holding continuity, relative strength, contribution, portfolio-role evidence, liquidity and preservation credits to compare all nine active positions.

For the 2026-07-17 evidence date, URNM is the supported review source. The reviewed path closes all 48 URNM shares, opens no new ticker, restores the active count from nine to eight and retains the estimated proceeds as cash.

URNM remains first when position-size and implementation-practicality points are removed. XLU ranks second. Position size is therefore not the selection authority.

### Consequence

This is review evidence only. It does not change the official portfolio or grant implementation authority. A separate explicitly approved package must refresh prices, rerun the same rubric and stop without changes if the source or evidence changes materially.

Persistent records:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
```
'''

CHANGELOG_MARKER = "## 2026-07-18 — Portfolio close-first execution review"
CHANGELOG_BLOCK = '''
---

## 2026-07-18 — Portfolio close-first execution review

`WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW` performed a fresh no-change comparison of all nine official holdings after the portfolio entered `close_first 9/8` status.

Result:

```text
evidence close: 2026-07-17
selected review source: URNM
reviewed quantity: 48 whole shares
destination: cash
estimated proceeds_eur: 2022.23
projected cash_eur: 4556.59
projected active count: 8
new ticker: none
portfolio change applied: false
email sent: false
```

The package added a deterministic builder, validator, seven focused tests, three outcome fixtures and a read-only GitHub Actions gate. Holding quality and current lane quality are recorded separately; the lower score forms the decision-quality floor.

Validation:

```text
PR: #95
run: 29622365939 success
job: 88019775095
artifact: 8422627986
artifact digest: sha256:9f0b833f6d9dd5bb7b7558afe598c20246e67707fc5cff974e1bfc661479851a
protected authority hashes: identical
historical report hashes: identical
```

The next package is `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION`, but it requires separate explicit approval and fresh implementation-time revalidation.
'''


def append_once(path: Path, marker: str, block: str) -> None:
    content = path.read_text(encoding="utf-8")
    if marker not in content:
        path.write_text(content.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def main() -> None:
    append_once(DECISION_LOG, DECISION_MARKER, DECISION_BLOCK)
    append_once(CHANGELOG, CHANGELOG_MARKER, CHANGELOG_BLOCK)
    SELF.unlink(missing_ok=True)
    WORKFLOW.unlink(missing_ok=True)

    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", str(DECISION_LOG), str(CHANGELOG)], check=True)
    subprocess.run(["git", "add", "-u", str(SELF), str(WORKFLOW)], check=True)
    subprocess.run(["git", "commit", "-m", "Append close-first review governance records [skip ci]"], check=True)
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Could not resolve feature branch")
    subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], check=True)
    print("ETF_CLOSE_FIRST_REVIEW_APPEND_OK | decision_log=true | changelog=true | temporary_files_removed=true")


if __name__ == "__main__":
    main()
