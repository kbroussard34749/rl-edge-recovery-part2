"""Build a fresh source-checkout ZIP and an external byte-identity manifest.

The candidate includes tracked working-tree files and named release records.
Pending revisions are identified against HEAD; packaging does not approve them,
commit, publish, change access, or replace an existing distribution.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXTRA_FILES = ("scripts/package_release.py", "docs/documentation_review.md", "docs/release_validation.md", "tests/test_release_verification.py")


def build(output):
    """Package checkout files with fixed archive metadata and no private extras."""
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("Place the candidate outside the repository")
    manifest_path = output.with_suffix(".manifest.json")
    if output.exists() or manifest_path.exists():
        raise ValueError("Choose a fresh candidate path; existing packages are preserved")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    names = sorted(set(filter(None, tracked)) | set(EXTRA_FILES))
    excluded = (".git/", ".idea/", "__pycache__/")
    names = [name for name in names if name != "AGENTS.md" and not name.startswith(excluded)
             and "__pycache__" not in Path(name).parts and not name.endswith((".pyc", ".DS_Store"))]
    entries = []
    for name in names:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Expected an ordinary checkout file: {name}")
        data = path.read_bytes()
        entries.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    pending = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for entry in entries:
            data = (ROOT / entry["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError(f"Source changed during packaging: {entry['path']}")
            info = zipfile.ZipInfo("rl-edge-recovery/" + entry["path"], (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    result = dict(package=output.name, base_commit=head, pending_checkout_changes=pending,
                  file_count=len(entries), files=entries,
                  package_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  bytes=output.stat().st_size,
                  excludes="Git metadata, IDE settings, local instructions, caches, adjacent course files and editable slides")
    manifest_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.output)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps({k: result[k] for k in ("package", "base_commit", "file_count", "bytes", "package_sha256")}, indent=2))
