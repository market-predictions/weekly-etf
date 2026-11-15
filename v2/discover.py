"""Probe the US universe and find/verify the European mirror line for each fund.

Prints and writes v2/evidence/discover.json. Run in CI (needs Yahoo)."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from v2 import sources as S

ROOT = Path(__file__).resolve().parent
EUR_EXCH = {"GER": ".DE", "AMS": ".AS", "PAR": ".PA", "MIL": ".MI", "EBS": ".SW"}
POOL_SUFFIX = {"Xetra": ".DE", "Euronext Amsterdam": ".AS"}


def chart(symbol: str, days: int = 1900) -> dict:
    end = date.today()
    start = end - timedelta(days=days)
    p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime(end.year, end.month, end.day, 23, 59, tzinfo=timezone.utc).timestamp())
    try:
        r = S._get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", period1=p1, period2=p2, interval="1d")
        c = (r.json().get("chart") or {}).get("result") or []
        if not c:
            return {"symbol": symbol, "ok": False}
        m = c[0].get("meta") or {}
        ts = c[0].get("timestamp") or []
        cl = [v for v in (((c[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []) if v is not None]
        first = datetime.fromtimestamp(ts[0], tz=timezone.utc).date().isoformat() if ts else None
        return {"symbol": symbol, "ok": bool(cl), "currency": m.get("currency"), "name": m.get("longName") or m.get("shortName"),
                "first": first, "n": len(cl), "last": round(cl[-1], 4) if cl else None}
    except Exception as exc:
        return {"symbol": symbol, "ok": False, "error": type(exc).__name__}


def search(q: str) -> list[dict]:
    try:
        r = S._get("https://query2.finance.yahoo.com/v1/finance/search", q=q, quotesCount=25, newsCount=0)
        return [x for x in (r.json().get("quotes") or []) if x.get("exchange") in EUR_EXCH]
    except Exception:
        return []


def main() -> None:
    uni = yaml.safe_load((ROOT / "universe.yml").read_text())["instruments"]
    pool = {i["id"]: i for i in yaml.safe_load((ROOT / "mirror_pool.yml").read_text())["instruments"]}
    import os
    only_f = ROOT / "only.txt"
    only = set(filter(None, (only_f.read_text().strip() if only_f.exists() else os.environ.get("V2_ONLY", "")).split(",")))
    out = []
    for inst in uni:
        m = inst.get("mirror") or {}
        if only and inst["id"] not in only:
            continue
        us = chart(inst["id"])
        row = {"id": inst["id"], "us": us, "mirror": m, "candidates": []}
        queries = m.get("query") or []
        queries = [queries] if isinstance(queries, str) else queries
        if only and inst["id"] not in only:
            continue
        seen = set()
        for qq in queries:
            for q in search(qq)[:8]:
                sym = q["symbol"]
                if sym in seen:
                    continue
                seen.add(sym)
                c = chart(sym)
                c["search_name"] = q.get("longname") or q.get("shortname")
                if c.get("currency") == "EUR":
                    row["candidates"].append(c)
                S.pause(0.3)
        for key in ("id", "fallback"):
            if m.get(key) in pool:
                p = pool[m[key]]
                row[f"pool_{key}"] = chart(p["id"] + POOL_SUFFIX[p["exchange"]], days=30)
        out.append(row)
        cands = "; ".join(f"{c['symbol']} {c['first']} {c.get('search_name')}" for c in row["candidates"][:5])
        print(f"DISC {inst['id']:5} us={us.get('ok')} {us.get('currency')} first={us.get('first')} name={us.get('name')} | "
              f"{m.get('kind')} id={m.get('id')} | {cands}", flush=True)
        S.pause(0.3)
    ev = ROOT / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "discover.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
