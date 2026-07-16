from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from runtime.deterministic_regime_client_surface import build_deterministic_regime_client_surface

MAX_BULLETS = 3

DEFAULT_DETERMINISTIC_VALIDATION_PATH = Path("output/macro/validation/latest_macro_regime_shadow_validation.json")
DEFAULT_DETERMINISTIC_COMPARISON_PATH = Path("output/macro/validation/latest_macro_regime_shadow_comparison.json")

REGIME_NL = {
    "Risk-on growth": "Risk-on groei",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Policy Transition / Mixed Regime": "Beleidstransitie / gemengd regime",
    "Policy transition / mixed regime": "Beleidstransitie / gemengd regime",
    "Unknown": "Onbekend",
}

GEOPOLITICAL_NL = {
    "Elevated but localized": "Verhoogd maar gelokaliseerd",
    "Mixed / policy-sensitive": "Gemengd / beleidsgevoelig",
}

STANCE_NL = {
    "Restrictive / data-dependent": "Restrictief / datagedreven",
    "Neutral / transition": "Neutraal / overgangsfase",
    "Tightening / inflation-sensitive": "Verkrappend / inflatiegevoelig",
    "Gradual normalization risk": "Geleidelijke normalisatierisico's",
    "Supportive but credibility-sensitive": "Ondersteunend maar geloofwaardigheidsgevoelig",
}

POLICY_AREA_NL = {
    "AI infrastructure and semiconductor supply chains": "AI-infrastructuur en semiconductor-toeleveringsketens",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "ECB rate-policy tightening": "ECB-renteverkrapping",
    "Energy security and nuclear policy": "Energiezekerheid en nucleair beleid",
    "China stimulus and platform regulation": "Chinese stimulering en platformregulering",
}

SAFE_REPLACEMENTS = {
    "deterministic_regime_shadow": "internal regime comparison",
    "client_facing_authority": "authority flag",
    "none_shadow_comparison_only": "comparison-only status",
    "shadow_only": "internal-only",
}

NL_TEXT_REPLACEMENTS = {
    "Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.": "SMH blijft de best onderbouwde kernpositie, maar smal marktleiderschap mag niet worden verward met brede portefeuillediversificatie.",
    "Keep SMH as the earned leader": "SMH blijft de best onderbouwde kernpositie",
    "Keep SMH": "Behoud SMH",
    "SMH remains the earned leader": "SMH blijft de best onderbouwde kernpositie",
    "earned leader": "best onderbouwde kernpositie",
    "Require replacement duels for SPY overlap, PPA implementation quality and PAVE versus GRID before funding challengers.": "Vervangingsanalyses zijn vereist voor SPY-overlap, de implementatiekwaliteit van PPA en PAVE versus GRID voordat alternatieven worden gefinancierd.",
    "Require replacement duels": "Vervangingsanalyses zijn vereist",
    "Require replacement": "Vervangingsanalyse vereist",
    "Force alternative duel; upgrade, reduce, replace, or close": "Vervangingsanalyse vereist; verhoog, verlaag, vervang of sluit de positie",
    "Replacement candidates remain evidence-gated": "Vervangingskandidaten blijven afhankelijk van voldoende bewijs",
    "pricing basis and duel status must be visible before funding": "prijsbasis en status van de vervangingsanalyse moeten zichtbaar zijn vóór allocatie",
    "Keep cash discipline because the regime supports selectivity more than broad risk expansion.": "Behoud kasdiscipline, omdat het regime selectiviteit sterker ondersteunt dan brede risico-uitbreiding.",
    "Keep cash discipline": "Behoud kasdiscipline",
    "Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation.": "De risicobereidheid blijft ondersteunend, maar aanvullende allocaties vragen nog ruimte binnen de positielimiet en koersbevestiging.",
    "Growth and infrastructure lanes can be considered if they do not worsen concentration.": "Groei- en infrastructuurthema’s kunnen worden overwogen zolang ze de concentratie niet vergroten.",
    "Defensive hedges should be reviewed for opportunity cost.": "Defensieve hedgeposities moeten worden getoetst op opportuniteitskosten.",
    "AI and semiconductor leadership remains the dominant equity impulse.": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.",
    "AI / semiconductor leadership remains the dominant equity impulse.": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.",
    "Gold hedge behavior remains under review rather than automatic ballast.": "Het gedrag van goud als hedge blijft onder herbeoordeling en is geen automatische stabilisator.",
    "Macro status informs selectivity; it does not override pricing, risk or portfolio-discipline gates.": "Het macrobeeld ondersteunt selectiviteit, maar vervangt geen koers-, risico- of portefeuillediscipline.",
    "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad.": "Roteer niet agressief tenzij een regimeverschuiving minstens twee runs aanhoudt of cross-asset bevestiging breed wordt.",
    "Regime memory is available but has no report summary.": "Regimegeheugen is beschikbaar, maar bevat geen rapportsamenvatting.",
    "The macro pack is present, but no specific regime change was recorded.": "De macro-pack is aanwezig, maar er is geen specifieke regimewijziging vastgelegd.",
    "Portfolio actions still require pricing, relative strength and position discipline.": "Portefeuilleacties vereisen nog steeds koersbevestiging, relatieve sterkte en positiediscipline.",
    "No direct portfolio action from policy stance alone.": "Geen directe portefeuilleactie op basis van beleid alleen.",
    "Prefer quality, profitable growth and cash discipline over weak balance-sheet beta.": "Geef voorkeur aan kwaliteit, winstgevende groei en kasdiscipline boven zwakke balans-bèta.",
    "Non-U.S. developed exposure remains watchlist, not automatic add.": "Blootstelling aan ontwikkelde markten buiten de VS blijft op de volglijst en is geen automatische toevoeging.",
    "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.": "IEFA-blootstelling is nu aanwezig, maar verdere allocaties naar ontwikkelde markten buiten de VS vragen nog bevestiging in relatieve sterkte, prijsbasis en portefeuillediscipline.",
    "Capital spending and strategic supply-chain policy continue to support semiconductor and infrastructure lanes.": "Kapitaaluitgaven en strategisch toeleveringsbeleid blijven semiconductor- en infrastructuurthema’s ondersteunen.",
    "Defense-budget durability remains a structural support, but ETF vehicle choice still matters.": "De duurzaamheid van defensiebudgetten blijft een structurele steun, maar de ETF-keuze blijft belangrijk.",
    "The ECB raised rates this week in response to renewed inflation pressure; this raises the hurdle for rate-sensitive and non-U.S. developed-market exposure but does not override pricing, relative-strength or portfolio-discipline gates.": "De ECB verhoogde deze week de rente vanwege hernieuwde inflatiedruk; dit verhoogt de toetsingsdrempel voor rentegevoelige en niet-Amerikaanse ontwikkelde-marktenblootstelling, maar vervangt geen koers-, relatieve-sterkte- of portefeuillediscipline.",
}

NL_REGEX_REPLACEMENTS = [
    (
        re.compile(r"\bRisk-on growth has persisted for (\d+) run\(s\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\.?,?", re.IGNORECASE),
        lambda m: f"Risk-on groei houdt al {m.group(1)} runs aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
    (
        re.compile(r"\bRisk-on narrow leadership has persisted for (\d+) run\(s\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\.?,?", re.IGNORECASE),
        lambda m: f"Risk-on met smal marktleiderschap houdt al {m.group(1)} runs aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
]


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def _replace_longest_first(text: str, replacements: dict[str, str]) -> str:
    for src, dst in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(src, dst)
    return text


def _client_safe(value: Any) -> str:
    text = _text(value)
    for bad, replacement in SAFE_REPLACEMENTS.items():
        text = re.sub(re.escape(bad), replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\bdriver[_-][a-z0-9_\-]+\b", "macro driver", text, flags=re.IGNORECASE)
    text = re.sub(r"\bStage[- ]?[12]\b", "review-stage", text, flags=re.IGNORECASE)
    return text.strip()


def _client_safe_nl(value: Any) -> str:
    text = _client_safe(value)
    for pattern, replacement in NL_REGEX_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    text = _replace_longest_first(text, NL_TEXT_REPLACEMENTS)
    text = re.sub(r"\bbut\b", "maar", text, flags=re.IGNORECASE)
    text = re.sub(r"\bfunding\b", "allocatie", text, flags=re.IGNORECASE)
    text = re.sub(r"\bfundable\b", "geschikt voor allocatie", text, flags=re.IGNORECASE)
    text = re.sub(r"\bunder review\b", "onder herbeoordeling", text, flags=re.IGNORECASE)
    return text.strip()


def _short(value: Any, fallback: str = "", max_len: int = 190) -> str:
    cleaned = _client_safe(value) or fallback
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) <= max_len else cleaned[: max_len - 1].rstrip() + "…"


def _short_nl(value: Any, fallback: str = "", max_len: int = 190) -> str:
    cleaned = _client_safe_nl(value) or fallback
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) <= max_len else cleaned[: max_len - 1].rstrip() + "…"


def _confidence_pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "not scored"
    if number <= 1.0:
        number *= 100.0
    return f"{number:.0f}%"


def _confidence_pct_nl(value: Any) -> str:
    result = _confidence_pct(value)
    return "niet gescoord" if result == "not scored" else result


def _macro_pack(state: dict[str, Any]) -> dict[str, Any]:
    pack = state.get("macro_policy_pack") or {}
    return pack if isinstance(pack, dict) else {}


def _regime(pack: dict[str, Any]) -> dict[str, Any]:
    regime = pack.get("regime") or {}
    return regime if isinstance(regime, dict) else {}


def _regime_memory(pack: dict[str, Any]) -> dict[str, Any]:
    memory = pack.get("regime_memory") or {}
    return memory if isinstance(memory, dict) else {}


def _central_bank(pack: dict[str, Any], key: str) -> dict[str, Any]:
    banks = pack.get("central_banks") or {}
    if not isinstance(banks, dict):
        return {}
    value = banks.get(key) or {}
    return value if isinstance(value, dict) else {}


def _transfer_catalysts(pack: dict[str, Any]) -> list[dict[str, Any]]:
    catalysts = pack.get("policy_catalysts") or []
    if not isinstance(catalysts, list):
        return []
    selected = []
    for item in catalysts:
        if isinstance(item, dict) and item.get("transfer_to_report") is True:
            selected.append(item)
    transfer = pack.get("report_transfer") if isinstance(pack.get("report_transfer"), dict) else {}
    try:
        limit = int(transfer.get("max_policy_catalysts") or 3)
    except (TypeError, ValueError):
        limit = 3
    return selected[: max(1, min(limit, 5))]


def _list_values(value: Any, limit: int = MAX_BULLETS) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        cleaned = _short(item)
        if cleaned:
            result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def _list_values_nl(value: Any, limit: int = MAX_BULLETS) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        cleaned = _short_nl(item)
        if cleaned:
            result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def _portfolio_implications(pack: dict[str, Any]) -> list[str]:
    return _list_values(pack.get("portfolio_implications"), limit=3) or [
        "Portfolio actions still require pricing, relative strength and position discipline.",
    ]


def _portfolio_implications_nl(pack: dict[str, Any]) -> list[str]:
    return _list_values_nl(pack.get("portfolio_implications"), limit=3) or [
        "Portefeuilleacties vereisen nog steeds koersbevestiging, relatieve sterkte en positiediscipline.",
    ]


def _what_changed(pack: dict[str, Any]) -> list[str]:
    regime = _regime(pack)
    values = _list_values(regime.get("what_changed"), limit=3)
    if values:
        return values
    memory = _regime_memory(pack)
    summary = ((memory.get("report_transfer") or {}) if isinstance(memory.get("report_transfer"), dict) else {}).get("summary")
    return [_short(summary, "The macro pack is present, but no specific regime change was recorded.")]


def _what_changed_nl(pack: dict[str, Any]) -> list[str]:
    regime = _regime(pack)
    values = _list_values_nl(regime.get("what_changed"), limit=3)
    if values:
        return values
    memory = _regime_memory(pack)
    summary = ((memory.get("report_transfer") or {}) if isinstance(memory.get("report_transfer"), dict) else {}).get("summary")
    return [_short_nl(summary, "De macro-pack is aanwezig, maar er is geen specifieke regimewijziging vastgelegd.")]


def _geopolitical_status(pack: dict[str, Any]) -> str:
    catalysts = _transfer_catalysts(pack)
    text = " ".join(_text(item.get("policy_area")) + " " + _text(item.get("latest_signal")) for item in catalysts)
    if re.search(r"defense|sovereign|china|supply-chain|security|shipping|geopolitical|ECB|rate|inflation", text, flags=re.IGNORECASE):
        return "Elevated but localized"
    return "Mixed / policy-sensitive"


def _decision_rule(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    return _short(
        memory.get("decision_rule"),
        "Macro status informs selectivity; it does not override pricing, risk or portfolio-discipline gates.",
        max_len=210,
    )


def _decision_rule_nl(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    return _short_nl(
        memory.get("decision_rule"),
        "Het macrobeeld ondersteunt selectiviteit, maar vervangt geen koers-, risico- of portefeuillediscipline.",
        max_len=210,
    )


def _current_regime(pack: dict[str, Any]) -> str:
    regime = _regime(pack)
    return _short(regime.get("current"), "Macro status pending", max_len=90)


def _confidence(pack: dict[str, Any]) -> str:
    regime = _regime(pack)
    return _confidence_pct(regime.get("confidence"))


def _confidence_nl(pack: dict[str, Any]) -> str:
    regime = _regime(pack)
    return _confidence_pct_nl(regime.get("confidence"))


def _memory_summary(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    report_transfer = memory.get("report_transfer") if isinstance(memory.get("report_transfer"), dict) else {}
    return _short(report_transfer.get("summary"), "Regime memory is available but has no report summary.", max_len=220)


def _memory_summary_nl(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    report_transfer = memory.get("report_transfer") if isinstance(memory.get("report_transfer"), dict) else {}
    return _short_nl(report_transfer.get("summary"), "Regimegeheugen is beschikbaar, maar bevat geen rapportsamenvatting.", max_len=220)


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _state_dict(state: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = state.get(key)
    return value if isinstance(value, dict) else None


def deterministic_regime_surface_dto(state: dict[str, Any]) -> dict[str, Any] | None:
    if state.get("include_deterministic_regime_surface") is False:
        return None

    validation = _state_dict(state, "deterministic_regime_shadow_validation") or _load_json_if_exists(DEFAULT_DETERMINISTIC_VALIDATION_PATH)
    comparison = _state_dict(state, "deterministic_regime_shadow_comparison") or _load_json_if_exists(DEFAULT_DETERMINISTIC_COMPARISON_PATH)
    if not validation or not comparison:
        return None

    return build_deterministic_regime_client_surface(
        validation_evidence=validation,
        comparison_evidence=comparison,
        source_evidence_path=str(DEFAULT_DETERMINISTIC_VALIDATION_PATH),
        source_comparison_path=str(DEFAULT_DETERMINISTIC_COMPARISON_PATH),
    )


def deterministic_regime_lines_en(state: dict[str, Any]) -> list[str]:
    dto = deterministic_regime_surface_dto(state)
    if not dto:
        return []
    return [f"- {dto['safe_surface_en']}"]


def deterministic_regime_lines_nl(state: dict[str, Any]) -> list[str]:
    dto = deterministic_regime_surface_dto(state)
    if not dto:
        return []
    return [f"- {dto['safe_surface_nl']}"]


def _central_bank_lines_en(pack: dict[str, Any]) -> list[str]:
    lines = []
    for key, label in (("fed", "Fed"), ("ecb", "ECB")):
        bank = _central_bank(pack, key)
        stance = _short(bank.get("stance"), "not classified", max_len=80)
        implication = _short(bank.get("etf_implication"), "No direct portfolio action from policy stance alone.", max_len=190)
        lines.append(f"- {label} stance: {stance}. Portfolio read-through: {implication}")
    return lines


def _central_bank_lines_nl(pack: dict[str, Any]) -> list[str]:
    lines = []
    for key, label in (("fed", "Fed"), ("ecb", "ECB")):
        bank = _central_bank(pack, key)
        stance = STANCE_NL.get(_text(bank.get("stance")), _short_nl(bank.get("stance"), "niet geclassificeerd", max_len=80))
        implication = _short_nl(bank.get("etf_implication"), "Geen directe portefeuilleactie op basis van beleid alleen.", max_len=190)
        lines.append(f"- {label}-houding: {stance}. Portefeuillelezing: {implication}")
    return lines


def _policy_catalyst_lines_en(pack: dict[str, Any]) -> list[str]:
    lines = []
    for item in _transfer_catalysts(pack):
        area = _short(item.get("policy_area"), "Policy catalyst", max_len=80)
        signal = _short(item.get("latest_signal"), "Current policy signal remains relevant but not decisive.", max_len=260)
        lines.append(f"- {area}: {signal}")
    return lines or ["- No report-transfer policy catalyst was selected in the macro pack."]


def _policy_catalyst_lines_nl(pack: dict[str, Any]) -> list[str]:
    lines = []
    for item in _transfer_catalysts(pack):
        area = POLICY_AREA_NL.get(_text(item.get("policy_area")), _short_nl(item.get("policy_area"), "Beleidscatalysator", max_len=80))
        signal = _short_nl(item.get("latest_signal"), "Het beleidssignaal blijft relevant maar niet beslissend.", max_len=260)
        lines.append(f"- {area}: {signal}")
    return lines or ["- Er is geen beleidscatalysator geselecteerd voor rapportage."]


def executive_lines_en(state: dict[str, Any]) -> dict[str, str]:
    pack = _macro_pack(state)
    return {
        "primary_regime": _current_regime(pack),
        "secondary_cross_current": "Macro policy inputs are now surfaced through the runtime macro pack; portfolio actions still require pricing, relative-strength and position-discipline gates.",
        "geopolitical_regime": _geopolitical_status(pack),
        "what_changed": _what_changed(pack)[0],
    }


def executive_lines_nl(state: dict[str, Any]) -> dict[str, str]:
    pack = _macro_pack(state)
    regime = REGIME_NL.get(_current_regime(pack), _current_regime(pack))
    geo = GEOPOLITICAL_NL.get(_geopolitical_status(pack), _geopolitical_status(pack))
    changed = _what_changed_nl(pack)[0]
    return {
        "primary_regime": regime,
        "geopolitical_regime": geo,
        "what_changed": changed,
    }


def dashboard_en(state: dict[str, Any]) -> str:
    pack = _macro_pack(state)
    changed = "\n".join(f"- {item}" for item in _what_changed(pack))
    implications = "\n".join(f"- {item}" for item in _portfolio_implications(pack))
    banks = "\n".join(_central_bank_lines_en(pack))
    catalysts = "\n".join(_policy_catalyst_lines_en(pack))
    deterministic = "\n".join(deterministic_regime_lines_en(state))
    deterministic_block = f"\n{deterministic}" if deterministic else ""
    return f"""### Macro regime
- Current regime: {_current_regime(pack)}.
- Confidence: {_confidence(pack)}.{deterministic_block}
- Regime memory: {_memory_summary(pack)}
- Decision rule: {_decision_rule(pack)}

### Policy and geopolitical status
- Status: {_geopolitical_status(pack)}.
{banks}

### What changed
{changed}

### Portfolio implications
{implications}

### Policy catalysts included in this report
{catalysts}"""


def dashboard_nl(state: dict[str, Any]) -> str:
    pack = _macro_pack(state)
    regime = REGIME_NL.get(_current_regime(pack), _current_regime(pack))
    geo = GEOPOLITICAL_NL.get(_geopolitical_status(pack), _geopolitical_status(pack))
    changed = "\n".join(f"- {item}" for item in _what_changed_nl(pack))
    implications = "\n".join(f"- {item}" for item in _portfolio_implications_nl(pack))
    banks = "\n".join(_central_bank_lines_nl(pack))
    catalysts = "\n".join(_policy_catalyst_lines_nl(pack))
    deterministic = "\n".join(deterministic_regime_lines_nl(state))
    deterministic_block = f"\n{deterministic}" if deterministic else ""
    return f"""### Regimesamenvatting
- Huidig regime: {regime}.
- Vertrouwen: {_confidence_nl(pack)}.{deterministic_block}
- Regimegeheugen: {_memory_summary_nl(pack)}
- Beslisregel: {_decision_rule_nl(pack)}

### Beleids- en geopolitieke status
- Status: {geo}.
{banks}

### Wat veranderde
{changed}

### Portefeuille-implicaties
{implications}

### Beleidscatalysatoren in dit rapport
{catalysts}"""
