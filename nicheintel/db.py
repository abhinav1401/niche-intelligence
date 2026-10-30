"""Immutable synthetic data access; no schema creation, migrations or write connection."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from .config import ROOT
from .integrity import verify_assets
from .public_mode import blocked

ASSET = ROOT / "assets" / "synthetic.sqlite3"


def utcnow():
    return "2026-10-30T18:00:00+00:00"


def authorizer(action, arg1, arg2, database, trigger):
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    if action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() in {"load_extension", "writefile", "readfile"}:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


class Store:
    def __init__(self, path=None, mode="demo"):
        if mode != "demo" or (path is not None and Path(path).resolve() != ASSET.resolve()):
            blocked()
        verify_assets()
        self.path, self.mode = ASSET, "demo"

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(ASSET.as_uri() + "?mode=ro&immutable=1", uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        connection.enable_load_extension(False)
        connection.set_authorizer(authorizer)
        try:
            yield connection
        finally:
            connection.close()

    def rows(self, sql, params=()):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(sql, params).fetchall()]

    def frame(self, sql, params=()):
        with self.connect() as connection:
            return pd.read_sql_query(sql, connection, params=params)

    def setting(self, key, default=None):
        rows = self.rows("SELECT value FROM meta WHERE key=?", (key,))
        return json.loads(rows[0]["value"]) if rows else default

    execute = set_setting = audit = channel = video = statistics = _upsert = classify = blocked
    override_short = run = save_idea = scrub_idea_examples = delete_channel = batch = locked_batch = blocked
    _save_snapshot = blocked
