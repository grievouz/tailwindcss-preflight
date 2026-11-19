"""Recover the immutable original 1.2.0 artifact, never rebuild or change its tag."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

from package_check import EXPECTED_FILES

TAG = "v1.2.0"
COMMIT = "73c53a0511de520082e4e5924dd3b63929135936"
SHA256 = "278abbbb61cb1a2584147dcbcfd483b9bc373cd431147e3eb5e2c79a92ab0f5f"
FILENAME = "tailwindcss-preflight-1.2.0.tgz"
ARTIFACT_ID = 14483930251
ARTIFACT_SHA256 = "908fb9d81072669ec094f7a7b07749547be3d9ab0af8b8cd4661f63ebd2cbfb0"
RUN_ID = 44423916921
REPO = "grievouz/tailwindcss-preflight"
ROOT = Path(__file__).resolve().parents[1]


def verify_artifact(destination, expected_files):
    destination = Path(destination)
    tarball = destination / FILENAME
    if sorted(p.name for p in destination.glob("*.tgz")) != [FILENAME]:
        raise ValueError("Expected exactly the original release tarball")
    if hashlib.sha256(tarball.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Existing release tarball does not match the recorded SHA-256")
    if (destination / "SHA256SUMS").read_text() != f"{SHA256}  {FILENAME}\n":
        raise ValueError("Release checksum file does not match the recorded artifact")
    with tarfile.open(tarball) as archive:
        members = archive.getmembers()
        if len(members) != len(EXPECTED_FILES) or {m.name for m in members} != EXPECTED_FILES:
            raise ValueError("Unexpected release package contents")
        for member in members:
            if not member.isfile() or archive.extractfile(member).read() != expected_files[member.name]:
                raise ValueError("Release file differs from original tagged source: " + member.name)


def download_original(destination):
    def api(path):
        return subprocess.check_output(["gh", "api", f"repos/{REPO}/{path}"])
    metadata = json.loads(api(f"actions/artifacts/{ARTIFACT_ID}"))
    if (metadata["id"] != ARTIFACT_ID or metadata["name"] != "release-package"
            or metadata["expired"] or metadata["digest"] != "sha256:" + ARTIFACT_SHA256
            or metadata["workflow_run"]["id"] != RUN_ID
            or metadata["workflow_run"]["head_sha"] != COMMIT):
        raise ValueError("Unexpected original artifact identity")
    run = json.loads(api(f"actions/runs/{RUN_ID}"))
    if (run["head_sha"] != COMMIT or run["event"] != "push" or run["head_branch"] != TAG
            or run["path"] != ".github/workflows/release.yml"
            or run["repository"]["full_name"] != REPO):
        raise ValueError("Unexpected original release run identity")
    jobs = json.loads(api(f"actions/runs/{RUN_ID}/jobs"))
    if not all(any(j["name"] == name and j["conclusion"] == "success" for j in jobs["jobs"])
               for name in ("test / test", "package")):
        raise ValueError("Original release tests and package job must have succeeded")
    archive = api(f"actions/artifacts/{ARTIFACT_ID}/zip")
    if hashlib.sha256(archive).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("Original immutable artifact ZIP digest mismatch")
    destination = Path(destination)
    destination.mkdir(exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        expected = {FILENAME, "SHA256SUMS", "release-notes.md"}
        if len(z.infolist()) != len(expected) or set(z.namelist()) != expected:
            raise ValueError("Unexpected artifact ZIP manifest")
        # Write only these fixed regular output names; never extract archive paths.
        for name in expected:
            (destination / name).write_bytes(z.read(name))


def main():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)
    if git("rev-parse", "--verify", f"refs/tags/{TAG}^{{commit}}").decode().strip() != COMMIT:
        raise ValueError("Existing release tag moved")
    subprocess.run(["git", "merge-base", "--is-ancestor", COMMIT, "origin/main"], cwd=ROOT, check=True)
    expected = {name: git("show", COMMIT + ":" + name.removeprefix("package/")) for name in EXPECTED_FILES}
    download_original(ROOT / "dist")
    verify_artifact(ROOT / "dist", expected)
    print("Immutable original run artifact verified against original tagged source:", TAG, COMMIT)


if __name__ == "__main__":
    main()
