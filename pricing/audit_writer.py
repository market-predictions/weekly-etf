from __future__ import annotations

import json
import re
from pathlib import Path

from .models import PricingPassResult


def _safe_token(value: str) -> str:
    token = re.sub(r"[^0-9A-Za-z_.-]", "_", str(value or "").strip())
    return token or "unknown"


def write_price_audit(output_dir: str | Path, result: PricingPassResult, run_id: str | None = None) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = result.to_dict()
    if run_id:
        payload["run_id"] = run_id
        close_token = _safe_token(result.requested_close_date)
        run_token = _safe_token(run_id)
        path = output_dir / f"price_audit_{close_token}_{run_token}.json"
    else:
        # Backward-compatible fallback for non-production callers. Production
        # workflow calls must pass a run_id so same-day/same-close reruns do not
        # overwrite audit provenance.
        path = output_dir / f"price_audit_{result.run_date}.json"

    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
