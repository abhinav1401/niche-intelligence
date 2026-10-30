import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("security_gate", ROOT / "scripts" / "security_check.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def test_draft_scan_passes_but_publication_requires_explicit_approval(monkeypatch):
    import json

    read_text = Path.read_text

    def draft_site(path, *args, **kwargs):
        text = read_text(path, *args, **kwargs)
        if path == ROOT / "site.json":
            site = json.loads(text)
            site["publication_approved"] = False
            return json.dumps(site)
        return text

    monkeypatch.setattr(Path, "read_text", draft_site)
    assert gate.run(allow_draft=True) == 0
    assert gate.run(allow_draft=False) == 1


def test_secret_and_private_path_checks_do_not_print_matching_values():
    issues = []
    example = ("AI" + "za" + "a" * 35).encode()
    gate.check_blob("fixture", example, issues)
    assert len(issues) == 1
    assert example.decode() not in issues[0]


def test_git_inspection_failure_cannot_look_like_an_empty_history(monkeypatch):
    from types import SimpleNamespace

    import pytest

    monkeypatch.setattr(gate.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout=b""))
    with pytest.raises(RuntimeError, match="publication cannot be verified"):
        gate.git("rev-list", "--objects", "--all")


def test_missing_or_stale_publication_manifest_blocks_release(tmp_path, monkeypatch):
    import hashlib
    import json

    monkeypatch.setattr(gate, "ROOT", tmp_path)
    issues = []
    gate.verify_publication_manifest(["app.py"], issues)
    assert issues and "missing" in issues[0]
    source = tmp_path / "app.py"
    source.write_text("public fixture")
    record = {"app.py": {"sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "bytes": source.stat().st_size}}
    (tmp_path / "PUBLICATION_MANIFEST.json").write_text(json.dumps({"files": record}))
    issues = []
    gate.verify_publication_manifest(["app.py", "PUBLICATION_MANIFEST.json"], issues)
    assert not issues
    source.write_text("unreviewed change")
    gate.verify_publication_manifest(["app.py", "PUBLICATION_MANIFEST.json"], issues)
    assert issues and "stale" in issues[0]


def test_forbidden_paths_cannot_hide_in_staging_or_history():
    for path in ["assets/.env", ".streamlit/secrets.toml", "assets/research.sqlite3", "data/private.db"]:
        for label in ["staged file", "historical tree"]:
            issues = []
            gate.check_path(path, issues, label)
            assert issues
    issues = []
    gate.check_path("assets/synthetic.sqlite3", issues, "historical tree")
    assert not issues
