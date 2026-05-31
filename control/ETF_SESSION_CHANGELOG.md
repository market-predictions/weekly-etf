# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

It is intentionally separate from specialized logs:

- `control/ETF_PRICING_LINEAGE_CHANGELOG.md` — pricing-lineage specific implementation/regression history
- `control/DECISION_LOG.md` — stable architecture decisions only
- `control/CURRENT_STATE.md` — current state snapshot
- `control/NEXT_ACTIONS.md` — roadmap / active backlog

## Rules

- Record every meaningful architecture, workflow, control-file, validator, runtime, delivery, roadmap, and handover-relevant change.
- Include the current issue, root cause, what changed, affected files, validation evidence, and remaining work.
- Keep entries specific enough that a fresh chat can continue without relying on hidden memory.
- Do not use this file for ordinary report-content edits unless they affect workflow, state, validation, delivery, or roadmap direction.
- Specialized changes may be summarized here and tracked in more detail in their dedicated changelog.

---

## 2026-05-31 — Macro/thesis roadmap reviewed, parked, and accepted as future workstream

### Current issue

The user provided macro/regime/thesis work packages for the `weekly-etf` repo and asked for first-principles assessment of what is valid, implementable, or should be discarded.

### Root cause / architectural tension

The repo is now a runtime-driven ETF report system. Macro/thesis improvements are valuable, but they touch all four layers:

1. decision framework
2. input/state contract
3. output contract
4. operational runbook

Implementing all WPs as one broad change would risk recreating the old patch-cycle problem.

### What changed

- Created and committed the discussion roadmap:
  - `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md`
- Recorded the roadmap in the control layer.
- Locked the sequencing:

```text
pricing lineage baseline confirmed
→ macro audit foundation
→ deterministic regime and confidence engine
→ macro policy pack schema
→ compliance and methodology gates
→ thesis candidates in shadow mode
→ Stage-2 confirmation and valuation flags
→ client-surface integration only after validation
```

### Stable decisions

- Macro/regime modernization is approved only as a post-pricing-lineage enhancement.
- WP-1 to WP-4 may be built as internal/shadow artifacts first.
- WP-9 Stage-1 thesis candidates must remain internal and must not appear as client-facing recommendations.
- Fundable means thesis + market confirmation + valuation-grade pricing + portfolio discipline gates.
- Institutional overlay may cap confidence but must never set regime or portfolio action.

### Remaining work

- Add macro policy pack schema / compatibility adapter.
- Add deterministic regime/confidence engine in shadow mode.
- Add methodology and compliance gates.
- Only later add WP-9 thesis candidates and Stage-2 confirmation.

---

## 2026-05-31 — Pricing-lineage status challenged with uploaded reports

### Current issue

The assistant initially described pricing as not fully fixed. The user challenged this by uploading the latest English and Dutch reports showing fresh close rows and NAV reconciliation.

### Root cause / clarification

There are two different questions:

1. Does pricing work in the client-facing report?
2. Is the full pricing-lineage contract proven end to end by hard validator and manifest evidence?

The uploaded reports proved the first, but PDFs alone could not prove the second.

### Conclusion

- Pricing retrieval and report-level reconciliation were reclassified as fixed.
- Remaining issue was narrowed to final audit-proof closure: manifest → pricing audit → runtime state → reports → persisted state → valuation history → hard validator.

### Remaining work at that point

- Confirm `tools/validate_etf_pricing_lineage_contract.py` exists.
- Confirm it is wired before send.
- Run one fresh workflow to prove `pricing_lineage_status=passed`.

---

## 2026-05-31 — Hard pricing-lineage validator confirmed and fresh workflow triggered

### Current issue

The repo needed proof that pricing lineage was not merely visible in the report but enforced before delivery.

### What changed / confirmed

Confirmed that the hard validator and pre-send gate already existed:

- `tools/validate_etf_pricing_lineage_contract.py`
- `tools/validate_etf_client_surface_clean.py`
- `tools/write_weekly_etf_run_manifest.py`
- `.github/workflows/send-weekly-report.yml`

Then triggered fresh report runs via safe run-queue request files under:

```text
control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
```

### Important workflow rule

From now on, ChatGPT should inspect GitHub run artifacts/manifests/logs itself rather than asking the user to manually check the Actions tab, unless connector evidence is insufficient.

---

## 2026-05-31 — First confirmation run failed after successful pricing

### Current issue

A fresh run produced a pricing audit and manifest, but failed before runtime report-state generation.

### Evidence

The run manifest showed:

```text
run_id: 20260531_195304
requested_close_date: 2026-05-29
pricing_lineage_status: workflow_failure
fresh_holdings_count: 7
holdings_count: 7
coverage_count_pct: 100.0
carried_forward_holdings_count: 0
unresolved_tickers: []
runtime_state_path: null
```

### Conclusion

Pricing was not the failure point. The failure happened after pricing and before runtime-state/report generation.

---

## 2026-05-31 — Relative-strength fetch made robust with cached fallback

### Current issue

The workflow failed after pricing and before runtime-state generation. The next fragile step was the public `yfinance` relative-strength refresh.

### Root cause

Relative strength is useful for discovery scoring but is not the same authority layer as valuation-grade pricing. A transient public-history failure should not block pricing-lineage confirmation if a previous valid artifact exists.

### What changed

Updated:

- `runtime/fetch_etf_relative_strength.py`

Added behavior:

- Attempt live `yfinance` refresh first.
- If live refresh fails, reuse existing `output/market_history/etf_relative_strength.json` only if it contains metrics.
- Mark fallback explicitly with:
  - `source: yfinance_cached_fallback`
  - `is_live_refresh: false`
  - `fallback_used: true`
  - `fallback_reason`
  - `fallback_at_utc`
  - `cache_source_file`
- Emit `ETF_RELATIVE_STRENGTH_FALLBACK_OK` when fallback is used.

### Commit

- `332570db5dfc4913b65124c809c292717a054b5b`

### Consequence

Pricing lineage remains strict. Relative-strength refresh becomes fail-soft with explicit artifact provenance.

---

## 2026-05-31 — Shadow macro audit made non-blocking

### Current issue

A second confirmation run progressed further and refreshed relative strength, but still failed before runtime-state generation. The next likely blocker was the Phase 2 macro audit live fetch.

### Root cause

The macro audit foundation is explicitly shadow-only and not yet production authority. It should not block report generation or pricing-lineage confirmation while deterministic regime/schema/compliance gates are not yet promoted.

### What changed

Updated:

- `runtime/build_macro_policy_pack.py`

Added behavior:

- If an explicit macro audit path is supplied, validate it strictly.
- If live shadow macro audit building fails, print `ETF_MACRO_DATA_AUDIT_SHADOW_UNAVAILABLE` and continue with `macro_data_audit_path=None`.
- Record macro audit status as:
  - `present: false`
  - `status: shadow_unavailable`
  - `shadow_only: true`
  - `client_facing_authority: false`
  - `decision_impact: none_phase2_audit_only`

### Commit

- `8b5bd55fff5aca9a78790afaa32223538cc76316`

### Consequence

The macro audit remains available as a shadow artifact but cannot block production report delivery while non-authoritative.

---

## 2026-05-31 — Pricing lineage passed in fresh confirmation run

### Current issue

The repo needed one fresh run to prove the full pricing-lineage contract after the hard validator and robustness patches.

### Evidence

The successful confirmation run produced:

```text
run_id: 20260531_200843
requested_close_date: 2026-05-29
pricing_lineage_status: passed
workflow_conclusion: success
english_report_path: output/weekly_analysis_pro_260529_22.md
dutch_report_path: output/weekly_analysis_pro_nl_260529_22.md
runtime_state_path: output/runtime/etf_report_state_20260529_20260531_200843.json
pricing_audit_path: output/pricing/price_audit_2026-05-29_20260531_200843.json
total_portfolio_value_eur: 109964.97
```

The validator confirmed holdings:

```text
GLD, GSG, PAVE, PPA, SMH, SPY, URNM
```

### What changed

Updated the control layer:

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`

### Commits

- `53ae01ae182beb3b070cbe39ad59189c82673e20` — update current state after pricing-lineage confirmation
- `f94ae972c1697f9b584e82e50d84d03ece6ea51a` — update next actions after pricing-lineage closure

### Stable status

```text
Pricing lineage: closed baseline / active regression guard
Next major roadmap: macro/regime/thesis modernization, shadow-first
```

### Important caveat

Do not claim independent email delivery success from this manifest alone. The run produced report/PDF artifacts and `workflow_conclusion: success`, but `delivery_manifest_path` was null in the manifest. Delivery still requires a receipt/manifest or explicit user confirmation.

---

## 2026-05-31 — Current roadmap after pricing-lineage closure

### Immediate next work

Continue the approved roadmap with Phase 2/3 macro-regime work, not more broad pricing repair:

1. Preserve Phase 2 macro audit as shadow-only.
2. Add fixture replay examples for no-network validation.
3. Define `schemas/macro_policy_pack.schema.json`.
4. Add a compatibility adapter so legacy `lane_adjustments` remains available.
5. Add deterministic regime/confidence engine in shadow mode.
6. Compare old versus new pack outputs before production promotion.

### Do not do yet

- Do not move WP-9 thesis candidates into production.
- Do not let macro audit values directly alter client-facing regime, confidence, lane scoring, fundability, or report wording.
- Do not expose Stage-1 thesis candidates in client reports.

---

## 2026-05-31 — Macro policy pack schema and compatibility gate added

### Current issue

After pricing-lineage closure, the next approved roadmap item was to formalize the macro policy pack contract before replacing the legacy regime/confidence logic.

### Root cause

`runtime/build_macro_policy_pack.py` already writes `output/macro/latest.json`, and lane discovery consumes that pack. Without a schema and validator, later macro/regime work could silently change lane scoring before fixture replay, methodology, compliance, and bilingual gates are ready.

### What changed

Added:

- `schemas/macro_policy_pack.schema.json`
- `tools/validate_macro_policy_pack.py`
- `control/MACRO_POLICY_PACK_SCHEMA_STATUS.md`

Updated:

- `runtime/build_macro_policy_pack.py`
- `.github/workflows/send-weekly-report.yml`
- `control/SYSTEM_INDEX.md`

### New contract

The macro policy pack now includes:

- `schema_version`
- `authority`
- `macro_data_audit_summary`
- `confidence_decomposition`
- `active_drivers`
- backward-compatible `lane_adjustments`

### Authority rules

- Legacy `lane_adjustments` remain available for existing lane discovery.
- `confidence_decomposition` is explanatory/shadow-only for now.
- `active_drivers` is an empty placeholder until WP-9 is built in shadow mode.
- Phase 2 macro audit remains shadow-only and non-authoritative.
- Deterministic regime/confidence is not yet production authority.

### Workflow change

The production workflow now validates the macro policy pack immediately after building it and before lane discovery consumes `output/macro/latest.json`.

Expected marker:

```text
ETF_MACRO_POLICY_PACK_SCHEMA_OK
```

### Commits

- `7dbaadaaa66ffa44a84b5cd9682619aac0a5828c` — add macro policy pack schema
- `296559dc4e84c12124a46ef9217106ed0c2602fb` — add macro policy pack validator
- `54e1f3d8b6408266bd98c72f585d693c24e3bbf4` — add schema compatibility fields to macro pack builder
- `cacfe1de2546b75303793158ffcaf42577ba5b63` — validate macro policy pack before lane discovery
- `1690c5f53c8f1200e5a710fc2e8d0be0411bb8c6` — register macro policy pack schema and validator in system index
- `133e475caa30f46c08b528a213a6bf5ce77390ed` — add macro policy pack schema status note

### Validation status

Not yet production-proven by a fresh workflow run after this patch set.

Next validation run should confirm:

```text
ETF_MACRO_POLICY_PACK_OK
ETF_MACRO_POLICY_PACK_SCHEMA_OK
ETF_LANE_DISCOVERY_OK
ETF_PRICING_LINEAGE_CONTRACT_OK
```

### Remaining work

Next roadmap item is deterministic regime/confidence in shadow mode:

- `config/regime_thresholds.yml`
- `macro_regime/classify.py`
- `macro_regime/confidence.py`

---

## Open watch items

### Delivery evidence

Workflow success is not the same as email delivery proof. The current manifest has `delivery_manifest_path: null`; delivery success needs a real receipt/manifest or user confirmation.

### Price verification

Rows may still show `fresh_exact_unverified`. Cross-provider verification could later upgrade rows to `fresh_exact_close` where independent sources agree.

### Dutch alias consolidation

Dutch labels and validator aliases are working but still distributed across several files. Consolidation remains a useful cleanup.

### Direct challenger-vs-holding scoring

The system has challenger pricing and broad relative strength, but still lacks explicit direct 1m/3m replacement-edge scoring versus each current holding.
