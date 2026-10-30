import importlib
import json
import sqlite3
from pathlib import Path

import pytest

from nicheintel.config import Config
from nicheintel.db import Store
from nicheintel.public_mode import PUBLIC_DEMO_MODE, PublicDemoViolation


def test_config_never_loads_credentials_or_env(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "private-sentinel-do-not-read")
    monkeypatch.setenv("LLM_API_KEY", "private-sentinel-do-not-read")
    monkeypatch.setenv("NICHE_DATA_DIR", "/private/nonexistent-private-research")
    monkeypatch.setenv("PUBLIC_DEMO_MODE", "false")
    config = Config.from_env()
    assert PUBLIC_DEMO_MODE and config.public_demo_mode
    assert config.youtube_key == config.llm_key == config.llm_base == config.llm_model == ""
    assert config.db_path().name == "synthetic.sqlite3"
    with pytest.raises(PublicDemoViolation):
        config.db_path("live")


def test_private_databases_and_live_mode_are_rejected(tmp_path):
    with pytest.raises(PublicDemoViolation):
        Store(tmp_path / "production.sqlite3")
    with pytest.raises(PublicDemoViolation):
        Store(mode="live")
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("sql", [
    "DELETE FROM videos", "UPDATE videos SET views=1", "CREATE TABLE visitor(x)",
    "DROP TABLE channels", "PRAGMA query_only=OFF", "ATTACH DATABASE ':memory:' AS visitor",
    "SELECT load_extension('anything')", "VACUUM INTO 'visitor.sqlite3'",
])
def test_raw_sql_and_alternative_read_methods_cannot_write(sql):
    store = Store()
    with store.connect() as connection, pytest.raises(sqlite3.DatabaseError):
        connection.execute(sql)
    with pytest.raises(Exception, match="not authorized|authorization denied|readonly|not permitted"):
        store.rows(sql)


@pytest.mark.parametrize("name", [
    "execute", "set_setting", "audit", "channel", "video", "statistics", "_upsert", "classify",
    "override_short", "run", "save_idea", "scrub_idea_examples", "delete_channel", "batch", "locked_batch",
])
def test_every_store_mutation_rejects_direct_calls(name):
    with pytest.raises(PublicDemoViolation):
        getattr(Store(), name)(None)


@pytest.mark.parametrize("module,names", [
    ("research", ["launch_worker"]),
    ("classification", ["classify_all", "llm_json", "local_model", "propose_clusters", "reassign_subjects"]),
    ("analysis", ["analyse", "video_metrics", "opportunity_metrics"]),
    ("ideas", ["generate_ideas"]),
    ("imports", ["import_signals", "import_trends", "import_studio"]),
    ("reconciliation", ["fetch_monitoring", "reconciliation_ui"]),
    ("demo", ["seed_demo"]),
    ("export", ["export_to"]),
    ("policy", ["require_analytics", "maintain_retention"]),
    ("dashboard", ["service_action", "invalidate"]),
])
def test_research_and_service_entry_points_fail_closed(module, names):
    imported = importlib.import_module("nicheintel." + module)
    for name in names:
        with pytest.raises(PublicDemoViolation):
            getattr(imported, name)(None)


@pytest.mark.parametrize("module,classname", [("youtube", "YouTube"), ("research", "ResearchEngine")])
def test_service_methods_reject_even_when_constructor_bypassed(module, classname):
    cls = getattr(importlib.import_module("nicheintel." + module), classname)
    with pytest.raises(PublicDemoViolation):
        cls(None, None)
    obj = object.__new__(cls)
    for name in vars(cls):
        if not name.startswith("__"):
            with pytest.raises(PublicDemoViolation):
                getattr(obj, name)(None)


def test_no_quota_reservations_or_cloud_reconciliation():
    from nicheintel.quota import QuotaManager

    quota = QuotaManager(Store())
    for method in [quota.reserve, quota.suspend]:
        with pytest.raises(PublicDemoViolation):
            method("search")
    assert quota.snapshot()["cloud_reconciled"] is False
    assert quota.history().status.eq("ok").all()


def test_assets_are_fictional_and_exports_contain_no_private_research():
    from io import BytesIO
    from zipfile import ZipFile

    from nicheintel.export import bundle
    from nicheintel.read_models import results

    store = Store()
    for table in ["channels", "videos", "snapshots"]:
        assert {row["source"] for row in store.rows(f"SELECT DISTINCT source FROM {table}")} == {"synthetic_demo"}
    assert len(store.rows("SELECT * FROM videos")) == 1920
    assert len(store.rows("SELECT * FROM channels")) == 24
    assert store.rows("SELECT * FROM provider_usage") == []
    assert store.rows("SELECT * FROM signals") == []
    for table in ["videos", "channels"]:
        assert store.rows(f"SELECT id FROM {table} WHERE url!='' OR thumbnail!=''") == []
    assert all(Path(str(row["name"])).name == row["name"] for row in store.rows("SELECT name FROM sqlite_master"))
    videos, ranking = results()
    archive = ZipFile(BytesIO(bundle(store, videos, ranking)))
    assert json.loads(archive.read("manifest.json"))["synthetic"] is True
    all_text = b"\n".join(archive.read(name) for name in archive.namelist())
    assert b"/Users/" not in all_text and b"private-sentinel" not in all_text
    assert b"DEMO" in archive.read("research.md")


def test_asset_integrity_gate_rejects_changed_manifest(monkeypatch):
    from nicheintel.integrity import verify_assets

    original = Path.read_text

    def changed(path, *args, **kwargs):
        if path.name == "manifest.json":
            return '{"synthetic":false}'
        return original(path, *args, **kwargs)

    verify_assets.cache_clear()
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(PublicDemoViolation):
        Store()
    verify_assets.cache_clear()
