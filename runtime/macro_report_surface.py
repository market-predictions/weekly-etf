from __future__ import annotations

import re
from typing import Any

MAX_BULLETS = 3

REGIME_NL = {
    "Risk-on growth": "Risk-on groei",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Policy Transition / Mixed Regime": "Beleidstransitie / gemengd regime",
    "Unknown": "Onbekend",
}

GEOPOLITICAL_NL = {
    "Elevated but localized": "Verhoogd maar gelokaliseerd",
    "Mixed / policy-sensitive": "Gemengd / beleidsgevoelig",
}

STANCE_NL = {
    "Restrictive / data-dependent": "Restrictief / datagedreven",
    "Neutral / transition": "Neutraal / overgangsfase",
    "Gradual normalization risk": "Geleidelijke normalisatierisico's",
    "Supportive but credibility-sensitive": "Ondersteunend maar geloofwaardigheidsgevoelig",
}

POLICY_AREA_NL = {
    "AI infrastructure and semiconductor supply chains": "AI-infrastructuur en semiconductor-toeleveringsketens",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "Energy security and nuclear policy": "Energiezekerheid en nucleair beleid",
    "China stimulus and platform regulation": "Chinese stimulering en platformregulering",
}

SAFE_REPLACEMENTS = {
    "deterministic_regime_shadow": "internal regime comparison",
    "client_facing_authority": "authority flag",
    "none_shadow_comparison_only": "comparison-only status",
    "shadow_only": "internal-only",
}


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def _short(value: Any, fallback: str = "", max_len: int = 190) -> str:
    cleaned = _client_safe(value) or fallback
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) <= max_len else cleaned[: max_len - 1].rstrip() + "…"


def _client_safe(value: Any) -> str:
    text = _text(value)
    for bad, replacement in SAFE_REPLACEMENTS.items():
        text = re.sub(re.escape(bad), replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\bdriver[_-][a-z0-9_\-]+\b", "macro driver", text, flags=re.IGNORECASE)
    text = re.sub(r"\bStage[- ]?[12]\b", "review-stage", text, flags=re.IGNORECASE)
    return text.strip()


def _confidence_pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "not scored"
    if number <= 1.0:
        number *= 100.0
    return f"{number:.0f}%"


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
    return selected[:2]


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


def _portfolio_implications(pack: dict[str, Any]) -> list[str]:
    return _list_values(pack.get("portfolio_implications"), limit=3) or [
        "Portfolio actions still require pricing, relative strength and position discipline.",
    ]


def _what_changed(pack: dict[str, Any]) -> list[str]:
    regime = _regime(pack)
    values = _list_values(regime.get("what_changed"), limit=3)
    if values:
        return values
    memory = _regime_memory(pack)
    summary = ((memory.get("report_transfer") or {}) if isinstance(memory.get("report_transfer"), dict) else {}).get("summary")
    return [_short(summary, "The macro pack is present, but no specific regime change was recorded.")]


def _geopolitical_status(pack: dict[str, Any]) -> str:
    catalysts = _transfer_catalysts(pack)
    text = " ".join(_text(item.get("policy_area")) + " " + _text(item.get("latest_signal")) for item in catalysts)
    if re.search(r"defense|sovereign|china|supply-chain|security|shipping|geopolitical", text, flags=re.IGNORECASE):
        return "Elevated but localized"
    return "Mixed / policy-sensitive"


def _decision_rule(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    return _short(
        memory.get("decision_rule"),
        "Macro status informs selectivity; it does not override pricing, risk or portfolio-discipline gates.",
        max_len=210,
    )


def _current_regime(pack: dict[str, Any]) -> str:
    regime = _regime(pack)
    return _short(regime.get("current"), "Macro status pending", max_len=90)


def _confidence(pack: dict[str, Any]) -> str:
    regime = _regime(pack)
    return _confidence_pct(regime.get("confidence"))


def _memory_summary(pack: dict[str, Any]) -> str:
    memory = _regime_memory(pack)
    report_transfer = memory.get("report_transfer") if isinstance(memory.get("report_transfer"), dict) else {}
    return _short(report_transfer.get("summary"), "Regime memory is available but has no report summary.", max_len=220)


def _central_bank_lines_en(pack: dict[str, Any]) -> list[str]:
    lines = []
    for key, label in (("fed", "Fed"), ("ecb", "ECB")):
        bank = _central_bank(pack, key)
        stance = _short(bank.get("stance"), "not classified", max_len=80)
        implication = _short(bank.get("etf_implication"), "No direct portfolio action from policy stance alone.", max_len=160)
        lines.append(f"- {label} stance: {stance}. Portfolio read-through: {implication}")
    return lines


def _central_bank_lines_nl(pack: dict[str, Any]) -> list[str]:
    lines = []
    for key, label in (("fed", "Fed"), ("ecb", "ECB")):
        bank = _central_bank(pack, key)
        stance = STANCE_NL.get(_text(bank.get("stance")), _short(bank.get("stance"), "niet geclassificeerd", max_len=80))
        implication = _short(bank.get("etf_implication"), "Geen directe portefeuilleactie op basis van beleid alleen.", max_len=160)
        lines.append(f"- {label}-houding: {stance}. Portefeuillelezing: {implication}")
    return lines


def _policy_catalyst_lines_en(pack: dict[str, Any]) -> list[str]:
    lines = []
    for item in _transfer_catalysts(pack):
        area = _short(item.get("policy_area"), "Policy catalyst", max_len=80)
        signal = _short(item.get("latest_signal"), "Current policy signal remains relevant but not decisive.", max_len=180)
        lines.append(f"- {area}: {signal}")
    return lines or ["- No report-transfer policy catalyst was selected in the macro pack."]


def _policy_catalyst_lines_nl(pack: dict[str, Any]) -> list[str]:
    lines = []
    for item in _transfer_catalysts(pack):
        area = POLICY_AREA_NL.get(_text(item.get("policy_area")), _short(item.get("policy_area"), "Beleidscatalysator", max_len=80))
        signal = _short(item.get("latest_signal"), "Het beleidssignaal blijft relevant maar niet beslissend.", max_len=180)
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
    changed = _what_changed(pack)[0]
    return {
        "primary_regime": regime,
        "geopolitical_regime": geo,
        "what_changed": f"Macro-, beleids- en regime-input komen nu uit de runtime macro-pack; portefeuilleacties blijven afhankelijk van prijs, relatieve sterkte en portefeuillediscipline. Kernpunt: {changed}",
    }


def dashboard_en(state: dict[str, Any]) -> str:
    pack = _macro_pack(state)
    changed = "\n".join(f"- {item}" for item in _what_changed(pack))
    implications = "\n".join(f"- {item}" for item in _portfolio_implications(pack))
    banks = "\n".join(_central_bank_lines_en(pack))
    catalysts = "\n".join(_policy_catalyst_lines_en(pack))
    return f"""### Macro regime
- Current regime: {_current_regime(pack)}.
- Confidence: {_confidence(pack)}.
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
    changed = "\n".join(f"- {item}" for item in _what_changed(pack))
    implications = "\n".join(f"- {item}" for item in _portfolio_implications(pack))
    banks = "\n".join(_central_bank_lines_nl(pack))
    catalysts = "\n".join(_policy_catalyst_lines_nl(pack))
    return f"""### Regimesamenvatting
- Huidig regime: {regime}.
- Vertrouwen: {_confidence(pack)}.
- Regimegeheugen: {_memory_summary(pack)}
- Beslisregel: {_decision_rule(pack)}

### Beleids- en geopolitieke status
- Status: {geo}.
{banks}

### Wat veranderde
{changed}

### Portefeuille-implicaties
{implications}

### Beleidscatalysatoren in dit rapport
{catalysts}"""
