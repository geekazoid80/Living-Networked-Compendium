#!/usr/bin/env python3
"""Rename 'id:' frontmatter field to 'module_id:' in all modules that use the old form."""

import re
import sys
from pathlib import Path


def fix_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False

    end = content.find("\n---\n", 3)
    if end == -1:
        return False

    frontmatter = content[3:end]

    has_old = bool(re.search(r"^id:", frontmatter, re.MULTILINE))
    has_new = bool(re.search(r"^module_id:", frontmatter, re.MULTILINE))

    if has_old and not has_new:
        new_frontmatter = re.sub(r"^id:", "module_id:", frontmatter, count=1, flags=re.MULTILINE)
        path.write_text("---" + new_frontmatter + content[end:], encoding="utf-8")
        return True

    return False


root = Path(__file__).parent.parent.parent / "modules"
count = 0
for md in sorted(root.rglob("*.md")):
    if fix_file(md):
        count += 1
        print(f"Fixed: {md.relative_to(root.parent)}")

print(f"\nTotal fixed: {count}")
