#!/bin/bash
set -e

# --- CONFIGURATION ---
REMOTE_NAME="tailwind-upstream"
REMOTE_URL="https://github.com/tailwindlabs/tailwindcss.git"
SOURCE_PATH="packages/tailwindcss/preflight.css"
TARGET_FILE="preflight.css"
SYNC_TAG="tailwind-preflight-last-sync"

# --- SETUP ---
if ! git remote | grep -q "$REMOTE_NAME"; then
    echo " Adding remote $REMOTE_NAME..."
    git remote add "$REMOTE_NAME" "$REMOTE_URL"
fi

echo " Fetching latest history from Tailwind..."
git fetch -q "$REMOTE_NAME"

# --- DETERMINE COMMITS ---
if git rev-parse -q --verify "$SYNC_TAG" >/dev/null; then
    LAST_SYNCED_COMMIT=$(git rev-parse "$SYNC_TAG")
    echo "Last synced commit: ${LAST_SYNCED_COMMIT:0:7}"
    COMMITS=$(git log --reverse --pretty=format:"%H" "$LAST_SYNCED_COMMIT".."$REMOTE_NAME/main" -- "$SOURCE_PATH")
else
    echo " First run detected. Importing full history..."
    if [ -f "$TARGET_FILE" ]; then
        echo " Error: $TARGET_FILE already exists. Please delete it first."
        exit 1
    fi
    COMMITS=$(git log --reverse --pretty=format:"%H" "$REMOTE_NAME/main" -- "$SOURCE_PATH")
fi

if [ -z "$COMMITS" ]; then
    echo " No new updates found."
    exit 0
fi

# --- APPLY COMMITS ---
COUNT=$(echo "$COMMITS" | wc -l)
echo " Found $COUNT new commit(s) to apply."

for COMMIT in $COMMITS; do
    SHORT_HASH=${COMMIT:0:7}
    
    # Try to apply as a patch first (keeps diff context)
    git format-patch -1 "$COMMIT" --no-renames --stdout -- "$SOURCE_PATH" | \
    sed -e "s|^--- a/.*|--- a/$TARGET_FILE|" \
        -e "s|^+++ b/.*|+++ b/$TARGET_FILE|" | \
    git am --quiet --3way --committer-date-is-author-date 2>/dev/null || {
        
        echo "  Conflict applying commit $SHORT_HASH. Retrying with fallback..."
        git am --abort
        
        # --- FALLBACK METHOD ---
        # 1. Checkout the file content from that specific commit
        git checkout "$COMMIT" -- "$SOURCE_PATH"
        
        # 2. Move it to the target location
        if [ "$SOURCE_PATH" != "$TARGET_FILE" ]; then
            mkdir -p "$(dirname "$TARGET_FILE")"
            mv "$SOURCE_PATH" "$TARGET_FILE"
            # Cleanup source dir if it was created
            rmdir -p "$(dirname "$SOURCE_PATH")" 2>/dev/null || true
        fi
        
        # 3. FORCE STAGE the file (This was missing before!)
        git add "$TARGET_FILE"
        
        # 4. Commit using original author info
        AUTHOR_NAME=$(git log -1 --format='%an' "$COMMIT")
        AUTHOR_EMAIL=$(git log -1 --format='%ae' "$COMMIT")
        AUTHOR_DATE=$(git log -1 --format='%ad' "$COMMIT")
        MSG=$(git log -1 --format='%s' "$COMMIT")
        
        GIT_AUTHOR_NAME="$AUTHOR_NAME" \
        GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL" \
        GIT_AUTHOR_DATE="$AUTHOR_DATE" \
        git commit -m "$MSG" --date="$AUTHOR_DATE" --quiet
    }
    
    # Update tag
    git tag -f "$SYNC_TAG" "$COMMIT" >/dev/null
    echo "   Applied: $SHORT_HASH"
done

echo " Success! $COUNT commits applied."
