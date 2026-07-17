from __future__ import annotations

from pathlib import Path

import tools.validate_cockpit_wp11_production_enablement as validator

_BASE_PREPARE = validator.prepare_temp_output


def _prepare_with_official_authority(repo_root: Path, work_root: Path) -> Path:
    output_dir = _BASE_PREPARE(repo_root, work_root)
    for relative in (
        "output/etf_portfolio_state.json",
        "output/etf_trade_ledger.csv",
    ):
        validator._copy_path(repo_root / relative, work_root / relative)
    return output_dir


validator.prepare_temp_output = _prepare_with_official_authority


if __name__ == "__main__":
    validator.main()
