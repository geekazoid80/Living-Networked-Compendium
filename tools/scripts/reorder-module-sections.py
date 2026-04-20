#!/usr/bin/env python3
"""
reorder-module-sections.py — Reorder module sections to the canonical order.

Canonical order:
  Learning Objectives -> Prerequisites -> The Problem -> (rest in original order)

Usage:
  python3 tools/scripts/reorder-module-sections.py [file_or_dir ...]

  If no arguments, processes all .md files under modules/
"""

import re
import sys
from pathlib import Path


def reorder_file(filepath: Path) -> bool:
    """Return True if the file was modified."""
    text = filepath.read_text(encoding='utf-8')

    # Separate YAML frontmatter (--- ... ---) from body
    fm_match = re.match(r'^---\n.*?\n---\n', text, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(0)
        body = text[fm_match.end():]
    else:
        frontmatter = ''
        body = text

    # Find all top-level (##) section start positions — skip lines inside code fences
    # We walk line by line to avoid matching ## inside ``` blocks
    lines = body.split('\n')
    in_fence = False
    section_starts = []  # (line_index, heading_text)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence
        if not in_fence and re.match(r'^## [^#]', line):
            section_starts.append((i, line))

    if not section_starts:
        return False

    # Split body into: preamble + list of (heading_line_idx, content_lines)
    preamble_lines = lines[:section_starts[0][0]]

    sections = []
    for idx, (line_no, heading) in enumerate(section_starts):
        if idx + 1 < len(section_starts):
            end = section_starts[idx + 1][0]
        else:
            end = len(lines)
        content = '\n'.join(lines[line_no:end])
        # Normalise: ensure section ends with exactly one blank line
        content = content.rstrip('\n') + '\n'
        title = heading.lstrip('#').strip()
        sections.append((title, content))

    # Locate the three sections we need to reorder
    def find(name):
        for i, (t, _) in enumerate(sections):
            if t == name:
                return i
        return -1

    lo_idx = find('Learning Objectives')
    pre_idx = find('Prerequisites')
    prob_idx = find('The Problem')

    if prob_idx == -1 or lo_idx == -1:
        return False  # Nothing to do

    # Check if already in correct order (LO before Problem, Prereq before Problem)
    pre_ok = pre_idx == -1 or pre_idx < prob_idx
    if lo_idx < prob_idx and pre_ok:
        return False  # Already correct

    # Build new section list:
    # - Everything before The Problem, minus LO and Prereq
    # - LO
    # - Prereq (if present)
    # - The Problem onwards (in original relative order)
    extracted = {lo_idx}
    if pre_idx != -1:
        extracted.add(pre_idx)

    before_prob = [(i, s) for i, s in enumerate(sections)
                   if i < prob_idx and i not in extracted]
    from_prob = [s for i, s in enumerate(sections)
                 if i >= prob_idx and i not in extracted]

    new_sections = [s for _, s in before_prob]
    new_sections.append(sections[lo_idx])
    if pre_idx != -1:
        new_sections.append(sections[pre_idx])
    new_sections.extend(from_prob)

    # Reconstruct file
    preamble = '\n'.join(preamble_lines)
    if preamble and not preamble.endswith('\n'):
        preamble += '\n'

    new_body = preamble + ''.join(s[1] for s in new_sections)
    new_text = frontmatter + new_body

    if new_text == text:
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
        targets = list((repo_root / 'modules').rglob('*.md'))

    modified = 0
    for path in sorted(targets):
        if path.suffix != '.md':
            continue
        try:
            if reorder_file(path):
                print(f'  Reordered: {path.relative_to(repo_root)}')
                modified += 1
        except Exception as e:
            print(f'  ERROR {path}: {e}')

    print(f'\nDone. {modified} file(s) reordered.')


if __name__ == '__main__':
    main()
