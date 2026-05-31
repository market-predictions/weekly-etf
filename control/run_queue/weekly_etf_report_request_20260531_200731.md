# Weekly ETF report request

requested_at_utc: 2026-05-31T20:07:31Z
requested_by: ChatGPT
mode: fresh-weekly-etf-review
purpose: pricing-lineage confirmation rerun after shadow macro audit fail-soft hardening

Run the production Weekly ETF workflow and verify the hard pricing-lineage pre-send gate.
Expected markers:

- ETF_RELATIVE_STRENGTH_OK or ETF_RELATIVE_STRENGTH_FALLBACK_OK
- ETF_MACRO_POLICY_PACK_OK
- ETF_PRICING_LINEAGE_CONTRACT_OK
- ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK

Do not treat delivery as confirmed unless the workflow produces the normal delivery evidence.
