from __future__ import annotations

import json
import urllib.parse
import urllib.request


def http_get_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def q(params: dict) -> str:
    return urllib.parse.urlencode(params)
