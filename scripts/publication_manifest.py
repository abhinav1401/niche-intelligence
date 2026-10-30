"""Record the exact local files proposed for publication; performs no remote action."""

import hashlib
import json

from security_check import IGNORED, ROOT

files = {}
for path in sorted(ROOT.rglob("*")):
    relative = path.relative_to(ROOT)
    if any(part in IGNORED for part in relative.parts) or relative.as_posix() == "PUBLICATION_MANIFEST.json":
        continue
    if path.is_symlink():
        raise SystemExit("Refusing a symbolic link in publication contents")
    if path.is_file():
        files[relative.as_posix()] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
output = {"repository": "https://github.com/abhinav1401/niche-intelligence", "branch": "main", "entrypoint": "app.py",
          "published": False, "note": "Local review manifest, not a deployed URL or publication approval. Excludes itself and local Git/cache/environment directories.", "files": files}
(ROOT / "PUBLICATION_MANIFEST.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
print(f"Publication manifest records {len(files)} files; no remote operation performed.")
