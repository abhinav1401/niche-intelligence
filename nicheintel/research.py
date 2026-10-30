"""No live service implementation is shipped in this public distribution."""

from .public_mode import PublicDemoViolation, blocked

ResearchError = PublicDemoViolation


class ResearchEngine:
    __init__ = blocked
    start = run = pause = resume = claim = enqueue = event = execute_task = select_competitors = discover_subjects = analysis = report = _api = heartbeat = add_candidate = blocked


launch_worker = blocked
