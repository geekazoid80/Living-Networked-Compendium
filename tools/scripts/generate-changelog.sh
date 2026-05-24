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
    # Awk fields after splitting on |:
    #   $1 = "" (before first pipe)
    #   $2 = MODULE_ID, $3 = Title, $4 = File, $5 = "" (after last pipe)
    # Emit MOD_ID\tTITLE\tFILE so downstream consumers can pick the column
    # they actually need (the earlier 2-column emit conflated Title and File).
    # Use basic regex (no `-P`) so the script works on macOS BSD grep as well
    # as GNU grep in CI; the pattern needs no PCRE features.
    grep '^| [A-Z]' "$manifest" 2>/dev/null | \
        awk -F'|' '{
            gsub(/^ +| +$/, "", $2)
            gsub(/^ +| +$/, "", $3)
            gsub(/^ +| +$/, "", $4)
            print $2 "\t" $3 "\t" $4
        }' || true
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

# For common modules, check whether the source file has changed between the
# previous release tag and HEAD. Three issues with the earlier implementation:
#
#   1. It diffed HEAD~1..HEAD, which catches only the very last commit. A
#      release that bundles many commits since the previous tag would report
#      "no modules modified" even when modules genuinely changed. We now diff
#      against ${OLD_TAG}..HEAD.
#
#   2. The MANIFEST File column records the bare basename (e.g. "osi-model.md")
#      while the actual source lives under modules/<area>/<topic>/. The earlier
#      `git diff -- "$FILE"` matched the bare path at the repo root, which
#      never exists, so no module could ever be flagged. We now resolve the
#      bare filename to its tracked path via `git ls-files`.
#
#   3. The earlier loop iterated $COMMON (just MOD_IDs) and pulled FILE via
#      `grep "^${MOD_ID}" | head -1`. For non-module front-matter / part-break
#      rows that share MOD_ID = "-", every iteration matched the first "-"
#      row, so most of those files were never inspected and the same row could
#      appear duplicated in the output. We now iterate the (MOD_ID, FILE) rows
#      from NEW_MODULES directly and filter by COMMON membership.
#
# If the previous tag isn't resolvable locally (e.g. shallow clone, first
# release), skip detection entirely rather than spuriously flagging every
# common module as modified.
MODIFIED=""
if git rev-parse --git-dir &>/dev/null && \
   git rev-parse --verify "$OLD_TAG" >/dev/null 2>&1; then
    while IFS=$'\t' read -r MOD_ID TITLE FILE; do
        [[ -z "$MOD_ID" || -z "$FILE" ]] && continue
        # only inspect rows present in both manifest versions
        echo "$COMMON" | grep -qxF "$MOD_ID" || continue
        REPO_PATH=$(git ls-files "**/${FILE}" 2>/dev/null | head -1)
        [[ -z "$REPO_PATH" ]] && continue
        if ! git diff --quiet "${OLD_TAG}..HEAD" -- "$REPO_PATH" 2>/dev/null; then
            MODIFIED="${MODIFIED}${MOD_ID}\t${FILE}\n"
        fi
    done <<< "$NEW_MODULES"
fi

# Pre-compute counts so the Summary table doesn't print "0\n0" when a section
# is empty. `grep -c '\S'` always prints a count, but exits 1 when there are
# no matches; the previous `|| echo 0` form appended a second "0" to the
# cell. `|| true` swallows the non-zero exit without adding output.
ADDED_COUNT=$(echo "$ADDED" | grep -c '\S' || true)
REMOVED_COUNT=$(echo "$REMOVED" | grep -c '\S' || true)
MODIFIED_COUNT=$(echo -e "$MODIFIED" | grep -c '\S' || true)

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
| Modules added | ${ADDED_COUNT} |
| Modules removed | ${REMOVED_COUNT} |
| Modules modified | ${MODIFIED_COUNT} |

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
