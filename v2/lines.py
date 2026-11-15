"""Try alternative EUR trading lines for instruments whose drafted line had no data."""
from __future__ import annotations

from datetime import date, timedelta

from v2 import sources as S

CANDIDATES = {
    "IBGS (IE00B14X4Q57 Euro Govt 1-3y)": [("IBGS", "Euronext Amsterdam"), ("IUSS", "Xetra"), ("EUN6", "Xetra")],
    "REMX (IE0002PG6CA6 VanEck Rare Earth)": [("VVMX", "Xetra"), ("REMX", "Euronext Amsterdam")],
    "EMBH (IE00B9M6RS56 JPM USD EM Bond EUR-H)": [("IUS7", "Xetra"), ("EMBE", "Euronext Amsterdam"), ("IEMB", "Euronext Amsterdam")],
    "UST10 (IE00B3VWN518 USD Treasury 7-10y)": [("SXRM", "Xetra"), ("CBU0", "Euronext Amsterdam"), ("IBTM", "Euronext Amsterdam")],
}


def main() -> None:
    end = date.today()
    start = end - timedelta(days=14)
    for label, options in CANDIDATES.items():
        for ticker, exchange in options:
            r = S.yahoo(ticker, exchange, start, end)
            print(f"LINE {label} | {r.symbol} | ok={bool(r.closes)} | cur={r.currency} | name={r.name} | last={r.last_date} {r.closes.get(r.last_date) if r.last_date else None}", flush=True)


if __name__ == "__main__":
    main()
