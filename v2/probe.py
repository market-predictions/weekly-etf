"""Probe every universe instrument against the free sources.

Answers two questions with evidence, per instrument:
1. Identity: does the ISIN map to the expected trading line, in EUR?
2. Coverage: which free sources return a recent daily close, and do they agree?

Writes v2/evidence/probe_<YYYYMMDD>.json and prints a summary table.
Quota-aware: Alpha Vantage (25/day) and EODHD (20/day) only probe a subset.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

import yaml

from v2 import sources as S

ROOT = Path(__file__).resolve().parent
AV_LIMIT = int(os.environ.get('V2_AV_LIMIT', '10'))
EODHD_LIMIT = int(os.environ.get('V2_EODHD_LIMIT', '15'))


STOP = {"ucits", "etf", "usd", "eur", "acc", "dist", "the", "and", "a", "of", "ii", "plc", "core"}


SYNONYMS = {"€": " euro ", "govt": "government", "corp": "corporate"}


def _tokens(text: str) -> set[str]:
    text = text.replace("€", SYNONYMS["€"])
    return {SYNONYMS.get(t, t) for t in _raw_tokens(text)}


def _raw_tokens(text: str) -> set[str]:
    return {t for t in "".join(c.lower() if c.isalnum() else " " for c in text).split() if t not in STOP and len(t) > 1}


def name_match(expected: str, reported: str) -> bool:
    exp, rep = _tokens(expected), _tokens(reported)
    return bool(exp) and len(exp & rep) / len(exp) >= 0.6


def main() -> None:
    universe = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    held = {"VWCE", "EUNA", "SXR8", "L0CK", "DFEN", "IQQQ"}
    today = date.today()
    start = today - timedelta(days=30)
    rows = []
    av_used = eod_used = 0
    # Held positions first so quota-limited sources cover them.
    ordered = sorted(universe, key=lambda i: (i["id"] not in held, i["id"]))
    for inst in ordered:
        ticker, exchange, isin = inst["id"], inst.get("exchange"), inst.get("isin")
        row = {"id": ticker, "isin": isin, "exchange": exchange, "draft_status": inst.get("status"), "sources": {}}
        if not isin or not exchange:
            row["identity"] = "isin_tbd"
            rows.append(row)
            continue
        expected = S.symbol_for("yahoo", ticker, exchange)
        mapped = S.yahoo_isin_symbols(isin)
        row["yahoo_isin_symbols"] = [m["symbol"] for m in mapped]
        row["isin_maps_to_expected_line"] = expected in row["yahoo_isin_symbols"]
        y = S.yahoo(ticker, exchange, start, today)
        row["yahoo_name"] = y.name
        row["yahoo_currency"] = y.currency
        results = [y]
        results.append(S.stooq(ticker, exchange, start))
        results.append(S.twelve_data(ticker, exchange, start))
        S.pause(8)  # Twelve Data free: 8 req/min
        if av_used < AV_LIMIT:
            results.append(S.alpha_vantage(ticker, exchange))
            av_used += 1
            S.pause(13)  # AV free: 5 req/min
        if eod_used < EODHD_LIMIT:
            results.append(S.eodhd(ticker, exchange, start))
            eod_used += 1
        for res in results:
            row["sources"][res.source] = {
                "symbol": res.symbol,
                "ok": bool(res.closes),
                "last_date": res.last_date,
                "last_close": res.closes.get(res.last_date) if res.last_date else None,
                "currency": res.currency,
                "error": res.error,
            }
        # Agreement on the most recent date that at least two sources share.
        shared = None
        dated = [r for r in results if r.closes]
        if len(dated) >= 2:
            common = set.intersection(*(set(r.closes) for r in dated[:2]))
            if common:
                shared = max(common)
        if shared:
            px = [r.closes[shared] for r in dated if shared in r.closes]
            row["agreement"] = {"date": shared, "n": len(px), "spread_pct": round((max(px) - min(px)) / min(px) * 100, 4)}
        # Yahoo's ISIN search returns only a fund's primary listing (often LSE), so it
        # cannot confirm the EUR line. Identity = EUR quote + fund-name match on the line.
        identity_ok = y.currency == "EUR" and name_match(inst.get("name", ""), y.name or "")
        row["identity"] = "verified" if identity_ok else "failed"
        rows.append(row)
        print("ROW " + json.dumps({k: row.get(k) for k in ("id", "yahoo_isin_symbols", "yahoo_currency", "yahoo_name")}
              | {s: (v["last_date"], v["last_close"], v["error"]) for s, v in row["sources"].items()}), flush=True)
        print(f"{ticker:6} identity={row['identity']:9} "
              + " ".join(f"{k}={'Y' if v['ok'] else 'n'}" for k, v in row["sources"].items())
              + (f" spread={row['agreement']['spread_pct']}%" if row.get("agreement") else ""), flush=True)

    out_dir = ROOT / "evidence"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"probe_{today:%Y%m%d}.json"
    out.write_text(json.dumps({"probe_date": today.isoformat(), "rows": rows}, indent=1))

    # Coverage summary
    srcs = ["yahoo", "stooq", "twelve_data", "alpha_vantage", "eodhd"]
    lines = ["| source | attempted | ok |", "|---|---|---|"]
    for s in srcs:
        att = sum(1 for r in rows if s in r["sources"])
        ok = sum(1 for r in rows if r["sources"].get(s, {}).get("ok"))
        lines.append(f"| {s} | {att} | {ok} |")
    ident = {k: sum(1 for r in rows if r.get("identity") == k) for k in ("verified", "failed", "isin_tbd")}
    lines.append(f"\nidentity: {ident}")
    summary = "\n".join(lines)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(summary)
    print(f"PROBE_WRITTEN {out}")


if __name__ == "__main__":
    main()
