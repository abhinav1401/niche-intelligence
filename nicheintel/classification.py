"""Frozen taxonomy; classification and model execution are unavailable."""

import json
from pathlib import Path

from .public_mode import blocked


def taxonomy(store=None):
    default = json.loads(Path(__file__).with_name("taxonomy.json").read_text())
    return store.setting("taxonomy", default) if store else default

classify_all = llm_json = local_model = propose_clusters = reassign_subjects = blocked
