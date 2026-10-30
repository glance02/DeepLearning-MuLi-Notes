"""Fast-forward main, build and validate, then atomically publish the website."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid


def run(*command, cwd=None):
    return subprocess.run(command, cwd=cwd, check=True, text=True)


def atomic_link(link: Path, target: Path):
    temporary = link.parent / f".{link.name}-{uuid.uuid4().hex}"
    try:
        temporary.symlink_to(target, target_is_directory=True)
        os.replace(temporary, link)
    finally:
        temporary.unlink(missing_ok=True)


def publish(base: Path, repository: Path, revision: str, python: str = sys.executable):
    releases = (base / "releases").resolve()
    releases.mkdir(parents=True, exist_ok=True)
    prefix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + revision[:12] + "-"
    candidate = Path(tempfile.mkdtemp(prefix=prefix, dir=releases)).resolve()
    current = base / "current"
    try:
        run(python, str(repository / "scripts/build_site.py"), "--output", str(candidate), "--revision", revision)
        # mkdtemp defaults to 0700; Nginx must be able to traverse the release.
        candidate.chmod(0o755)
    except BaseException:
        # Only remove the newly created build directory, never the live release.
        if candidate.parent == releases:
            shutil.rmtree(candidate)
        raise
    previous = current.resolve() if current.is_symlink() else None
    if previous:
        atomic_link(base / "previous", previous)
    atomic_link(current, candidate)
    # Keep the live version and its immediate predecessor only.
    keep = {candidate, previous}
    for release in releases.iterdir():
        if release.is_dir() and not release.is_symlink() and release.resolve().parent == releases and release.resolve() not in keep:
            shutil.rmtree(release)
    print(f"Published {revision} -> {candidate}", flush=True)
    return candidate


def update(base: Path, repository: Path, force: bool = False, pull: bool = True):
    if pull:
        dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=repository, text=True)
        if dirty.strip():
            raise RuntimeError("Server checkout has local changes; refusing to overwrite them")
        run("git", "pull", "--ff-only", "origin", "main", cwd=repository)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip()
    manifest = base / "current/build.json"
    if not force and manifest.is_file() and json.loads(manifest.read_text(encoding="utf-8"))["revision"] == revision:
        print(f"No changes ({revision}); build skipped", flush=True)
        return None
    run(sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", str(repository / "deploy/requirements.txt"))
    return publish(base, repository, revision)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path("/srv/deep-learning"))
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--force", action="store_true", help="Rebuild even when the current commit is already published")
    actions.add_argument("--rollback", action="store_true", help="Swap the current and previous published versions")
    args = parser.parse_args()
    base = args.base.resolve()
    # systemd serializes service starts; flock also covers direct CLI invocations.
    import fcntl
    with (base / ".update.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.rollback:
            previous = base / "previous"
            if not previous.is_symlink() or not previous.is_dir():
                raise RuntimeError("No previous release is available")
            old, restored = (base / "current").resolve(), previous.resolve()
            atomic_link(base / "current", restored)
            atomic_link(previous, old)
            print(f"Restored {restored}", flush=True)
        else:
            update(base, base / "repo", force=args.force)


if __name__ == "__main__":
    main()
