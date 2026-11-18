"""Build and inspect the exact npm tarball; install offline without lifecycle scripts."""
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

EXPECTED_FILES = {
    "package/package.json", "package/preflight.css", "package/README.md",
    "package/LICENSE.txt", "package/LICENSE-preflight.txt", "package/CHANGELOG.md",
}


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True).stdout


def pack_and_check(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((root / "package.json").read_text())
    assert metadata["name"] == "tailwindcss-preflight"
    assert re.fullmatch(r"\d+\.\d+\.\d+", metadata["version"])
    assert metadata["main"] == metadata["style"] == "preflight.css"
    assert metadata["license"] == "MIT"
    assert metadata["repository"]["url"] == "git+https://github.com/grievouz/tailwindcss-preflight.git"
    for field in ("scripts", "dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "bundledDependencies"):
        assert not metadata.get(field), field
    with tempfile.TemporaryDirectory(prefix="preflight-pack-") as work:
        work = Path(work)
        cache = str(work / "cache")
        packed = json.loads(run([
            "npm", "pack", "--ignore-scripts", "--json", "--cache", cache,
            "--pack-destination", str(destination),
        ], root))
        assert len(packed) == 1
        filename = f"tailwindcss-preflight-{metadata['version']}.tgz"
        assert packed[0]["filename"] == filename
        tarball = destination / filename
        # Inspect regular files without extracting untrusted tar paths or links.
        with tarfile.open(tarball) as archive:
            members = archive.getmembers()
            assert {entry.name for entry in members} == EXPECTED_FILES
            assert len(members) == len(EXPECTED_FILES)
            for entry in members:
                assert entry.isfile(), entry.name
                assert archive.extractfile(entry).read() == (root / entry.name.removeprefix("package/")).read_bytes(), entry.name
        consumer = work / "consumer"
        consumer.mkdir()
        (consumer / "package.json").write_text('{"private":true}')
        run([
            "npm", "install", "--offline", "--ignore-scripts", "--no-audit", "--no-fund",
            "--package-lock=false", "--cache", cache, str(tarball),
        ], consumer)
        # Resolve/read CSS; deliberately do not execute it as JavaScript.
        paths = json.loads(run([
            "node", "-e", "console.log(JSON.stringify([require.resolve('tailwindcss-preflight'),require.resolve('tailwindcss-preflight/preflight.css')]))",
        ], consumer))
        assert paths[0] == paths[1]
        assert Path(paths[0]).read_bytes() == (root / "preflight.css").read_bytes()
    return tarball
