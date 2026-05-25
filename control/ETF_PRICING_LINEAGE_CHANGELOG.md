# ETF Pricing Lineage Changelog

This file is the central changelog for the ETF pricing-lineage repair track. It is separate from the root `changelog.md` so pricing regressions, design decisions, and validation changes can be reviewed without scanning unrelated rendering, localization, or delivery changes.

## Rules

- Record every meaningful pricing-lineage design, code, workflow, validation, and state-contract change.
- Keep entries implementation-facing and regression-friendly.
- Include why the change was made, what changed, affected files, and validation evidence.
- Do not use this file for ordinary report content changes unless they affect pricing lineage.
- Keep root `changelog.md` updated for repo-level visibility; keep this file as the detailed pricing-lineage log.

---

## 2026-05-24 — Upgrade ETF price-row schema and exact/prior status semantics

### Current issue

The ETF report now exposes close-price rows, but the audit still used legacy statuses such as `fresh_close` and `fresh_fallback_source`. That allowed an exact requested-date close and a latest prior provider close to be treated too similarly. The audit also lacked a normalized place for selected close, raw/adjusted close, provider symbol, provider exchange, finality, price role, and pricing tier.

### Root cause

The old pricing model treated provider success as enough. It did not separate the evidence questions required by `ETF_PRICING_LINEAGE_CONTRACT_V1`:

- Was the close exactly on the requested close date?
- Was it merely the latest valid prior market close?
- Which provider symbol was requested?
- Which close field was selected?
- Was the row valuation-grade or research-grade?

### What changed

- `pricing/models.py`
  - Added explicit statuses:
    - `fresh_exact_close`
    - `fresh_exact_unverified`
    - `prior_valid_close`
    - `carried_forward`
    - `unresolved`
    - `blocked`
  - Kept `fresh_close` and `fresh_fallback_source` as legacy inputs, normalized by `PriceResult.__post_init__`.
  - Added close-lineage fields: `provider_symbol`, `provider_exchange`, `raw_close`, `adjusted_close`, `selected_close`, `selected_close_type`, `provider_timestamp`, `provider_timezone`, `is_final_eod_bar`, `asset_role`, `pricing_tier`, and `verification`.
  - Added shared status sets for exact and priced closes.

- `pricing/close_resolver.py`
  - Uses explicit priced-close statuses as success states.
  - Adds resolver-level asset role and pricing tier to each resolved row.
  - Passes provider symbol and expected exchange into provider clients.

- `pricing/symbol_resolver.py`
  - Added provider-symbol and expected-exchange lookup.

- `pricing/source_registry.yaml`
  - Added explicit provider-symbol and expected-exchange metadata for current ETF holdings.

- Provider clients:
  - `pricing/clients/twelve_data.py`
  - `pricing/clients/yahoo_history.py`
  - `pricing/clients/fmp.py`
  - `pricing/clients/alpha_vantage.py`
  - `pricing/clients/issuer_override.py`
  - `pricing/clients/ecb_reference.py`
  - `pricing/fx_resolver.py`
  - These now emit exact/prior status semantics and lineage fields where available.

- Runtime/report consumers:
  - `pricing/run_pricing_pass.py` now counts only exact-close holdings as fresh and records prior-valid rows separately.
  - `runtime/build_etf_report_state.py` now values holdings from `selected_close` when present and records pricing close type/tier into runtime positions.
  - `runtime/add_etf_pricing_basis_section.py` now renders client-facing exact/prior status labels and uses `selected_close` when present.
  - `pricing/augment_challenger_pricing.py` and `runtime/score_etf_lanes.py` now understand explicit priced-close statuses.

### Affected files

- `pricing/models.py`
- `pricing/close_resolver.py`
- `pricing/symbol_resolver.py`
- `pricing/source_registry.yaml`
- `pricing/clients/twelve_data.py`
- `pricing/clients/yahoo_history.py`
- `pricing/clients/fmp.py`
- `pricing/clients/alpha_vantage.py`
- `pricing/clients/issuer_override.py`
- `pricing/clients/ecb_reference.py`
- `pricing/fx_resolver.py`
- `pricing/run_pricing_pass.py`
- `pricing/augment_challenger_pricing.py`
- `runtime/build_etf_report_state.py`
- `runtime/add_etf_pricing_basis_section.py`
- `runtime/score_etf_lanes.py`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `changelog.md`

### Validation / evidence

No production workflow run has been executed yet after this implementation. The next validation step is a fresh ETF workflow run. Expected evidence:

- New audit rows contain `selected_close`, `selected_close_type`, `provider_symbol`, `provider_exchange`, `is_final_eod_bar`, `pricing_tier`, and `verification`.
- Exact requested-date rows are labeled `fresh_exact_unverified` unless/until independent verification is added.
- Prior rows are labeled `prior_valid_close` rather than generic `fresh_fallback_source`.
- The report disclosure renders these as readable client-facing statuses.

### Remaining gaps

This closes Phase 1B step 7 at schema/status level, but independent verification remains intentionally open. `fresh_exact_close` should be reserved for rows that pass the future cross-provider verification layer. The next implementation step is Phase 1B step 8: persist successful runtime valuation state into `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv`.

---

## 2026-05-24 — Implement immutable ETF run identity and run manifest wiring

### Current issue

The ETF workflow had started to show close-price disclosure in the report, but the production run still relied on multiple `latest_file()` selections. Same-day pricing runs could overwrite the audit file, and downstream stages could independently choose the latest audit/runtime artifact instead of using the exact artifact created by the current run.

### Root cause

The workflow did not establish one immutable run id before pricing, did not pass an exact pricing-audit path forward, and did not write a central run manifest that connected the audit, runtime state, English report, Dutch report, and persisted artifacts.

### What changed

- `pricing/audit_writer.py`
  - Added optional `run_id` support.
  - Production audit files now use `price_audit_<requested_close_date>_<run_id>.json` when a run id is supplied.
  - The old `price_audit_<run_date>.json` naming remains only as a backward-compatible fallback for non-production callers.

- `pricing/run_pricing_pass.py`
  - Added `--run-id`.
  - Emits `run_id`, `report_token`, and immutable `audit=` path in the pricing log.
  - Writes `output/pricing/latest_price_audit_path.txt` as a compatibility pointer, while keeping the immutable audit as source of truth.

- `runtime/build_etf_report_state.py`
  - Added `--pricing-audit`, `--lane-artifact`, and `--output-path` support.
  - Reads explicit pricing/lane paths from CLI or environment.
  - Writes run-scoped runtime files when `run_id` exists.
  - Writes `output/runtime/latest_etf_report_state_path.txt` as a compatibility pointer.

- `tools/write_weekly_etf_run_manifest.py`
  - New manifest writer under `output/run_manifests/`.
  - Captures run id, requested close date, report token, pricing audit, runtime state, English/Dutch report paths, state paths, pricing summary, and runtime summary.

- `.github/workflows/send-weekly-report.yml`
  - Added `contents: write` and full checkout history for artifact commit-back.
  - Added `Resolve ETF run identity` step.
  - Passes `--requested-close-date` and `--run-id` into pricing.
  - Captures `ETF_PRICING_AUDIT_PATH` from pricing output.
  - Passes explicit pricing audit into first and final lane discovery.
  - Passes explicit audit/lane paths into challenger pricing and runtime state build.
  - Passes explicit runtime state and pricing audit into pricing-basis disclosure injection.
  - Writes a run manifest after report build and a final manifest in an `always()` step.
  - Commits output artifacts, pricing audits, runtime state, run manifests, market history, lane reviews, macro output, and state files back to `main` with `[skip ci]`.

### Affected files

- `pricing/audit_writer.py`
- `pricing/run_pricing_pass.py`
- `runtime/build_etf_report_state.py`
- `tools/write_weekly_etf_run_manifest.py`
- `.github/workflows/send-weekly-report.yml`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `changelog.md`

### Validation / evidence

This is a workflow/code commit. No production run has been executed yet after these changes. The next validation step is a manual or run-queue triggered ETF workflow run. Expected evidence:

- `output/pricing/price_audit_<requested_close_date>_<run_id>.json`
- `output/runtime/etf_report_state_<requested_close_date_without_dashes>_<run_id>.json`
- `output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json`
- workflow log lines for `PRICING_AUDIT_PATH_OK`, `LANE_ARTIFACT_PATH_OK`, `ETF_RUNTIME_STATE_OK`, and `ETF_RUN_MANIFEST_OK`

### Remaining gaps

This closes Phase 1B step 6 only. It does not yet implement:

- independent verification
- canonical portfolio-state and valuation-history persistence from runtime valuation
- hard `tools/validate_etf_pricing_lineage_contract.py`

---

## 2026-05-24 — Create ETF Pricing Lineage Contract V1

### Current issue

The ETF report can now display a per-holding close-price disclosure table that reconciles internally with Section 7 and Section 15, but the repository still lacks a hard proof that one immutable pricing audit flows through runtime state, English/Dutch report render, persisted portfolio state, valuation history, and delivery manifest.

### Root cause

The existing system still relies too heavily on latest-file selection and report-time runtime derivation. It can show fresh prices without also proving immutable audit identity, provider symbol lineage, exact close-date semantics, independent verification, and post-run state persistence.

### What changed

- Added `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`.
- Defined the target artifact chain:
  - requested close date and report token
  - immutable pricing audit
  - explicit run manifest
  - runtime report state
  - English/Dutch reports
  - delivery assets
  - persisted portfolio state
  - persisted valuation history
- Defined the required status split:
  - `fresh_exact_close`
  - `fresh_exact_unverified`
  - `prior_valid_close`
  - `carried_forward`
  - `unresolved`
  - `blocked`
- Defined valuation-grade versus research-grade challenger pricing tiers.
- Defined the required future hard validator: `tools/validate_etf_pricing_lineage_contract.py`.

### Weekly Index lesson imported

The Weekly Index repo already has a stronger pattern where pricing writes canonical state and valuation history, and the workflow commits pricing, runtime, report, manifest, state, and candidate artifacts back to the repo. ETF should copy that operating discipline.

### Improvement beyond Weekly Index

ETF should not copy Weekly Index blindly. The ETF contract requires stronger immutable run identity, exact/prior close-date semantics, provider-symbol lineage, independent verification, and valuation-grade challenger enforcement.

### Affected files

- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

### Validation / evidence

No runtime code was changed in this entry. This is a design/control-layer commit that defines the implementation target before touching production pricing code.

---

## Open regression themes to close

### A. Latest-file ambiguity

Partly addressed. Production workflow now passes explicit audit/runtime/lane paths through the current run. Some legacy scripts and validators still use latest-file selection and need to be migrated in later phases.

### B. State persistence gap

Current ETF reports can derive a new runtime NAV without updating `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv` as canonical state. This remains open.

### C. Weak fresh-close semantics

Addressed at schema/status level. New rows now distinguish exact requested-date closes from prior valid market closes. Independent verification remains open, so most exact provider closes should be `fresh_exact_unverified` until the cross-provider verifier is added.

### D. Challenger pricing tier ambiguity

Partly addressed. Resolver-level rows now carry `pricing_tier`, with holdings and challengers treated as valuation-grade and broad radar rows treated as research-grade. Enforcement that fundable challengers must have valuation-grade pricing remains open.

### E. Missing independent verification

Provider closes should be cross-checked where feasible. When cross-check is unavailable, the audit now says `verification.status = not_checked`; cross-provider verification remains open.
