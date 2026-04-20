#!/usr/bin/env bash
# build-pdf.sh — Generate versioned PDF handouts from all modules using Pandoc
#
# Usage:
#   ./tools/scripts/build-pdf.sh [version_number]
#
#   version_number: optional integer (e.g. 1, 2, 42). If omitted, auto-increments
#                   from the last version found in handouts/versions/.
#
# Prerequisites:
#   - pandoc (https://pandoc.org/installing.html)
#   - A LaTeX engine: pdflatex, xelatex, or lualatex
#     (e.g. on Ubuntu: sudo apt install texlive-xetex)
#     (e.g. on macOS:  brew install --cask mactex-no-gui)
#     (e.g. on Windows: winget install JohnMacFarlane.Pandoc MiKTeX.MiKTeX)
#
# Output:
#   handouts/versions/vNNN-YYYY-MM-DD/
#     compendium-vNNN-YYYY-MM-DD.pdf   — full combined handout
#     MANIFEST.md                       — module list

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# ── Version calculation ────────────────────────────────────────────────────────

if [[ $# -ge 1 ]]; then
    VERSION_NUM="$1"
else
    # Auto-increment: find highest existing vNNN
    LAST=$(ls -d handouts/versions/v[0-9][0-9][0-9]-* 2>/dev/null | \
           grep -oE 'v[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1)
    VERSION_NUM=$(( ${LAST:-0} + 1 ))
fi

VERSION=$(printf "v%03d" "$VERSION_NUM")
DATE=$(date +%Y-%m-%d)
OUTDIR="${REPO_ROOT}/handouts/versions/${VERSION}-${DATE}"
OUTFILE="${OUTDIR}/compendium-${VERSION}-${DATE}.pdf"

mkdir -p "$OUTDIR"

echo "==> Building PDF handout ${VERSION} (${DATE})..."

# ── Collect modules in logical order ──────────────────────────────────────────

MODULES=()

# Fundamentals — ordered by domain
for DOMAIN in networking ip routing switching services security qos rf automation \
              access-media carrier-transport datacentre protocols functions professional-standards; do
    if [[ -d "modules/fundamentals/${DOMAIN}" ]]; then
        while IFS= read -r -d '' f; do
            MODULES+=("$f")
        done < <(find "modules/fundamentals/${DOMAIN}" -name "*.md" ! -name "*.gitkeep" -print0 | sort -z)
    fi
done

# Applied — ordered
for PATH_DIR in data-network-engineer rf-satellite-engineer broadcast-engineer \
                rf-coax-engineer voice-telephony-engineer rf-mobile-engineer \
                storage-network-engineer carrier-engineer datacentre-engineer \
                _new-path-template; do
    if [[ -d "modules/applied/${PATH_DIR}" ]]; then
        while IFS= read -r -d '' f; do
            MODULES+=("$f")
        done < <(find "modules/applied/${PATH_DIR}" -name "*.md" ! -name "*.gitkeep" -print0 | sort -z)
    fi
done

if [[ ${#MODULES[@]} -eq 0 ]]; then
    echo "No modules found. Nothing to build."
    exit 0
fi

echo "   Modules found: ${#MODULES[@]}"

# ── Preprocess modules into a short temp path ─────────────────────────────────
#
# MiKTeX's on-the-fly package installer fails when the working directory has a
# long path (e.g. OneDrive folders). Preprocessing to /tmp and running pandoc
# from there keeps paths short enough for Windows to handle correctly.

if [[ "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* || "$(uname -s)" == MSYS* ]]; then
    BUILD_TMP="/c/tmp/compendium-build-$$"
else
    BUILD_TMP=$(mktemp -d /tmp/compendium-build-XXXXXX)
fi
mkdir -p "$BUILD_TMP"
trap 'rm -rf "$BUILD_TMP"' EXIT

PREPROCESSED_MODULES=()
i=0
for f in "${MODULES[@]}"; do
    TMP="${BUILD_TMP}/$(printf '%04d' $i)-$(basename "$f")"
    python3 tools/scripts/preprocess-module.py "$f" "$TMP" pdf
    PREPROCESSED_MODULES+=("$TMP")
    (( i++ )) || true
done

echo "   Preprocessed: ${#PREPROCESSED_MODULES[@]} modules"

# ── Generate cover page ────────────────────────────────────────────────────────

COVER_TMP="${BUILD_TMP}/0000-cover.md"

cat > "$COVER_TMP" << EOF
---
title: "Living Networked Compendium"
subtitle: "A Progressive Guide for Data Network Engineers"
date: "${DATE}"
version: "${VERSION}"
---

# Living Networked Compendium

**${VERSION} — ${DATE}**

A living, community-built body of knowledge for data network engineers.
From novice to professional, one module at a time.

---

**Licence:** Content: CC BY-SA 4.0 | Code: Apache 2.0

*See the accompanying CHANGES file for what is new in this version.*

---
EOF

# ── Build PDF (run from BUILD_TMP to keep working directory path short) ────────

echo "   Running pandoc..."
cd "$BUILD_TMP"

pandoc \
    "$COVER_TMP" \
    "${PREPROCESSED_MODULES[@]}" \
    --output="$OUTFILE" \
    --pdf-engine=xelatex \
    --toc \
    --toc-depth=2 \
    --number-sections \
    --variable geometry:margin=2.5cm \
    --variable fontsize=11pt \
    --variable colorlinks=true \
    --variable linkcolor=blue \
    --variable urlcolor=blue \
    --variable toccolor=black \
    --metadata title="Living Networked Compendium ${VERSION}" \
    --metadata author="Community Contributors" \
    --metadata date="${DATE}" \
    --syntax-highlighting=tango \
    2>&1

cd "$REPO_ROOT"

echo "   PDF written to: ${OUTFILE}"

# ── Write version manifest ─────────────────────────────────────────────────────

MANIFEST="${OUTDIR}/MANIFEST.md"
{
    echo "# Handout Manifest — ${VERSION} (${DATE})"
    echo ""
    echo "| Module ID | Title | File |"
    echo "|---|---|---|"
    for f in "${MODULES[@]}"; do
        TITLE=$(grep -m1 '^title:' "$f" 2>/dev/null | sed 's/title: *//;s/"//g' || echo "Unknown")
        MOD_ID=$(grep -m1 '^id:' "$f" 2>/dev/null | sed 's/id: *//;s/"//g' || echo "—")
        echo "| ${MOD_ID} | ${TITLE} | ${f##*/} |"
    done
} > "$MANIFEST"

echo "   Manifest written to: ${MANIFEST}"
echo ""
echo "Done. Handout ${VERSION} is ready in: ${OUTDIR}/"
echo ""
echo "Next step: run generate-changelog.sh to produce the change sheet."
