# Contribution Specification

This document defines the **accepted contribution types, structural requirements, and review criteria** for the Network Living Compendium.

It exists to ensure contributions are:
- High quality
- Coherent with the compendium
- Legally and ethically sound
- Consistent over time

This specification complements:
- CONTRIBUTING.md (process)
- AI_GUARDRAILS.md (AI usage)
- LICENSE (legal terms)

---

## 1. Scope of Contributions

The compendium accepts contributions that increase shared understanding, practical usefulness, or structural coherence.

Out of scope:
- Personal notes without synthesis
- Opinion pieces without reasoning or context
- Marketing, promotion, or advocacy content
- Undocumented AI‑generated dumps

---

## 2. Contribution Types

### 2.1 Knowledge Contributions
- Concepts and definitions
- Principles and frameworks
- Patterns and playbooks
- Explanatory lessons
- Case‑derived insights (anonymized where required)

### 2.2 Synthesis Contributions
- Summaries of multiple related lessons
- Cross‑domain connections
- Conceptual unification or clarification

### 2.3 Corrective Contributions
- Error corrections
- Clarifications
- Updates to outdated material

### 2.4 Structural Contributions
- Reorganization for clarity
- Improved linking and navigation
- Taxonomy or categorization improvements

### 2.5 Tooling & Automation
- Scripts or workflows supporting the compendium
- Validation, linting, or consistency tools
- Visualization aids

---

## 3. Required Metadata (Knowledge Content)

### 3.1 Editorial intent

Each substantive knowledge contribution must clearly include:
- **Title** — the module body's opening level-1 heading, in the form `# <module_id> - <title>`, matching the frontmatter `module_id` and `title` fields (see § 3.2). Enforced by CI.
- **Purpose** (what this helps a reader understand or do)
- **Context** (assumptions, prerequisites, scope)
- **Core Content**
- **References / Sources** (if applicable)
- **Attribution** (original author or adapted sources)
Exact formatting of the remaining elements is flexible, but intent must be clear. The Title form above is fixed because it drives the rendered page heading and the document outline.

### 3.2 Knowledge‑module frontmatter (operational catalogue)

Modules under `modules/` additionally carry a YAML frontmatter block that the CI validator enforces. This catalogue layer exists for indexability, prerequisite resolution, and navigation; it sits alongside the editorial intent in §3.1, not in place of it.

Required keys:

| Key | Value shape | Notes |
|---|---|---|
| `title` | quoted string | Human‑readable module title. |
| `module_id` | quoted string `<PREFIX>-<NNN>` | Globally unique within the corpus. Established prefixes include `NW`, `IP`, `RT`, `SEC`, `SW`, `QOS`, `SV`, `CT`, `AUTO`, `AM`, `BRD`, `CE`, `DC`, `DCE`, `DNE`, `PS`, `RCE`, `RME`, `RSE`, `SNE`, `VTE`. |
| `domain` | quoted string, path under `modules/` | The directory the file lives in, e.g. `"fundamentals/routing"`, `"applied/data-network-engineer"`. Mechanically derivable from file location. |
| `difficulty` | `beginner` / `intermediate` / `advanced` | Reader skill threshold. |
| `prerequisites` | YAML list of `module_id` strings | Inline (`["RT-001", "NW-002"]`) or block‑list shape both accepted. Empty list (`[]`) is valid for foundational modules. |
| `estimated_time` | integer (minutes) | Realistic study time, not minimum reading time. |
| `version` | quoted SemVer `MAJOR.MINOR.PATCH` | Three-component form required, e.g. `"1.0.0"`. Two-component values (`"1.0"`) are rejected by CI. |
| `last_updated` | ISO date `"YYYY-MM-DD"` | Quoted. Authoritative for "is this stale" checks. |
| `maintainer` | quoted GitHub handle `"@<handle>"` | The accountable steward, not necessarily the original author. |
| `human_reviewed` | boolean | `false` is permitted on drafts. Per `AI_GUARDRAILS.md`, `true` is required before a module is treated as authoritative. The CI validator checks presence, not truth. |
| `ai_assisted` | quoted string or `false` | E.g. `"drafting"`, `"editing"`, `"synthesis"`, or `false` if no AI assistance was used. |

Optional supplementary keys (`tags`, `vendors`, `language`, `cert_alignment`, `description`, `module_type`, `status`) may appear and are not validator‑gated. They are documented per author convention rather than spec‑mandated.

`learning_path_tags` was retired in favour of build-time reverse navigation: each module page now links up to its learning paths, derived from the hand-curated stage tables in `learning-paths/` (see `tools/scripts/inject_learning_paths.py`).

### 3.3 Learning-path stage-table schema

Each file in `learning-paths/` sequences modules through stages. Every stage table uses one canonical five-column schema:

```
| Order | Module ID | Title | Status | Est. Time |
```

- `Order` is the module's position in the path's overall sequence. Some paths begin numbering above 1 because their earliest stage references a prerequisite block rather than a table.
- `Module ID` holds the `<PREFIX>-<NNN>` token, optionally as a markdown link to the module page. Reverse navigation keys on this token alone (`inject_learning_paths.py` reads only this column); the remaining columns are presentation.
- `Title` is the learner-facing label. It need not match the module's frontmatter `title` verbatim, since a path may add context for its audience (for example a protocol number or a scope note).
- `Status` is build-readiness: `done` (module written and build-ready), `pending` (the module file exists but is not yet marked build-ready), or `needed` (no module file exists yet).
- `Est. Time` is the learner study budget. Leave the cell blank when the module is not yet written and no realistic estimate exists; do not invent a time.

`Status` and `Est. Time` are orthogonal and both columns are retained: one signals curation state to stewards, the other signals study effort to learners. Resource and certification tables elsewhere in a path use their own column shapes and are not stage tables.

The validator job in `.github/workflows/build-deploy.yml` is the executable definition; this table is its prose mirror. If the two ever diverge, the spec is authoritative and the validator must catch up (per §9).

---

## 4. Content Standards

All contributions must:
- Be understandable without private context
- Make assumptions explicit
- Prefer explanation over assertion
- Use consistent terminology
- Avoid unnecessary verbosity
- Preserve intellectual honesty (uncertainty is allowed and encouraged)

---

## 5. Attribution & Licensing Integrity

Contributors must:
- Attribute third‑party material clearly
- Respect original licenses
- Avoid implicit relicensing
- Prefer over‑attribution to under‑attribution

AI‑assisted content does not alter attribution obligations.

---

## 6. AI‑Assisted Contributions

AI may assist with:
- Drafting
- Editing
- Synthesis
- Structural suggestions

AI may not:
- Act as the author of record
- Introduce unattributed content
- Decide licensing or attribution

All AI use is governed by `AI_GUARDRAILS.md`.

---

## 7. Review & Acceptance Criteria

Maintainers evaluate contributions based on:
- Alignment with the compendium’s purpose
- Clarity and coherence
- Structural fit
- Attribution correctness
- Long‑term usefulness

Meeting these criteria does not guarantee acceptance; maintainers may request revisions or defer contributions.

---

## 8. Maintenance & Evolution

Some contributions aim to:
- Reduce redundancy
- Improve consistency
- Address drift or staleness

These are valid and encouraged, even when no new content is added.

---

## 9. Authority

This specification is authoritative for contribution evaluation.
When conflicts arise, maintainers interpret and apply this document in service of the compendium’s long‑term integrity.

End of Specification
