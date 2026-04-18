from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML is required for pricing configs. Install with: pip install pyyaml") from exc


class SymbolResolver:
    def __init__(self, registry_file: str | Path):
        self.cfg = yaml.safe_load(Path(registry_file).read_text(encoding="utf-8"))

    def normalize_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def get_source_order(self, symbol: str, kind: str) -> list[str]:
        symbol = self.normalize_symbol(symbol)
        overrides = self.cfg.get("overrides", {})
        defaults = self.cfg["defaults"]

        if kind == "holding":
            order = list(defaults["holding_source_order"])
            if symbol not in overrides:
                order = [x for x in order if x != "issuer_override"]
            return order

        return list(defaults["generic_source_order"])

    def get_issuer_handler(self, symbol: str) -> str | None:
        symbol = self.normalize_symbol(symbol)
        return self.cfg.get("overrides", {}).get(symbol, {}).get("issuer_handler")
