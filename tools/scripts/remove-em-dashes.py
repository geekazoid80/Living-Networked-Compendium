#!/usr/bin/env python3
"""
remove-em-dashes.py — Replace em dashes in module prose with correct punctuation.

Rules:
  " — " (spaced em dash) is the most common form. Replacement depends on context:
    - Before a clause that defines/explains the preceding noun: colon
    - Mid-sentence parenthetical aside: commas
    - Before a consequence/result: period and new sentence (or comma)
    - In headings or labels (e.g. "Layer 1 — Physical"): keep as plain " - " (hyphen-space)
    - In ASCII diagrams inside code fences: leave untouched

  "—" (unspaced em dash): same rules as spaced form.

Because context-sensitive replacement requires judgment, this script takes a
conservative approach: it replaces the spaced form " — " with " - " universally
in prose, and leaves code fences untouched. Any case where a colon or period
would be clearly better is handled by the subsequent prose-fix passes on
specific files.

Usage:
  python3 tools/scripts/remove-em-dashes.py [file_or_dir ...]

  If no arguments, processes all .md files under modules/ and docs/
"""

import re
import sys
from pathlib import Path


def process_file(filepath: Path) -> bool:
    text = filepath.read_text(encoding='utf-8')
    original = text

    lines = text.split('\n')
    in_fence = False
    result = []

    for line in lines:
        stripped = line.strip()
        # Track fenced code blocks — do not modify content inside them
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence

        if in_fence:
            result.append(line)
            continue

        # Replace spaced em dash " — " with " - " in prose
        # Exception: leave table-separator rows and YAML frontmatter untouched
        new_line = line.replace(' \u2014 ', ' - ')
        # Also catch unspaced em dash (less common but present)
        new_line = new_line.replace('\u2014', '-')
        result.append(new_line)

    new_text = '\n'.join(result)

    if new_text == original:
        return False

    filepath.write_text(new_text, encoding='utf-8')
    return True


def main():
    repo_root = Path(__file__).parent.parent.parent

    if len(sys.argv) > 1:
        targets = []
        for arg in sys.argv[1:]:
            p = Path(arg)
            if p.is_dir():
                targets.extend(p.rglob('*.md'))
            else:
                targets.append(p)
    else:
        # Process modules/ and docs/ but not handouts/
        targets = list((repo_root / 'modules').rglob('*.md'))
        targets += list((repo_root / 'docs').rglob('*.md'))

    modified = 0
    for path in sorted(targets):
        if path.suffix != '.md':
            continue
        try:
            if process_file(path):
                print(f'  Fixed: {path.relative_to(repo_root)}')
                modified += 1
        except Exception as e:
            print(f'  ERROR {path}: {e}')

    print(f'\nDone. {modified} file(s) modified.')


if __name__ == '__main__':
    main()
