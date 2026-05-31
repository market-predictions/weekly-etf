# Weekly ETF report request

requested_at_utc: 2026-05-31T19:52:05Z
requested_by: ChatGPT
mode: fresh-weekly-etf-review
purpose: pricing-lineage confirmation run

Run the production Weekly ETF workflow and verify the hard pricing-lineage pre-send gate.
Expected markers:

- ETF_PRICING_LINEAGE_CONTRACT_OK
- ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK

Do not treat delivery as confirmed unless the workflow produces the normal delivery evidence.
