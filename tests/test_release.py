"""Release metadata validation never creates tags/releases or contacts registries."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_release import release_notes


class ReleaseMetadata(unittest.TestCase):
    def test_current_metadata_matches_stable_tag(self):
        version = json.loads((ROOT / "package.json").read_text())["version"]
        self.assertTrue(release_notes(ROOT, "v" + version).strip())

    def test_rejects_mismatched_or_unsupported_tags(self):
        for tag in ("v1.1.1", "1.2.0", "v1.2.0-beta.1", "v01.2.0", "v1.2.0\n", "v1.2.0; echo unsafe"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release_notes(ROOT, tag)

    def test_rejects_missing_empty_or_duplicate_changelog_and_stale_cdn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text('{"version":"1.2.0"}')
            (root / "README.md").write_text("https://cdn.jsdelivr.net/npm/tailwindcss-preflight@latest/preflight.css")
            for changelog in ("## 1.1.1\nold", "## 1.2.0\n", "## 1.2.0\none\n## 1.2.0\ntwo"):
                (root / "CHANGELOG.md").write_text(changelog)
                with self.subTest(changelog=changelog), self.assertRaises(ValueError):
                    release_notes(root, "v1.2.0")
            (root / "CHANGELOG.md").write_text("## 1.2.0\nValid notes\n## 1.1.1\nOld")
            self.assertEqual(release_notes(root, "v1.2.0"), "Valid notes\n")
            (root / "README.md").write_text("tailwindcss-preflight@1.1.1/preflight.css")
            with self.assertRaises(ValueError):
                release_notes(root, "v1.2.0")

    def test_latest_cdn_url_survives_future_version_bumps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("https://cdn.jsdelivr.net/npm/tailwindcss-preflight@latest/preflight.css")
            for version in ("1.2.1", "2.0.0"):
                (root / "package.json").write_text(json.dumps({"version": version}))
                (root / "CHANGELOG.md").write_text(f"## {version}\nValid notes\n")
                with self.subTest(version=version):
                    self.assertEqual(release_notes(root, "v" + version), "Valid notes\n")
