# ETF Review OS — Current State

Date: 2026-08-28
Repository: `market-predictions/weekly-etf`
Authoritative code baseline: `main` at `3ffff5e6104fcc2b72ce6553718a59be2905d3af`

## Purpose of this file

This is the stable session-start summary for the US Weekly ETF Review OS. It describes current integrated architecture and authority boundaries. It deliberately does **not** copy volatile prices, holdings, NAV, latest run IDs or delivery receipts from machine state.

For volatile operational truth, read the canonical artifacts named in `control/SYSTEM_INDEX.md`, especially:

- `output/etf_portfolio_state.json`
- `output/etf_trade_ledger.csv`
- `output/etf_valuation_history.csv`
- `output/pricing/`
- `output/run_manifests/`
- `output/delivery/`
- `output/runtime/`

Git history and those artifacts retain prior run evidence. Historical July 2026 values previously copied into this file are evidence, not current routing authority.

## Integrated Review OS state

The repository currently has a governed four-layer operating model:

1. decision framework;
2. authoritative input/state contracts;
3. deterministic English/Dutch output contracts;
4. operational runbooks and delivery workflows.

Current `main` includes, among other integrated capabilities:

- the shared ETF strategy/portfolio-target contract while preserving product-specific implementation boundaries;
- project-local implementation versus independent release-assurance separation;
- exact-head and exact-main release-assurance validation;
- runtime-derived report state and persisted pricing/run lineage;
- bilingual report and delivery validation;
- receiving-system-aware delivery evidence rather than SMTP success alone;
- production-boundary cleanup that removed inherited FX runtime/output contamination from the US Weekly ETF product;
- client-safe macro/regime surfaces with explicit shadow/promotion boundaries;
- isolated cockpit-preview and optimization research lanes that do not become production authority by existence.

The current main head is the merge of PR #122, which enables exact-main release-assurance validation. Later work must be reconstructed from live GitHub state rather than inferred from this prose.

## Product identity

This repository is the **US Weekly ETF** product and donor/reference implementation for shared ETF contracts where explicitly governed.

It does not absorb:

- EU UCITS/investability semantics;
- broker-specific EU availability;
- PRIIPs/KID handling;
- FX-product runtime or outputs;
- a second portfolio/pricing/state authority.

Those remain separate product concerns.

## Operational authority

The machine-readable portfolio, ledger, pricing, run and delivery artifacts are authoritative for their respective facts. Markdown is not the primary holdings/pricing database.

No mission, documentation or review task may infer authority to:

- send or resend a report;
- invoke SMTP;
- execute broker actions;
- mutate portfolio state or the trade ledger;
- release or deploy;
- treat a review recommendation as an executed change.

Those actions require their separate current project authority and exact evidence gates.

## Current governance reconciliation

`WEEKLY_REVIEW_OS@2026-08-16-r2:WRO-GAP-10` identified that the former session-start state mixed a 19 July operational snapshot with later August architecture and governance. This file now separates stable architecture/authority from volatile machine state.

The companion `control/NEXT_ACTIONS.md` follows the same rule: it states only the current governed control direction and does not reactivate historical portfolio execution packages.

After this reconciliation is independently assured and integrated, Control must re-evaluate the active Mission Contract from authoritative state. This file does not hard-code a later mission gap as already authorized.

## Non-negotiable boundaries

- GitHub repository state outranks chat memory.
- Exact machine artifacts outrank copied narrative values for volatile state.
- Independent assurance never modifies the candidate it reviews.
- Delivery-ready is not delivered.
- Review evidence is not broker/portfolio execution authority.
- Missing or conflicting evidence fails closed.
- Shadow/lab/preview outputs are not production truth without explicit promotion.
- `principal_manual_relay_count` remains 0 in Control-managed lifecycle state.
