from __future__ import annotations

from pathlib import Path

from apply_etf_report_integrity_source_patch import apply as apply_base


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Follow-up patch anchor not found in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply() -> None:
    apply_base()
    replace_once(
        "runtime/report_portfolio_integrity_contract.py",
        '''    duplicate_patterns = [\n        r"(Review has persisted for multiple report cycles;\\s*)\\1+",''',
        '''    spy_link = r"(?:\\[SPY\\]\\([^\\)]+\\)|SPY)"\n    if language == "nl":\n        text = re.sub(\n            spy_link + r"-relative performance",\n            "prestaties tegenover de SPY-marktbenchmark",\n            text,\n            flags=re.IGNORECASE,\n        )\n    else:\n        text = re.sub(\n            spy_link + r"-relative performance",\n            "performance versus the SPY market benchmark",\n            text,\n            flags=re.IGNORECASE,\n        )\n\n    text = text.replace(\n        "Monitor commodity breadth and hedge contribution after execution.",\n        "Monitor commodity breadth and hedge contribution in the current portfolio.",\n    )\n    text = text.replace(\n        "Monitor grondstoffenbreedte en bijdrage aan de hedgefunctie na uitvoering.",\n        "Monitor grondstoffenbreedte en bijdrage aan de hedgefunctie in de huidige portefeuille.",\n    )\n    text = text.replace(\n        "A stronger alternative is available for…",\n        "A stronger alternative is available; complete the PAVE-versus-GRID review",\n    )\n    text = text.replace(\n        "Sterker alternatief is beschikbaar voor…",\n        "Sterker alternatief beschikbaar; rond de PAVE-versus-GRID-review af",\n    )\n    text = re.sub(\n        r"Review has persisted for multiple report cycles;\\s*Review has persisted for several report(?: cycles)?…?",\n        "Review has persisted for multiple report cycles",\n        text,\n        flags=re.IGNORECASE,\n    )\n    text = re.sub(\n        r"Review loopt al meerdere rapportcycli;\\s*Review loopt al meerdere rapport(?:cycli)?…?",\n        "Review loopt al meerdere rapportcycli",\n        text,\n        flags=re.IGNORECASE,\n    )\n    text = text.replace(\n        "- PPA / ITA: Defense spending remains structurally durable, but vehicle selection must be proven.",\n        "- PPA / ITA (non-held watchlist comparison): Defense spending remains structurally durable, but vehicle selection must be proven.",\n    )\n    text = text.replace(\n        "- PPA / ITA: Defensie-uitgaven blijven structureel ondersteund, maar ETF-keuze blijft belangrijk.",\n        "- PPA / ITA (niet-aangehouden volglijstvergelijking): Defensie-uitgaven blijven structureel ondersteund, maar ETF-keuze blijft belangrijk.",\n    )\n\n    duplicate_patterns = [\n        r"(Review has persisted for multiple report cycles;\\s*)\\1+",''',
    )


if __name__ == "__main__":
    apply()
    print("ETF_REPORT_INTEGRITY_SOURCE_FOLLOWUP_PATCH_OK")
