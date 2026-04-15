# Private Research Materials

This folder is **gitignored** — it is never committed to the public repository.

It stores local source materials used during research and content development sessions.

---

## Folder Structure

```
private/
├── uploads/        Source documents: PDFs, vendor manuals, slide decks, whitepapers
│                   Drop files here before parsing. Name them descriptively.
│                   e.g. cisco-ios-xe-ospf-guide-2024.pdf
│                   e.g. juniper-junos-bgp-configuration-guide.pdf
│
├── parsed/         Markdown output from parsed uploads.
│                   Each parsed file maps 1:1 to an uploaded source.
│                   e.g. cisco-ios-xe-ospf-guide-2024.md
│                   These are raw extracts — not yet structured as modules.
│
├── research/       Notes, bookmarks, web archive snapshots, reference lookups.
│                   Organised by topic or session date.
│                   e.g. research/ospf-area-types-notes.md
│                   e.g. research/2026-04-15-bgp-communities-research.md
│
└── notes/          Session working notes — rough, temporary, not for publication.
                    Use freely. Nothing here goes to the repo.
```

---

## Workflow: Upload → Parse → Integrate

1. **Drop source material** into `uploads/` with a descriptive filename
2. **Parse to markdown** — ask Claude to read the document and extract key facts into `parsed/`
3. **Review the parsed output** — check for accuracy, note what's vendor-specific vs standard
4. **Integrate into modules** — use the parsed facts to write or update module content in `modules/`
5. **Cite the source** — every fact that comes from a specific document should be cited in the module's References section

---

## Attribution Reminder

Just because a document is in `private/` doesn't change the attribution requirement.

- If you use content from a Cisco configuration guide, cite it
- If you use content from a Juniper Day One book, cite it
- If the source is copyrighted, do not reproduce it verbatim — paraphrase and cite
- RFC text can be quoted directly (public domain)
- Vendor documentation is generally copyright the vendor — summarise, don't copy

See [AI_GUARDRAILS.md](../AI_GUARDRAILS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## What Goes Here

Good candidates for `uploads/`:
- Vendor configuration guides and white papers (Cisco, Juniper, Nokia, Arista, Huawei, ZTE, MikroTik)
- RFC PDFs downloaded locally
- Training slide decks (your own, or openly licensed)
- ITU-T and MEF standards documents
- Textbook chapters (if licensed for personal use)
- Technical blogs or articles saved for reference

Not suitable:
- Confidential employer documents
- Copyrighted textbooks you don't have a licence to use
- Materials with NDA restrictions
