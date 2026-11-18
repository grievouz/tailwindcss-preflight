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
After one-time npm trust setup, an approved version tag automatically runs checks,
creates the GitHub release and publishes to npm. There is no repository opt-in
variable or separate per-release environment reviewer approval.

1. Run the full existing + new test suite through the reusable test workflow.
2. Require a stable `vMAJOR.MINOR.PATCH` tag equal to package.json, a nonempty
   unique matching changelog section, matching pinned README CDN version, a clean
   tracked checkout, and the exact tagged commit reachable from `origin/main`.
   Only then build a tarball, inspect its exact allowlist and both licenses,
   install it offline with lifecycle scripts disabled, resolve/read its CSS entry,
   and generate `SHA256SUMS` and changelog-derived release notes.
3. Pass these assets through an immutable same-run Actions artifact. A separate
   `contents: write` job (no checkout/repository code execution) verifies the
   checksum, rechecks the remote tag against the triggering SHA, and creates the
   GitHub release and assets from the existing tag. It never creates/moves tags or
   overwrites an existing release.
4. After the GitHub release succeeds, the `npm` job automatically publishes the
   same checksum-verified tarball to npm `latest`, using OIDC and provenance,
   without lifecycle scripts or a stored npm token. It uses environment `npm`,
   checks the remote tag still matches the triggering SHA, and is the only job
   with `id-token: write`. No auth token or registry credential is configured by
   setup-node. Missing or incorrect npm trust fails publication; it does not
   silently skip npm or fall back to a long-lived credential.

The workflow uses GitHub-hosted runners, SHA-pinned actions, no caches, no
`pull_request_target`, no persisted checkout credential and no `secrets: inherit`.
Release permissions are scoped to their individual jobs; tests/package are read-only.
GitHub release creation precedes npm publication, so a GitHub release alone is not
proof npm/CDNs have updated; verify the npm job and registry version too.

## One-time owner setup for npm (before pushing a release tag)

Julia/Tammo owns account and repository settings; this PR does not change them.
Do not supply tokens in chat or reuse a Homebrew tap credential.

1. On GitHub, configure environment **`npm`** with a custom deployment policy
   allowing **tags only**, pattern **`v*`**, not branches. No required reviewer
   gate is needed: pushing the approved valid version tag authorizes publication.
   Restrict release-tag creation/updates to authorized maintainers with an
   appropriate ruleset where available; the environment policy limits eligible
   refs but does not itself restrict who can create tags.
2. In the npm settings of **`tailwindcss-preflight`**, add a GitHub Actions trusted
   publisher with user **`grievouz`**, repository **`tailwindcss-preflight`**,
   workflow filename **`release.yml`**, environment **`npm`**. If npm offers allowed
   actions, allow direct `npm publish`; no independent dist-tag management is needed.
   The publisher must match all fields exactly. npm does not validate them on save.
3. Confirm package ownership, repository URL, and that the publisher is actually
   saved after reloading settings. Trusted publishing requires GitHub-hosted
   runners, Node >=22.14.0 and npm >=11.5.1; the pinned runtime meets these requirements.
   There is no `NPM_TRUSTED_PUBLISHING_ENABLED` variable to set.

Setup status on 2026-11-19: GitHub's `npm` environment was independently read-back
verified with custom tag policy `v*` and no reviewer gate. Julia reports npm's
trusted-publisher save returned `Not Found`, and reload showed no saved publisher.
**npm trust remains blocked/unverified; resolve it before pushing `v1.2.0`.**
These external settings are not established by merging the PR.

Reference: [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).
Do not add an `NPM_TOKEN` fallback or test OIDC by publishing an unapproved version.
A read-only registry request cannot establish that private trusted-publisher
configuration is correct. Preparing or merging the PR is not release authorization.

## Publishing 1.2.0 (Julia/Tammo only after approval)

- Review and merge the preparation PR. Confirm exact merged main commit and green CI.
- Finish and verify the one-time npm trust setup above before creating a tag.
- Recheck npm and GitHub to ensure `1.2.0`/`v1.2.0` do not already exist. Run the
  full suite on a clean checkout of the approved main commit.
- Only with tag/release/npm publication authorization, create an annotated
  `v1.2.0` tag on that exact commit and push **only that tag**. This automatically
  triggers tests, packaging, a public GitHub release/assets and then npm publication.
  There is no additional per-release opt-in or deployment approval step.
  Preparing/merging the PR alone does not create a tag or release.
- Verify the GitHub release's tag/commit/assets, checksum, Actions result,
  npm `1.2.0` metadata/provenance/entry and CDN CSS.

If GitHub release succeeds but npm fails, fix the trust/policy issue and rerun
**only failed jobs**. Rerunning all jobs will intentionally fail rather than
replace an existing GitHub release. npm versions are immutable: if publication
already succeeded, verify it rather than republishing; never move/delete tags or
unpublish/overwrite a version to retry. Do not rewrite the release tag to retrigger
publication. No automatic release version bump or scheduler exists.
