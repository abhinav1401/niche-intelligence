"""Frozen adjacent questions from the existing idea engine; generation cannot run."""

import copy
import json

from .config import ROOT
from .public_mode import blocked


def adjacent_opportunities(store, topic, videos):
    data = json.loads((ROOT / "assets" / "adjacent.json").read_text())
    return copy.deepcopy(data[topic])


generate_ideas = deduplicate = similarities = topic_sample = blocked
