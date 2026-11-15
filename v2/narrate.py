"""AI commentary for the report — narrates facts, never computes or decides.

The model receives the facts JSON and returns commentary sections. Every number
in its text must already exist in the facts (same rounding); otherwise the text
is rejected, retried once, and replaced by deterministic fallback text. The
report therefore never depends on the AI being available or correct.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

LANGS = ("en", "nl")
SECTIONS = ("headline", "what_happened", "why", "what_we_do", "trades", "markets", "watch")
BANNED = {
    "en": ["you should", "we recommend", "guaranteed", "will rise", "will fall", "certain to", "buy now", "sell now"],
    "nl": ["u moet", "je moet", "wij raden", "we raden", "gegarandeerd", "zal stijgen", "zal dalen", "nu kopen", "nu verkopen"],
}

SYSTEM = """You write the commentary for a premium weekly model-portfolio report on European UCITS ETFs.

Hard rules:
1. Use ONLY the facts in the JSON you receive. Do not add any number, date, price, rate, event or name that is not in it.
2. Copy every number exactly as it appears in the facts (same rounding). You may drop a minus sign when the sentence already says "fell"/"daalde".
3. Explain trades mechanically from their "why" and "detail" fields: what rule triggered, with its numbers.
4. No forecasts, no personal advice, no "you should". This is a model portfolio run by fixed rules.
5. Tone: calm, precise, plain language for private investors. No jargon, no hype, no exclamation marks.
   Positioning: this is a disciplined, explained portfolio that aims to keep up with its benchmark while limiting large losses. Never claim or imply that it will beat the market.
6. Name funds by a short form of their name (e.g. "Vanguard FTSE All-World"), with the ticker in brackets the first time.
7. Macro items with "stale": true or "available": false must be described as not current / unavailable, or left out.

Return a JSON object with exactly these keys, written in the requested language. The first page tells one story in three short parts — keep each part focused on its own question:
- "headline": one sentence, at most 14 words: the single most important thing about the portfolio this week or since the start.
- "what_happened": 2-3 sentences. How did the portfolio do this week and since the start, compared with the benchmark? Lead with the result.
- "why": 2-3 sentences. Explain the gap with the benchmark using "attribution.since_start" (and "attribution.week" if relevant): name the one or two items with the largest contribution in points ("pts"), with their own return ("own_return_pct") and weight at the start ("start_weight_pct"). Cash counts as an item: idle cash costs return when the benchmark rises. Contributions are in percentage points of the gap.
- "what_we_do": 2-3 sentences. What the rules decided this week and why, in plain words (summarise the trades and deferred changes; details follow in a table).
- "trades": a list with one object {"id": <ticker>, "text": <one sentence>} per trade, then one per deferred change (say it is planned for a later week and why).
- "markets": 3-4 sentences on the market panel and the macro indicators.
- "watch": a list of 2-3 short sentences on what the rules are watching next (e.g. held funds whose rank or trend is close to a threshold, deferred changes).
"""


# ── Number check ─────────────────────────────────────────────────────────────
NUM_RE = re.compile(r"(?<![\w])-?\d[\d.,]*")


def _parse(token: str, lang: str) -> float | None:
    t = token.strip(".,")
    if not t or not re.search(r"\d", t):
        return None
    if lang == "nl":
        t = t.replace(".", "").replace(",", ".") if "," in t else (t.replace(".", "") if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t) else t)
    else:
        t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def allowed_numbers(facts: Any) -> set[float]:
    out: set[float] = set()

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            out.add(round(abs(float(x)), 2))  # exact displayed value only
        elif isinstance(x, str):
            for tok in NUM_RE.findall(x):
                v = _parse(tok, "en")
                if v is not None:
                    out.add(round(abs(v), 2))
            for part in re.findall(r"\d+", x):  # dates and codes: 2026, 11, 14
                out.add(float(int(part)))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(facts)
    return out


def unknown_numbers(text: str, lang: str, allowed: set[float]) -> list[str]:
    bad = []
    for tok in NUM_RE.findall(text):
        v = _parse(tok, lang)
        if v is None:
            continue
        a = abs(v)
        if round(a, 2) != a or a not in allowed:
            bad.append(tok)
    return bad


def check(sections: dict, lang: str, facts: dict) -> list[str]:
    problems = []
    for k in SECTIONS:
        if k not in sections:
            problems.append(f"missing section {k}")
    allowed = allowed_numbers(facts)
    texts = []
    for k in ("headline", "what_happened", "why", "what_we_do", "markets"):
        texts.append(str(sections.get(k, "")))
    texts += [str(t.get("text", "")) for t in sections.get("trades", []) if isinstance(t, dict)]
    texts += [str(t) for t in sections.get("watch", [])]
    blob = "\n".join(texts)
    for tok in unknown_numbers(blob, lang, allowed):
        problems.append(f"number not in facts: {tok}")
    low = blob.lower()
    for b in BANNED[lang]:
        if b in low:
            problems.append(f"banned phrase: {b}")
    return problems


# ── Model call ───────────────────────────────────────────────────────────────
def _call_openai(facts: dict, lang: str, feedback: str | None) -> dict:
    key = os.environ["OPENAI_API_KEY"]
    model = os.environ.get("V2_OPENAI_MODEL", "gpt-4o")
    lang_name = {"en": "English", "nl": "Dutch (Netherlands; use comma as decimal separator, e.g. 0,49%)"}[lang]
    user = f"Language: {lang_name}.\n\nFacts JSON:\n{json.dumps(facts, ensure_ascii=False)}"
    if feedback:
        user += f"\n\nYour previous answer was rejected: {feedback}. Fix it; use only numbers that appear in the facts."
    r = requests.post("https://api.openai.com/v1/chat/completions", timeout=120,
                      headers={"Authorization": f"Bearer {key}"},
                      json={"model": model, "response_format": {"type": "json_object"},
                            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]})
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def _facts_for_model(facts: dict) -> dict:
    slim = {k: v for k, v in facts.items() if k not in ("chart",)}
    return slim


# ── Deterministic fallback ───────────────────────────────────────────────────
def _fmt(v: float, lang: str, nd: int = 2) -> str:
    s = f"{v:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if lang == "nl" else s


def reason_text(t: dict, lang: str) -> str:
    """One sentence per trade, from the structured reason — both languages."""
    p, w, nl = t.get("params") or {}, t.get("why"), lang == "nl"
    f = lambda v, nd=1: _fmt(v, lang, nd)
    if w == "trend_down":
        return (f"Koers {f(p['close'], 2)} staat twee weken op rij onder het 200-daags gemiddelde ({f(p['sma200'], 2)}): de trend is gekeerd, de positie wordt gesloten." if nl
                else f"Price {f(p['close'], 2)} has been below its 200-day average ({f(p['sma200'], 2)}) for two weeks running: the trend has turned, so the position is closed.")
    if w == "rank_dropped":
        return (f"Gezakt naar plaats {p['rank']} van {p['n']}; een positie blijft alleen zolang ze in de top {p['keep_limit']} staat." if nl
                else f"Dropped to rank {p['rank']} of {p['n']}; a holding stays only while it ranks in the top {p['keep_limit']}.")
    if w == "replaced":
        return (f"Vervangen door {p['new_id']}: score {p['new_score']} tegen {p['old_score']}, meer dan de vereiste {p['margin']} punten verschil." if nl
                else f"Replaced by {p['new_id']}: score {p['new_score']} against {p['old_score']}, more than the required {p['margin']}-point margin.")
    if w == "slots_reduced":
        return (f"Defensieve stand: nog {p['slots']} satellieten; dit is de zwakste positie (plaats {p['rank']})." if nl
                else f"Defensive mode allows {p['slots']} satellites; this is the weakest holding (rank {p['rank']}).")
    if w == "not_in_target":
        return (f"Geen onderdeel van de doelportefeuille: de kern bestaat uit {p['core_equity']} en {p['core_bonds']}." if nl
                else f"Not part of the target portfolio: the core is {p['core_equity']} plus {p['core_bonds']}.")
    if w == "selected":
        return (f"Nieuw: plaats {p['rank']} van {p['n']} in de scan, score {p['score']}, opwaartse trend." if nl
                else f"New: rank {p['rank']} of {p['n']} in the scan, score {p['score']}, in an uptrend.")
    if w == "resize":
        return (f"Gewicht {f(p['weight_pct'])}% tegen doel {f(p['target_pct'])}%; bijgesteld omdat het verschil groter is dan {p['band_pts']} procentpunt." if nl
                else f"Weight {f(p['weight_pct'])}% against a target of {f(p['target_pct'])}%; resized because the gap exceeds {p['band_pts']} percentage points.")
    if w == "deploy_cash":
        return (f"Kas {f(p['cash_pct'])}% ligt boven het plafond van {p['ceiling_pct']}%; aangevuld richting doel {f(p['target_pct'])}%." if nl
                else f"Cash {f(p['cash_pct'])}% is above the {p['ceiling_pct']}% ceiling; topped up toward the {f(p['target_pct'])}% target.")
    if w == "inflation_regime":
        return (f"Inflatie {f(p['hicp'])}% ligt boven {f(p['threshold'])}% en stijgt: de obligatiekern gaat van {p['from']} naar kortlopende obligaties ({p['to']}), die minder lijden onder stijgende rente." if nl
                else f"Inflation at {f(p['hicp'])}% is above {f(p['threshold'])}% and rising: the bond core moves from {p['from']} to short-dated bonds ({p['to']}), which suffer less from rising rates.")
    if w == "inflation_regime_end":
        return (f"De inflatieregel is niet langer actief: de obligatiekern gaat terug van {p['from']} naar {p['to']}." if nl
                else f"The inflation rule is no longer active: the bond core moves back from {p['from']} to {p['to']}.")
    if w == "core_or_defensive":
        return (f"Kern- of defensieve positie, doelgewicht {f(p['target_pct'])}%." if nl else f"Core or defensive position, target weight {f(p['target_pct'])}%.")
    return t.get("detail", "")


def short(name: str) -> str:
    from v2.render import short_name
    return short_name(name)


def _long(d: str, lang: str) -> str:
    from v2.render import long_date
    return long_date(d, lang)


def fallback(facts: dict, lang: str) -> dict:
    p, rg = facts["portfolio"], facts["regime"]
    nl = lang == "nl"
    up_dn = lambda v: (("steeg" if v >= 0 else "daalde") if nl else ("rose" if v >= 0 else "fell"))
    headline = ("Portefeuille " + up_dn(p["week_return_pct"]) + f" {_fmt(abs(p['week_return_pct']), lang)}% deze week" if nl
                else f"Portfolio {up_dn(p['week_return_pct'])} {_fmt(abs(p['week_return_pct']), lang)}% this week")
    regime = {"risk_on": ("risicobereid" if nl else "risk-on"), "risk_off": ("defensief" if nl else "risk-off")}[rg["state"]]
    _att = ((facts.get("attribution") or {}).get("since_start") or {}).get("items") or []
    _w = min(_att, key=lambda x: x["pts"]) if _att else None
    if _w and p["difference_vs_benchmark_pts"] < 0 and _w["pts"] < 0 and _w["id"] != "CASH":
        headline = (f"{_w['id']} is de belangrijkste reden voor de achterstand op de benchmark" if nl
                    else f"{_w['id']} is the main reason the portfolio trails its benchmark")
    happened = (f"De modelportefeuille {up_dn(p['week_return_pct'])} deze week {_fmt(abs(p['week_return_pct']), lang)}%, tegen {_fmt(p['benchmark_week_return_pct'], lang)}% voor de benchmark (70% VWCE / 30% EUNA). "
                f"Sinds {_long(facts['track_record_start'], lang)} is het rendement {_fmt(p['since_start_return_pct'], lang)}% tegen {_fmt(p['benchmark_since_start_return_pct'], lang)}%: een achterstand van {_fmt(abs(p['difference_vs_benchmark_pts']), lang)} procentpunt."
                if nl and p['difference_vs_benchmark_pts'] < 0 else
                f"De modelportefeuille {up_dn(p['week_return_pct'])} deze week {_fmt(abs(p['week_return_pct']), lang)}%, tegen {_fmt(p['benchmark_week_return_pct'], lang)}% voor de benchmark (70% VWCE / 30% EUNA). "
                f"Sinds {_long(facts['track_record_start'], lang)} is het rendement {_fmt(p['since_start_return_pct'], lang)}% tegen {_fmt(p['benchmark_since_start_return_pct'], lang)}%."
                if nl else
                f"The model portfolio {up_dn(p['week_return_pct'])} {_fmt(abs(p['week_return_pct']), lang)}% this week, against {_fmt(p['benchmark_week_return_pct'], lang)}% for the benchmark (70% VWCE / 30% EUNA). "
                f"Since {_long(facts['track_record_start'], lang)} it returned {_fmt(p['since_start_return_pct'], lang)}% against {_fmt(p['benchmark_since_start_return_pct'], lang)}%"
                + (f", a shortfall of {_fmt(abs(p['difference_vs_benchmark_pts']), lang)} percentage points." if p['difference_vs_benchmark_pts'] < 0 else "."))
    att = (facts.get("attribution") or {}).get("since_start") or {"items": []}
    worst = min(att["items"], key=lambda x: x["pts"]) if att["items"] else None
    best = max(att["items"], key=lambda x: x["pts"]) if att["items"] else None
    why = ""
    if worst:
        wn = ("kaspositie" if nl else "cash position") if worst["id"] == "CASH" else worst["id"]
        why = (f"Het grootste effect kwam van {wn}: {_fmt(worst['pts'], lang)} procentpunt (gewicht {_fmt(worst['start_weight_pct'], lang, 1)}%, eigen rendement {_fmt(worst['own_return_pct'], lang)}%). " if nl
               else f"The largest effect came from {wn}: {_fmt(worst['pts'], lang)} percentage points (weight {_fmt(worst['start_weight_pct'], lang, 1)}%, own return {_fmt(worst['own_return_pct'], lang)}%). ")
    if best and best["pts"] > 0:
        why += (f"De sterkste bijdrage kwam van {best['id']}: +{_fmt(best['pts'], lang)} procentpunt." if nl
                else f"The strongest contribution came from {best['id']}: +{_fmt(best['pts'], lang)} percentage points.")
    n_tr, n_def = len(facts["trades"]), len(facts["deferred"])
    what_we_do = (f"De regels leiden deze week tot {n_tr} transacties; {n_def} nieuwe posities volgen in de komende weken vanwege het maximum van {facts['rules']['max_changes_per_week']} fondswissels per week." if nl
                  else f"The rules lead to {n_tr} trades this week; {n_def} new positions follow in the coming weeks because of the limit of {facts['rules']['max_changes_per_week']} fund changes per week.")
    trades = [{"id": t["id"], "text": reason_text(t, lang)} for t in facts["trades"]]
    trades += [{"id": x["id"], "text": reason_text(x, lang) + (f" Gepland voor een volgende week: maximaal {facts['rules']['max_changes_per_week']} fondswissels per week." if nl
                                        else f" Planned for a later week: at most {facts['rules']['max_changes_per_week']} fund changes per week.")} for x in facts["deferred"]]
    mk = facts["market"]
    best = max(mk, key=lambda m: m["week_pct"] or -99)
    worst = min(mk, key=lambda m: m["week_pct"] or 99)
    markets = (f"Sterkste categorie deze week: {best['label_nl']} ({_fmt(best['week_pct'], lang)}%); zwakste: {worst['label_nl']} ({_fmt(worst['week_pct'], lang)}%)." if nl
               else f"Strongest asset class this week: {best['label_en']} ({_fmt(best['week_pct'], lang)}%); weakest: {worst['label_en']} ({_fmt(worst['week_pct'], lang)}%).")
    watch = [(f"Gepland: {('koop' if x['kind'] == 'entry' else 'verkoop')} {x['id']} ({short(x['name'])})." if nl
              else f"Planned: {('buy' if x['kind'] == 'entry' else 'sell')} {x['id']} ({short(x['name'])}).") for x in facts["deferred"][:3]] or [
        "Geen geplande wijzigingen." if nl else "No planned changes."]
    return {"headline": headline, "what_happened": happened, "why": why, "what_we_do": what_we_do, "trades": trades, "markets": markets, "watch": watch}


def narrate(facts: dict) -> dict:
    """Return {"en": sections, "nl": sections, "source": {...}, "problems": {...}}."""
    out: dict[str, Any] = {"source": {}, "problems": {}}
    model_facts = _facts_for_model(facts)
    for lang in LANGS:
        sections, problems = None, []
        if os.environ.get("OPENAI_API_KEY"):
            feedback = None
            for attempt in (1, 2):
                try:
                    cand = _call_openai(model_facts, lang, feedback)
                    problems = check(cand, lang, facts)
                    if not problems:
                        sections = cand
                        out["source"][lang] = f"ai:{os.environ.get('V2_OPENAI_MODEL', 'gpt-4o')}:attempt{attempt}"
                        break
                    feedback = "; ".join(problems[:10])
                except Exception as exc:
                    problems = [f"api_error: {type(exc).__name__}: {str(exc)[:120]}"]
                    break
        else:
            problems = ["no OPENAI_API_KEY"]
        if sections is None:
            sections = fallback(facts, lang)
            out["source"][lang] = "fallback"
            fb_problems = check(sections, lang, facts)
            if fb_problems:
                raise SystemExit(f"fallback text failed its own number check ({lang}): {fb_problems}")
        out[lang] = sections
        out["problems"][lang] = problems
    return out
