#!/usr/bin/env bash
# build-pdf.sh — Thin wrapper; delegates to build_pdf.py to avoid MSYS2 path issues.
#
# Usage:
#   ./tools/scripts/build-pdf.sh [version_number]
#
# Prerequisites:
#   - pandoc (https://pandoc.org/installing.html)
#   - xelatex (e.g. MiKTeX on Windows, texlive-xetex on Ubuntu, MacTeX on macOS)
#
# Output:
#   handouts/versions/vNNN-YYYY-MM-DD/
#     compendium-vNNN-YYYY-MM-DD.pdf   — full combined handout
#     MANIFEST.md                       — module list

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "${REPO_ROOT}/tools/scripts/build_pdf.py" "$@"
