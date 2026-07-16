# Post-execution correction runbook changelog

## 2026-07-16 — Canonical runbook cleanup

Implemented and validated under PR #72.

Changes:

- introduced `runtime/post_execution_correction_runbook.py` as the shared contract layer;
- converted the correction workflow to manual-only `validate_only`, `recover_no_send` and `send` modes;
- adopted the production `MRKT_RPRTS_*` mail contract;
- replaced JSON-manifest discovery with parsing of the positive bilingual text receipt and `.txt` manifest names;
- required independent request-file and workflow-dispatch confirmation before delivery;
- blocked reuse of an existing correction suffix;
- made recovery render-only and removed mail configuration from its environment;
- added transactional restoration when recovery would change existing historical report files;
- retired the one-shot dispatch bridge;
- added focused tests, a static contract validator and a read-only validation workflow.

Validation:

```text
final_head: b4aa326eefc42784537cb5baba76544ac59618ed
runbook_validation: 29520607344 — success
post_execution_consistency: 29520608204 — success
merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
```

No delivery or portfolio execution was performed as part of this cleanup.
