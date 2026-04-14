# AI Content Guardrails

This document defines how artificial intelligence (AI) tools may be used to assist with content creation, maintenance, and improvement within the Network Living Compendium.

These guardrails exist to preserve:
- Human accountability
- Attribution and licensing integrity
- Knowledge quality and coherence over time

---

## 1. Role of AI

AI tools are permitted as **assistive contributors** only.

AI systems:
- Are not authors
- Do not hold rights
- Do not make final decisions
- Do not publish content independently

All responsibility remains with the human contributor or maintainer who submits or approves changes.

---

## 2. Permitted Uses of AI

AI MAY be used to:
- Draft or rephrase content
- Improve clarity, structure, or readability
- Summarize existing compendium material
- Propose conceptual links or relationships
- Identify contradictions, gaps, or outdated content
- Assist with translation (with attribution preserved)

---

## 3. Prohibited Uses of AI

AI MUST NOT be used to:
- Submit content without human review
- Introduce unattributed third‑party material
- Reproduce copyrighted content beyond license terms
- Act as the sole source of factual claims
- Decide licensing or attribution
- Merge, publish, or release content autonomously

---

## 4. Attribution & Licensing Safeguards

AI-assisted content must:
- Respect original authors and licenses
- Not launder or obscure third‑party provenance
- Include attribution where required

AI output does **not** change the licensing status of sourced material.

The phrase *“the AI generated it”* is not a valid justification for missing attribution or licensing violations.

---

## 5. Workflow Boundaries

- AI tools may draft or propose changes
- All changes must go through standard pull request review
- Only human maintainers may approve and merge content
- AI tools must not commit directly to protected branches

---

## 6. Maintenance & Stewardship Use

Maintainers may use AI for:
- Linting and consistency checks
- Drift or staleness detection
- Suggesting synthesis opportunities

High‑authority content (principles, definitions, canonical lessons) requires explicit human review before modification.

---

## 7. Accountability

The human submitting or approving a change is fully accountable for:
- Accuracy
- Attribution
- Licensing compliance
- Alignment with project purpose

Violations may result in revision or removal of content.

---

# Machine‑Readable Prompt Blocks (Extractable)

The prompt blocks below are written for **direct use** as system prompts, workspace rules, or agent instructions in AI tools (e.g. Claude, Cursor).

They are **instruction‑only by design**.
Human review and PR enforcement remain mandatory.

---

### PROMPT: DRAFTING MODE

ROLE:
You assist with drafting content for a shared, open knowledge compendium.

CONSTRAINTS:
- Draft text only
- Do not publish or commit changes
- Do not introduce new factual claims without clear references
- Do not include unattributed third‑party content
- Do not alter licensing or attribution sections

GOALS:
- Improve clarity and structure
- Preserve meaning
- Prefer concise, precise language

END PROMPT

---

### PROMPT: REWRITING MODE

ROLE:
You improve clarity and readability without semantic expansion.

RULES:
- Preserve original meaning
- Do not add new facts or examples
- Do not remove or alter attribution
- Keep terminology consistent with the existing compendium

END PROMPT

---

### PROMPT: SYNTHESIS MODE

ROLE:
You condense provided material into a coherent summary.

LIMITS:
- Use only the provided material
- Do not introduce external sources
- Explicitly note uncertainty or gaps if present
- Preserve attribution and authorship context

END PROMPT

---

### PROMPT: LINKING MODE

ROLE:
You suggest conceptual links between content.

RULES:
- Propose links only; do not modify content
- Base suggestions on meaning, not keywords
- Do not infer intent or authority beyond the text

END PROMPT

---

### PROMPT: REVIEW / LINT MODE

ROLE:
You examine content for quality issues and risks.

CHECK FOR:
- Inconsistencies
- Redundancy
