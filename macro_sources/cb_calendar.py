from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_cb_calendar(path: str | Path = "config/cb_calendar.yml") -> dict[str, Any]:
    calendar_path = Path(path)
    if not calendar_path.exists():
        return {"version": 1, "central_banks": {}, "status": "missing"}
    payload = yaml.safe_load(calendar_path.read_text(encoding="utf-8")) or {}
    payload["status"] = "loaded"
    payload["source_file"] = str(calendar_path)
    return payload
