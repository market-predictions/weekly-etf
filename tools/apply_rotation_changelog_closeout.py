from pathlib import Path

path = Path("control/ETF_PORTFOLIO_ROTATION_CHANGELOG.md")
text = path.read_text(encoding="utf-8")
marker = "## 2026-07-15 — Current-run state authority and alternative-candidate correction"
if marker not in text:
    entry = r'''

---

## 2026-07-15 — Current-run state authority and alternative-candidate correction

The 2026-07-14 production report used fresh pricing and relative-strength discovery, but its rotation plan still consumed stale recommendation-memory valuation fields. It also treated lane alternatives as descriptive metadata rather than independently selectable destinations.

Added:

- `runtime/rotation_state_authority.py`;
- `runtime/portfolio_rotation_engine_v2.py`;
- `tools/validate_etf_rotation_state_authority.py`;
- `tests/test_etf_rotation_state_authority.py`;
- `.github/workflows/validate-etf-rotation-state-authority.yml`.

Changed:

- current-run pricing now determines market value, NAV and weights before rotation;
- P/L is recomputed from current close versus average entry;
- missing average entry is reconstructed from official trade-ledger references and model-execution artifacts or blocks rotation;
- the recommendation scorecard is refreshed before capital-release scoring;
- primary and alternative ETFs are scored independently;
- replacement-only alternatives require a direct 3-month edge of at least 10%;
- capped destination-score ties use direct-duel evidence, live-radar status, primary implementation, structural score, relative strength and liquidity rather than alphabetical order.

Validation:

```text
PR: #58
workflow_run_id: 29438154551
job_id: 87429929415
focused_tests: 10 passed
actual_2026-07-14_replay: passed
validated_holdings: 9
replay_mutation: URNM -> XBI, -5.00% / +5.00%, EUR 5511.24
```

This entry records implementation and replay proof. Official state mutation and client delivery remain dependent on merge and a fresh production report run.
'''
    path.write_text(text.rstrip() + entry + "\n", encoding="utf-8")
print("ETF_PORTFOLIO_ROTATION_CHANGELOG_CLOSEOUT_OK")
