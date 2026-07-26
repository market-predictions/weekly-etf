# Weekly ETF report request — portfolio-integrity corrected retry

Requested: 2026-07-26
Source blocker: run `20260726_165219` failed at the Dutch client-surface gate before delivery.
Mode: production Weekly ETF Pro, English and Dutch
Close basis: latest completed U.S. market close
Portfolio execution authorized: no
Broker execution authorized: no

Use the validated portfolio/watchlist integrity contract and the corrected native Dutch regime/ECB macro surface. Preserve the official 9-position portfolio, cash, whole-share quantities and close-first constraint. Open no new ticker and send only after all production gates pass. Persist run and delivery manifests.
