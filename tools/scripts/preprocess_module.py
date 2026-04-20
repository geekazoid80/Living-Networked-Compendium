#!/usr/bin/env python3
"""
preprocess_module.py - Transform a module markdown file for a specific output target.

Handles the three-bucket content structure:
  Bucket 1 (Critical)      - regular markdown  -> all outputs
  Bucket 2 (Supplementary) - ??? blocks        -> collapsed web | Notes in PDF
  Bucket 3 (XREF)          - XREF-START/END    -> markdown only, stripped from PDF

Usage:
    python3 preprocess_module.py <input.md> <output.md> <target>

    target: web | pdf | pptx

Behaviour by target:
    web  - pass through unchanged (MkDocs handles ??? natively)
    pdf  - strip XREF; convert admonitions and ??? blocks; insert page breaks
    pptx - strip XREF; convert ??? supplementary to Marp speaker note blocks

Exit code 0 on success, 1 on error.
"""

import sys
import re


def sanitise_yaml_hrules(content: str) -> str:
    """Replace --- thematic breaks in the document body with * * *.

    Pandoc can interpret --- in the body as a YAML metadata block opener
    when processing multi-file inputs. Replacing with * * * (an equivalent
    thematic break) avoids the ambiguity without changing visual output.
    """
    if content.startswith('---'):
        end = content.find('\n---\n', 3)
        if end == -1:
            end = content.find('\n...\n', 3)
        if end == -1:
            return content
        frontmatter = content[:end + 5]
        body = content[end + 5:]
    else:
        frontmatter = ''
        body = content

    body = re.sub(r'^-{3,}\s*$', '* * *', body, flags=re.MULTILINE)
    return frontmatter + body


def prepend_newpage(content: str) -> str:
    """Insert a LaTeX \\newpage raw block before the first # heading (PDF only)."""
    m = re.search(r'^# ', content, re.MULTILINE)
    if m:
        newpage = '```{=latex}\n\\newpage\n```\n\n'
        return content[:m.start()] + newpage + content[m.start():]
    return content


def admonition_to_pdf(content: str) -> str:
    """Convert MkDocs !!! admonition blocks to blockquotes for PDF output."""
    type_labels = {
        'success': 'Standard', 'info': 'Note', 'note': 'Note',
        'tip': 'Tip', 'warning': 'Warning', 'danger': 'Warning',
    }

    def replace_block(m):
        """Render a single admonition block as a blockquote."""
        kind = m.group(1).lower()
        title = m.group(2).strip().strip('"')
        body = m.group(3)
        lines = body.split('\n')
        de_indented = [
            l[4:] if l.startswith('    ') else (l[1:] if l.startswith('\t') else l)
            for l in lines
        ]
        body_text = '\n'.join(de_indented).strip()
        label = type_labels.get(kind, kind.capitalize())
        body_quoted = '\n'.join(f'> {l}' if l else '>' for l in body_text.split('\n'))
        return f'\n> **{label} - {title}**\n>\n{body_quoted}\n'

    pattern = r'^!!!\s+(\w+)\s+"([^"]+)"\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)


def strip_xref(content: str) -> str:
    """Remove everything between XREF-START and XREF-END markers (inclusive)."""
    return re.sub(
        r'<!--\s*XREF-START\s*-->.*?<!--\s*XREF-END\s*-->',
        '',
        content,
        flags=re.DOTALL,
    )


def supplementary_to_pdf_notes(content: str) -> str:
    """Convert ??? supplementary blocks to a LaTeX quote environment for PDF.

    MkDocs ??? details syntax:
        ??? supplementary "Title"
            content

    PDF output uses raw LaTeX begin/end{quote} tags so pandoc processes the
    markdown body but LaTeX handles paragraph wrapping (avoiding the line-
    overflow that occurs with markdown blockquotes in long paragraphs).
    """
    def replace_block(m):
        """Render a single supplementary block as a LaTeX quote."""
        title = m.group(1).strip().strip('"')
        body = m.group(2)
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
        return (
            f'\n`\\begin{{quote}}`{{=latex}}\n\n'
            f'**Notes - {title}**\n\n'
            f'{body_text}\n\n'
            f'`\\end{{quote}}`{{=latex}}\n'
        )

    pattern = r'^\?\?\?[+]?\s+supplementary\s+"([^"]+)"\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)


def supplementary_to_pptx_notes(content: str) -> str:
    """Convert ??? supplementary blocks to Marp speaker note HTML comments."""
    def replace_block(m):
        """Render a single supplementary block as a Marp presenter note."""
        title = m.group(1).strip().strip('"')
        body = m.group(2)
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
        return f'\n<!--\nNotes - {title}:\n\n{body_text}\n-->\n'

    pattern = r'^\?\?\?[+]?\s+supplementary\s+"([^"]+)"\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)


def answer_to_pdf_notes(content: str) -> str:
    """Convert ??? answer blocks to a visible blockquote for PDF output."""
    def replace_block(m):
        """Render a single answer block as a blockquote."""
        body = m.group(1)
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
        body_quoted = '\n'.join(f'> {l}' if l else '>' for l in body_text.split('\n'))
        return f'\n> **Answer:**\n>\n{body_quoted}\n'

    pattern = r'^\?\?\?[+]?\s+answer\n((?:(?:    |\t)[^\n]*\n?)*)'
    return re.sub(pattern, replace_block, content, flags=re.MULTILINE)


def strip_local_md_links(content: str) -> str:
    """Convert local .md file links to plain text for PDF output.

    Links like [text](../../../path/file.md) point to other source files.
    In PDF context they cannot be followed; keeping them causes pandoc to
    attempt media extraction and fail. Replace with just the link text.
    """
    return re.sub(r'\[([^\]]+)\]\([^)]*\.md[^)]*\)', r'\1', content)

def strip_html_comments(content: str) -> str:
    """Remove HTML comments (template guidance) - used for PPTX/PDF."""
    return re.sub(r'<!--(?!.*XREF).*?-->', '', content, flags=re.DOTALL)


def process(input_path: str, output_path: str, target: str) -> None:
    """Transform input_path for target and write to output_path."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if target == 'web':
        result = content

    elif target == 'pdf':
        result = strip_xref(content)
        result = sanitise_yaml_hrules(result)
        result = strip_local_md_links(result)
        result = admonition_to_pdf(result)
        result = supplementary_to_pdf_notes(result)
        result = answer_to_pdf_notes(result)
        result = strip_html_comments(result)
        result = prepend_newpage(result)

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
