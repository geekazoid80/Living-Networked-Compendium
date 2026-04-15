# Living Networked Compendium

A living, community-built body of knowledge for network engineers — from your first "what even is a subnet?" through to designing carrier-grade networks, storage fabrics, and 5G cores. Lessons are atomic, linked, and sequenced by role. The compendium provides the map and the tools; real-world experience completes the journey.

---

## Who Is This For?

Anyone who works with networks or wants to. The assumed baseline is a technical diploma or degree in Information Systems, Computer Science, or Electrical Engineering, or equivalent hands-on experience. If you don't have that background, modules point you to reputable free resources to fill the gaps.

You don't need to read this cover to cover. Pick a learning path, or jump straight to any module you need.

---

## How It's Organised

```
modules/
├── fundamentals/          Standalone atomic modules — one concept per module
│   ├── networking/        OSI model, topologies, Ethernet, cabling
│   ├── ip/                IP addressing, subnetting, IPv6
│   ├── routing/           Static routes, OSPF, IS-IS, BGP
│   ├── switching/         VLANs, STP, EtherChannel, port security
│   ├── services/          DNS, DHCP, NAT, NTP, SNMP
│   ├── security/          ACLs, firewalls, VPN, AAA, encryption
│   ├── qos/               Quality of Service concepts and tools
│   ├── rf/                RF fundamentals, modulation, antennas, link budgets
│   ├── automation/        Python, APIs, Ansible, Terraform, NETCONF
│   ├── access-media/      Physical layer evolution — serial to optical to wireless
│   ├── carrier-transport/ MPLS, SR, EVPN, MEF, OTN
│   ├── datacentre/        Spine-leaf, VXLAN, EVPN-DC, DCI
│   ├── protocols/         One module per standard protocol (DNS, ARP, NTP, SNMP…)
│   ├── functions/         Switching, routing, NAT, ACL, IDS/IPS, DPI, ALG
│   └── professional-standards/  ITIL, NIST, BCP38, TIA-942, ISO 27001, MEF
│
└── applied/               Learning paths that link fundamentals into a role
    ├── data-network-engineer/
    ├── carrier-engineer/
    ├── datacentre-engineer/
    ├── rf-satellite-engineer/
    ├── rf-coax-engineer/
    ├── voice-telephony-engineer/
    ├── rf-mobile-engineer/
    ├── storage-network-engineer/
    └── broadcast-engineer/

learning-paths/            Ordered module sequences per role
labs/                      Hands-on exercises (Packet Tracer, GNS3, CLI)
```

**Fundamental modules** are atomic — each one covers exactly one concept and can be read independently. They are the building blocks.

**Applied paths** link fundamentals into a structured curriculum for a specific engineering role. They sequence and connect the building blocks; they don't repeat them.

---

## Learning Paths

| Path | Who it's for | Status |
|---|---|---|
| [Data Network Engineer](learning-paths/data-network-engineer.md) | Enterprise, carrier, and ISP network engineers | Active |
| [Carrier / SP Engineer](learning-paths/carrier-engineer.md) | Service provider, telco, and backbone engineers | Seeking contributors |
| [Data Centre Engineer](learning-paths/datacentre-engineer.md) | DC fabric, spine-leaf, VXLAN/EVPN engineers | Seeking contributors |
| [RF & Satellite Engineer](learning-paths/rf-satellite-engineer.md) | Engineers working on satellite or RF links | Active |
| [RF-Coax / Cable Engineer](learning-paths/rf-coax-engineer.md) | HFC, DOCSIS, cable broadband engineers | Seeking contributors |
| [Voice / Telephony Engineer](learning-paths/voice-telephony-engineer.md) | SIP, VoIP, PSTN, and UC engineers | Seeking contributors |
| [RF Mobile / Cellular Engineer](learning-paths/rf-mobile-engineer.md) | LTE/5G RAN, core, and backhaul engineers | Seeking contributors |
| [Storage Network Engineer](learning-paths/storage-network-engineer.md) | FC SAN, iSCSI, NVMe-oF engineers | Seeking contributors |
| [Broadcast Network Engineer](learning-paths/broadcast-engineer.md) | Broadcast/media network engineers | Seeking contributors |

---

## Multi-Vendor Coverage

Modules cover technology as the standard describes it, then show how major vendors implement it. Configuration examples use tabbed syntax so no vendor is treated as the default.

Vendors covered include: Cisco (IOS-XE, IOS-XR, NX-OS), Juniper (Junos), Nokia (SR-OS), Arista (EOS), Huawei (VRP), Brocade/Broadcom, and MikroTik (RouterOS) where relevant.

Three layers of vendor content are distinguished:
- **Standard** — defined by RFC/IEEE/ITU; vendor-independent
- **Seeking standardisation** — widely implemented but not yet fully standardised (e.g., EVPN extensions, SR policy)
- **Vendor proprietary** — specific to one vendor, explicitly labelled

---

## Content Structure — Three Buckets

Every module organises content into three tiers:

| Bucket | Format | Web | PDF | PPTX |
|---|---|---|---|---|
| Critical | Plain markdown | Visible | Included | Included |
| Supplementary | `??? supplementary` block | Collapsed | Notes section | Speaker notes |
| Cross-references | `<!-- XREF-START/END -->` | Visible | Stripped | Stripped |

This means a single source file cleanly produces a web page, a printed handout, and a presentation deck — each with the right level of detail for its context.

---

## Certification Alignment

Modules note relevant certifications as **benchmarks** — not as curriculum targets. The curriculum follows skills and standards; certifications are a useful self-assessment tool.

Certifications referenced include: Cisco CCNA/CCNP/CCIE, Juniper JNCIA/JNCIS/JNCIP, Nokia NRS, Arista ACE, Huawei HCIA/HCIP, CompTIA Network+, MEF-CECP, and role-specific specialist certs.

---

## How to Use This Compendium

**Reading online:** Published as a website via GitHub Pages. Navigate by learning path or browse modules directly.

**Handouts and slides:** Versioned PDF handouts and PPTX slides are generated automatically and available as GitHub Release artifacts. Each release is numbered (`v001`, `v002`, …) and dated. A change sheet accompanies each release.

**Offline:** Clone or download the repository. All content is plain Markdown — readable in any text editor, IDE, or Markdown viewer.

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [CONTRIBUTION_SPEC.md](CONTRIBUTION_SPEC.md) first.

Key requirements:
- Every module must follow the template in [docs/MODULE_TEMPLATE.md](docs/MODULE_TEMPLATE.md)
- AI assistance is allowed but all content requires human review before `human_reviewed: true`
- One concept per module — keep it atomic
- Attribution is mandatory — never pass off third-party material as original
- Multi-vendor: include at minimum Cisco and Juniper configuration examples for any CLI content

Interested in contributing to a seeking-contributors path? Open a GitHub Issue with the relevant label (e.g., `carrier-path`, `storage-network-path`).

---

## Licensing

- **Content** (modules, learning paths, documentation): [CC BY-SA 4.0](LICENSE)
- **Code** (scripts, tools, automation): [Apache License 2.0](LICENSE)

---

## Building Locally

```bash
# Install dependencies (Python)
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin

# Serve locally with live reload
mkdocs serve

# Build static site
mkdocs build --strict
```

See [tools/scripts/](tools/scripts/) for PDF and PPTX generation scripts.
