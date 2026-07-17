from __future__ import annotations

from pathlib import Path

DECISION_LOG = Path("control/DECISION_LOG.md")
CHANGELOG = Path("control/ETF_SESSION_CHANGELOG.md")
TEMPORARY_FILES = (
    Path(".github/workflows/append-position-count-governance-20260717.yml"),
    Path("control/run_queue/append_position_count_governance_20260717.md"),
    Path("tools/append_position_count_governance_20260717.py"),
)

DECISION_MARKER = "## 2026-07-17 — Every non-zero ETF position counts toward the maximum"
DECISION_ENTRY = r'''

---

## 2026-07-17 — Every non-zero ETF position counts toward the maximum

### Decision

Every unique ticker with `shares > 0` counts as one active position. Zero-share rows do not count, duplicate active ticker rows are invalid, and there is no generic residual-position exception. The default maximum is eight active positions.

The current nine-position state is classified `close_first`. A no-trade review may preserve that state, but any proposed trade while above the limit must reduce the active count and may not open a new ticker. At exactly eight positions, opening a new ticker requires another ticker to reach zero shares in the same projected whole-share execution. A partial reduction that leaves positive shares does not free a slot.

### Consequence

The standard production preflight evaluates projected whole-share quantities before guarded mutation and fails closed on a count breach. Current matching English and Dutch report surfaces disclose the actual count; historical reports with a different ticker set remain unchanged.

This decision does not select a holding to close and does not authorize portfolio mutation or delivery. A separately claimed, current-evidence close-first review is required before any count-reducing execution.

Persistent decision and evidence:

```text
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
```
'''

CHANGELOG_MARKER = "## 2026-07-17 — Position-count constraint reconciled with close-first enforcement"
CHANGELOG_ENTRY = r'''

---

## 2026-07-17 — Position-count constraint reconciled with close-first enforcement

`WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION` resolved the ambiguity between the official nine-position whole-share state and the eight-position maximum without changing holdings.

Decision:

```text
every non-zero position counts
generic residual exception: false
current state: close_first 9/8
new ticker while over limit: blocked
new ticker at limit: full source close required in same whole-share transition
```

Implemented:

```text
runtime/position_count_contract.py
runtime/position_count_report_surface.py
tools/validate_etf_persisted_valuation_state.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_position_count_contract.py
tests/test_etf_position_count_contract.py
.github/workflows/validate-etf-position-count-contract.yml
```

Validation:

```text
PR: #91
merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
focused tests: 13 passed
final position-count run: 29618185729 success
final report-surface run: 29618185736 success
final current-runtime cockpit run: 29618185701 success
final WP08 run: 29618185711 success
final WP11 run: 29618185709 success
final recovery run: 29618185751 success
final fresh-send diagnostic run: 29618185706 success
protected authority hashes: identical
historical report hashes: identical
portfolio execution: false
email sent: false
```

The client output guard is current-state-aware: it discloses `9 / 8` only when the report ticker set exactly matches official state and leaves historical reports unchanged. The next package is `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW`; it must use fresh evidence and must not assume XLU is automatically the correct closure source.
'''


def append_once(path: Path, marker: str, entry: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    path.write_text(text.rstrip() + entry.rstrip() + "\n", encoding="utf-8")
    return True


def main() -> None:
    decision_changed = append_once(DECISION_LOG, DECISION_MARKER, DECISION_ENTRY)
    changelog_changed = append_once(CHANGELOG, CHANGELOG_MARKER, CHANGELOG_ENTRY)

    for path in TEMPORARY_FILES:
        path.unlink(missing_ok=True)

    print(
        "ETF_POSITION_COUNT_GOVERNANCE_APPEND_OK | "
        f"decision_changed={str(decision_changed).lower()} | "
        f"changelog_changed={str(changelog_changed).lower()} | "
        "temporary_files_removed=true | portfolio_mutation=false | email_sent=false"
    )


if __name__ == "__main__":
    main()
