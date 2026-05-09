# ETF run queue

This folder contains small operational request files for repo-native pre-report and report-generation actions.

## Fresh Weekly ETF Pro report request

When the user asks ChatGPT to generate a fresh Weekly ETF Review, ChatGPT should create a request file here instead of creating placeholder files in `output/`.

Creating a file matching this path triggers `.github/workflows/send-weekly-report.yml`:

```text
control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
```

Recommended content:

```text
# Weekly ETF report request

requested_at_utc: YYYY-MM-DDTHH:MM:SSZ
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
note: User requested a fresh Weekly ETF Pro Review from ChatGPT.
```

The workflow itself generates the real English/Dutch runtime reports under `output/` during execution.

## Persistent ETF pricing audit

To run the persistent pricing preflight before generating a new Weekly ETF Review, create a file matching:

```text
control/run_queue/etf_pricing_request_YYYYMMDD_HHMMSS.md
```

The `Persist ETF pricing audit` workflow will:
1. run `python -m pricing.run_pricing_pass`,
2. write `output/pricing/price_audit_YYYY-MM-DD.json`,
3. validate the audit shape,
4. commit the audit back to GitHub if it changed.

## Important rule

Do **not** create trigger placeholder files under `output/`.

Bad:

```text
output/weekly_analysis_pro_trigger_*.md
```

Those files can be confused with production report files by old or fallback selection paths.

Good:

```text
control/run_queue/weekly_etf_report_request_*.md
```

The production send workflow should be triggered either by `workflow_dispatch`, by a real production report file, or by a safe request file in this run queue.
