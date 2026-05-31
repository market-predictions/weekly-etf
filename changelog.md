# Weekly ETF OS — Changelog

This file records meaningful codebase, workflow, rendering, state-contract, pricing, and delivery changes for `market-predictions/weekly-etf`.

## 2026-05-31 — Add hard ETF pricing-lineage validator and pre-send gate

### What changed
- Added `tools/validate_etf_pricing_lineage_contract.py` as the hard end-to-end validator required by `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`.
- The validator checks manifest → exact pricing audit → runtime state → report disclosure/Section 7/Section 15 → persisted portfolio state → valuation history.
- The validator recalculates NAV from shares × selected close ÷ FX + cash and fails on divergence.
- The validator checks exact/prior close semantics and required priced-row lineage fields.
- The validator verifies that fundable challenger lanes have valuation-grade priced audit rows.
- Updated `tools/write_weekly_etf_run_manifest.py` so `pricing_lineage_status=passed` is not overwritten by a later generic `workflow_*` status.
- Updated `tools/validate_etf_client_surface_clean.py` so the hard pricing-lineage validator runs in the existing pre-send validation path before email delivery.
- Updated `control/ETF_PRICING_LINEAGE_CHANGELOG.md` with the detailed implementation record.

### Why
The repo already had run ids, immutable audit filenames, run manifests, runtime state, visible close-price disclosure, and persisted valuation state. The missing piece was one hard gate proving that the full pricing lineage reconciles before delivery. Without this, workflow success and pricing-lineage proof could still be conflated.

### Affected files
- `tools/validate_etf_pricing_lineage_contract.py`
- `tools/write_weekly_etf_run_manifest.py`
- `tools/validate_etf_client_surface_clean.py`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `changelog.md`

### Validation / evidence
- No production workflow run has been executed yet after this validator/gate patch.
- Next fresh ETF run should show:
  - `ETF_PRICING_LINEAGE_CONTRACT_OK`
  - `ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK`
- The final manifest should preserve `pricing_lineage_status=passed` while separately recording workflow lifecycle status/conclusion.

---

## 2026-05-24 — Upgrade ETF price-row schema and exact/prior close semantics

### What changed
- Updated `pricing/models.py` with explicit pricing statuses: `fresh_exact_close`, `fresh_exact_unverified`, `prior_valid_close`, `carried_forward`, `unresolved`, and `blocked`, while preserving legacy `fresh_close` / `fresh_fallback_source` normalization for older rows.
- Added audit-row lineage fields for provider symbol, provider exchange, raw close, adjusted close, selected close, selected close type, provider timestamp/timezone, finality, asset role, pricing tier, and verification status.
- Updated `pricing/close_resolver.py`, `pricing/symbol_resolver.py`, and `pricing/source_registry.yaml` so provider-symbol and expected-exchange context flows into the pricing clients.
- Updated provider and FX clients to emit exact/prior status semantics and selected-close lineage where available.
- Updated `pricing/run_pricing_pass.py` so only exact requested-date holding closes count as fresh; prior valid rows are separated from exact fresh rows.
- Updated `pricing/augment_challenger_pricing.py`, `runtime/build_etf_report_state.py`, `runtime/add_etf_pricing_basis_section.py`, and `runtime/score_etf_lanes.py` to consume explicit priced-close statuses and selected close values.
- Updated `control/ETF_PRICING_LINEAGE_CHANGELOG.md` with the detailed implementation record.

### Why
The pricing audit must no longer treat exact requested-date closes and latest prior provider closes as equivalent. The audit row now carries the selected close, close type, provider symbol, expected exchange, pricing tier, and verification placeholder needed for the future hard pricing-lineage validator.

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
- No production workflow run has been executed yet after this schema/status change. Next validation step is a fresh ETF workflow run confirming that the audit rows contain the new lineage fields and that the report renders exact/prior statuses correctly.

---

## 2026-05-24 — Implement immutable ETF run identity and manifest wiring

### What changed
- Updated `pricing/audit_writer.py` so production pricing audits can be written as immutable `price_audit_<requested_close_date>_<run_id>.json` files.
- Updated `pricing/run_pricing_pass.py` with `--run-id`, explicit requested-close/report-token logging, immutable audit output, and a compatibility pointer at `output/pricing/latest_price_audit_path.txt`.
- Updated `runtime/build_etf_report_state.py` with explicit `--pricing-audit`, `--lane-artifact`, and `--output-path` support, plus run-scoped runtime state output and `output/runtime/latest_etf_report_state_path.txt`.
- Added `tools/write_weekly_etf_run_manifest.py` to write central run manifests under `output/run_manifests/`.
- Updated `.github/workflows/send-weekly-report.yml` to resolve one run id, pass explicit audit/lane/runtime paths through the workflow, write a manifest, and commit run artifacts back to main with `[skip ci]`.
- Updated `control/ETF_PRICING_LINEAGE_CHANGELOG.md` with the detailed implementation record.

### Why
The ETF pipeline needed to stop relying on independently selected `latest` audit/runtime artifacts. A report must be traceable to one immutable pricing audit and one run manifest before the deeper pricing-lineage validator can be added.

### Affected files
- `pricing/audit_writer.py`
- `pricing/run_pricing_pass.py`
- `runtime/build_etf_report_state.py`
- `tools/write_weekly_etf_run_manifest.py`
- `.github/workflows/send-weekly-report.yml`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `changelog.md`

### Validation / evidence
- No production workflow run has been executed yet after these code changes. Next validation step is a fresh ETF workflow run confirming immutable audit, runtime state, and run manifest artifacts are written and committed.

---

## 2026-05-24 — Add ETF pricing-lineage contract and central pricing changelog

### What changed
- Added `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md` as the authority for the next pricing hardening cycle.
- Added `control/ETF_PRICING_LINEAGE_CHANGELOG.md` as the central detailed changelog for pricing-lineage changes and regressions.
- Updated `control/SYSTEM_INDEX.md` to register the new pricing-lineage control files and the intended `output/run_manifests/` location.
- Updated `control/CURRENT_STATE.md` to mark pricing lineage as the active engineering priority and to clarify that visible close-price disclosure is not sufficient proof that the fresh-pricing issue is solved.
- Updated `control/NEXT_ACTIONS.md` with a dedicated Phase 1B for immutable audit identity, exact manifest linkage, price-row schema/status upgrades, state persistence, challenger pricing tiers, and a hard pricing-lineage validator.

### Why
The latest investigation showed that the report can display fresh closes and reconcile internally while still lacking a deterministic proof chain from immutable pricing audit to runtime state, report tables, persisted portfolio state, valuation history, and delivery manifest. The new contract prevents another round of surface-level patches and defines the implementation target before production pricing code is changed.

### Affected files
- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `control/SYSTEM_INDEX.md`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `changelog.md`

### Validation / evidence
- No runtime pricing code changed in this entry. This is a control/design-layer commit. Next validation is implementation of the contract and the future `tools/validate_etf_pricing_lineage_contract.py` gate.

---

## 2026-05-24 — Render ETF close disclosure from pricing audit, not portfolio state

### What changed
- Updated `runtime/add_etf_pricing_basis_section.py` so the close-price disclosure table is built from the latest `output/pricing/price_audit_*.json` rather than from the simplified portfolio-state position fields.
- The disclosure now shows requested close date, actual close date used, close price, currency, client-facing market-data source, and status.
- Internal resolver labels such as `issuer_override`, `source_detail`, and `handler` are no longer rendered client-facing.
- Removed visible HTML comment markers from the markdown/PDF output.
- Updated `tools/validate_etf_pricing_basis_disclosure.py` so it validates the heading/table itself instead of relying on hidden marker comments, and fails if internal pricing labels leak into the client report.

### Why
The previous disclosure made the pricing basis visible but was still not client-grade. It exposed implementation markers and showed `issuer_override` as the source, even when the audit showed delegated market data such as Yahoo history. The report must show the real audit-derived pricing basis in readable language, not internal plumbing labels.

### Affected files
- `runtime/add_etf_pricing_basis_section.py`
- `tools/validate_etf_pricing_basis_disclosure.py`
- `changelog.md`

### Validation / evidence
- User review showed visible `ETF_PRICE_BASIS_DISCLOSURE_*` markers and `issuer_override` in the delivered report. Next validation step is a fresh ETF production run.

---

## 2026-05-24 — Prioritize live API close discovery before issuer override

### What changed
- Updated `pricing/source_registry.yaml` so ETF holdings try `twelve_data`, `fmp`, `alpha_vantage`, and `yahoo_history` before `issuer_override`.
- Updated `pricing/clients/issuer_override.py` to describe itself as a last-resort issuer hook and record delegated Yahoo history explicitly in `source_detail` and metadata.

### Why
The report made clear that all current holding prices were coming from `issuer_override`. That was not the intended layered close-discovery behavior. The old source order let `issuer_override` short-circuit the normal API cascade, and the override implementation internally delegated to Yahoo while relabeling the result as `issuer_override`. The new order restores the expected API-first discovery path and keeps issuer override only as a final operational fallback.

### Affected files
- `pricing/source_registry.yaml`
- `pricing/clients/issuer_override.py`
- `changelog.md`

### Validation / evidence
- Previous report showed all six holdings with pricing source `issuer_override`. Next validation step is a fresh ETF production run; the disclosure table should show live/API sources where available, with `issuer_override:...:delegated_yahoo_history` only if all normal sources fail.

---

## 2026-05-24 — Treat DBC as optional RS duel proxy

### What changed
- Updated `tools/validate_replacement_duel_rs_coverage.py` so `DBC` is no longer a hard-required GLD challenger for the 1m/3m relative-strength gate.
- `GSG` remains the required broad-commodity challenger and `BIL` remains the required cash-like ballast challenger for GLD.
- `DBC` remains configured in the replacement-duel target map and can still be used when relative-strength data is available.

### Why
A fresh production run failed before report rendering because `DBC` lacked 1m/3m yfinance return data. That should not block the entire ETF production run when the required GLD replacement-duel coverage is still available through `GSG` and `BIL`. This keeps the RS quality gate intact for strategic required duels while treating source-fragile secondary proxies as optional.

### Affected files
- `tools/validate_replacement_duel_rs_coverage.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure: `Replacement duel RS coverage failed: required strategic tickers lack 1m/3m returns: DBC`. Next validation step is a fresh ETF production run.

---

## 2026-05-24 — Keep valuation history as first Section 7 table

### What changed
- Updated `runtime/add_etf_pricing_basis_section.py` so the explicit closing-price disclosure is inserted after the Section 7 valuation-history table rather than before it.
