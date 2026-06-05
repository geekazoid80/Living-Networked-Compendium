#!/usr/bin/env python3
"""inject_learning_paths.py - inject reverse learning-path navigation into staged module pages.

Reverse navigation: each module page gains a "Part of these learning paths" block linking UP
to every role learning-path page that includes the module. Authoritative membership is the
hand-curated stage tables in learning-paths/*.md (the module-id token in the Module ID column),
plus the 1:1 mapping learning-paths/<role>.md <-> modules/applied/<role>/overview.md so each
role overview links to its own path.

This runs ONLY on the staged docs/ tree (build-web.sh copies repo content into docs/ first).
Tracked source modules are never touched. Injection is idempotent: the block is wrapped in
<!-- LP-NAV-START / END --> sentinels and any existing block is stripped before re-inserting.

Modules listed in no learning path get no block. Learning-path tables reference many future
module ids that have no file yet; those are silently ignored (no integrity gate).

Usage:
    python3 inject_learning_paths.py <docs_root>

Exit code 0 on success, 1 on error.
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

MODULE_ID_RE = re.compile(r"\b([A-Z]{2,5}-\d{3})\b")
START = "<!-- LP-NAV-START -->"
END = "<!-- LP-NAV-END -->"


def read(path):
    return path.read_text(encoding="utf-8")


def frontmatter(text):
    """Return the YAML frontmatter block (between the first two '---' fences), or ''."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    return text[3:end]


def fm_value(text, key):
    """Read a single scalar frontmatter value by key, stripping surrounding quotes."""
    block = frontmatter(text)
    m = re.search(r"^" + re.escape(key) + r':\s*"?([^"\n]*?)"?\s*$', block, re.MULTILINE)
    return m.group(1).strip() if m else None


def build_membership(paths_dir, modules_dir):
    """Map module_id -> ordered unique list of (role_label, path_file_Path)."""
    membership = defaultdict(list)
    for pf in sorted(paths_dir.glob("*.md")):
        text = read(pf)
        title = fm_value(text, "title") or pf.stem
        label = title.replace("Learning Path: ", "").strip()

        def add(module_id):
            entry = (label, pf)
            if entry not in membership[module_id]:
                membership[module_id].append(entry)

        # Stage-table rows: any 4+ column table whose Module ID column holds an id token.
        # Catches linked ids ([NW-001](...)) and bare ids (SV-001) alike. Header and
        # separator rows carry no id token; 3-column resource/certification tables are skipped.
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 4:
                continue
            m = MODULE_ID_RE.search(cells[1])
            if m:
                add(m.group(1))

        # 1:1 applied-overview mapping: learning-paths/<stem>.md -> modules/applied/<stem>/overview.md.
        overview = modules_dir / "applied" / pf.stem / "overview.md"
        if overview.exists():
            overview_id = fm_value(read(overview), "module_id")
            if overview_id:
                add(overview_id)

    return membership


def index_modules(modules_dir):
    """Map module_id -> module file Path for existing files (skipping _ templates)."""
    by_id = {}
    for mf in sorted(modules_dir.rglob("*.md")):
        rel_parts = mf.relative_to(modules_dir).parts
        if any(part.startswith("_") for part in rel_parts):
            continue
        module_id = fm_value(read(mf), "module_id")
        if module_id:
            by_id[module_id] = mf
    return by_id


def strip_block(text):
    """Remove any existing sentinel-wrapped block (and a trailing blank line)."""
    pattern = re.escape(START) + r".*?" + re.escape(END) + r"\n?"
    text = re.sub(pattern, "", text, flags=re.DOTALL)
    return text


def render_block(links):
    """Build the sentinel-wrapped admonition lines for a module's path links."""
    lines = [
        START,
        "",
        '!!! abstract "Part of these learning paths"',
        "",
    ]
    for label, rel in links:
        lines.append(f"    - [{label}]({rel})")
    lines += ["", END]
    return lines


def insert_after_h1(text, block_lines):
    """Insert the block after the body H1 (first '# ' line below the frontmatter)."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0] == "---":
        for j in range(1, len(lines)):
            if lines[j] == "---":
                start = j + 1
                break
    for k in range(start, len(lines)):
        if lines[k].startswith("# "):
            at = k + 1
            new = lines[:at] + [""] + block_lines + [""] + lines[at:]
            tail = "\n" if text.endswith("\n") else ""
            return "\n".join(new) + tail
    return text  # no H1: leave unchanged


def main(argv):
    if len(argv) != 2:
        print("usage: inject_learning_paths.py <docs_root>", file=sys.stderr)
        return 1
    docs_root = Path(argv[1])
    paths_dir = docs_root / "learning-paths"
    modules_dir = docs_root / "modules"
    if not paths_dir.is_dir() or not modules_dir.is_dir():
        print(
            f"error: expected {paths_dir} and {modules_dir} to exist (stage the docs tree first)",
            file=sys.stderr,
        )
        return 1

    membership = build_membership(paths_dir, modules_dir)
    by_id = index_modules(modules_dir)

    injected = 0
    for module_id, mf in by_id.items():
        entries = membership.get(module_id)
        if not entries:
            continue
        text = read(mf)
        if START in text:
            text = strip_block(text)
        links = [(label, os.path.relpath(pf, start=mf.parent)) for (label, pf) in entries]
        new = insert_after_h1(text, render_block(links))
        if new != text:
            mf.write_text(new, encoding="utf-8")
            injected += 1

    print(f"inject_learning_paths: injected reverse-nav into {injected} module page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
