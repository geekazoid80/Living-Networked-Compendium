#!/usr/bin/env python3
"""
preprocess-module.py — Transform a module markdown file for a specific output target.

Handles the three-bucket content structure:
  Bucket 1 (Critical)    — regular markdown  → all outputs
  Bucket 2 (Supplementary) — ??? blocks      → collapsed web | Notes in PDF | speaker notes in PPTX
  Bucket 3 (XREF)        — XREF-START/END    → markdown only, stripped from PDF and PPTX

Usage:
    python3 preprocess-module.py <input.md> <output.md> <target>

    target: web | pdf | pptx

Behaviour by target:
    web  — pass through unchanged (MkDocs handles ??? natively)
    pdf  — strip XREF blocks; convert ??? supplementary to a "Notes" section with smaller visual hint
    pptx — strip XREF blocks; convert ??? supplementary content to Marp speaker note blocks (^^)

Exit code 0 on success, 1 on error.
"""

import sys
import re

def strip_xref(content: str) -> str:
    """Remove everything between XREF-START and XREF-END markers (inclusive)."""
    return re.sub(
        r'<!--\s*XREF-START\s*-->.*?<!--\s*XREF-END\s*-->',
        '',
        content,
        flags=re.DOTALL
    )

def supplementary_to_pdf_notes(content: str) -> str:
    """
    Convert ??? supplementary "Title" blocks to a Notes callout for PDF output.

    MkDocs ??? details syntax:
        ??? supplementary "Title"
            content

    PDF output:
        > **Notes — Title**
        > content

    This preserves the content in the PDF as clearly marked supplementary material
    in a distinct visual style (blockquote = indented, visually separated).
    """
    def replace_block(m):
        title = m.group(1).strip().strip('"')
        body = m.group(2)
        # De-indent the body (remove 4-space indent from ??? block)
        lines = body.split('\n')
        de_indented = []
        for line in lines:
            if line.startswith('    '):
                de_indented.append(line[4:])
            elif line.startswith('\t'):
                de_indented.append(line[1:])
            else:
                de_indented.append(line)
        body_text = '\n'.join(de_indented).strip()
        # Format as blockquote Notes section
        body_quoted = '\n'.join(f'> {l}' if l else '>' for l in body_text.split('\n'))
        return f'\n> **Notes — {title}**\n>\n{body_quoted}\n'

    # Match ??? supplementary "Title"\n    body (indented block)
    pattern = r'^\?\?\?[+]?\s+supplementary\s+"([^"]+)"\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)

def supplementary_to_pptx_notes(content: str) -> str:
    """
    Convert ??? supplementary "Title" blocks to Marp speaker notes for PPTX output.

    Marp speaker notes use HTML comment blocks starting with <!--:
        <!-- Title: content -->
    Or the standard Marp convention of a paragraph starting with ^^ in some themes.
    We use the HTML comment convention which Marp renders as presenter notes.
    """
    def replace_block(m):
        title = m.group(1).strip().strip('"')
        body = m.group(2)
        # De-indent
        lines = body.split('\n')
        de_indented = []
        for line in lines:
            if line.startswith('    '):
                de_indented.append(line[4:])
            elif line.startswith('\t'):
                de_indented.append(line[1:])
            else:
                de_indented.append(line)
        body_text = '\n'.join(de_indented).strip()
        # Format as Marp speaker note (HTML comment — Marp strips these from slides,
        # shows in presenter view)
        return f'\n<!--\nNotes — {title}:\n\n{body_text}\n-->\n'

    pattern = r'^\?\?\?[+]?\s+supplementary\s+"([^"]+)"\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)

def strip_html_comments(content: str) -> str:
    """Remove HTML comments (template guidance) — used for PPTX/PDF."""
    return re.sub(r'<!--(?!.*XREF).*?-->', '', content, flags=re.DOTALL)

def process(input_path: str, output_path: str, target: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if target == 'web':
        # Web: pass through unchanged. MkDocs handles ??? natively.
        # Only strip HTML template comments (not XREF markers).
        result = content  # leave as-is; MkDocs does the rendering

    elif target == 'pdf':
        result = strip_xref(content)
        result = supplementary_to_pdf_notes(result)
        result = strip_html_comments(result)

    elif target == 'pptx':
        result = strip_xref(content)
        result = supplementary_to_pptx_notes(result)
        result = strip_html_comments(result)

    else:
        print(f"ERROR: Unknown target '{target}'. Use: web | pdf | pptx", file=sys.stderr)
        sys.exit(1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input.md> <output.md> <target>", file=sys.stderr)
        sys.exit(1)
    process(sys.argv[1], sys.argv[2], sys.argv[3])
