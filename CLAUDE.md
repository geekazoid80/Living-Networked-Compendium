# Claude Context – Network Living Compendium

## Project North Star

Before scoping any work in this repository (content, validation, tooling, or governance) measure every priority decision against the project's stated purpose:

> A living, community-curated network-engineering compendium of atomic, linked, multi-vendor lessons sequenced by role, designed to compound in usefulness over time under human stewardship.

Derived from: README.md opening, CONTRIBUTING.md § 2 Philosophy, AI_GUARDRAILS.md § 7 Final Principle, CONTRIBUTION_SPEC.md § 1 Scope.

### Qualities to defend (priority order when work items conflict)

1. **Coherence / no entropy.** Stewardship infrastructure (validators, checks, gates) takes precedence. Bad data is hard to fix later; a closed gate prevents new noise.
2. **Interconnectedness / no orphans.** Every lesson links into a learning path; orphan modules silently break the map the README promises. Cross-link health and nav coverage are north-star concerns.
3. **Atomic, readable lessons.** Each module is intelligible to a reader without private context (CONTRIBUTING.md § 2: "Assume future readers do not share your context").
4. **Multi-vendor parity + multi-format outputs.** No vendor is the default; one source produces web + PDF + PPTX. Build chains that bias one platform are entropy.
5. **Catalogue indexability.** Frontmatter drives navigation, search, prerequisite resolution, and learning-path sequencing. Catalogue cosmetics are TIER 2 unless a field actually drives surface behaviour (e.g. `tags`, which feeds the rendered tag index), in which case it promotes.

### Tiering rule for work selection

- **TIER 1**: directly defends a north-star quality. Land first.
- **TIER 2**: improves a north-star quality but not on the critical path. Land after TIER 1.
- **TIER 3**: tooling hygiene; does not directly serve the north star unless visibly blocking contributors. Land last.

Apply the tier first; only then weigh scope size, mechanical convenience, and reviewer load. A TIER 3 item never jumps a TIER 1 item just because it is smaller or easier.

---

This repository is governed by strict contribution, licensing, and AI‑use rules.

Claude, before generating, editing, synthesizing, or reviewing any content in this repository, you MUST do the following:

## 1. Mandatory Context Loading

You MUST read and follow these documents in full:

- AI_GUARDRAILS.md  
- CONTRIBUTION_SPEC.md  
- CONTRIBUTING.md  

If any instructions conflict:
- AI_GUARDRAILS.md takes precedence
- CONTRIBUTION_SPEC.md is the authoritative source for structure, licensing, and validation

## 2. Acknowledgement Requirement

After reading and ingesting the repository context, you MUST acknowledge once with:

> ✅ Context loaded. Guardrails and contribution rules understood.

Do not repeat this acknowledgement unless context is reloaded.

## 3. Binding Behavioral Rules

You MUST:

- Treat all AI output as *draft assistance*, never authority
- Preserve and surface all attribution and provenance metadata
- Never invent sources, licenses, or citations
- Never relicense or obscure third‑party material
- Enforce required frontmatter, structure, and relationship sections
- Require `human_reviewed: true` for any AI‑assisted contribution

When provenance, licensing, or evidence is unclear:
- STOP
- Flag the issue
- Request human clarification

## 4. Forbidden Actions

You MUST NOT:

- Assume content is original without explicit declaration
- Introduce new policies, licenses, or rules
- Self‑approve, self‑merge, or declare content “correct”
- Flatten or remove network structure or relationships
- Generate content that bypasses contribution validation rules

## 5. Failure Mode

If you cannot comply with the guardrails or contribution spec:

- Do not proceed
- Explain the blocking issue in plain language
- Defer to human stewards

## 6. Final Principle

AI accelerates understanding.  
Stewardship remains human.

These rules are binding for all Claude interactions with this repository.
