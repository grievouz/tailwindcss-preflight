# Upstream provenance and updates

Source: [Tailwind CSS Preflight](https://github.com/tailwindlabs/tailwindcss/blob/d49dd3ea67605b1a77f85b506b2b0f6cbe7f685d/packages/tailwindcss/preflight.css).

Checked against upstream `main` at `d49dd3ea67605b1a77f85b506b2b0f6cbe7f685d`
on 2026-11-18. The last included file-changing upstream commit is
`e48c5e80473c25fe5a27fe267fbaf4f6512424a3`.

The earlier import ended at upstream
`88b9f15b65588a87c5b6b13316530b4aecbc1b0b` (local `3492596`). Its CSS was
byte-for-byte identical to our pre-update file. These two subsequent file commits
were replayed, in order, with `git am` and only the Preflight path selected:

| Upstream | Local | Change |
| --- | --- | --- |
| [b53fa096](https://github.com/tailwindlabs/tailwindcss/commit/b53fa096c92d830fc64b7cf69581496242583446) | `29da33a` | Respect Firefox's native iframe focus outline |
| [e48c5e80](https://github.com/tailwindlabs/tailwindcss/commit/e48c5e80473c25fe5a27fe267fbaf4f6512424a3) | `a5c604e` | Correct font fallback on Windows with Japanese locale |

Original authors, author dates and full commit messages (including existing
co-author trailers) are retained. Commit hashes change because the parent history
and file path differ; other Tailwind files are intentionally not imported.
Before the standalone adaptation, our CSS was byte-for-byte identical to the
pinned upstream source above.

## Standalone adaptation

`tests/fixtures/upstream-preflight.css` is the unmodified pinned upstream file.
The production `preflight.css` differs only by replacing the six `--theme(`
function names with native `var(`. Fallback values and all other rules are kept.
Tests enforce this exact relationship and check browser behavior without Tailwind.

## Updating again

The old `update-preflight.sh` is deliberately disabled: its conflict fallback
replaced the entire file, silently discarding local adaptations. Its last-sync
marker was also an unpublished local tag, so fresh clones could not resume it.
Until a safe automated importer is added, use this explicit procedure:

1. Start on a clean working branch. Fetch/read upstream without pushing to it.
2. List commits affecting `packages/tailwindcss/preflight.css` after the last
   included upstream commit above, in chronological order. Inspect every patch.
3. Export each upstream commit using `git format-patch -1 --stdout <sha> --
   packages/tailwindcss/preflight.css`. Remap **only** the patch's file paths to
   `preflight.css`, retaining the author, author date and full message. Replay with
   `git am`; do not squash the upstream commits together.
4. If a patch conflicts with our native CSS adaptations, stop and inspect it.
   Resolve deliberately, then use `git am --continue`, or abort. Never fall back
   to overwriting production CSS with a raw upstream snapshot.
5. Update the raw test fixture from the pinned final upstream file, update this
   provenance record and make any required standalone adaptation in a **separate**
   local commit. Inspect new Tailwind-only syntax; do not assume substitution
   remains sufficient forever.
6. Run `python3 -m unittest discover -s tests -v`, inspect the full diff, and push
   only the working branch in this repository. Merging and publishing are separate
   maintainer decisions.

The suite requires Python 3.9+ and Chromium/Chrome (or `CHROME_BIN` pointing to it).
There are no Python/npm package dependencies and no Tailwind compilation step.
The full suite also requires Node.js and npm for offline package smoke tests. Browser
checks currently cover Chromium, not Firefox/Safari or Japanese Windows rendering.
