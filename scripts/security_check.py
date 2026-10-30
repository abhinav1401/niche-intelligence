"""Local release gate: inspect the deployment tree, staged files and every Git blob.

No network requests, environment dumps or matched secret values are printed.
"""

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "playwright-results", ".DS_Store"}
PATTERNS = [
    re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    re.compile(rb"(?:sk-proj-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}"),
    re.compile(rb"ya29\.[A-Za-z0-9._-]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"/(?:Users|home)/[A-Za-z0-9_-]+/"),
]
ALLOWED_ROOTS = {"nicheintel", "assets", "content", "docs", "tests", "scripts", ".streamlit", ".github", ".githooks"}
ALLOWED_FILES = {"app.py", "README.md", "requirements.txt", "requirements-dev.txt", ".python-version", ".gitignore", "pyproject.toml", "site.json", "PUBLICATION_MANIFEST.json"}


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("Git inspection failed; publication cannot be verified")
    return result.stdout


def check_path(name, errors, label="deployment file"):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"Unsafe {label} path")
        return
    if relative.parts[0] not in ALLOWED_ROOTS and name not in ALLOWED_FILES:
        errors.append(f"Unexpected {label}: {name}")
    if relative.name.startswith(".env") or relative.name == "secrets.toml":
        errors.append(f"Forbidden credential/configuration file in {label}")
    if relative.suffix in {".db", ".sqlite", ".sqlite3"} and name != "assets/synthetic.sqlite3":
        errors.append(f"Unexpected database in {label}")


def check_blob(label, data, errors):
    if any(pattern.search(data) for pattern in PATTERNS):
        errors.append(f"Potential secret or private home path in {label}; matching values suppressed")


def verify_publication_manifest(files, errors):
    path = ROOT / "PUBLICATION_MANIFEST.json"
    if not path.is_file():
        errors.append("Publication blocked: exact file/hash manifest is missing")
        return
    try:
        manifest = json.loads(path.read_text())
        proposed = manifest["files"]
        if set(proposed) != set(files) - {"PUBLICATION_MANIFEST.json"}:
            errors.append("Publication blocked: file manifest does not match deployment tree")
            return
        for name, record in proposed.items():
            file = ROOT / name
            if hashlib.sha256(file.read_bytes()).hexdigest() != record["sha256"] or file.stat().st_size != record["bytes"]:
                errors.append("Publication blocked: file manifest is stale")
                return
    except (OSError, ValueError, KeyError, TypeError):
        errors.append("Publication blocked: file manifest cannot be verified")


def run(allow_draft=False):
    errors = []
    files = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append("Symbolic links are not allowed in the deployment tree")
            continue
        if not path.is_file():
            continue
        name = relative.as_posix()
        files.append(name)
        check_path(name, errors)
        check_blob(name, path.read_bytes(), errors)
    manifest = json.loads((ROOT / "assets" / "manifest.json").read_text())
    if manifest.get("synthetic") is not True:
        errors.append("Synthetic fixture declaration missing")
    for name, digest in manifest.get("sha256", {}).items():
        if Path(name).name != name or hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest() != digest:
            errors.append("Synthetic fixture integrity check failed")
    con = sqlite3.connect((ROOT / "assets" / "synthetic.sqlite3").as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        for table in ["channels", "videos", "snapshots"]:
            sources = {row[0] for row in con.execute(f"SELECT DISTINCT source FROM {table}")}
            if sources != {"synthetic_demo"}:
                errors.append("Non-synthetic source in bundled fixture")
        if con.execute("SELECT COUNT(*) FROM provider_usage").fetchone()[0]:
            errors.append("Provider data must not be bundled")
        if con.execute("SELECT COUNT(*) FROM channels WHERE id NOT LIKE 'demo_channel_%'").fetchone()[0]:
            errors.append("Unexpected creator identifier in fixture")
        for table in ["channels", "videos"]:
            if con.execute(f"SELECT COUNT(*) FROM {table} WHERE url!='' OR thumbnail!=''").fetchone()[0]:
                errors.append("External creator/video/media URLs must not be bundled")
    finally:
        con.close()
    # Inspect staged bytes, not only their working-tree counterparts.
    staged = git("diff", "--cached", "--name-only", "-z").decode().split("\0")
    for name in filter(None, staged):
        check_path(name, errors, "staged file")
        check_blob("staged file", git("show", ":" + name), errors)
        if name not in files:
            errors.append("An unexpected staged file is present")
    # New deployment history only; never import private application history.
    for commit in git("log", "--all", "--format=%H").decode().splitlines():
        for raw_path in git("ls-tree", "-r", "--name-only", "-z", commit).split(b"\0"):
            if raw_path:
                check_path(raw_path.decode(), errors, "historical tree")
    objects = git("rev-list", "--objects", "--all").splitlines()
    blobs = 0
    for row in objects:
        oid = row.split(b" ", 1)[0].decode()
        kind = git("cat-file", "-t", oid).strip()
        if kind == b"blob":
            blobs += 1
            check_blob("historical Git blob", git("cat-file", "blob", oid), errors)
        elif kind == b"commit":
            check_blob("Git commit metadata", git("cat-file", "commit", oid), errors)
    info = json.loads((ROOT / "site.json").read_text())
    if not allow_draft:
        git("rev-parse", "--verify", "HEAD")
        verify_publication_manifest(files, errors)
        required = ["operator_name", "privacy_contact", "support_contact", "effective_date", "legal_review_confirmed", "publication_approved"]
        if not all(info.get(name) for name in required) or any(info.get(name) is not True for name in ["legal_review_confirmed", "publication_approved"]):
            errors.append("Publication blocked: final operator/contact, legal review and explicit publication approval are required")
        if any(re.search(r"pending|placeholder|todo|tbd|\{\{|\[", str(info.get(name, "")), re.I) for name in ["operator_name", "privacy_contact", "support_contact"]):
            errors.append("Publication blocked: unresolved legal placeholder")
        try:
            date.fromisoformat(info.get("effective_date", ""))
        except (TypeError, ValueError):
            errors.append("Publication blocked: effective date must be an approved ISO date")
        for name in ["privacy_contact", "support_contact"]:
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", str(info.get(name, ""))):
                errors.append("Publication blocked: approved public contact email is missing or invalid")
    print(json.dumps({"status": "blocked" if errors else "passed", "draft_allowed": allow_draft,
                      "files_checked": len(files), "staged_files_checked": len(list(filter(None, staged))),
                      "history_blobs_checked": blobs, "issues": sorted(set(errors))}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-draft", action="store_true", help="Local preparation only; not permission to publish")
    raise SystemExit(run(parser.parse_args().allow_draft))
