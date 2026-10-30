"""Verify only the fixed public asset set; never accept a visitor-selected path."""

import hashlib
import json
from functools import lru_cache

from .config import ROOT
from .public_mode import PublicDemoViolation

EXPECTED_ASSETS = {"synthetic.sqlite3", "videos.json", "ranking.json", "adjacent.json", "quota.json", "workflow.json", "theme.css"}


@lru_cache(maxsize=1)
def verify_assets():
    manifest = json.loads((ROOT / "assets" / "manifest.json").read_text())
    if manifest.get("synthetic") is not True or set(manifest.get("sha256", {})) != EXPECTED_ASSETS:
        raise PublicDemoViolation("The public synthetic fixture could not be verified.")
    for name, expected in manifest["sha256"].items():
        actual = hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()
        if actual != expected:
            raise PublicDemoViolation("The public synthetic fixture could not be verified.")
    return True
