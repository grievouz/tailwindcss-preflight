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
The `1.2.0` preparation realigns package/tag/changelog for future releases.

## Tag-driven pipeline

`.github/workflows/release.yml` runs only on pushed `v*` tags in
`grievouz/tailwindcss-preflight`; it is not run by PRs or ordinary branch pushes.
After one-time npm trust setup, an approved version tag automatically runs checks,
creates the GitHub release and publishes to npm. There is no repository opt-in
variable or separate per-release environment reviewer approval.

1. Run the full existing + new test suite through the reusable test workflow.
2. Require a stable `vMAJOR.MINOR.PATCH` tag equal to package.json, a nonempty
   unique matching changelog section, the auto-updating README CDN URL, a clean
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
verified with custom tag policy `v*` and no reviewer gate. After owner passkey
verification, npm's publisher was saved and verified after a full reload with
`grievouz/tailwindcss-preflight`, `release.yml`, environment `npm`, and direct
`npm publish` permitted. npm reports **Pending validation** until a first successful
publication. A saved connection alone does not prove OIDC publication works.

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

## One-time recovery of npm 1.2.0

Release run [44423916921](https://github.com/grievouz/tailwindcss-preflight/actions/runs/44423916921)
passed tests and packaging, created GitHub `v1.2.0` and both assets, then failed
before npm authentication: `npm publish dist/*.tgz` was parsed as a GitHub
shorthand. The corrected command uses an explicit local path, `./dist/*.tgz`.
An offline, scripts-disabled npm publish **dry run** is now a regression test;
it proves local-path handling, not npm authorization.

Do not move/delete the existing tag, rebuild its package, or rerun all jobs.
Rerunning the failed job of that original run still uses the old workflow code.
The manual `Release` workflow on **main** provides a deliberately fixed 1.2.0
recovery path, without a user-supplied ref, version or checksum:

1. After owner merge/recovery approval, verify npm `1.2.0` is still absent.
2. Temporarily add an exact **branch `main`** deployment policy to environment
   `npm`, retaining the existing tag-only `v*` policy. This exception requires
   explicit owner approval; it is not part of the normal tagged-release policy.
3. Dispatch `release.yml` on `main`. It runs tests on the recovery workflow source,
   downloads immutable original Actions artifact `14483930251` from run
   `44423916921`. It checks original run identity and successful tests/package jobs,
   the recorded artifact ZIP digest/manifest, the tarball SHA-256,
   original tag commit, main ancestry, file allowlist and every packaged file byte
   against the original tagged source. It neither rebuilds nor creates a release.
4. The existing least-privilege npm job rechecks the original tag, requires an npm
   HTTP 404 for `1.2.0` immediately before publication, requires exactly one local
   archive, and publishes
   exactly that verified artifact via OIDC. Provenance identifies the recovery
   workflow's **main commit**, not the original release-tag commit. The byte checks
   establish the link to the original source; do not describe these as identical refs.
5. Remove **only the temporary main branch policy**, even if publication fails,
   and verify `npm` is tag-only `v*` again. Verify npm version, provenance, artifact
   integrity, offline entry points and both versioned/latest CDN CSS before declaring
   the release complete. Never republish an already-existing npm version.

This one-time dispatch does not fix/replace the failed historical Actions run;
normal future release tags use the corrected local tarball path automatically.
