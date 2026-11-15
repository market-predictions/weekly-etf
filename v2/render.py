"""Render the weekly report (NL + EN) to HTML and PDF with WeasyPrint.

Layout: 1 summary & decisions · 2 performance & positions · 3 scan & markets ·
4 method & disclaimer. Every number comes from facts; every sentence of
commentary comes from narrate (AI or fallback).
"""
from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "assets" / "fonts"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1–3, validated adjacent (dataviz validator, light); aqua <3:1 → always labelled + legend

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
}
T = {
    "title": {"en": "Weekly ETF Review · US", "nl": "Wekelijkse ETF Review · VS"},
    "subtitle": {"en": "Model portfolio of US-listed ETFs, with a European UCITS mirror", "nl": "Modelportefeuille van Amerikaanse ETF's, met een Europese UCITS-spiegel"},
    "footer": {"en": "Model portfolio · rules-based · not personal advice", "nl": "Modelportefeuille · regelgebaseerd · geen persoonlijk advies"},
    "value": {"en": "Portfolio value", "nl": "Waarde portefeuille"},
    "week": {"en": "This week", "nl": "Deze week"},
    "since": {"en": "Since", "nl": "Sinds"},
    "cash": {"en": "Cash", "nl": "Kas"},
    "vs": {"en": "benchmark", "nl": "benchmark"},
    "decisions": {"en": "This week's decisions", "nl": "Besluiten deze week"},
    "h_happened": {"en": "What happened", "nl": "Wat er gebeurde"},
    "h_why": {"en": "Why", "nl": "Waarom"},
    "h_do": {"en": "What we are doing", "nl": "Wat we doen"},
    "att_title": {"en": "What explains the gap with the benchmark", "nl": "Wat verklaart het verschil met de benchmark"},
    "bench_label": {"en": "Benchmark (70% SPY / 30% AGG)", "nl": "Benchmark (70% SPY / 30% AGG)"},
    "mirror": {"en": "European mirror", "nl": "Europese spiegel"},
    "mirror_title": {"en": "The European mirror", "nl": "De Europese spiegel"},
    "mirror_intro": {"en": "European investors cannot buy US-listed ETFs. The mirror follows every decision above in UCITS funds that can be bought in Europe, one European trading day later. Where no UCITS twin exists it holds a related fund (approximation) or the money-market fund.",
                     "nl": "Europese beleggers kunnen Amerikaanse ETF's niet kopen. De spiegel volgt elk besluit hierboven in UCITS-fondsen die in Europa te koop zijn, één Europese handelsdag later. Waar geen UCITS-tweeling bestaat, houdt hij een verwant fonds (benadering) of het geldmarktfonds."},
    "follows": {"en": "Follows", "nl": "Volgt"}, "kind": {"en": "Match", "nl": "Soort"},
    "twin": {"en": "Twin", "nl": "Tweeling"}, "proxy": {"en": "Approximation", "nl": "Benadering"}, "sold": {"en": "To sell", "nl": "Te verkopen"},
    "us_weight": {"en": "US weight", "nl": "Gewicht VS"},
    "mirror_traded": {"en": "Mirror trades this week", "nl": "Transacties van de spiegel deze week"},
    "mirror_planned": {"en": "Planned for the next European close", "nl": "Gepland voor de volgende Europese slotkoers"},
    "mirror_no_trades": {"en": "No mirror trades this week: every line is within 2 points of its US weight.", "nl": "Geen transacties in de spiegel deze week: elke positie zit binnen 2 punten van het gewicht in de VS."},
    "mirror_vs": {"en": "Since {d}: mirror {m}%, US portfolio {u}%, gap {g} points. Mirror benchmark ({b}): {mb}%.",
                  "nl": "Sinds {d}: spiegel {m}%, Amerikaanse portefeuille {u}%, verschil {g} punten. Benchmark van de spiegel ({b}): {mb}%."},
    "inception": {"en": "since {d}", "nl": "sinds {d}"},
    "att_sub": {"en": "Contribution since {d}, percentage points", "nl": "Bijdrage sinds {d}, procentpunt"},
    "att_total": {"en": "Total gap", "nl": "Totaal verschil"},
    "cash_item": {"en": "Cash", "nl": "Kas"},
    "action": {"en": "Action", "nl": "Actie"}, "fund": {"en": "Fund", "nl": "Fonds"},
    "amount": {"en": "Amount", "nl": "Bedrag"}, "why": {"en": "Why", "nl": "Waarom"},
    "buy": {"en": "Buy", "nl": "Koop"}, "sell": {"en": "Sell", "nl": "Verkoop"}, "planned": {"en": "Planned", "nl": "Gepland"},
    "no_trades": {"en": "No trades this week: every holding is within its rules.", "nl": "Geen transacties deze week: alle posities vallen binnen de regels."},
    "performance": {"en": "Performance", "nl": "Rendement"},
    "chart_title": {"en": "Value of €100 invested on", "nl": "Waarde van €100 belegd op"},
    "portfolio": {"en": "Portfolio", "nl": "Portefeuille"},
    "positions": {"en": "Positions after this week's trades", "nl": "Posities na de transacties van deze week"},
    "role": {"en": "Role", "nl": "Rol"}, "weight": {"en": "Weight", "nl": "Gewicht"},
    "w1": {"en": "1 wk", "nl": "1 wk"}, "m3": {"en": "3 mo", "nl": "3 mnd"}, "m6": {"en": "6 mo", "nl": "6 mnd"}, "m12": {"en": "12 mo", "nl": "12 mnd"},
    "trend": {"en": "Trend", "nl": "Trend"}, "rank": {"en": "Rank", "nl": "Rang"}, "score": {"en": "Score", "nl": "Score"},
    "core": {"en": "Core", "nl": "Kern"}, "reference": {"en": "To sell", "nl": "Te verkopen"}, "satellite": {"en": "Satellite", "nl": "Satelliet"}, "defensive": {"en": "Defensive", "nl": "Defensief"},
    "up": {"en": "Up", "nl": "Op"}, "down": {"en": "Down", "nl": "Neer"},
    "scan": {"en": "The scan: all funds ranked", "nl": "De scan: alle fondsen gerangschikt"},
    "scan_intro": {"en": "{n} funds ranked on 3-, 6- and 12-month returns (score 0–100). Trend is up when the price is above its 200-day average.",
                   "nl": "{n} fondsen gerangschikt op rendement over 3, 6 en 12 maanden (score 0–100). De trend is op wanneer de koers boven het 200-daags gemiddelde staat."},
    "state": {"en": "Market state", "nl": "Markttoestand"},
    "risk_on": {"en": "Risk-on", "nl": "Risicobereid"}, "risk_off": {"en": "Risk-off (defensive)", "nl": "Defensief"},
    "breadth": {"en": "{b}% of ranked funds in an uptrend (defensive below {t}% with world equity in a downtrend)",
                "nl": "{b}% van de gerangschikte fondsen in een opwaartse trend (defensief onder {t}% bij een dalende trend in wereldaandelen)"},
    "top10": {"en": "Top 10", "nl": "Top 10"}, "bottom5": {"en": "Bottom 5", "nl": "Onderste 5"},
    "held": {"en": "held", "nl": "in bezit"}, "new": {"en": "new", "nl": "nieuw"},
    "markets": {"en": "Markets and macro", "nl": "Markten en macro"},
    "asset": {"en": "Asset class", "nl": "Categorie"},
    "indicator": {"en": "Indicator", "nl": "Indicator"}, "latest": {"en": "Latest", "nl": "Laatste"},
    "m1ago": {"en": "1 mo ago", "nl": "1 mnd geleden"}, "y1ago": {"en": "1 yr ago", "nl": "1 jaar geleden"}, "asof": {"en": "Date", "nl": "Datum"},
    "unavailable": {"en": "unavailable", "nl": "niet beschikbaar"}, "not_current": {"en": "not current", "nl": "niet actueel"},
    "watch": {"en": "What the rules are watching", "nl": "Waar de regels op letten"},
    "method": {"en": "How this portfolio works", "nl": "Zo werkt deze portefeuille"},
    "data": {"en": "Data and method", "nl": "Data en methode"},
    "disclaimer": {"en": "Important information", "nl": "Belangrijke informatie"},
}
WHY_DROP = re.compile(r"[a-z]+_[a-z_]+")  # internal identifiers must never reach the reader


def t(key: str, lang: str, **kw) -> str:
    entry = T.get(key)
    return entry[lang].format(**kw) if entry else str(key).replace("_", " ")


def e(x) -> str:
    return html.escape(str(x))


def num(v, lang: str, nd: int = 2, sign: bool = False) -> str:
    if v is None:
        return "–"
    s = f"{v:+,.{nd}f}" if sign else f"{v:,.{nd}f}"
    if lang == "nl":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def eur(v, lang: str, nd: int = 0) -> str:
    return ("€ " if lang == "nl" else "€") + num(v, lang, nd)


def long_date(d: str, lang: str) -> str:
    x = date.fromisoformat(d)
    return f"{x.day} {MONTHS[lang][x.month - 1]} {x.year}"


def short_name(name: str) -> str:
    n = re.sub(r"\s+UCITS ETF.*$", "", name)
    return n.replace("iShares ", "iShares ").strip()


def tone(v) -> str:
    return "" if v is None else ("pos" if v > 0 else "neg" if v < 0 else "")


# ── Chart ───────────────────────────────────────────────────────────────────
def chart_svg(points: list[dict], lang: str) -> str:
    W, H, L, R, TP, B = 640, 230, 44, 92, 14, 30
    has_m = all("mirror_index" in p for p in points)
    ys = [p["portfolio_index"] for p in points] + [p["benchmark_index"] for p in points] + ([p["mirror_index"] for p in points] if has_m else [])
    lo, hi = min(ys), max(ys)
    pad = max(0.5, (hi - lo) * 0.15)
    lo, hi = lo - pad, hi + pad
    n = len(points)
    X = lambda i: L + (W - L - R) * (i / (n - 1 if n > 1 else 1))
    Y = lambda v: TP + (H - TP - B) * (1 - (v - lo) / (hi - lo))
    step = 1 if hi - lo <= 6 else 2 if hi - lo <= 12 else 5
    grid = []
    g = int(lo // step + 1) * step
    while g < hi:
        grid.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(g):.1f}" y2="{Y(g):.1f}" stroke="{'#b9b6ae' if g == 100 else '#e6e4df'}" stroke-width="1"/>'
                    f'<text x="{L - 6}" y="{Y(g) + 3.5:.1f}" font-family="Inter" font-size="9" fill="#6b6a66" text-anchor="end">{num(g, lang, 0)}</text>')
        g += step
    xl, seen = [], set()
    for i, p in enumerate(points):
        m = p["date"][:7]
        if m not in seen:
            seen.add(m)
            d = date.fromisoformat(p["date"])
            xl.append(f'<text x="{X(i):.1f}" y="{H - 10}" font-family="Inter" font-size="9" fill="#6b6a66" text-anchor="middle">{MONTHS[lang][d.month - 1][:3]}</text>')
    def path(key):
        return "M" + " L".join(f"{X(i):.1f},{Y(p[key]):.1f}" for i, p in enumerate(points))
    ends = [("portfolio_index", BLUE, t("portfolio", lang)), ("benchmark_index", ORANGE, "Benchmark")] + ([("mirror_index", AQUA, t("mirror", lang))] if has_m else [])
    labs = sorted(([Y(points[-1][k]), k, col, name] for k, col, name in ends), key=lambda x: x[0])
    for i in range(1, len(labs)):  # keep end labels at least 13 px apart
        labs[i][0] = max(labs[i][0], labs[i - 1][0] + 13)
    over = labs[-1][0] - (H - B)
    if over > 0:
        for lab in labs:
            lab[0] -= over
    endmarks = "".join(f'<circle cx="{X(n - 1):.1f}" cy="{Y(points[-1][k]):.1f}" r="3" fill="{col}" stroke="#fff" stroke-width="2"/>'
                       f'<text x="{X(n - 1) + 8:.1f}" y="{yl + 3:.1f}" font-family="Inter" font-weight="600" font-size="9.5" fill="#1d1d1b">{name} {num(points[-1][k], lang)}</text>'
                       for yl, k, col, name in labs)
    mpath = f'<path d="{path("mirror_index")}" fill="none" stroke="{AQUA}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' if has_m else ""
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img">
{''.join(grid)}{''.join(xl)}
<path d="{path("benchmark_index")}" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
{mpath}
<path d="{path("portfolio_index")}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
{endmarks}
</svg>'''


def attribution_svg(att: dict, lang: str) -> str:
    items = sorted(att["items"], key=lambda x: x["pts"])
    W, row, L, R = 250, 19, 44, 40
    H = row * len(items) + 8
    m = max(0.5, max(abs(x["pts"]) for x in items))
    zero = L + (W - L - R) * 0.5 if any(x["pts"] > 0 for x in items) and any(x["pts"] < 0 for x in items) else (W - R if all(x["pts"] <= 0 for x in items) else L)
    scale = (W - L - R) * (0.5 if zero not in (L, W - R) else 1.0) / m
    out = []
    for k, x in enumerate(items):
        y = 4 + k * row
        w = abs(x["pts"]) * scale
        x0 = zero - w if x["pts"] < 0 else zero
        col = ORANGE if x["pts"] < 0 else BLUE
        label = t("cash_item", lang) if x["id"] == "CASH" else x["id"]
        out.append(f'<text x="{L - 6}" y="{y + 12:.1f}" font-family="Inter" font-weight="600" font-size="9" fill="#1d1d1b" text-anchor="end">{e(label)}</text>')
        if w >= 0.5:
            out.append(f'<rect x="{x0:.1f}" y="{y + 3:.1f}" width="{w:.1f}" height="11" rx="2" fill="{col}"/>')
        vx = (x0 - 4) if x["pts"] < 0 else (zero + w + 4)
        anchor = "end" if x["pts"] < 0 else "start"
        if x["pts"] < 0 and vx < L + 22:  # no room left of the bar: write inside-right of zero
            vx, anchor = zero + 4, "start"
        out.append(f'<text x="{vx:.1f}" y="{y + 12:.1f}" font-family="Inter" font-size="8.5" fill="#3a3936" text-anchor="{anchor}">{num(x["pts"], lang, 2, True)}</text>')
    out.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="0" y2="{H}" stroke="#8a8882" stroke-width="1"/>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img">{"".join(out)}</svg>'


# ── Page builders ───────────────────────────────────────────────────────────
def kpi(label, main, sub="", cls=""):
    return f'<div class="kpi"><div class="k-label">{label}</div><div class="k-main {cls}">{main}</div><div class="k-sub">{sub}</div></div>'


def decisions_table(f, c, lang):
    texts = {x.get("id"): x.get("text", "") for x in c.get("trades", []) if isinstance(x, dict)}
    rows = []
    for tr in f["trades"]:
        rows.append(f'<tr><td><span class="tag {tr["side"]}">{t(tr["side"], lang)}</span></td><td><b>{e(tr["id"])}</b><div class="sub">{e(short_name(tr["name"]))}</div></td>'
                    f'<td class="num">{eur(tr["amount_eur"], lang)}</td><td>{e(texts.get(tr["id"], ""))}</td></tr>')
    if f["deferred"]:  # one compact row: planned changes follow in later weeks
        ids = ", ".join(f'{x["id"]} ({("koop" if x["kind"] == "entry" else "verkoop") if lang == "nl" else ("buy" if x["kind"] == "entry" else "sell")})' for x in f["deferred"])
        note = (f"Volgen in de komende weken: maximaal {f['rules']['max_changes_per_week']} fondswissels per week." if lang == "nl"
                else f"Follow in the coming weeks: at most {f['rules']['max_changes_per_week']} fund changes per week.")
        rows.append(f'<tr class="muted"><td><span class="tag planned">{t("planned", lang)}</span></td><td colspan="2"><b>{e(ids)}</b></td><td>{e(note)}</td></tr>')
    return (f'<table class="dec"><thead><tr><th>{t("action", lang)}</th><th>{t("fund", lang)}</th><th class="num">{t("amount", lang)}</th><th>{t("why", lang)}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
            if rows else f'<p class="note">{t("no_trades", lang)}</p>')


def page_summary(f, c, lang):
    p = f["portfolio"]
    tiles = "".join([
        kpi(t("value", lang), eur(p["value_eur"], lang),
            (f'{t("inception", lang, d=long_date(f["inception"]["date"], lang))}: {num(f["inception"]["return_pct"], lang, sign=True)}%' if f.get("inception")
             else f'{p["n_positions"]} ' + ("funds" if lang == "en" else "fondsen"))),
        kpi(t("week", lang), num(p["week_return_pct"], lang, sign=True) + "%", f'{t("vs", lang)} {num(p["benchmark_week_return_pct"], lang, sign=True)}%', tone(p["week_return_pct"])),
        kpi(f'{t("since", lang)} {long_date(f["track_record_start"], lang)}', num(p["since_start_return_pct"], lang, sign=True) + "%",
            f'{t("vs", lang)} {num(p["benchmark_since_start_return_pct"], lang, sign=True)}%', tone(p["since_start_return_pct"])),
        kpi(t("mirror", lang), num(f["mirror"]["since_start_return_pct"], lang, sign=True) + "%",
            f'{"gap with US" if lang == "en" else "verschil met VS"} {num(f["mirror"]["gap_vs_us_pts"], lang, sign=True)} {"pts" if lang == "en" else "pt"}', tone(f["mirror"]["since_start_return_pct"])),
    ])
    att = (f.get("attribution") or {}).get("since_start")
    side = ""
    if att and att["items"]:
        side = (f'<div class="att"><div class="att-title">{t("att_title", lang)}</div><div class="att-sub">{t("att_sub", lang, d=long_date(att["from"], lang))}</div>'
                f'{attribution_svg(att, lang)}<div class="att-total">{t("att_total", lang)}: <b>{num(att["gap_pts"], lang, 2, True)}</b></div></div>')
    return f'''<section class="page first">
<header class="mast"><div><div class="brand">{t("title", lang)}</div><div class="subbrand">{t("subtitle", lang)}</div></div><div class="date">{long_date(f["report_date"], lang)}</div></header>
<h1>{e(c["headline"])}</h1>
<div class="kpis">{tiles}</div>
<div class="chart-head"><span>{t("chart_title", lang)} {long_date(f["track_record_start"], lang)}</span>
<span class="legend"><i style="background:{BLUE}"></i>{t("portfolio", lang)} <i style="background:{ORANGE}"></i>{t("bench_label", lang)} <i style="background:{AQUA}"></i>{t("mirror", lang)}</span></div>
{chart_svg(f["chart"], lang)}
<div class="story"><div class="narr">
<h3>{t("h_happened", lang)}</h3><p>{e(c["what_happened"])}</p>
<h3>{t("h_why", lang)}</h3><p>{e(c["why"])}</p>
<h3>{t("h_do", lang)}</h3><p>{e(c["what_we_do"])}</p>
</div>{side}</div>
</section>'''


def page_performance(f, c, lang):
    rows = []
    for p in f["positions"]:
        rows.append(f'<tr><td><b>{e(p["id"])}</b><div class="sub">{e(short_name(p["name"]))}</div></td><td>{t(p["role"], lang) if p["role"] else ""}</td>'
                    f'<td class="num">{eur(p["value_eur"], lang)}</td><td class="num">{num(p["weight_pct"], lang, 1)}%</td>'
                    f'<td class="num {tone(p["week_return_pct"])}">{num(p["week_return_pct"], lang, sign=True)}%</td>'
                    f'<td class="num {tone(p["return_3m_pct"])}">{num(p["return_3m_pct"], lang, sign=True)}%</td>'
                    f'<td>{t(p["trend"], lang) if p["trend"] else "–"}</td><td class="num">{p["rank"] or "–"}</td></tr>')
    cash = f["portfolio"]
    rows.append(f'<tr class="muted"><td><b>{t("cash", lang)}</b></td><td></td><td class="num">{eur(cash["cash_eur"], lang)}</td><td class="num">{num(cash["cash_pct"], lang, 1)}%</td><td></td><td></td><td></td><td></td></tr>')
    return f'''<section class="page">
<h2 class="top">{t("decisions", lang)}</h2>
{decisions_table(f, c, lang)}
<h2>{t("positions", lang)}</h2>
<table><thead><tr><th>{t("fund", lang)}</th><th>{t("role", lang)}</th><th class="num">{"Value" if lang == "en" else "Waarde"}</th><th class="num">{t("weight", lang)}</th>
<th class="num">{t("w1", lang)}</th><th class="num">{t("m3", lang)}</th><th>{t("trend", lang)}</th><th class="num">{t("rank", lang)}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
</section>'''


def page_mirror(f, c, lang):
    m = f["mirror"]
    rows = []
    for p in m["positions"]:
        kind = t(p["kind"], lang) if p["kind"] != "cash" else ("Money market" if lang == "en" else "Geldmarkt")
        rows.append(f'<tr><td><b>{e(p["ticker"])}</b><div class="sub">{e(short_name(p["name"]))}</div></td><td>{e(", ".join(p["us_ids"]) or "–")}</td>'
                    f'<td><span class="tag {"planned" if p["kind"] == "proxy" else "buy" if p["kind"] == "twin" else "sell"}">{kind}</span></td>'
                    f'<td class="num">{eur(p["value_eur"], lang)}</td><td class="num">{num(p["weight_pct"], lang, 1)}%</td><td class="num">{num(p["us_weight_pct"], lang, 1)}%</td></tr>')
    rows.append(f'<tr class="muted"><td><b>{t("cash", lang)}</b></td><td></td><td></td><td class="num">{eur(m["cash_eur"], lang)}</td><td class="num">{num(m["cash_pct"], lang, 1)}%</td><td></td></tr>')
    trades = "".join(f'<tr><td><span class="tag {x["side"]}">{t(x["side"], lang)}</span></td><td><b>{e(x["ticker"])}</b><div class="sub">{e(short_name(x["name"]))}</div></td>'
                     f'<td>{long_date(x["date"], lang)}</td><td class="num">{eur(x["amount_eur"], lang)}</td></tr>' for x in m["executed"])
    traded = (f'<table class="dec"><thead><tr><th>{t("action", lang)}</th><th>{t("fund", lang)}</th><th>{"Date" if lang == "en" else "Datum"}</th><th class="num">{t("amount", lang)}</th></tr></thead><tbody>{trades}</tbody></table>'
              if trades else f'<p class="note">{t("mirror_no_trades", lang)}</p>')
    planned = ""
    if m["planned"]:
        planned = (f'<h3>{t("mirror_planned", lang)}</h3><p class="small">' +
                   e(", ".join(f'{x["ticker"]} {num(x["target_pct"], lang, 1)}%' for x in m["planned"])) + "</p>")
    vs = t("mirror_vs", lang, d=long_date(m["start"], lang), m=num(m["since_start_return_pct"], lang, sign=True), u=num(m["us_since_start_return_pct"], lang, sign=True),
           g=num(m["gap_vs_us_pts"], lang, sign=True), b=m["benchmark_label"], mb=num(m["benchmark_since_start_return_pct"], lang, sign=True))
    return f'''<section class="page">
<h2 class="top">{t("mirror_title", lang)}</h2>
<p>{e(t("mirror_intro", lang))}</p>
<p><b>{e(vs)}</b></p>
<table><thead><tr><th>{t("fund", lang)} (UCITS)</th><th>{t("follows", lang)}</th><th>{t("kind", lang)}</th><th class="num">{"Value" if lang == "en" else "Waarde"}</th>
<th class="num">{t("weight", lang)}</th><th class="num">{t("us_weight", lang)}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<h2>{t("mirror_traded", lang)}</h2>
{traded}
{planned}
</section>'''


def page_scan(f, c, lang, method=""):
    rg = f["regime"]
    def srow(r):
        flags = []
        if r["held"]:
            flags.append(f'<span class="pill">{t("held", lang)}</span>')
        if r.get("new_in_top10"):
            flags.append(f'<span class="pill new">{t("new", lang)}</span>')
        bar = f'<span class="bar"><span style="width:{max(2, r["score"])}%"></span></span>'
        return (f'<tr><td class="num">{r["rank"]}</td><td><b>{e(r["id"])}</b> {"".join(flags)}<div class="sub">{e(short_name(r["name"]))}</div></td>'
                f'<td class="num">{r["score"]} {bar}</td>'
                f'<td class="num {tone(r["return_3m_pct"])}">{num(r["return_3m_pct"], lang, 1, True)}%</td>'
                f'<td class="num {tone(r["return_6m_pct"])}">{num(r["return_6m_pct"], lang, 1, True)}%</td>'
                f'<td class="num {tone(r["return_12m_pct"])}">{num(r["return_12m_pct"], lang, 1, True)}%</td><td>{t(r["trend"], lang)}</td></tr>')
    head = (f'<thead><tr><th class="num">#</th><th>{t("fund", lang)}</th><th class="num">{t("score", lang)}</th><th class="num">{t("m3", lang)}</th>'
            f'<th class="num">{t("m6", lang)}</th><th class="num">{t("m12", lang)}</th><th>{t("trend", lang)}</th></tr></thead>')
    mk = "".join(f'<tr><td>{e(m["label_" + lang])} <span class="sub-inline">{e(m["id"])}</span></td><td class="num {tone(m["week_pct"])}">{num(m["week_pct"], lang, sign=True)}%</td>'
                 f'<td class="num {tone(m["return_3m_pct"])}">{num(m["return_3m_pct"], lang, 1, True)}%</td><td class="num {tone(m["return_12m_pct"])}">{num(m["return_12m_pct"], lang, 1, True)}%</td></tr>' for m in f["market"])
    mac = []
    for m in f["macro"].values():
        if not m.get("available"):
            mac.append(f'<tr class="muted"><td>{e(m["label_" + lang])}</td><td colspan="4">{t("unavailable", lang)}</td></tr>')
            continue
        u = m["unit"]
        monthly = m.get("source") == "eurostat"
        nd = 4 if not u else (1 if monthly else 2)
        stale = f' <span class="pill">{t("not_current", lang)}</span>' if m.get("stale") else ""
        mac.append(f'<tr><td>{e(m["label_" + lang])}{stale}</td><td class="num"><b>{num(m["value"], lang, nd)}{u}</b></td><td class="num">{num(m["value_1m_ago"], lang, nd)}{u if m["value_1m_ago"] is not None else ""}</td>'
                   f'<td class="num">{num(m["value_1y_ago"], lang, nd)}{u if m["value_1y_ago"] is not None else ""}</td><td class="num sub-inline">{(MONTHS[lang][int(m["date"][5:7]) - 1] + " " + m["date"][:4]) if monthly else long_date(m["date"], lang)}</td></tr>')
    watch = "".join(f"<li>{e(w)}</li>" for w in c.get("watch", []))
    return f'''<section class="page">
<h2 class="top">{t("scan", lang)}</h2>
<div class="state"><span class="tag {"pos" if rg["state"] == "risk_on" else "neg"}-bg">{t("state", lang)}: {t(rg["state"], lang)}</span>
<span>{t("breadth", lang, b=num(rg["breadth_pct"], lang, 1), t=rg["breadth_threshold_pct"])}</span></div>
<p class="note">{t("scan_intro", lang, n=rg["n_ranked"])}</p>
<h3>{t("top10", lang)}</h3><table class="scan">{head}<tbody>{"".join(srow(r) for r in f["scan_top10"])}</tbody></table>
<h3>{t("bottom5", lang)}</h3><table class="scan">{head}<tbody>{"".join(srow(r) for r in f["scan_bottom5"])}</tbody></table>
<h2>{t("watch", lang)}</h2><ul class="watch">{watch}</ul>
</section>
<section class="page">
<h2 class="top">{t("markets", lang)}</h2>
<p>{e(c["markets"])}</p>
<table><thead><tr><th>{t("asset", lang)}</th><th class="num">{t("w1", lang)}</th><th class="num">{t("m3", lang)}</th><th class="num">{t("m12", lang)}</th></tr></thead><tbody>{mk}</tbody></table>
<table class="gap"><thead><tr><th>{t("indicator", lang)}</th><th class="num">{t("latest", lang)}</th><th class="num">{t("m1ago", lang)}</th><th class="num">{t("y1ago", lang)}</th><th class="num">{t("asof", lang)}</th></tr></thead><tbody>{"".join(mac)}</tbody></table>
{method}'''


def page_method(f, lang):
    r = f["rules"]
    if lang == "nl":
        how = [
            f"Kern: SPY (Amerikaanse aandelen) en AGG (Amerikaanse obligaties). Daaromheen {r['satellites']['risk_on']} satellieten van circa {num(r['satellite_weight_pct'], 'nl', 0)}% en een kleine kaspositie (doel {num(r['cash_target_pct'], 'nl', 0)}%).",
            "Elke week worden alle fondsen gerangschikt op rendement in euro over 3, 6 en 12 maanden; de sterkste met een opwaartse trend vullen de satellietplaatsen, één per thema, sector of regio.",
            f"Een satelliet blijft zolang hij in de top 15 staat en de trend op is; een nieuw fonds vervangt hem alleen bij minstens {r['replacement_margin_pts']} punten meer. Verkoop op trend volgt na twee weken onder het 200-daags gemiddelde.",
            f"Defensief bij een dalende trend in Amerikaanse aandelen en zwakke breedte: {r['satellites']['risk_off']} satellieten, de rest in kortlopend Amerikaans staatspapier (BIL).",
            f"Maximaal {r['max_changes_per_week']} fondswissels per week. Doel: meedoen met de markt en grote verliezen beperken; de regels beloven geen beter rendement dan de benchmark.",
            "De Europese spiegel volgt elk besluit in UCITS-fondsen op de eerstvolgende Europese slotkoers; een positie wordt alleen aangepast bij meer dan 2 punten afwijking.",
        ]
        data = ("Benchmark: 70% Amerikaanse aandelen (SPY) en 30% Amerikaanse obligaties (AGG), in euro, wekelijks geherbalanceerd; voor de spiegel 70% SXR8 en 30% EUNA. "
                "Koersen: slotkoersen van de Amerikaanse fondsen in dollar (Yahoo Finance), posities gecontroleerd tegen Alpha Vantage, omgerekend naar euro met de EUR/USD-slotkoers van dezelfde dag; "
                "de spiegel tegen slotkoersen in euro op Europese beurzen. Rendementen zijn koersrendementen zonder dividend. Transacties worden gemodelleerd met hele stukken en "
                f"{num(r['cost_bps'] / 100, 'nl')}% geschatte kosten. Het rendement sinds de start (28 maart 2026) koppelt de waarde van het vorige rapportsysteem tot 7 augustus aan de herberekende waarde daarna. "
                "Het commentaar is opgesteld met behulp van AI op basis van uitsluitend de cijfers in dit rapport; elk getal in de tekst wordt automatisch gecontroleerd.")
        disc = ("Dit rapport beschrijft fictieve modelportefeuilles die volgens vaste regels worden beheerd. Er wordt niet daadwerkelijk belegd. Het is algemene informatie en geen persoonlijk "
                "beleggingsadvies: het houdt geen rekening met uw financiële situatie, doelen of risicobereidheid. Amerikaanse ETF's zijn voor Europese particuliere beleggers doorgaans niet verkrijgbaar; "
                "de Europese spiegel laat zien hoe de portefeuille met UCITS-fondsen te volgen is. Beleggen brengt risico's met zich mee; u kunt (een deel van) uw inleg verliezen. "
                "In het verleden behaalde resultaten bieden geen garantie voor de toekomst. Lees voor u belegt de essentiële-informatiedocumenten (KID) van de fondsen.")
    else:
        how = [
            f"Core: SPY (US equities) and AGG (US bonds). Around it {r['satellites']['risk_on']} satellites of about {num(r['satellite_weight_pct'], 'en', 0)}% and a small cash position (target {num(r['cash_target_pct'], 'en', 0)}%).",
            "Every week all funds are ranked on 3-, 6- and 12-month returns in euro; the strongest in an uptrend fill the satellite slots, one per theme, sector or region.",
            f"A satellite stays while it ranks in the top 15 and its trend is up; a newcomer replaces it only if it scores at least {r['replacement_margin_pts']} points higher. A trend sale follows two weeks below the 200-day average.",
            f"Defensive when US equities are in a downtrend and breadth is weak: {r['satellites']['risk_off']} satellites, the rest in short-dated US Treasury bills (BIL).",
            f"At most {r['max_changes_per_week']} fund changes per week. Aim: keep up with the market and limit large losses; the rules do not promise to beat the benchmark.",
            "The European mirror follows every decision in UCITS funds at the next European close; a line is only resized when it is more than 2 points off.",
        ]
        data = ("Benchmark: 70% US equities (SPY) and 30% US bonds (AGG), in euro, rebalanced weekly; for the mirror 70% SXR8 and 30% EUNA. "
                "Prices: closing prices of the US funds in dollars (Yahoo Finance), holdings checked against Alpha Vantage, converted to euro at the same day's EUR/USD close; "
                "the mirror at euro closing prices on European exchanges. Returns are price returns without dividends. Trades are modelled in whole shares with an estimated "
                f"{num(r['cost_bps'] / 100, 'en')}% cost. The return since inception (28 March 2026) links the previous report system's value up to 7 August to the recalculated value after it. "
                "The commentary is drafted with the help of AI from the figures in this report only; every number in the text is checked automatically.")
        disc = ("This report describes hypothetical model portfolios managed by fixed rules. No money is actually invested. It is general information, not personal investment advice: "
                "it does not take your financial situation, objectives or risk tolerance into account. US-listed ETFs are generally not available to European retail investors; "
                "the European mirror shows how the portfolio can be followed with UCITS funds. Investing involves risk; you can lose some or all of your money. "
                "Past performance is no guarantee of future results. Read the funds' key information documents (KID) before investing.")
    items = "".join(f"<li>{e(x)}</li>" for x in how)
    return f'''<h2>{t("method", lang)}</h2><ol class="how">{items}</ol>
<h2>{t("data", lang)}</h2><p class="small">{e(data)}</p>
<h2>{t("disclaimer", lang)}</h2><p class="small">{e(disc)}</p>
</section>'''


CSS = f"""
@font-face {{ font-family: Inter; src: url('{(FONTS / "Inter-Regular.otf").as_uri()}'); font-weight: 400; }}
@font-face {{ font-family: Inter; src: url('{(FONTS / "Inter-Medium.otf").as_uri()}'); font-weight: 500; }}
@font-face {{ font-family: Inter; src: url('{(FONTS / "Inter-SemiBold.otf").as_uri()}'); font-weight: 600; }}
@font-face {{ font-family: Inter; src: url('{(FONTS / "Inter-Bold.otf").as_uri()}'); font-weight: 700; }}
@font-face {{ font-family: InterDisplay; src: url('{(FONTS / "InterDisplay-SemiBold.otf").as_uri()}'); font-weight: 600; }}
@page {{ size: A4; margin: 16mm 15mm 16mm 15mm;
  @bottom-left {{ content: var(--footer); font: 7.5pt Inter; color: #8a8882; }}
  @bottom-right {{ content: counter(page) " / " counter(pages); font: 7.5pt Inter; color: #8a8882; }} }}
html {{ font-family: Inter, sans-serif; font-size: 9pt; color: #1d1d1b; line-height: 1.45; }}
.page {{ page-break-after: always; }} .page:last-child {{ page-break-after: auto; }}
.mast {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #1d1d1b; padding-bottom: 6pt; margin-bottom: 14pt; }}
.brand {{ font: 600 17pt InterDisplay, Inter; letter-spacing: -0.2pt; white-space: nowrap; }}
.subbrand {{ font-size: 8.5pt; color: #6b6a66; }}
.date {{ font-weight: 500; font-size: 9.5pt; }}
h1 {{ font: 600 19pt/1.2 InterDisplay, Inter; margin: 0 0 8pt; letter-spacing: -0.3pt; }}
h2 {{ font: 600 11.5pt InterDisplay, Inter; margin: 16pt 0 6pt; padding-top: 6pt; border-top: 1px solid #e6e4df; }}
h3 {{ font-size: 9pt; font-weight: 600; margin: 10pt 0 4pt; color: #52514e; text-transform: uppercase; letter-spacing: 0.4pt; }}
.lead {{ font-size: 10.5pt; color: #2e2d2a; margin: 0 0 12pt; }}
.kpis {{ display: flex; gap: 8pt; margin-bottom: 4pt; }}
.kpi {{ flex: 1; background: #f6f5f2; border-radius: 4pt; padding: 8pt 9pt; }}
.k-label {{ font-size: 7.5pt; color: #6b6a66; text-transform: uppercase; letter-spacing: 0.3pt; }}
.k-main {{ font: 600 15pt InterDisplay, Inter; margin: 2pt 0; }}
.k-sub {{ font-size: 8pt; color: #6b6a66; }}
.pos {{ color: #1a7f37; }} .neg {{ color: #b42318; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.3pt; }}
th {{ text-align: left; font-weight: 600; color: #6b6a66; font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.3pt; border-bottom: 1px solid #1d1d1b; padding: 3pt 4pt; }}
td {{ padding: 4pt 4pt; border-bottom: 1px solid #ecebe7; vertical-align: top; }}
.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
.sub {{ font-size: 7.3pt; color: #6b6a66; }} .sub-inline {{ font-size: 7.3pt; color: #8a8882; }}
.muted td {{ color: #6b6a66; }}
.tag {{ display: inline-block; font-size: 7pt; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3pt; padding: 1.5pt 5pt; border-radius: 3pt; }}
.tag.buy {{ background: #e3f1e7; color: #1a7f37; }} .tag.sell {{ background: #fbe7e5; color: #b42318; }} .tag.planned {{ background: #efeee9; color: #52514e; }}
.tag.pos-bg {{ background: #e3f1e7; color: #1a7f37; }} .tag.neg-bg {{ background: #fbe7e5; color: #b42318; }}
.dec td:last-child {{ width: 52%; }}
.pill {{ font-size: 6.5pt; font-weight: 600; color: #52514e; background: #efeee9; border-radius: 6pt; padding: 0.5pt 4pt; margin-left: 2pt; }}
.pill.new {{ color: #1c5cab; background: #e6eefb; }}
.bar {{ display: inline-block; width: 34pt; height: 4pt; background: #efeee9; border-radius: 2pt; margin-left: 4pt; vertical-align: middle; }}
.bar span {{ display: block; height: 4pt; background: {BLUE}; border-radius: 2pt; }}
.state {{ display: flex; gap: 8pt; align-items: center; font-size: 8.5pt; margin-bottom: 4pt; }}
.note {{ color: #6b6a66; font-size: 8pt; margin: 2pt 0 6pt; }}
.chart-head {{ display: flex; justify-content: space-between; font-size: 8pt; color: #52514e; margin-bottom: 2pt; }}
.legend i {{ display: inline-block; width: 10pt; height: 2pt; vertical-align: middle; margin: 0 3pt 0 8pt; border-radius: 1pt; }}
table.gap {{ margin-top: 10pt; }} h2.top {{ margin-top: 0; }}
b {{ font-feature-settings: "zero" 1; }}
ul.watch, ol.how {{ margin: 0; padding-left: 14pt; }} ul.watch li {{ margin-bottom: 4pt; }}
ol.how li {{ margin-bottom: 2.5pt; font-size: 8.5pt; }}
.small {{ font-size: 7.8pt; color: #3a3936; margin: 0 0 4pt; }}
.kpis {{ margin-bottom: 12pt; }}
.story {{ display: flex; gap: 16pt; margin-top: 8pt; border-top: 1px solid #e6e4df; padding-top: 4pt; }}
.narr {{ flex: 1.45; }} .narr p {{ margin: 0 0 4pt; font-size: 9.3pt; color: #2e2d2a; }}
.att {{ flex: 1; padding-top: 10pt; }}
.att-title {{ font-weight: 600; font-size: 9pt; }} .att-sub {{ font-size: 7.5pt; color: #6b6a66; margin-bottom: 4pt; }}
.att-total {{ font-size: 8pt; color: #52514e; border-top: 1px solid #e6e4df; margin-top: 3pt; padding-top: 3pt; }}
"""


def render_html(f: dict, c: dict, lang: str) -> str:
    css = CSS.replace("var(--footer)", f'"{T["footer"][lang]}"')
    body = page_summary(f, c, lang) + page_performance(f, c, lang) + page_mirror(f, c, lang) + page_scan(f, c, lang, method=page_method(f, lang))
    return f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{t("title", lang)} {f["report_date"]}</title><style>{css}</style></head><body>{body}</body></html>'


def layout_problems(html_text: str, pdf_pages: int) -> list[str]:
    probs = []
    text = re.sub(r"<style>.*?</style>", "", html_text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    if not 3 <= pdf_pages <= 5:
        probs.append(f"page count {pdf_pages} outside 3–5")
    for bad in ("/tmp", "/home/", r"\bNone\b", r"\bnan\b", r"\bnull\b"):
        if re.search(bad, text):
            probs.append(f"forbidden text: {bad}")
    ids = WHY_DROP.findall(text)
    if ids:
        probs.append(f"internal identifiers in text: {sorted(set(ids))[:5]}")
    return probs


def render(f: dict, c: dict, out_dir: Path) -> dict:
    from weasyprint import HTML
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for lang in ("nl", "en"):
        h = render_html(f, c[lang], lang)
        stem = f"weekly_etf_review_{'nl_' if lang == 'nl' else ''}{f['report_date'].replace('-', '')}"
        (out_dir / f"{stem}.html").write_text(h, encoding="utf-8")
        doc = HTML(string=h, base_url=str(ROOT)).render()
        doc.write_pdf(out_dir / f"{stem}.pdf")
        result[lang] = {"pdf": str(out_dir / f"{stem}.pdf"), "pages": len(doc.pages), "problems": layout_problems(h, len(doc.pages))}
    return result
