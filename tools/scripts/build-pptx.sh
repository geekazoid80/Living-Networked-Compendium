#!/usr/bin/env bash
# build-pptx.sh — Generate versioned PPTX slide decks using Marp CLI
#
# Usage:
#   ./tools/scripts/build-pptx.sh [version_number]
#
# Each module gets its own PPTX file, plus a combined PDF-format slide deck.
#
# Prerequisites:
#   npm install -g @marp-team/marp-cli
#
# Output:
#   handouts/versions/vNNN-YYYY-MM-DD/slides/
#     NW-001-osi-model.pptx
#     IP-001-ip-addressing.pptx
#     IP-002-subnetting.pptx
#     ...
#     all-modules-vNNN-YYYY-MM-DD.pdf   (combined PDF presentation)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# ── Version calculation ────────────────────────────────────────────────────────

if [[ $# -ge 1 ]]; then
    VERSION_NUM="$1"
else
    LAST=$(ls -d handouts/versions/v[0-9][0-9][0-9]-* 2>/dev/null | \
           grep -oP 'v\K[0-9]+' | sort -n | tail -1)
    VERSION_NUM="${LAST:-1}"
fi

VERSION=$(printf "v%03d" "$VERSION_NUM")
DATE=$(date +%Y-%m-%d)
OUTDIR="handouts/versions/${VERSION}-${DATE}/slides"
THEME="tools/templates/marp-theme.css"

mkdir -p "$OUTDIR"

echo "==> Building PPTX slides ${VERSION} (${DATE})..."

# ── Check Marp is available ───────────────────────────────────────────────────

if ! command -v marp &>/dev/null; then
    echo "ERROR: marp not found. Install with: npm install -g @marp-team/marp-cli"
    exit 1
fi

# ── Process each module ───────────────────────────────────────────────────────

BUILT=0
SKIPPED=0

process_module() {
    local MD_FILE="$1"
    local BASENAME
    BASENAME=$(basename "$MD_FILE" .md)

    # Extract module_id for filename prefix
    local MOD_ID
    MOD_ID=$(grep -m1 '^module_id:' "$MD_FILE" 2>/dev/null | \
             sed 's/module_id: *//;s/"//g;s/ //g' || echo "UNKNOWN")

    local OUT_PPTX="${OUTDIR}/${MOD_ID}-${BASENAME}.pptx"

    # Preprocess module through three-bucket transformer (pptx target)
    # This: strips XREF blocks, converts ??? supplementary to Marp speaker notes,
    # and removes template HTML comments while preserving speaker note comments.
    local PREPROCESSED_TMP
    PREPROCESSED_TMP=$(mktemp /tmp/preprocessed-XXXXXX.md)

    # Generate a Marp-compatible slide version of the module
    # We create a temp file that wraps the module markdown with Marp front matter
    local MARP_TMP
    MARP_TMP=$(mktemp /tmp/marp-XXXXXX.md)
    trap 'rm -f "$MARP_TMP" "$PREPROCESSED_TMP"' RETURN

    python3 tools/scripts/preprocess-module.py "$MD_FILE" "$PREPROCESSED_TMP" pptx

    local TITLE
    TITLE=$(grep -m1 '^title:' "$MD_FILE" 2>/dev/null | sed 's/title: *//;s/"//g' || echo "$BASENAME")

    local VERSION_LABEL="${VERSION} — ${DATE}"

    cat > "$MARP_TMP" << MARP_HEADER
---
marp: true
theme: default
paginate: true
header: "Living Networked Compendium | ${MOD_ID}"
footer: "${VERSION_LABEL} | CC BY-SA 4.0"
style: |
  section { font-size: 1.4rem; }
  h1 { color: #1a5276; }
  h2 { color: #1a5276; border-bottom: 2px solid #1a5276; }
  code { background: #f4f4f4; }
  table { font-size: 1.1rem; }
---

# ${TITLE}

**${MOD_ID}** | Living Networked Compendium

${VERSION_LABEL}

---

MARP_HEADER

    # Append preprocessed module content, converting ## headings to slide breaks.
    # HTML comment stripping is handled by preprocess-module.py (pptx target);
    # speaker note comments (<!-- Notes — ... -->) are preserved intentionally.
    python3 - "$PREPROCESSED_TMP" >> "$MARP_TMP" << 'PYEOF'
import sys, re

with open(sys.argv[1]) as f:
    content = f.read()

# Strip YAML frontmatter
content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)

# Convert ## headings to slide breaks (---)
content = re.sub(r'\n## ', '\n\n---\n\n## ', content)

print(content.strip())
PYEOF

    marp "$MARP_TMP" \
        --output "$OUT_PPTX" \
        --pptx \
        --allow-local-files \
        2>/dev/null && \
        echo "   [OK] ${MOD_ID}: ${OUT_PPTX}" && \
        BUILT=$((BUILT + 1)) || \
        (echo "   [SKIP] ${MOD_ID}: failed to convert" && SKIPPED=$((SKIPPED + 1)))
}

# Process all modules
for DOMAIN in networking ip routing switching services security qos rf automation \
              access-media carrier-transport datacentre protocols functions professional-standards; do
    for MD in "modules/fundamentals/${DOMAIN}"/*.md; do
        [[ -f "$MD" ]] && process_module "$MD"
    done
done

for PATH_DIR in data-network-engineer rf-satellite-engineer broadcast-engineer \
                rf-coax-engineer voice-telephony-engineer rf-mobile-engineer \
                storage-network-engineer carrier-engineer datacentre-engineer \
                _new-path-template; do
    for MD in "modules/applied/${PATH_DIR}"/*.md; do
        [[ -f "$MD" ]] && process_module "$MD"
    done
done

echo ""
echo "Built: ${BUILT} slides | Skipped: ${SKIPPED}"
echo "Slides written to: ${OUTDIR}/"
