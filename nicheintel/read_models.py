"""Load precomputed synthetic analyses; no research executes on the public server."""

import json
from functools import lru_cache

import pandas as pd

from .config import ROOT
from .integrity import verify_assets


@lru_cache(maxsize=1)
def frozen_results():
    verify_assets()
    videos = pd.DataFrame(json.loads((ROOT / "assets" / "videos.json").read_text()))
    videos["published"] = pd.to_datetime(videos["published"], unit="ms", utc=True)
    ranking = pd.DataFrame(json.loads((ROOT / "assets" / "ranking.json").read_text()))
    return videos, ranking


def results():
    videos, ranking = frozen_results()
    return videos.copy(deep=True), ranking.copy(deep=True)
