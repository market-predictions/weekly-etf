from __future__ import annotations

import json
from pathlib import Path

from .models import PricingPassResult


def write_price_audit(output_dir: str | Path, result: PricingPassResult) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"price_audit_{result.run_date}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path
