# Weekly ETF report request

requested_at_utc: 2026-05-31T20:22:50Z
requested_by: ChatGPT
mode: fresh-weekly-etf-review
purpose: validate macro policy pack schema gate before deterministic regime/confidence work

Run the production Weekly ETF workflow and verify the new macro policy pack schema gate.
Expected markers:

- ETF_MACRO_POLICY_PACK_OK
- ETF_MACRO_POLICY_PACK_SCHEMA_OK
- ETF_LANE_DISCOVERY_OK
- ETF_PRICING_LINEAGE_CONTRACT_OK
- ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK

Do not treat email delivery as confirmed unless the workflow produces a delivery receipt/manifest or the user confirms receipt.
