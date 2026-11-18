"""Dependency-free structural and real-browser checks for standalone Preflight."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VARIABLES = (
    "--default-font-family",
    "--default-font-feature-settings",
    "--default-font-variation-settings",
    "--default-mono-font-family",
    "--default-mono-font-feature-settings",
    "--default-mono-font-variation-settings",
)


class StandaloneCSS(unittest.TestCase):
    def test_only_native_function_substitution_differs_from_upstream(self):
        upstream = (ROOT / "tests/fixtures/upstream-preflight.css").read_text()
        standalone = (ROOT / "preflight.css").read_text()
        self.assertEqual(upstream.count("--theme("), 6)
        self.assertEqual(standalone, upstream.replace("--theme(", "var("))
        self.assertNotIn("--theme(", standalone)
        for variable in VARIABLES:
            self.assertIn(variable + ",", standalone)

    def test_upstream_fixes_are_retained(self):
        css = (ROOT / "preflight.css").read_text()
        self.assertIn(":-moz-focusring:where(:not(iframe))", css)
        self.assertIn("'Noto Sans'", css)
        self.assertNotIn("    system-ui,", css)
        self.assertNotIn("    ui-sans-serif,", css)

    def test_legacy_importer_refuses_without_mutating_checkout(self):
        # Run in an empty directory: no repository or remote access is needed.
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["bash", str(ROOT / "update-preflight.sh")], cwd=directory,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("docs/upstream.md", result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_browser_defaults_overrides_and_shadow_dom(self):
        browser = os.environ.get("CHROME_BIN") or next(
            (path for name in ("chromium", "chromium-browser", "google-chrome")
             if (path := shutil.which(name))), None
        )
        self.assertIsNotNone(browser, "Install Chromium or set CHROME_BIN; browser tests are required")
        css = (ROOT / "preflight.css").read_text()
        script = (ROOT / "tests/browser.js").read_text()
        with tempfile.TemporaryDirectory(prefix="preflight-test-") as directory:
            directory = Path(directory)
            page = directory / "test.html"
            page.write_text(
                "<!doctype html><meta charset='utf-8'><style>" + css + "</style>"
                "<body><code id='mono'>code</code><button id='button'>button</button>"
                "<pre id='result'>PENDING</pre><script>" + script + "</script>"
            )
            result = subprocess.run(
                [str(browser), "--headless", "--no-sandbox", "--disable-gpu",
                 "--disable-dev-shm-usage", "--disable-background-networking",
                 "--no-first-run", "--no-default-browser-check",
                 "--user-data-dir=" + str(directory / "profile"),
                 "--dump-dom", page.as_uri()],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('id="result">PASS:', result.stdout, result.stdout + result.stderr)
            print(result.stdout.split('id="result">', 1)[1].split('</pre>', 1)[0])


if __name__ == "__main__":
    unittest.main()
