#!/usr/bin/env bash
# build-web.sh — Build the MkDocs static site for GitHub Pages
#
# This script stages repository-root content into docs/ before running
# `mkdocs build`. mkdocs does not allow docs_dir to be the parent of
# mkdocs.yml, so we copy README.md, CONTRIBUTING.md, learning-paths/,
# modules/, etc. into docs/ at build time. Staged paths are gitignored.
#
# Usage:
#   ./tools/scripts/build-web.sh           # build to site/
#   ./tools/scripts/build-web.sh --clean   # only remove staged content
#   ./tools/scripts/build-web.sh --serve   # stage, then run `mkdocs serve`
#
# Prerequisites:
#   pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin
#
# Output:
#   site/  (static HTML — ready to deploy to GitHub Pages)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# ── Files and directories to stage from repo root into docs/ ─────────────────
STAGED_FILES=(
  "README.md"
  "CONTRIBUTING.md"
  "CONTRIBUTION_SPEC.md"
  "AI_GUARDRAILS.md"
)
STAGED_DIRS=(
  "learning-paths"
  "modules"
)

clean_staged() {
  for f in "${STAGED_FILES[@]}"; do
    rm -f "docs/${f}"
  done
  for d in "${STAGED_DIRS[@]}"; do
    rm -rf "docs/${d}"
  done
}

stage() {
  echo "==> Staging repo-root content into docs/..."
  clean_staged
  for f in "${STAGED_FILES[@]}"; do
    if [[ -f "$f" ]]; then
      cp "$f" "docs/${f}"
    else
      echo "warn: source file $f not found, skipping" >&2
    fi
  done
  for d in "${STAGED_DIRS[@]}"; do
    if [[ -d "$d" ]]; then
      cp -R "$d" "docs/${d}"
    else
      echo "warn: source directory $d not found, skipping" >&2
    fi
  done
}

# Always clean up staged content on exit (success or failure)
trap clean_staged EXIT

case "${1:-build}" in
  --clean)
    trap - EXIT  # We're already cleaning; don't double-clean
    clean_staged
    echo "==> Removed staged content from docs/"
    ;;
  --serve)
    stage
    trap - EXIT  # Keep staged content while mkdocs serve is running
    echo "==> Starting mkdocs serve (Ctrl-C to stop)..."
    echo "    Note: staged docs/ content will remain on disk after exit."
    echo "    Run with --clean to remove it."
    mkdocs serve
    ;;
  build|"")
    stage
    echo "==> Building MkDocs site..."
    mkdocs build --strict
    echo ""
    echo "Done. Static site is in: site/"
    echo "To preview locally: ./tools/scripts/build-web.sh --serve"
    ;;
  *)
    echo "Unknown argument: $1" >&2
    echo "Usage: $0 [--clean | --serve | build]" >&2
    exit 2
    ;;
esac
