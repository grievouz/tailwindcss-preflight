#!/bin/bash
set -eu

# The old importer replaced the entire file on conflicts, discarding local
# standalone adaptations. Do not silently reintroduce Tailwind build syntax.
echo "The legacy importer is disabled to protect standalone CSS changes." >&2
echo "See docs/upstream.md for the history-preserving update procedure." >&2
exit 1
