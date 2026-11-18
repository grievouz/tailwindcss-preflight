"""Exercise the workflow's local tarball syntax without registry publication."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_check import pack_and_check
from recover_release import verify_artifact, FILENAME, SHA256


class PublishArtifact(unittest.TestCase):
    def test_workflow_publish_uses_explicit_local_path_and_dry_run_accepts_it(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn('set -- ./dist/*.tgz', workflow)
        self.assertIn('test "$#" -eq 1', workflow)
        self.assertIn('test -f "$1"', workflow)
        self.assertIn('npm publish "$1" --access public --provenance --ignore-scripts --tag latest --registry https://registry.npmjs.org', workflow)
        with tempfile.TemporaryDirectory(prefix="preflight-publish-") as directory:
            directory = Path(directory)
            tarball = pack_and_check(ROOT, directory / "dist")
            # Shell expands the wildcard to this explicit ./dist path. Disable provenance
            # for this local, offline dry run; the actual OIDC job keeps it enabled.
            result = subprocess.run([
                "npm", "publish", "./dist/" + tarball.name, "--dry-run", "--offline",
                "--json", "--access", "public", "--provenance=false", "--ignore-scripts",
                "--tag", "latest", "--cache", str(directory / "cache"),
                "--registry", "https://registry.npmjs.org",
            ], cwd=directory, text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)["tailwindcss-preflight"]["name"], "tailwindcss-preflight")

    def test_recovery_rejects_unrecorded_tarball(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / FILENAME).write_bytes(b"not the released tarball")
            (directory / "SHA256SUMS").write_text(f"{SHA256}  {FILENAME}\n")
            with self.assertRaisesRegex(ValueError, "recorded SHA-256"):
                verify_artifact(directory, {})

    def test_recovery_rejects_extra_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / FILENAME).write_bytes(b"original")
            (directory / "other.tgz").write_bytes(b"extra")
            with self.assertRaisesRegex(ValueError, "exactly"):
                verify_artifact(directory, {})
