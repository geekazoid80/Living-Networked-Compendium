#!/usr/bin/env bash
# build-web.sh — Build the MkDocs static site for GitHub Pages
#
# Usage:
#   ./tools/scripts/build-web.sh
#
# Prerequisites:
#   pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin
#
# Output:
#   site/  (static HTML — ready to deploy to GitHub Pages)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> Building MkDocs site..."
mkdocs build --strict

echo ""
echo "Done. Static site is in: site/"
echo "To preview locally: mkdocs serve"
