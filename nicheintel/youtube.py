"""No live service implementation is shipped in this public distribution."""

from .public_mode import PublicDemoViolation, blocked

ResearchError = PublicDemoViolation


class YouTube:
    __init__ = blocked
    get = reserve = discover = collect = refresh = videos = batch_stats = channel_items = add_channel = coverage = record_search = blocked
