"""Fail closed on tag/version/main drift, then build the verified release assets."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from package_check import pack_and_check

ROOT = Path(__file__).resolve().parents[1]


def release_notes(root, tag):
    root = Path(root)
    if not re.fullmatch(r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", tag):
        raise ValueError("Only stable vMAJOR.MINOR.PATCH tags are supported")
    version = json.loads((root / "package.json").read_text())["version"]
    if tag != "v" + version:
        raise ValueError("Tag must exactly match package.json version")
    changelog = (root / "CHANGELOG.md").read_text()
    heading = "## " + version + "\n"
    if changelog.count(heading) != 1:
        raise ValueError("Changelog must contain exactly one matching version section")
    notes = changelog.split(heading, 1)[1].split("\n## ", 1)[0].strip()
    if not notes:
        raise ValueError("Release notes must not be empty")
    if f"tailwindcss-preflight@{version}/preflight.css" not in (root / "README.md").read_text():
        raise ValueError("README CDN version must match package version")
    return notes + "\n"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    args = parser.parse_args()
    notes = release_notes(ROOT, args.tag)
    commit = git("rev-parse", "HEAD")
    if git("rev-parse", "--verify", f"refs/tags/{args.tag}^{{commit}}") != commit:
        raise ValueError("Checkout must be the exact release tag commit")
    subprocess.run(["git", "merge-base", "--is-ancestor", commit, "origin/main"], cwd=ROOT, check=True)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Tracked checkout must be clean")
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Refusing to reuse a non-empty dist directory")
    tarball = pack_and_check(ROOT, destination)
    digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
    (destination / "SHA256SUMS").write_text(f"{digest}  {tarball.name}\n")
    (destination / "release-notes.md").write_text(notes + (
        "\n## Distribution\n\n"
        "Attached is the tested npm tarball with its SHA-256 checksum. "
        "A GitHub release does not by itself publish to npm/CDNs. "
        "Check npm for this version before using the pinned CDN URL.\n"
    ))
    print("Release assets verified for", args.tag, "at", commit)


if __name__ == "__main__":
    main()
