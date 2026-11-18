"""Exercise real npm pack and offline consumer installation, with no registry/auth."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_check import pack_and_check


class Package(unittest.TestCase):
    def test_pack_contents_licenses_and_offline_package_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            tarball = pack_and_check(ROOT, directory)
            self.assertTrue(tarball.is_file())
            print("Package smoke PASS:", tarball.name)
