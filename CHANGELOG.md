# Changelog

## 1.2.0

- Fix standalone browser CSS: replace six Tailwind-only `--theme()` calls with
  native `var()` custom properties and unchanged fallback values. Fixes #1.
- Include upstream Firefox iframe focus-outline and Japanese Windows font-stack
  fixes, preserving upstream authorship/history. See [provenance](docs/upstream.md).
- Include both MIT license files in the npm package and retain the bare package
  entry (`main`/`style`) plus explicit `preflight.css` import for CSS-aware tooling.
- Add package-content, offline install/entry-point and release-metadata checks to
  the existing structural and Chromium regression suite.
- Add validated, tag-driven GitHub releases with the tested npm tarball and SHA-256
  checksum. npm trusted publishing is separately opt-in and requires owner setup.

No Tailwind dependency, CSS compilation or new runtime dependency is introduced.

## Historical versions

npm previously published `1.0.1` and `1.1.1`. The existing GitHub `v1.1.1` tag
points to a commit whose package metadata says `1.0.1`; this historical mismatch
is left intact. Starting with `1.2.0`, releases require tag/package/changelog
version agreement. Existing versions and tags are never rewritten.
