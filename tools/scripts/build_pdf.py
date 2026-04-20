#!/usr/bin/env python3
"""
build_pdf.py - Generate versioned PDF handouts from all modules using Pandoc.

Usage:
    python3 tools/scripts/build_pdf.py [version_number]

    version_number: optional integer (e.g. 1, 2, 42). If omitted,
                    auto-increments from the last version in handouts/versions/.

Prerequisites:
    - pandoc  (https://pandoc.org/installing.html)
    - xelatex (e.g. MiKTeX on Windows, texlive-xetex on Ubuntu, MacTeX on macOS)

Output:
    handouts/versions/vNNN-YYYY-MM-DD/
        compendium-vNNN-YYYY-MM-DD.pdf
        MANIFEST.md
"""

import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

FRONT_MATTER = [
    "docs/front-matter/00-introduction.md",
    "docs/front-matter/01-how-to-read.md",
    "docs/front-matter/02-learning-paths.md",
    "docs/front-matter/03-platform-reference.md",
]

DOMAIN_BREAK = {
    "networking":        "docs/front-matter/domain-breaks/part-networking.md",
    "ip":                "docs/front-matter/domain-breaks/part-ip.md",
    "routing":           "docs/front-matter/domain-breaks/part-routing.md",
    "switching":         "docs/front-matter/domain-breaks/part-switching.md",
    "services":          "docs/front-matter/domain-breaks/part-services.md",
    "security":          "docs/front-matter/domain-breaks/part-security.md",
    "qos":               "docs/front-matter/domain-breaks/part-qos.md",
    "automation":        "docs/front-matter/domain-breaks/part-automation.md",
    "carrier-transport": "docs/front-matter/domain-breaks/part-carrier.md",
}

FUNDAMENTAL_DOMAINS = [
    "networking", "ip", "routing", "switching", "services", "security",
    "qos", "rf", "automation", "access-media", "carrier-transport",
    "datacentre", "protocols", "functions", "professional-standards",
]

APPLIED_PATHS = [
    "data-network-engineer", "rf-satellite-engineer", "broadcast-engineer",
    "rf-coax-engineer", "voice-telephony-engineer", "rf-mobile-engineer",
    "storage-network-engineer", "carrier-engineer", "datacentre-engineer",
]


def get_module_id(path: Path) -> str:
    """Extract module_id from YAML frontmatter, or empty string if absent."""
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


def sorted_modules(directory: Path) -> list[Path]:
    """Return .md files from directory sorted by module_id frontmatter."""
    files = list(directory.glob("*.md"))
    files.sort(key=lambda p: (get_module_id(p) == "", get_module_id(p), p.name))
    return files


def collect_modules() -> list[Path]:
    modules: list[Path] = []

    for rel in FRONT_MATTER:
        p = REPO_ROOT / rel
        if p.exists():
            modules.append(p)

    for domain in FUNDAMENTAL_DOMAINS:
        domain_dir = REPO_ROOT / "modules" / "fundamentals" / domain
        if not domain_dir.is_dir():
            continue
        break_rel = DOMAIN_BREAK.get(domain)
        if break_rel:
            bp = REPO_ROOT / break_rel
            if bp.exists():
                modules.append(bp)
        modules.extend(sorted_modules(domain_dir))

    for path_dir in APPLIED_PATHS:
        applied_dir = REPO_ROOT / "modules" / "applied" / path_dir
        if applied_dir.is_dir():
            modules.extend(sorted_modules(applied_dir))

    return modules


def compute_version(version_arg: str | None) -> int:
    if version_arg is not None:
        return int(version_arg)
    versions_dir = REPO_ROOT / "handouts" / "versions"
    last = 0
    if versions_dir.exists():
        for d in versions_dir.iterdir():
            m = re.match(r"v(\d+)-", d.name)
            if m:
                last = max(last, int(m.group(1)))
    return last + 1


def write_cover(path: Path, version: str, build_date: str) -> None:
    path.write_text(
        f'---\ntitle: "Living Networked Compendium"\n'
        f'subtitle: "A Progressive Guide for Data Network Engineers"\n'
        f'date: "{build_date}"\nversion: "{version}"\n---\n\n'
        f'# Living Networked Compendium\n\n'
        f'**{version} - {build_date}**\n\n'
        f'A living, community-built body of knowledge for data network engineers.\n'
        f'From novice to professional, one module at a time.\n\n'
        f'* * *\n\n'
        f'**Licence:** Content: CC BY-SA 4.0 | Code: Apache 2.0\n\n'
        f'*See the accompanying CHANGES file for what is new in this version.*\n\n'
        f'* * *\n',
        encoding="utf-8",
    )


def write_manifest(path: Path, version: str, build_date: str, modules: list[Path]) -> None:
    lines = [
        f"# Handout Manifest — {version} ({build_date})",
        "",
        "| Module ID | Title | File |",
        "|---|---|---|",
    ]
    for mod in modules:
        title, mod_id = "Unknown", "-"
        try:
            for line in mod.read_text(encoding="utf-8").splitlines():
                if line.startswith("title:"):
                    title = line[6:].strip().strip('"').strip("'")
                elif line.startswith("module_id:"):
                    mod_id = line[10:].strip().strip('"').strip("'")
        except OSError:
            pass
        lines.append(f"| {mod_id} | {title} | {mod.name} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    version_arg = sys.argv[1] if len(sys.argv) >= 2 else None
    version_num = compute_version(version_arg)
    version = f"v{version_num:03d}"
    build_date = date.today().isoformat()

    out_dir = REPO_ROOT / "handouts" / "versions" / f"{version}-{build_date}"
    out_pdf = out_dir / f"compendium-{version}-{build_date}.pdf"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> Building PDF handout {version} ({build_date})...")

    modules = collect_modules()
    if not modules:
        print("No modules found. Nothing to build.")
        sys.exit(0)
    print(f"   Modules found: {len(modules)}")

    preprocess_script = str(REPO_ROOT / "tools" / "scripts" / "preprocess_module.py")

    # On Windows keep the build path short so MiKTeX on-demand installer works.
    # On other platforms the system temp dir is fine.
    if platform.system() == "Windows":
        short_tmp = Path("C:/tmp")
        short_tmp.mkdir(exist_ok=True)
        tmp_dir = Path(tempfile.mkdtemp(prefix="compendium-build-", dir=short_tmp))
    else:
        tmp_dir = Path(tempfile.mkdtemp(prefix="compendium-build-"))
    try:
        preprocessed: list[Path] = []
        for i, mod in enumerate(modules):
            dst = tmp_dir / f"{i:04d}-{mod.name}"
            subprocess.run(
                [sys.executable, preprocess_script, str(mod), str(dst), "pdf"],
                check=True,
            )
            preprocessed.append(dst)
        print(f"   Preprocessed: {len(preprocessed)} modules")

        cover = tmp_dir / "cover.md"
        write_cover(cover, version, build_date)

        tmp_pdf = tmp_dir / "compendium.pdf"

        print("   Running pandoc...")
        subprocess.run(
            [
                "pandoc",
                str(cover),
                *[str(p) for p in preprocessed],
                f"--output={tmp_pdf}",
                "--pdf-engine=xelatex",
                "--toc",
                "--toc-depth=2",
                "--number-sections",
                "--variable", "geometry:margin=2.5cm",
                "--variable", "fontsize=11pt",
                "--variable", "colorlinks=true",
                "--variable", "linkcolor=blue",
                "--variable", "urlcolor=blue",
                "--variable", "toccolor=black",
                f"--metadata=title=Living Networked Compendium {version}",
                "--metadata=author=Community Contributors",
                f"--metadata=date={build_date}",
                "--syntax-highlighting=tango",
            ],
            check=True,
            cwd=str(tmp_dir),
        )

        shutil.copy2(str(tmp_pdf), str(out_pdf))
        print(f"   PDF written to: {out_pdf}")

        manifest = out_dir / "MANIFEST.md"
        write_manifest(manifest, version, build_date, modules)
        print(f"   Manifest written to: {manifest}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\nDone. Handout {version} is ready in: {out_dir}/")
    print("\nNext step: run generate-changelog.sh to produce the change sheet.")


if __name__ == "__main__":
    main()
