---
# REQUIRED FRONTMATTER — fill in every field before submitting
title: "Module Title Here"
module_id: "XX-NNN"           # Domain prefix + 3-digit number. See INSTRUCTION.md for prefix table.
domain: "fundamentals/xx"     # Path within modules/ (e.g. fundamentals/ip, applied/data-network-engineer)
difficulty: "novice"          # novice | intermediate | advanced | professional
prerequisites: []             # List of module_ids required before this one.
estimated_time: 45            # Minutes including lab time (be honest)
version: "1.0"
last_updated: "YYYY-MM-DD"
maintainer: "@github-handle"
human_reviewed: false         # A human reviewer sets this to true after checking — not the author
ai_assisted: "drafting"       # false | drafting | synthesis | linking | editing
tags: []                      # Searchable keywords
cert_alignment: ""            # e.g. "CCNA 200-301 — 1.1 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: []                   # Vendors covered in Vendor Implementations section
language: "en"                # en | zh-CN | ms | ta (for translated versions, add translated_from:)
---

<!-- ═══════════════════════════════════════════════════════════════════════════
     MODULE TEMPLATE — REMOVE ALL COMMENTS BEFORE SUBMITTING
     Read docs/INSTRUCTION.md Section 3–6 before writing.
     ═══════════════════════════════════════════════════════════════════════════

     THREE BUCKETS:
     ┌─ BUCKET 1: Critical/Key Points ──────────────────────────────────────┐
     │  Regular markdown content. Visible in ALL outputs.                   │
     │  Web: main content | PDF: body text | PPTX: slide content            │
     └──────────────────────────────────────────────────────────────────────┘
     ┌─ BUCKET 2: Supplementary Points ─────────────────────────────────────┐
     │  Wrap in: ??? supplementary "Title"                                  │
     │                 content here                                         │
     │  Web: collapsed | PDF: small-font Notes | PPTX: speaker notes only   │
     └──────────────────────────────────────────────────────────────────────┘
     ┌─ BUCKET 3: Cross-References / Housekeeping ───────────────────────────┐
     │  Wrap in: <!-- XREF-START --> ... <!-- XREF-END -->                  │
     │  Markdown only. Completely stripped from PDF and PPTX.               │
     └──────────────────────────────────────────────────────────────────────┘
-->

## The Analogy

<!-- MANDATORY. Start here. No jargon. One real-world analogy that maps to the concept.
     Then explicitly map analogy terms → technical terms. -->

Think of [concept] like [real-world thing].

[One paragraph describing the analogy in plain, jargon-free language. A layman should understand this completely.]

**Mapping to the technical:**

| Analogy | Technical Term |
|---|---|
| [analogy element 1] | [technical term 1] |
| [analogy element 2] | [technical term 2] |
| [analogy element 3] | [technical term 3] |

---

## Learning Objectives

<!-- 3–5 objectives. Start each with a measurable Bloom's verb:
     Remember/Understand → Apply → Analyse → Evaluate → Create -->

By the end of this module, you will be able to:

1. **[Understand/Define]** — what [concept] is and why it exists
2. **[Apply]** — how to [do the thing] in a real network
3. **[Analyse]** — identify [common issues or trade-offs]
4. **[Evaluate]** — choose between [alternatives] given specific requirements

---

## Prerequisites

<!-- List what the reader must know first, by module_id and one-line note. -->

- [Module Name](../domain/module-file.md) (`XX-NNN`) — specifically, [what you need from it]

If you're new to networking entirely, start with [NW-001 — The OSI Model](../networking/osi-model.md).

---

## Core Content

<!-- BUCKET 1: Write the main lesson here.
     Use ### sub-headings for each major concept.
     Inline ??? supplementary blocks where deeper detail is available.
     Use vendor tabs in the Vendor Implementations section (not here). -->

### [First Major Concept]

[Plain-language explanation first — 2–3 sentences. Then the technical detail.]

[Tables for comparisons. ASCII or Mermaid diagrams for topology. Worked examples inline.]

```text
[Example — a packet trace, a calculation, a config snippet — generic/pseudocode here]
```

??? supplementary "Deep Dive: [Optional deeper detail on this concept]"
    [Supplementary content. This will be collapsed on the web, appear as Notes in PDF,
    and as speaker notes in PPTX. It can be as long as needed.]

    [Use full markdown here — tables, code blocks, etc.]

### [Second Major Concept]

[Repeat the pattern.]

??? supplementary "Historical context / Why this exists"
    [Context that's useful but not essential to the core understanding.]

### [Third Major Concept]

<!-- Use as many concepts as the content requires. Don't force exactly three. -->

---

## Vendor Implementations

<!-- Show how major vendors implement this. Use tabbed syntax — all vendors equal.
     Put only the CRITICAL config/behaviour differences here (Bucket 1).
     Use ??? supplementary inside tabs for deeper vendor-specific detail. -->

The standard behaviour is defined in [RFC XXXX / IEEE 802.xx]. All compliant implementations share [core behaviour]. The differences below are in syntax and [any genuine behavioural differences].

!!! success "Standard — [RFC XXXX / IEEE 802.xx / ITU-T]"
    [What the standard mandates. One paragraph.]

=== "Cisco IOS-XE"
    ```cisco-ios
    ! [Minimal working configuration]
    ```
    [One-line note on any Cisco-specific behaviour or defaults.]

    ??? supplementary "Cisco-specific: [topic]"
        [Deeper Cisco detail — proprietary features, show commands, etc.]

=== "Juniper Junos"
    ```junos
    # [Minimal working configuration]
    ```
    [One-line note.]

    ??? supplementary "Juniper-specific: [topic]"
        [Deeper Juniper detail.]

=== "Nokia SR-OS"
    ```nokia-sros
    # [Minimal working configuration]
    ```

=== "Arista EOS"
    ```arista-eos
    ! [Minimal working configuration]
    ```

=== "Huawei VRP"
    ```huawei-vrp
    # [Minimal working configuration]
    ```

<!-- Add or remove vendor tabs based on what's relevant for this topic.
     Minimum for routing/switching: Cisco + Juniper + Nokia.
     Add Arista for DC topics. Add Huawei for SP/DC topics.
     Use proprietary callouts where appropriate: -->

!!! warning "Proprietary — Vendor Specific"
    [Vendor X feature name] — only works on [Vendor X] equipment. Does not interoperate.
    [Brief description of what it does and when it matters.]

---

## Common Pitfalls

### Pitfall 1: [Name]

[What the mistake looks like, why people make it, observable symptom, how to fix.]

### Pitfall 2: [Name]

[Repeat pattern.]

---

## Practice Problems

<!-- 3–5 problems that require thinking, not just recall.
     Mix application, analysis, and evaluation questions. -->

1. [Specific problem with enough detail to actually work through.]

2. [Problem that requires comparing two approaches or vendors.]

3. [Problem that requires applying the concept to a design scenario.]

??? "Answers"
    **1.** [Answer with explanation — the reasoning matters as much as the result.]

    **2.** [Answer.]

    **3.** [Answer.]

---

## Lab

<!-- Optional but strongly encouraged. Omit only if truly impractical. -->

### Lab: [Lab Title]

**Tools:** [Packet Tracer | GNS3 | Containerlab | CLI access | vendor simulator]
**Estimated time:** [X minutes]
**Objective:** [What the learner will build and verify.]

**Topology:**
```text
[ASCII diagram — label interfaces and addresses]
```

**Steps:**

1. [Specific step with exact commands.]

    ```cisco-ios
    [commands]
    ```

2. [Verification step — what does success look like?]

    ```text
    [Expected output]
    ```

??? supplementary "Lab extension: [Optional harder challenge]"
    [A stretch goal for faster learners. Not required.]

---

## Summary & Key Takeaways

<!-- BUCKET 1 only. Bullet list. Should function as a standalone refresher.
     Someone who finished the module should re-orient in 60 seconds by reading this. -->

- [Key point 1 — state it as a fact]
- [Key point 2]
- [Key point 3]
- [Key point 4]
- [Key point 5]

---

## Where to Next

- **Continue:** [Module Name](../domain/module-file.md) (`XX-NNN`) — [one line]
- **Related:** [Module Name](../domain/module-file.md) (`XX-NNN`) — [why relevant]
- **Applied context:** [Learning Path or Applied Module](../../applied/path/file.md) — [how this is used in role]

---

## Standards & Certifications

<!-- Benchmark references only. Do not frame content around cert objectives. -->

**Relevant standards:**
- [RFC XXXX — Title](https://www.rfc-editor.org/rfc/rfcXXXX)
- [IEEE 802.xx — Title]
- [ITU-T G.xxx — Title]

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | [Exam section] |
| JNCIA-Junos JN0-103 | Juniper | [Exam section] |
| Nokia NRS I | Nokia | [Exam section] |
| Huawei HCIA-Routing & Switching | Huawei | [Exam section] |

---

## References

<!-- Authoritative sources only. RFCs, IEEE, ITU-T, vendor official docs, established textbooks. -->

- IETF — [RFC XXXX: Title](https://www.rfc-editor.org/rfc/rfcXXXX)
- [Author] — *[Book Title]*, [Edition], [Publisher], [Year] — Ch. [X], pp. [X–Y]
- [Vendor] — [Official documentation page](https://...)

---

## Attribution & Licensing

**Author:** [@github-handle]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** [Describe what AI was used for and what was verified against which sources]

<!-- If adapted from third-party material: -->
<!-- **Adapted from:** [Title] by [Author], licensed under [License], [URL] -->

---

<!-- XREF-START -->
## Internal Cross-References

<!-- BUCKET 3 — Markdown only. Stripped from PDF and PPTX by build scripts.
     Maintain these bidirectionally: when you add a reference here,
     add a back-reference in the target module's XREF section too.
     Update the "Last checked" date whenever you verify a link is still accurate. -->

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [XX-NNN](../path/file.md) | [Title] | [Why it references this module] | YYYY-MM-DD |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [XX-NNN](../path/file.md) | [Title] | [What it's needed for] | YYYY-MM-DD |

### Vendor Mapping

<!-- Record how each vendor implements the concept covered here.
     Update this when new vendor information is added. -->

| Concept | Standard | Cisco | Juniper | Nokia | Arista | Huawei |
|---|---|---|---|---|---|---|
| [concept] | [RFC/std] | [Cisco term/feature] | [Juniper term] | [Nokia term] | [Arista term] | [Huawei term] |

### Maintenance Notes

<!-- Record any "when this changes, also update these" relationships. -->

- When [X] is updated, also check [Y module] — it references [specific section]
- This module's [section] maps to [Applied Path X, Stage Y]

<!-- XREF-END -->
