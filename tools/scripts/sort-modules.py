#!/usr/bin/env python3
"""Print sorted .md file paths from a directory, ordered by module_id frontmatter field.

Modules without a module_id sort to the end of their group, ordered by filename.

Usage:
    python3 sort-modules.py <directory>
"""

import re
import sys
from pathlib import Path


def get_module_id(path: Path) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            in_frontmatter = False
            for i, line in enumerate(f):
                if i == 0:
                    if line.strip() == "---":
                        in_frontmatter = True
                    else:
                        break
                    continue
                if i > 30:
                    break
                if line.strip() == "---":
                    break
                m = re.match(r'^module_id:\s*["\']?([^"\']+?)["\']?\s*$', line)
                if m:
                    return m.group(1).strip()
    except OSError:
        pass
    return ""


if len(sys.argv) < 2:
    print("Usage: sort-modules.py <directory>", file=sys.stderr)
    sys.exit(1)

directory = Path(sys.argv[1])
if not directory.is_dir():
    sys.exit(0)

files = list(directory.glob("*.md"))
files.sort(key=lambda p: (get_module_id(p) == "", get_module_id(p), p.name))

for f in files:
    print(f)
