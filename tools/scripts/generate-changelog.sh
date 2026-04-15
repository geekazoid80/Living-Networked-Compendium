#!/usr/bin/env bash
# generate-changelog.sh — Generate a change sheet between two handout versions
#
# Compares the MANIFEST.md files from two consecutive handout versions to produce
# a human-readable summary of: modules added, modules removed, modules modified.
#
# Usage:
#   ./tools/scripts/generate-changelog.sh [old_version] [new_version]
#
#   Examples:
#     ./tools/scripts/generate-changelog.sh v001 v002
#     ./tools/scripts/generate-changelog.sh           # auto-detects last two versions
#
# Output:
#   handouts/versions/vNNN-DATE/CHANGES-vNNN-vs-vMMM.md

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

VERSIONS_DIR="handouts/versions"

# ── Resolve version directories ───────────────────────────────────────────────

if [[ $# -ge 2 ]]; then
    OLD_TAG="$1"
    NEW_TAG="$2"
    OLD_DIR=$(ls -d "${VERSIONS_DIR}/${OLD_TAG}-"* 2>/dev/null | head -1)
    NEW_DIR=$(ls -d "${VERSIONS_DIR}/${NEW_TAG}-"* 2>/dev/null | head -1)
else
    # Auto-detect last two versions
    mapfile -t VDIRS < <(ls -d "${VERSIONS_DIR}"/v[0-9][0-9][0-9]-* 2>/dev/null | sort)
    if [[ ${#VDIRS[@]} -lt 2 ]]; then
        echo "Need at least 2 versions in ${VERSIONS_DIR}/ to generate a changelog."
        echo "Run build-pdf.sh at least twice first."
        exit 1
    fi
    OLD_DIR="${VDIRS[-2]}"
    NEW_DIR="${VDIRS[-1]}"
    OLD_TAG=$(basename "$OLD_DIR" | grep -oP '^v[0-9]+')
    NEW_TAG=$(basename "$NEW_DIR" | grep -oP '^v[0-9]+')
fi

if [[ -z "${OLD_DIR:-}" || ! -d "$OLD_DIR" ]]; then
    echo "ERROR: Cannot find version directory for '${OLD_TAG}'"
    exit 1
fi
if [[ -z "${NEW_DIR:-}" || ! -d "$NEW_DIR" ]]; then
    echo "ERROR: Cannot find version directory for '${NEW_TAG}'"
    exit 1
fi

OLD_MANIFEST="${OLD_DIR}/MANIFEST.md"
NEW_MANIFEST="${NEW_DIR}/MANIFEST.md"
DATE=$(date +%Y-%m-%d)
OUTFILE="${NEW_DIR}/CHANGES-${NEW_TAG}-vs-${OLD_TAG}.md"

echo "==> Generating changelog: ${NEW_TAG} vs ${OLD_TAG}"

# ── Extract module lists from manifests ───────────────────────────────────────

extract_modules() {
    local manifest="$1"
    # Parse table rows: | MODULE_ID | Title | File |
    grep -P '^\| [A-Z]' "$manifest" 2>/dev/null | \
        awk -F'|' '{gsub(/^ +| +$/, "", $2); gsub(/^ +| +$/, "", $3); print $2 "\t" $3}' || true
}

OLD_MODULES=$(extract_modules "$OLD_MANIFEST")
NEW_MODULES=$(extract_modules "$NEW_MANIFEST")

# ── Compute diff ──────────────────────────────────────────────────────────────

# Get module IDs in each version
OLD_IDS=$(echo "$OLD_MODULES" | awk -F'\t' '{print $1}' | sort)
NEW_IDS=$(echo "$NEW_MODULES" | awk -F'\t' '{print $1}' | sort)

ADDED=$(comm -13 <(echo "$OLD_IDS") <(echo "$NEW_IDS"))
REMOVED=$(comm -23 <(echo "$OLD_IDS") <(echo "$NEW_IDS"))
COMMON=$(comm -12 <(echo "$OLD_IDS") <(echo "$NEW_IDS"))

# For common modules, check if the source file has changed (git diff)
MODIFIED=""
if git rev-parse --git-dir &>/dev/null; then
    while IFS= read -r MOD_ID; do
        [[ -z "$MOD_ID" ]] && continue
        FILE=$(echo "$NEW_MODULES" | grep "^${MOD_ID}" | awk -F'\t' '{print $2}' | head -1)
        if [[ -n "$FILE" ]] && git diff --quiet HEAD~1 HEAD -- "$FILE" 2>/dev/null; then
            : # no change
        elif [[ -n "$FILE" ]]; then
            MODIFIED="${MODIFIED}${MOD_ID}\t${FILE}\n"
        fi
    done <<< "$COMMON"
fi

# ── Write change sheet ────────────────────────────────────────────────────────

{
cat << EOF
# Change Sheet: ${NEW_TAG} vs ${OLD_TAG}

**Generated:** ${DATE}
**Previous version:** ${OLD_TAG} ($(basename "$OLD_DIR"))
**Current version:** ${NEW_TAG} ($(basename "$NEW_DIR"))

---

## Summary

| Change | Count |
|---|---|
| Modules added | $(echo "$ADDED" | grep -c '\S' || echo 0) |
| Modules removed | $(echo "$REMOVED" | grep -c '\S' || echo 0) |
| Modules modified | $(echo -e "$MODIFIED" | grep -c '\S' || echo 0) |

---

## Modules Added

EOF

if [[ -z "$(echo "$ADDED" | tr -d '[:space:]')" ]]; then
    echo "*(none)*"
    echo ""
else
    echo "| Module ID | Title |"
    echo "|---|---|"
    while IFS= read -r MOD_ID; do
        [[ -z "$MOD_ID" ]] && continue
        TITLE=$(echo "$NEW_MODULES" | grep "^${MOD_ID}" | awk -F'\t' '{print $2}')
        echo "| ${MOD_ID} | ${TITLE} |"
    done <<< "$ADDED"
    echo ""
fi

cat << EOF

## Modules Removed

EOF

if [[ -z "$(echo "$REMOVED" | tr -d '[:space:]')" ]]; then
    echo "*(none)*"
    echo ""
else
    echo "| Module ID | Title |"
    echo "|---|---|"
    while IFS= read -r MOD_ID; do
        [[ -z "$MOD_ID" ]] && continue
        TITLE=$(echo "$OLD_MODULES" | grep "^${MOD_ID}" | awk -F'\t' '{print $2}')
        echo "| ${MOD_ID} | ${TITLE} |"
    done <<< "$REMOVED"
    echo ""
fi

cat << EOF

## Modules Modified

EOF

if [[ -z "$(echo -e "$MODIFIED" | tr -d '[:space:]')" ]]; then
    echo "*(none detected, or git history unavailable)*"
    echo ""
else
    echo "| Module ID | File |"
    echo "|---|---|"
    echo -e "$MODIFIED" | while IFS=$'\t' read -r MOD_ID FILE; do
        [[ -z "$MOD_ID" ]] && continue
        echo "| ${MOD_ID} | ${FILE} |"
    done
    echo ""
fi

cat << EOF

---

*This change sheet is auto-generated. Add human annotations below this line.*

## Notes from This Release

<!-- Add a human-written summary of the key changes, corrections, or additions here before distributing to students. -->

EOF
} > "$OUTFILE"

echo "   Change sheet written to: ${OUTFILE}"
echo ""
echo "Done. Review and annotate ${OUTFILE} before distributing."
