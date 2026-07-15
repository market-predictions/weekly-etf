from __future__ import annotations

from pathlib import Path


class PatchError(RuntimeError):
    pass


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise PatchError(f"Expected exact-phrase anchor missing in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> None:
    path = Path("runtime/report_freshness_contract.py")
    changed = False
    changed |= replace_once(
        path,
        '"Only watchlist; non-U.S. exposure remains a diversification gap.": f"IEFA already represents {iefa_weight:.2f}% of the portfolio; further expansion is not automatic and remains relative-strength and concentration gated.",',
        '"Watchlist only; non-U.S. exposure remains a diversification gap.": f"IEFA already represents {iefa_weight:.2f}% of the portfolio; further expansion is not automatic and remains relative-strength and concentration gated.",',
    )
    changed |= replace_once(
        path,
        '            "only watchlist; non-u.s. exposure remains a diversification gap",\n',
        '            "only watchlist; non-u.s. exposure remains a diversification gap",\n            "watchlist only; non-u.s. exposure remains a diversification gap",\n',
    )
    print(f"ETF_REPORT_FRESHNESS_EXACT_PHRASE_PATCH_OK | changed={str(changed).lower()}")


if __name__ == "__main__":
    main()
