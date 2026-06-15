#!/usr/bin/env python3
"""retire_learning_path_tags.py - one-shot removal of the retired `learning_path_tags` field.

`learning_path_tags` is superseded by build-time reverse navigation (see inject_learning_paths.py):
each module page now links up to its learning paths, derived from the hand-curated stage tables in
learning-paths/. The field had zero tooling consumers, so removal is schema-safe.

This strips the `learning_path_tags:` key and its block-list items from every module under
modules/. It is human-invoked once, reviewed via `git diff`, then committed. It is NOT wired into
any build pipeline.

The field only ever held uppercase path-id tokens (DNE / CE / DCE). As a guard, the script asserts
no lowercase token is present: a lowercase token would have been a topic keyword that belongs in
`tags`, and would need merging rather than dropping. If that assertion ever fires, stop and handle
the merge by hand.

Usage:
    python3 retire_learning_path_tags.py [modules_dir]   # default: modules

Exit code 0 on success, 1 on error.
"""

import re
import sys
from pathlib import Path

KEY_RE = re.compile(r"^learning_path_tags:\s*$")
ITEM_RE = re.compile(r"^\s*-\s+(.*\S)\s*$")


def strip_field(text):
    """Return (new_text, removed_tokens). Removes the key line and its following list items."""
    lines = text.splitlines(keepends=True)
    out = []
    removed = []
    i = 0
    n = len(lines)
    while i < n:
        if KEY_RE.match(lines[i].rstrip("\n")):
            i += 1
            while i < n:
                m = ITEM_RE.match(lines[i].rstrip("\n"))
                if not m:
                    break
                removed.append(m.group(1).strip())
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), removed


def main(argv):
    modules_dir = Path(argv[1]) if len(argv) > 1 else Path("modules")
    if not modules_dir.is_dir():
        print(f"error: {modules_dir} is not a directory", file=sys.stderr)
        return 1

    changed = 0
    for mf in sorted(modules_dir.rglob("*.md")):
        text = mf.read_text(encoding="utf-8")
        if "learning_path_tags:" not in text:
            continue
        new, removed = strip_field(text)
        lowercase = [t for t in removed if t and t == t.lower()]
        assert not lowercase, (
            f"{mf}: unexpected lowercase token(s) {lowercase} - these are topic keywords that "
            f"belong in `tags`; merge by hand rather than dropping"
        )
        if new != text:
            mf.write_text(new, encoding="utf-8")
            changed += 1

    print(f"retire_learning_path_tags: removed the field from {changed} module file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
