# Compendium Session Instructions

Persistent instruction reference for all Claude sessions. Read this file and `docs/TASK.md` at the start of every session before doing any work.

---

## 1. Project Mission

Build a progressive, modular educational compendium for **network engineers** - from novice to professional - grounded in what a Singapore polytechnic or university IS/CS/EE graduate already knows.

**Scope:** Enterprise, carrier/SP, data centre, RF/satellite, cable/HFC, mobile, voice/telephony, storage networking, and broadcast.

**Purpose:** Break down vendor-specific speak. Explain things once at the standard/concept level. Then show how each major vendor implements it - objectively, with honest pros and cons. No vendor is default. Cisco is not "the" way; it's one way.

**Voice:** Start with a layman analogy. Map the analogy to the technical. Then show the implementation. This order is mandatory.

The compendium is:
- **Atomic**: every module stands alone and is self-contained
- **Linked**: modules declare prerequisites, next steps, and cross-references
- **Progressive**: modules sequence into learning paths for specific roles
- **Multi-vendor**: standards first, then vendor implementations as equals
- **Three-tier content**: critical facts visible everywhere, supplementary detail collapsible/notes, cross-references markdown-only

---

## 2. Module vs. Learning Path - The Distinction

This is important. Get it wrong and the architecture breaks.

### Module
**What it is:** A self-contained explanation of ONE concept or technology.

**Analogy:** A single textbook chapter. You can read it standalone. It has everything you need to understand that topic.

**Contains:** Analogy → concept → standard definition → vendor implementations → practice → references.

**Does not contain:** "Before this, you should know X" beyond a brief prerequisite list. Does not contain role-specific context. Does not repeat content from other modules.

**Example:** "OSPF Fundamentals" - covers what OSPF is, how it works, how to configure it on major vendors, common pitfalls.

### Learning Path
**What it is:** A curriculum document for a specific engineering role. It lists modules in order, explains what each stage achieves, and provides role context.

**Analogy:** A university course syllabus. It doesn't teach anything itself - it tells you which textbook chapters to read, in what order, and why that sequence makes sense for the degree you're pursuing.

**Contains:** Ordered module list, stage descriptions, role context, suggested pacing, and optional benchmark certifications for self-assessment.

**Does not contain:** Technical content. No explanations, no configs, no analogies. Just structure and sequence.

**Example:** "Carrier/SP Network Engineer path" - lists 30 modules in a specific order, grouped into stages, with a note at each stage on what competency is achieved.

### The Rule
If you're explaining something technical → it goes in a module.
If you're sequencing modules for a role → it goes in a learning path.
Never mix the two.

---

## 3. Three-Bucket Content Structure

Every module is divided into three information buckets. Each bucket renders differently depending on the output medium.

### Bucket 1 - Critical / Key Points
**What goes here:** The core concept. The layman analogy. The standard definition. The things a reader MUST understand. The minimum viable knowledge.

**Rendered in ALL outputs:**
- Web: main visible content
- PDF/Handout: main body text, standard font
- PPTX: slide content (visible on the slide itself)

**Markdown:** Just write it. No special markers needed. Everything that's not Bucket 2 or 3 is Bucket 1.

### Bucket 2 - Supplementary Points
**What goes here:** Deeper dives, edge cases, additional vendor detail, historical context, optional worked examples, "for the curious" content.

**Rendered differently by output:**
- Web: collapsed by default (MkDocs `???` details block)
- PDF/Handout: included but visually distinct - smaller font, indented, labelled "Notes"
- PPTX: speaker notes only (not visible on slide)

**Markdown syntax:**
```markdown
??? supplementary "Deep Dive: How DR/BDR election actually works"
    [Supplementary content here. Can be as long as needed.]
    This renders collapsed on the web, as notes in PDF/PPTX.
```

Use `???` (collapsed by default). If the content should default to open on web but still be "supplementary" in PDF/PPTX, use `???+`.

### Bucket 3 - Cross-References / Mapping / Housekeeping
**What goes here:** Back-references to other modules. Forward references ("this concept is used in…"). Vendor mapping tables. Maintenance notes ("when this module is updated, also update…"). Standard/proprietary classification notes.

**Rendered only in markdown source.** Completely stripped from PDF and PPTX.

**Markdown syntax:**
```markdown
<!-- XREF-START -->
## Internal Cross-References

[Cross-reference content here — tables, links, notes]

<!-- XREF-END -->
```

Everything between `<!-- XREF-START -->` and `<!-- XREF-END -->` is stripped by build scripts before PDF/PPTX generation.

**Maintenance rule:** Every time you update a module, follow its XREF section to identify related modules that may also need updating. Update the XREF sections in related modules bidirectionally.

---

## 4. Module Structure - Section Order

Every module follows this exact section order. Do not reorder, do not skip (except Lab, which is optional).

1. **Frontmatter** (YAML)
2. **The Problem** - progressive build-up from first principles. Two parties, simplest possible scenario. Add constraints one at a time; solve each; name what was invented. End with a summary mapping table. See Section 5 for the full pattern.
3. **Learning Objectives** - 3–5 measurable outcomes (Bloom's verbs)
4. **Prerequisites** - list of module IDs + one line on what specifically you need from each
5. **Core Content** - Bucket 1 content, with Bucket 2 `???` blocks inline where relevant
6. **Vendor Implementations** - tabbed, all vendors as equals. Standard first, then vendor tabs. Bucket 2 for deeper vendor-specific notes.
7. **Common Pitfalls** - the mistakes everyone makes at least once
8. **Practice Problems** - 3–5 problems with collapsed answers
9. **Lab** - optional, hands-on exercise
10. **Summary & Key Takeaways** - Bucket 1 only. Bullet list. Functions as a standalone refresher.
11. **Where to Next** - 2–3 links to next modules or applied path context
12. **Standards & Certifications** - benchmark references only (see Section 7)
13. **References** - authoritative sources cited in the module
14. **Attribution & Licensing**
15. **Internal Cross-References** - Bucket 3, between `<!-- XREF-START -->` and `<!-- XREF-END -->`

---

## 5. The Problem-First Pattern

Every module must open with a **progressive problem build-up** before any technical content. This is mandatory - not optional.

The reader constructs the concept themselves by solving a series of constraints. By the time the formal name appears, they already understand what it is and why it exists.

### The Pattern

1. **Starting scenario** - two parties in the simplest possible situation. No jargon, no technical terms. Describe it working.
2. **Add one constraint** - something breaks or becomes impossible. Describe the problem plainly.
3. **Solve it** - what do the parties invent or agree on? Name it in plain language first, then in technical terms.
4. **Repeat** - add the next constraint, solve it, name it. Use as many steps as the concept genuinely requires.
5. **Summary table** - at the end, map each scenario element to its technical term.

### Which scenario to use

- **Foundational modules** (OSI, IP addressing, subnetting, topologies, cabling): two humans trying to communicate. Start literally - two people standing next to each other.
- **Advanced modules** (OSPF, BGP, MPLS, VLANs, etc.): two systems or operators with a specific technical problem. The scenario is still plain-language, but adapted to the domain.

### Example - NW-001 (OSI Model)

Two people standing next to each other. They want to communicate. They open their mouths and speak. It works - problem solved.

Now move them to different rooms. They can't hear each other. They need a medium - a string between tin cans, a wire, a radio signal. They've just invented the **Physical layer**.

Now there are five people in the room. When you speak, everyone hears you. How does anyone know which message is for them? You agree to start every message with the recipient's name. They've just invented **addressing** - the foundation of the **Data Link layer**.

Now they're in different buildings, with many rooms each. The street-level name alone isn't enough. You need to know which building and which room. They've just invented **logical addressing** - the **Network layer**.

...and so on, through Transport, Session, Presentation, Application.

**Summary table:**

| Scenario element | Technical term |
|---|---|
| The wire, radio wave, or string | Physical layer (L1) |
| "Start every message with the recipient's name" | MAC addressing, Data Link layer (L2) |
| Building + room addressing | IP addressing, Network layer (L3) |
| Guaranteed vs. unguaranteed delivery | TCP vs. UDP, Transport layer (L4) |
| Tracking a long multi-part conversation | Session layer (L5) |
| Agreeing on a shared language / encoding | Presentation layer (L6) |
| The message itself | Application layer (L7) |

### What this achieves

A reader who has never heard of the OSI model now understands *why each layer exists* - not just what it is called. This is the engineering mindset: decompose the problem, identify each constraint, solve it. The same method applies across every domain in the compendium.

---

## 6. Multi-Vendor Guidelines

### The Three-Layer Distinction

Every implementation must be classified as one of:

1. **Standard** - defined by RFC, IEEE, ITU-T, or MEF. Interoperable by specification.
2. **Proprietary - seeking standardisation** - originated with one vendor, submitted to a standards body or adopted by multiple vendors, not yet (or only recently) an official standard.
3. **Proprietary - vendor specific** - works only on that vendor's equipment. Will not interoperate.

### Callout Admonitions

```
!!! success "Standard — RFC / IEEE / ITU-T / MEF"
    Behaviour defined in [RFC XXXX / IEEE 802.xx / ITU-T G.xxx / MEF xx].
    All compliant implementations must behave this way.

!!! info "Proprietary — Seeking Standardisation"
    Originated with [Vendor]. Submitted to [body] as [draft/RFC XXXX] or adopted by [other vendors].
    Behaviour may vary between implementations — verify interoperability before deploying in mixed environments.

!!! warning "Proprietary — Vendor Specific"
    [Vendor]-only feature. Will not work on other vendors' equipment.
    Document clearly in your network design and change records.
```

### Vendor Configuration - Use Tabs

When showing configuration examples for multiple vendors, use MkDocs tabbed syntax. All vendors are equal - no default tab preference:

```markdown
=== "Cisco IOS-XE"
    ```cisco-ios
    router ospf 1
     network 10.0.0.0 0.255.255.255 area 0
    ```

=== "Juniper Junos"
    ```junos
    set protocols ospf area 0.0.0.0 interface ge-0/0/0.0
    ```

=== "Nokia SR-OS"
    ```nokia-sros
    configure router ospf area 0.0.0.0 interface "ge-1/1/1"
    ```

=== "Arista EOS"
    ```arista-eos
    router ospf 1
       network 10.0.0.0/8 area 0.0.0.0
    ```

=== "Huawei VRP"
    ```huawei-vrp
    ospf 1
     area 0.0.0.0
      network 10.0.0.0 0.255.255.255
    ```

=== "MikroTik RouterOS"
    ```mikrotik-ros
    /routing ospf network add network=10.0.0.0/8 area=backbone
    ```
```

Not every module needs every vendor. Minimum for routing/switching topics: **Cisco + Juniper + Nokia**. Add Arista for DC topics. Add Huawei where it's widely deployed. MikroTik for ISP/SME-relevant topics.

### Vendor Tab Rules

- Show a **minimal config snippet** - the lines that illustrate the concept-critical parameters. Not a full working config.
- Follow each snippet with a link to the official vendor documentation for that specific feature: `Full configuration reference: [link]`
- If official documentation for a feature cannot be found for a vendor, **omit that tab silently** - no warning, no explanation.
- Platform context (what each OS runs on, where it is commonly deployed) lives in the **Platform Overview** reference page (`modules/fundamentals/networking/platform-overview.md`). Do not repeat it in module content.

### Vendor Coverage by Domain

| Domain | Vendors |
|---|---|
| Enterprise routing/switching | Cisco IOS-XE, Juniper Junos, Arista EOS, Huawei VRP, MikroTik RouterOS |
| Carrier / SP | Cisco IOS-XR, Juniper Junos, Nokia SR-OS, Huawei VRP, ZTE |
| Data Centre | Arista EOS, Cisco NX-OS, Juniper, Nokia, Huawei |
| RF / Satellite | Vendor-neutral (standards-dominated: DVB, ITU) |
| Cable / HFC | Cisco, Harmonic, Casa Systems (DOCSIS-focused) |
| Mobile / Cellular | Ericsson, Nokia, Huawei, ZTE (RAN-specific), Cisco (core) |
| Voice / Telephony | Cisco, Avaya, Ribbon, Audiocodes, open-source (Asterisk) |
| Storage Networking | Cisco (MDS), Brocade/Broadcom, Pure Storage, NetApp |

---

## 7. Standards & Certifications - Benchmark Only

Certifications appear in modules only as **self-assessment benchmarks** - not as the primary curriculum structure.

**What to include:**
> **Benchmark certifications:** Cisco CCNA 200-301 (3.0 IP Connectivity) | Juniper JNCIA-Junos (JN0-103) | Nokia NRS I

**What not to do:** Don't structure content around exam objectives. Don't say "this is on the CCNA exam." Don't make certifications the reason to learn something.

**Why:** The curriculum is structured around understanding and application, not exam preparation. Certs are signposts a student can use to benchmark themselves - not the destination.

**Vendors to include benchmarks for:**

| Vendor | Cert Track | Levels |
|---|---|---|
| Cisco | CCNA → CCNP → CCIE | Associate → Professional → Expert |
| Juniper | JNCIA → JNCIS → JNCIP → JNCIE | Associate → Specialist → Professional → Expert |
| Nokia | NRS I → NRS II → SRA | Associate → Professional → Expert |
| Arista | ACE-A → ACE-P | Associate → Professional |
| Huawei | HCIA → HCIP → HCIE | Associate → Professional → Expert |
| CompTIA | Network+ | Foundation (vendor-neutral) |
| MEF | MEF-CECP | Carrier Ethernet (vendor-neutral) |

---

## 8. Roles & Responsibilities (Claude's)

### Researcher
Pull from authoritative sources. Parse `private/uploads/` → `private/parsed/`. Never invent facts. Cite everything.

### Ghost Writer
Write modules following the exact section order in Section 4. Analogy first. Bucket 1 content clearly separated from Bucket 2. Bucket 3 at the end.

### Editor
- Check analogy is present and maps explicitly to technical terms
- Check Bucket 2 uses `???` syntax
- Check Bucket 3 is wrapped in XREF markers
- Check vendor tabs are used for multi-vendor configs
- Check standards/proprietary callouts are accurate
- Check cross-references are bidirectional

---

## 9. Language & Style Guide

**Voice:** Direct, casual, technically grounded. Senior engineer explaining to a motivated junior over lunch.

- Second person ("you", "your network") or active third person - never passive
- Short sentences. Break complex ideas into steps.
- Introduce every term on first use: "Open Shortest Path First (OSPF)"
- Use the abbreviation freely after first use
- Use callout admonitions (see Section 6)
- No filler phrases ("it is worth noting", "it should be noted")
- No excessive hedging
- Humour: light and dry, never forced
- Target length per module: 30–60 minutes including lab time

**Difficulty levels:**
- `novice` - what is this, why does it exist, how does it basically work
- `intermediate` - how do I configure it, what are the failure modes
- `advanced` - how does it interact with other systems, how do I design with it
- `professional` - edge cases, RFC-level detail, architecture trade-offs, vendor nuance

---

## 10. Multilingual / Translation Support

The compendium supports multiple languages via a **file-naming convention**. English is the default and canonical language.

**Convention:**
```
osi-model.md           ← English (default, canonical)
osi-model.zh-CN.md     ← Simplified Chinese
osi-model.ms.md        ← Malay (Bahasa Melayu)
osi-model.ta.md        ← Tamil
```

**Rules:**
- The English file is always canonical - all other languages are translations, not separate content
- When the English version is updated, add a flag to the translated files: `translation_status: needs-review`
- Translated files carry the same frontmatter, plus `language:` and `translated_from:` fields
- MkDocs `mkdocs-static-i18n` plugin handles language switching in the web output
- PDF and PPTX builds run per-language when translations exist

**Frontmatter additions for translated files:**
```yaml
language: "zh-CN"
translated_from: "osi-model.md"
translation_status: "current"   # current | needs-review | in-progress
translator: "@github-handle"
translation_date: "YYYY-MM-DD"
```

---

## 11. Professional Standards & Best Practices Domain

A dedicated domain covers the non-technical professional frameworks every network engineer should know. These go in `modules/fundamentals/professional-standards/` (prefix `PS`).

Topics:
- **ITIL** - IT Service Management (incident, change, problem, capacity management)
- **NIST SP 800 series** - Cybersecurity frameworks; SP 800-53 (controls), SP 800-82 (OT/ICS)
- **ISO 27001 / 27002** - Information Security Management System
- **BCP38 / RFC 2827** - Network Ingress Filtering (anti-spoofing best practice)
- **BCP84 / RFC 3704** - Ingress Filtering for Multihomed Networks
- **TIA-942** - Data Centre infrastructure standard (Tier I–IV)
- **MEF 3.0** - Carrier Ethernet service definitions and attributes
- **IEEE 802.x** - The family of LAN/MAN standards
- **IETF BCP documents** - Best Current Practices (not just RFCs)
- **ANSI/TIA-568** - Commercial building telecommunications cabling standard
- **ANSI/TIA-606** - Administration standard for telecommunications infrastructure
- **Network documentation standards** - NetBox, diagramming conventions (Cisco icons, draw.io)
- **IPAM practices** - IP address management, VLAN management, circuit inventory

---

## 12. Additional Subject Areas

Beyond the core networking domains, a well-rounded engineer should be familiar with:

| Area | Where It Fits |
|---|---|
| Cloud networking fundamentals (AWS VPC, Azure VNet, GCP VPC) | New: `applied/cloud-network-engineer` |
| SD-WAN concepts (Cisco Viptela, VMware VeloCloud, Fortinet) | Can be a module in `fundamentals/routing` or applied path |
| Network Function Virtualisation (NFV) and SDN concepts | Module in `fundamentals/carrier-transport` or new domain |
| Disaster recovery & business continuity | Module in `fundamentals/professional-standards` |
| Network documentation & diagramming | Module in `fundamentals/professional-standards` |
| IP Address Management (IPAM) | Module in `fundamentals/protocols` or `professional-standards` |
| Observability & monitoring (Grafana, Prometheus, ELK stack) | Module in `fundamentals/automation` |
| Vendor/contract management basics | Module in `fundamentals/professional-standards` |

---

## 13. Private Research Workflow

When processing materials from `private/uploads/`:

1. Read the document and extract key technical facts, definitions, CLI examples
2. Write raw extracts to `private/parsed/<source-filename>.md` - include source doc name, vendor, version at top
3. Summarise and paraphrase vendor docs (copyright); quote RFCs directly (public domain)
4. Integrate extracted facts into the relevant module
5. Add citation in the module's References section
6. Set `ai_assisted: drafting` in the module frontmatter

---

## 14. Session Workflow

**Start of session:**
1. Read this file (`docs/INSTRUCTION.md`)
2. Read `docs/TASK.md` - check status, identify what to work on
3. Acknowledge: "Context loaded. Resuming from TASK.md."

**During session:**
- Mark tasks `in-progress` before starting them
- Mark tasks `done` immediately on completion
- Add new follow-up items to TASK.md as discovered

**End of session:**
- Ensure TASK.md is current
- Note any new cross-references discovered in relevant module XREF sections

---

## 15. Build & Output Overview

| Output | Tool | Command | Bucket 1 | Bucket 2 | Bucket 3 |
|---|---|---|---|---|---|
| Web (GitHub Pages) | MkDocs | `build-web.sh` | Visible | Collapsed | Hidden |
| PDF Handout | Pandoc | `build-pdf.sh` | Body text | Small font / Notes | Stripped |
| PPTX Slides | Marp | `build-pptx.sh` | Slide content | Speaker notes | Stripped |

Version format: `v{NNN}-{YYYY-MM-DD}`. CI auto-builds on push to `main`.
