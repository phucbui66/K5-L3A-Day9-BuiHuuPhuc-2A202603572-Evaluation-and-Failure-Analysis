"""Check the byte-identical Day 8 snapshot; no access to the original repo needed."""
import hashlib
import json
from pathlib import Path


def main() -> int:
    manifest = json.loads(Path("config/lab8_snapshot.sha256.json").read_text(encoding="utf-8"))
    bad = [name for name, digest in manifest["files"].items()
           if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest]
    extra = {p.as_posix() for p in Path("lab8").rglob("*.py")} - manifest["files"].keys()
    for name in sorted(set(bad) | extra):
        print(f"FAIL changed/missing/extra Lab 8 file: {name}")
    ok = not bad and not extra
    print(f"Lab 8 snapshot: {len(manifest['files'])} files; {'PASS' if ok else 'FAIL'}; source {manifest['source_revision']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
