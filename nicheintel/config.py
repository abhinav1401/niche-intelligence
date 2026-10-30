"""Credential-free public configuration. Never loads dotenv, secrets or environment values."""

from dataclasses import dataclass
from pathlib import Path

from .public_mode import PUBLIC_DEMO_MODE, blocked

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WEIGHTS = {"demand": 30, "underserved": 25, "advantage": 20, "repeatability": 15, "momentum": 10}


@dataclass(frozen=True)
class Config:
    public_demo_mode: bool = PUBLIC_DEMO_MODE
    youtube_key: str = ""
    llm_key: str = ""
    llm_base: str = ""
    llm_model: str = ""
    embedding_model: str = ""
    daily_units: int = 9000
    search_calls: int = 80
    quota_scheme: str = "separate"

    @classmethod
    def from_env(cls):
        # Compatibility name for reused presentation components; no environment read.
        return cls()

    def db_path(self, mode="demo"):
        if mode != "demo":
            blocked()
        return ROOT / "assets" / "synthetic.sqlite3"
