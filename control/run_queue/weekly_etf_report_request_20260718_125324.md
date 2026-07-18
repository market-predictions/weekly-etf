# Weekly ETF report request

requested_at_utc: 2026-07-18T12:53:24Z
requested_by: ChatGPT
mode: fresh-runtime-production-report-only
repository: market-predictions/weekly-etf
report_scope: standard U.S. Weekly ETF Pro report
requested_close_date: 2026-07-17
portfolio_execution_authorized: false
delivery_authorized: true
broker_execution_authorized: false
note: User explicitly requested a fresh Weekly ETF report generation and bilingual email delivery after the cockpit email inline-style correction.

## Required production proof

1. refresh holding and challenger pricing for the latest completed U.S. session;
2. refresh relative strength, macro evidence and lane scoring;
3. generate current English and Dutch reports from official portfolio authority;
4. do not write model trades to official portfolio shares or the trade ledger;
5. render one inline-styled email cockpit per language and preserve the classic report body;
6. validate pricing lineage, whole shares, position count, client language, HTML and PDF;
7. send both language editions;
8. persist run and delivery manifests;
9. confirm both messages in the receiving inbox before delivery is called successful.
