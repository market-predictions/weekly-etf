# Weekly ETF report request

## Request

```text
Send fresh weekly ETF Pro reports.
```

## Trigger intent

This file intentionally triggers the production workflow:

```text
.github/workflows/send-weekly-report.yml
```

## Scope

```text
normal production report generation and delivery validation
```

## Boundaries

```text
no new deterministic-regime logic
no manual portfolio mutation outside guarded workflow logic
no delivery success claim until workflow and manifest evidence exist
```

## Requested by

```text
user via ChatGPT project session
```
