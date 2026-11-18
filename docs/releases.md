# Releases

## Existing CI versus this release setup

The repository already had `.github/workflows/test.yml`: Python structural tests
and Chromium defaults, six overrides, form inheritance and shadow-DOM assertions.
That coverage is retained. This change adds offline npm pack/install/entry-point,
license/content and release-metadata checks, plus SHA-pinned Node-24-based actions
(removing checkout's Node 20 deprecation warning).

There are no npm dependencies, install lifecycle scripts or CSS build step.
`python3 -m unittest discover -s tests -v` requires Python 3.9+, Chrome/Chromium
(or `CHROME_BIN`), Node.js and npm. CI pins Node 24.22.3 (bundled npm 11.19.1).
`main` and `style` point to CSS for CSS-aware bundlers; plain Node.js cannot execute
CSS. The smoke test resolves both bare and explicit CSS entries and reads the
installed bytes; it does not pretend Node can execute CSS.

## Historical drift (do not rewrite)

Read-only inspection on 2026-11-19 found npm `latest` = `1.1.1`, versions `1.0.1`
and `1.1.1`, and a single GitHub tag/release `v1.1.1` at
`e032fdf0158565e247169966bc484a036331b07a`. npm's `1.1.1` gitHead matches that
commit, but its committed package.json says `1.0.1`. Existing main subsequently
said `1.1.1`. No old tag, GitHub release or npm version is changed by this PR.
The `1.2.0` preparation realigns package/tag/changelog/README for future releases.

## Tag-driven pipeline

`.github/workflows/release.yml` runs only on pushed `v*` tags in
`grievouz/tailwindcss-preflight`; it is not run by PRs or ordinary branch pushes.

1. Run the full existing + new test suite through the reusable test workflow.
2. Require a stable `vMAJOR.MINOR.PATCH` tag equal to package.json, a nonempty
   unique matching changelog section, matching pinned README CDN version, a clean
   tracked checkout, and the exact tagged commit reachable from `origin/main`.
   Only then build a tarball, inspect its exact allowlist and both licenses,
   install it offline with lifecycle scripts disabled, resolve/read its CSS entry,
   and generate `SHA256SUMS` and changelog-derived release notes.
3. Pass these assets through an immutable same-run Actions artifact. A separate
   `contents: write` job (no checkout/repository code execution) verifies the
   checksum, rechecks the remote tag against the triggering SHA, and creates the GitHub release and assets from the existing tag.
   It never creates/moves tags or overwrites an existing release.
4. **npm is OFF by default.** Only when the repository variable
   `NPM_TRUSTED_PUBLISHING_ENABLED` equals exactly `true` does the npm job become
   eligible. It additionally uses the `npm` environment. Configure its protection
   rules **before** opting in: merely naming an environment does not protect it.
   It publishes the same checksum-verified tarball, using OIDC and provenance,
   without lifecycle scripts or a stored npm token. Only that job has
   `id-token: write`. No auth token or registry credential is configured by setup-node.

The workflow uses GitHub-hosted runners, SHA-pinned actions, no caches, no
`pull_request_target`, no persisted checkout credential and no `secrets: inherit`.
Release permissions are scoped to their individual jobs; tests/package are read-only.

## Owner setup for npm (separate approval required)

No npm authentication, publisher settings or repository settings are assumed or
changed by this PR. Julia/Tammo owns these steps; do not supply tokens in chat.

1. On GitHub, configure environment **`npm`** with required owner/reviewer approval
   (and prevent self-review where available), restricting deployment to intended
   release tags. Protect release-tag creation/updates with an appropriate ruleset.
2. In the npm settings of **`tailwindcss-preflight`**, add a GitHub Actions trusted
   publisher with user **`grievouz`**, repository **`tailwindcss-preflight`**,
   workflow filename **`release.yml`**, environment **`npm`**. If npm offers allowed
   actions, allow direct `npm publish`; no independent dist-tag management is needed.
   The publisher must match all fields exactly. npm does not validate them on save.
3. Confirm package ownership, repository URL and GitHub plan/environment protection
   availability. Trusted publishing requires GitHub-hosted runners, Node >=22.14.0
   and npm >=11.5.1; the pinned runtime meets these requirements.
4. Only after setup/review, set repository variable
   **`NPM_TRUSTED_PUBLISHING_ENABLED=true`**. Never opt in before environment
   protections and npm trust are ready. This PR does not set that variable.

Reference: [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).
Do not add an `NPM_TOKEN` fallback or test OIDC by publishing an unapproved version.
A read-only registry request cannot establish that private trusted-publisher
configuration is correct. Actual publication is a distinct owner-approved step.

## Publishing 1.2.0 (Julia/Tammo only after approval)

- Review and merge the preparation PR. Confirm exact merged main commit and green CI.
- Decide whether to publish npm now. Configure/approve the separate npm setup above
  first if desired. Without opt-in, only the GitHub release/assets are created;
  **npm/CDN users will not receive 1.2.0**.
- Recheck npm and GitHub to ensure `1.2.0`/`v1.2.0` do not already exist. Run the
  full suite on a clean checkout of the approved main commit.
- Only with tag/release authorization, create an annotated `v1.2.0` tag on that
  exact commit and push **only that tag**. Pushing it triggers a public GitHub
  release after checks pass, and, if explicitly opted in, the npm approval job.
  Preparing/merging the PR alone does not create a tag or release.
- Review the package/permissions and approve the environment deployment only with
  npm publication authorization. Verify the GitHub release's tag/commit/assets,
  checksum, Actions result, npm `1.2.0` metadata/provenance/entry and CDN CSS.

If GitHub release succeeds but npm fails, fix the trust/protection issue and rerun
**only failed jobs**. Rerunning all jobs will intentionally fail rather than
replace an existing GitHub release. npm versions are immutable: if publication
already succeeded, verify it rather than republishing; never move/delete tags or
unpublish/overwrite a version to retry. If npm was deliberately skipped, a later
publication needs a separately reviewed/approved recovery step—do not rewrite the
release tag to retrigger it. No automatic release version bump or scheduler exists.
