"""Live macro context from official sources (no hard-coded stances).

Each indicator: latest value, its date, the value ~1 month earlier, and a
staleness flag. Missing or stale data is reported as such — never filled in.

Sources (no keys): ECB Data Portal, New York Fed (EFFR), Eurostat (HICP).
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (weekly-etf v2)"}

# id: (source, series key, label EN, label NL, unit, max_age_days)
SERIES = {
    "ecb_deposit_rate": ("ecb", "FM/D.U2.EUR.4F.KR.DFR.LEV", "ECB deposit rate", "ECB-depositorente", "%", 10),
    "fed_funds_effective": ("nyfed", "effr", "US federal funds rate (effective)", "Amerikaanse federal funds-rente (effectief)", "%", 10),
    "us_10y_yield": ("treasury", "10 Yr", "US 10-year Treasury yield", "Rente 10-jaars Amerikaanse staatsobligaties", "%", 10),
    "eurusd": ("ecb", "EXR/D.USD.EUR.SP00.A", "EUR/USD", "EUR/USD", "", 10),
    "us_inflation": ("bls", "CUUR0000SA0", "US inflation (CPI, y/y)", "Inflatie VS (CPI, j/j)", "%", 75),
}


def _ecb(key: str, start: date) -> list[tuple[str, float]]:
    flow, series = key.split("/", 1)
    r = requests.get(f"https://data-api.ecb.europa.eu/service/data/{flow}/{series}",
                     params={"startPeriod": start.isoformat(), "format": "csvdata"}, headers=UA, timeout=30)
    r.raise_for_status()
    out = []
    for row in csv.DictReader(io.StringIO(r.text)):
        if row.get("OBS_VALUE") not in (None, ""):
            p = row["TIME_PERIOD"]
            p = p + "-01" if len(p) == 7 else p  # monthly → first of month
            out.append((p, float(row["OBS_VALUE"])))
    return sorted(out)


def _fred(key: str, start: date) -> list[tuple[str, float]]:
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": key, "cosd": start.isoformat()}, headers=UA, timeout=30)
    r.raise_for_status()
    out = []
    for row in csv.reader(io.StringIO(r.text)):
        if len(row) == 2 and row[1] not in ("", ".") and row[0][:1].isdigit():
            out.append((row[0], float(row[1])))
    return sorted(out)


def _nyfed(key: str, start: date) -> list[tuple[str, float]]:
    r = requests.get(f"https://markets.newyorkfed.org/api/rates/unsecured/{key}/search.json",
                     params={"startDate": start.isoformat(), "endDate": date.today().isoformat()}, headers=UA, timeout=30)
    r.raise_for_status()
    return sorted((x["effectiveDate"], float(x["percentRate"])) for x in r.json().get("refRates", []) if x.get("percentRate") is not None)


def _eurostat(key: str, start: date) -> list[tuple[str, float]]:
    # key = "dataset:dim=value,dim=value". HICP moved to ECOICOP v2 in Jan 2026:
    # dataset prc_hicp_minr, dimension coicop18 (the old prc_hicp_manr froze at Dec 2025).
    dataset, dims = key.split(":", 1)
    params = dict(kv.split("=", 1) for kv in dims.split(","))
    params.update({"format": "JSON", "sinceTimePeriod": start.strftime("%Y-%m")})
    r = requests.get(f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}", params=params, headers=UA, timeout=30)
    r.raise_for_status()
    js = r.json()
    times = js["dimension"]["time"]["category"]["index"]  # {"2026-09": 0, ...}
    vals = js.get("value", {})
    out = []
    for period, idx in times.items():
        v = vals.get(str(idx))
        if v is not None:
            out.append((period + "-01", float(v)))
    return sorted(out)


def _treasury(key: str, start: date) -> list[tuple[str, float]]:
    out = []
    for y in range(start.year, date.today().year + 1):
        r = requests.get(f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all",
                         params={"type": "daily_treasury_yield_curve", "field_tdr_date_value": y, "page": "", "_format": "csv"}, headers=UA, timeout=30)
        r.raise_for_status()
        for row in csv.DictReader(io.StringIO(r.text)):
            if row.get(key) not in (None, ""):
                m, d_, yy = row["Date"].split("/")
                out.append((f"{yy}-{m}-{d_}", float(row[key])))
    return sorted(x for x in out if x[0] >= start.isoformat())


def _bls(key: str, start: date) -> list[tuple[str, float]]:
    """CPI index from the BLS public API (no key); returns year-on-year % per month."""
    r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                      json={"seriesid": [key], "startyear": str(start.year - 1), "endyear": str(date.today().year)}, headers=UA, timeout=30)
    r.raise_for_status()
    rows = r.json()["Results"]["series"][0]["data"]
    lvl = {f"{x['year']}-{x['period'][1:]}": float(x["value"]) for x in rows if x["period"].startswith("M") and x["period"] != "M13"}
    out = []
    for k, v in lvl.items():
        y, m = k.split("-")
        prev = lvl.get(f"{int(y) - 1}-{m}")
        if prev:
            out.append((f"{k}-01", round((v / prev - 1) * 100, 1)))
    return sorted(x for x in out if x[0] >= start.isoformat())


FETCHERS = {"ecb": _ecb, "fred": _fred, "nyfed": _nyfed, "eurostat": _eurostat, "treasury": _treasury, "bls": _bls}


def fetch(asof: date) -> dict:
    start = asof - timedelta(days=500)
    result = {}
    for sid, (src, key, en, nl, unit, max_age) in SERIES.items():
        item = {"label_en": en, "label_nl": nl, "unit": unit, "source": src, "series": key}
        try:
            obs = [(d, v) for d, v in FETCHERS[src](key, start) if d <= asof.isoformat()]
            if not obs:
                raise ValueError("no observations")
            d, v = obs[-1]
            month_ago = (date.fromisoformat(d) - timedelta(days=30)).isoformat()
            prev = [x for x in obs if x[0] <= month_ago]
            q_ago = (date.fromisoformat(d) - timedelta(days=88)).isoformat()
            prev_q = [x for x in obs if x[0] <= q_ago]
            year_ago = (date.fromisoformat(d) - timedelta(days=365)).isoformat()
            prev_y = [x for x in obs if x[0] <= year_ago]
            item.update({
                "date": d, "value": round(v, 4),
                "value_1m_ago": round(prev[-1][1], 4) if prev else None,
                "value_1y_ago": round(prev_y[-1][1], 4) if prev_y else None,
                "value_3m_ago": round(prev_q[-1][1], 4) if prev_q else None,
                "stale": (asof - date.fromisoformat(d)).days > max_age,
                "available": True,
            })
        except Exception as exc:
            item.update({"available": False, "error": f"{type(exc).__name__}: {str(exc)[:80]}"})
        result[sid] = item
    return result


def runtime(macro: dict) -> dict:
    """Inputs for the inflation rule. Missing or stale data → None (rule keeps the current bond fund)."""
    i = macro.get("euro_inflation") or {}
    if not i.get("available") or i.get("stale"):
        return {"hicp": None, "hicp_3m_ago": None}
    return {"hicp": i.get("value"), "hicp_3m_ago": i.get("value_3m_ago")}


def main() -> None:
    m = fetch(date.today())
    for k, v in m.items():
        print(f"MACRO {k}: {json.dumps(v)}")


if __name__ == "__main__":
    main()
