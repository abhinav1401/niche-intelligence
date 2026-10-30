"""Frozen illustrative quota data; reservations and suspensions always reject."""

import json

from .config import ROOT
from .public_mode import blocked


class QuotaManager:
    def __init__(self, store, config=None, now=None):
        if store.mode != "demo":
            blocked()
        self.store = store

    def snapshot(self):
        return json.loads((ROOT / "assets" / "quota.json").read_text())

    def history(self):
        return self.store.frame("""SELECT r.id,r.quota_day,r.endpoint,r.status,r.attempt,r.stage,
            c.metric,c.period,c.units FROM api_requests r JOIN quota_charges c ON c.request_id=r.id""")

    reserve = suspend = blocked
