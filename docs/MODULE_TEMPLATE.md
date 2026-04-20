---
# REQUIRED FRONTMATTER - fill in every field before submitting
title: "Module Title Here"
module_id: "XX-NNN"           # Domain prefix + 3-digit number. See INSTRUCTION.md for prefix table.
domain: "fundamentals/xx"     # Path within modules/ (e.g. fundamentals/ip, applied/data-network-engineer)
difficulty: "novice"          # novice | intermediate | advanced | professional
prerequisites: []             # List of module_ids genuinely required before this one (not "related topics").
estimated_time: 45            # Minutes including lab time (be honest)
version: "1.0"
last_updated: "YYYY-MM-DD"
maintainer: "@github-handle"
human_reviewed: false         # A human reviewer sets this to true after checking - not the author
ai_assisted: "drafting"       # false | drafting | synthesis | linking | editing
tags: []                      # Searchable keywords
cert_alignment: ""            # e.g. "CCNA 200-301 - 1.1 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: []                   # Vendors covered in Vendor Implementations section
language: "en"                # en | zh-CN | ms | ta (for translated versions, add translated_from:)
---

<!-- ═══════════════════════════════════════════════════════════════════════════
     MODULE TEMPLATE - REMOVE ALL COMMENTS BEFORE SUBMITTING
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

     SECTION ORDER - do not change this sequence:
       1. Learning Objectives
       2. Prerequisites
       3. The Problem
       4. Core Content
       5. Vendor Implementations (omit if not applicable)
       6. Common Pitfalls
       7. Practice Problems
       8. Lab (omit if truly impractical)
       9. Summary & Key Takeaways
      10. Where to Next
      11. Standards & Certifications
      12. References
      13. Attribution & Licensing
      14. Internal Cross-References (XREF - stripped from PDF/PPTX)
-->

## Learning Objectives

<!-- MANDATORY. 3–5 objectives. Each must be a capability statement - something the reader will be
     able to DO after finishing this module. Start with a Bloom's taxonomy verb.

     BAD (topic list, not a capability):
       - Understand the OSI model layers
       - Know what encapsulation means

     GOOD (capability statements):
       - Identify which OSI layer is responsible for a given symptom and use that to narrow a fault
       - Explain why a frame header is stripped at the receiving node rather than passed up intact
       - Choose the correct layer to apply a policy given a specific network design requirement

     If you cannot write a capability statement for an objective, the objective is too vague. -->

By the end of this module, you will be able to:

1. **[Verb]** - [what the reader can do with this knowledge in a real situation]
2. **[Verb]** - [second capability]
3. **[Verb]** - [third capability]
4. **[Verb]** - [fourth capability, if needed]

---

## Prerequisites

<!-- List what the reader must genuinely know before this module makes sense.
     "Genuinely required" means: if they lack this knowledge, they will not be able to follow
     the Core Content. Related or useful-but-optional knowledge goes in "Where to Next" instead.

     Do NOT list a module as a prerequisite if this module builds that concept from first principles.
     Example: OSI model should not be a prerequisite for a module that constructs the OSI model
     step by step - it IS the thing being taught. -->

- [Module Name](../domain/module-file.md) (`XX-NNN`) - specifically, [what you need from it]

If you're new to networking entirely, start with [NW-001 - The OSI Model](../networking/osi-model.md).

---

## The Problem

<!-- MANDATORY. 2–4 sentences maximum. Pose the motivating question or scenario that makes
     the reader ask "how do you solve that?" Do NOT walk through the solution here - that is
     Core Content. The Problem is the frame, not the lesson.

     For FOUNDATIONAL modules: one plain-language scenario involving two parties, one sentence
     saying it works, then one sentence introducing the constraint that breaks it.
     For ADVANCED modules: one technical situation that exposes the gap this module fills.

     If you find yourself writing more than a short paragraph, stop - the extra content
     belongs in Core Content as named subsections. -->

[One sentence: the situation works.] [One or two sentences: here is the constraint that breaks it, and why the obvious fix is not good enough.] [Optional: the question this module answers.]

---

## Core Content

<!-- BUCKET 1: Write the main lesson here.
     Use ### sub-headings for each major concept - each concept gets its own heading, its own
     number, its own visual weight. Readers must be able to see where one concept ends and
     another begins.

     If your module builds a concept step by step (as OSI does), each step is a ### subsection
     here, not a sub-step inside The Problem.

     Inline ??? supplementary blocks where deeper detail is available.
     Use vendor tabs in the Vendor Implementations section (not here). -->

### [First Major Concept]

[Plain-language explanation first - 2–3 sentences. Then the technical detail.]

[Tables for comparisons. ASCII diagrams in fenced code blocks for topology. Worked examples inline.]

```text
[Example — a packet trace, a calculation, a config snippet — generic/pseudocode here]
```

??? supplementary "Deep Dive: [Optional deeper detail on this concept]"
    [Supplementary content. Collapsed on web, appears as Notes in PDF, speaker notes in PPTX.]

    [Use full markdown here - tables, code blocks, etc.]

### [Second Major Concept]

[Repeat the pattern.]

??? supplementary "Historical context / Why this exists"
    [Context that is useful but not essential to the core understanding.]

### [Third Major Concept]

<!-- Use as many concepts as the content requires. Do not force exactly three. -->

---

## Vendor Implementations

<!-- Show how major vendors implement this. Use tabbed syntax - all vendors equal.
     Put only the CRITICAL config/behaviour differences here (Bucket 1).
     Use ??? supplementary inside tabs for deeper vendor-specific detail. -->

The standard behaviour is defined in [RFC XXXX / IEEE 802.xx]. All compliant implementations share [core behaviour]. The differences below are in syntax and [any genuine behavioural differences].

!!! success "Standard - [RFC XXXX / IEEE 802.xx / ITU-T]"
    [What the standard mandates. One paragraph.]

=== "Cisco IOS-XE"
    ```cisco-ios
    ! [Minimal working configuration]
    ```
    [One-line note on any Cisco-specific behaviour or defaults.]

    ??? supplementary "Cisco-specific: [topic]"
        [Deeper Cisco detail - proprietary features, show commands, etc.]

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

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # [Minimal working configuration]
    ```
    Full configuration reference: [MikroTik documentation](https://help.mikrotik.com)

<!-- VENDOR TAB RULES:
     - Show a MINIMAL config snippet - enough to understand the key parameters and compare syntax
       across vendors. This is not a full working config; it highlights concept-critical lines only.
     - Follow each snippet with: Full configuration reference: [vendor doc link]
     - Add or remove tabs based on what is relevant for this topic.
       Minimum for routing/switching: Cisco + Juniper + Nokia.
       Add Arista for DC topics. Add Huawei for SP/DC/carrier topics. Add MikroTik where docs exist.
     - If documentation for a feature cannot be found for a vendor, omit that tab silently.
     - Platform context (what each OS runs on, where it is commonly deployed) lives in the
       Platform Overview reference - do not repeat it in module content. -->

!!! warning "Proprietary - Vendor Specific"
    [Vendor X feature name] - only works on [Vendor X] equipment. Does not interoperate.
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
    **1.** [Answer with explanation - the reasoning matters as much as the result.]

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

2. [Verification step - what does success look like?]

    ```text
    [Expected output]
    ```

??? supplementary "Lab extension: [Optional harder challenge]"
    [A stretch goal for faster learners. Not required.]

---

## Summary & Key Takeaways

<!-- THREE-TIER RULE - this is Tier 3 (synthesis), not a repeat of Tier 2 (Core Content).

     Tier 1: Learning Objectives + The Problem - "what I am going to tell you"
     Tier 2: Core Content - "what I am telling you"
     Tier 3: Summary - "what I have told you, told another way"

     The Summary must NOT copy sentences or bullet points from Core Content. If a sentence here
     could be pasted into Core Content unchanged, rewrite it or cut it.

     Instead, the Summary should:
     - Abstract upward: state the principle behind the details
       (NOT "Mesh uses N(N-1)/2 cables" - YES "every topology trades cost against resilience")
     - Connect back to the opening problem: "The question was X - the answer is Y"
     - Use a different framing or angle from Core Content where possible
     - Close with what the reader can now do or where this knowledge leads next

     BAD (copy of Core Content facts):
       - The OSI model has 7 layers: Physical, Data Link, Network...
       - Encapsulation adds a header at each layer going down the stack

     GOOD (synthesis):
       - The model's value is not its layer names - it is a structured fault-isolation tool.
         When something breaks, you eliminate layers from the bottom up until you find the one
         that is misbehaving.
       - Every protocol you will encounter maps to one or two layers; understanding which layer
         owns which problem is what makes troubleshooting systematic rather than guesswork. -->

[2–5 sentences or short bullet points that synthesise, not recap. Connect back to The Problem.
Close with what the reader can now do that they could not do before.]

---

## Where to Next

- **Continue:** [Module Name](../domain/module-file.md) (`XX-NNN`) - [one line]
- **Related:** [Module Name](../domain/module-file.md) (`XX-NNN`) - [why relevant]
- **Applied context:** [Learning Path or Applied Module](../../applied/path/file.md) - [how this is used in role]

---

## Standards & Certifications

<!-- Authoritative standards only. Do not frame content around cert objectives. -->

**Relevant standards:**
- [RFC XXXX - Title](https://www.rfc-editor.org/rfc/rfcXXXX)
- [IEEE 802.xx - Title]
- [ITU-T G.xxx - Title]

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | [Exam section] |
| JNCIA-Junos JN0-103 | Juniper | [Exam section] |
| Nokia NRS I | Nokia | [Exam section] |
| Huawei HCIA-Routing & Switching | Huawei | [Exam section] |

---

## References

<!-- Authoritative sources only. RFCs, IEEE, ITU-T, vendor official docs, established textbooks. -->

- IETF - [RFC XXXX: Title](https://www.rfc-editor.org/rfc/rfcXXXX)
- [Author] - *[Book Title]*, [Edition], [Publisher], [Year] - Ch. [X], pp. [X–Y]
- [Vendor] - [Official documentation page](https://...)

---

## Attribution & Licensing

**Author:** [@github-handle]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** [Describe what AI was used for and what was verified against which sources]

<!-- If adapted from third-party material: -->
<!-- **Adapted from:** [Title] by [Author], licensed under [License], [URL] -->

---

<!-- XREF-START -->
## Internal Cross-References

<!-- BUCKET 3 - Markdown only. Stripped from PDF and PPTX by build scripts.
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
| [XX-NNN](../path/file.md) | [Title] | [What it is needed for] | YYYY-MM-DD |

### Vendor Mapping

<!-- Record how each vendor implements the concept covered here.
     Update this when new vendor information is added. -->

| Concept | Standard | Cisco | Juniper | Nokia | Arista | Huawei |
|---|---|---|---|---|---|---|
| [concept] | [RFC/std] | [Cisco term/feature] | [Juniper term] | [Nokia term] | [Arista term] | [Huawei term] |

### Maintenance Notes

<!-- Record any "when this changes, also update these" relationships. -->

- When [X] is updated, also check [Y module] - it references [specific section]
- This module's [section] maps to [Applied Path X, Stage Y]

<!-- XREF-END -->
