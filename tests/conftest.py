import hashlib
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def public_isolation(monkeypatch):
    """Application tests must neither use network nor change any bundled asset."""
    assets = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "assets").iterdir() if p.is_file()}

    def forbidden(*args, **kwargs):
        pytest.fail("Application attempted an outbound network connection")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    yield
    assert assets == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in assets}
