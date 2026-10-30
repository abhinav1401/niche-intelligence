"""Read-only public distribution never grants live analytics permission."""

from .public_mode import blocked

POLICY_URL = "https://developers.google.com/youtube/terms/derived-metrics-policy"


def analytics_available(store):
    return store.mode == "demo"


require_analytics = maintain_retention = blocked
