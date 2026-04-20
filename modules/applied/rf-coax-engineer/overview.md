---
title: "Applied: RF-Coax / Cable Network Engineer - Overview"
module_id: "RCE-000"
domain: "applied/rf-coax-engineer"
difficulty: "intermediate"
prerequisites: ["NW-001", "IP-001", "IP-002", "AM-005", "AM-006", "AM-008"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, cable, hfc, docsis, coax, rf-coax, access-network]
---

## The Analogy

Think of a cable TV network like the plumbing in a large apartment building. One main water main (the fibre trunk from the headend) runs down the street. At each block, a smaller pipe branches off (the coax distribution). Every apartment taps off that smaller pipe. Everyone in the building shares the same water pressure - and the same pipe.

Now add the internet: instead of one flow of water going one way, the pipe carries data in both directions simultaneously - downstream to you and upstream from you - on different frequency bands, like different radio stations sharing the same airwave. The more neighbours sharing the pipe, the more contention. That's the fundamental engineering challenge of cable/HFC networks.

**Mapping:**
| Analogy | Technical Term |
|---|---|
| Main water main | Fibre trunk (fibre node) |
| Smaller pipe to block | Coaxial distribution cable |
| Apartment tap | Subscriber drop |
| Different frequency bands | DOCSIS upstream/downstream spectrum |
| Shared pipe | Shared medium (CSMA/CD heritage) |
| Water pressure | RF signal level (dBmV) |

---

## What Is an RF-Coax / Cable Network Engineer?

A cable network engineer designs and operates **Hybrid Fibre-Coaxial (HFC)** networks - the infrastructure used by cable operators (MSOs) to deliver broadband internet, TV, and phone services over a mix of optical fibre and coaxial cable.

Day-to-day responsibilities include:
- Designing HFC plant: fibre nodes, amplifier cascades, tap values, signal levels
- Deploying and managing DOCSIS (Data Over Cable Service Interface Specification) infrastructure
- Configuring and troubleshooting Cable Modem Termination Systems (CMTS)
- Managing RF spectrum for upstream and downstream channels
- Planning network upgrades: DOCSIS 3.0 → 3.1 → 4.0; node splitting; Remote PHY / Remote MACPHY
- Integrating HFC access with IP backbone and internet infrastructure

**Where you'll find these engineers:** Cable operators (StarHub in Singapore, Comcast/Charter in North America, Virgin Media in UK, Liberty Global), telcos with HFC infrastructure, and equipment vendors (Cisco, Casa Systems, Harmonic, CommScope).

---

## Why This Is a Distinct Path

Cable network engineering is genuinely different from both IP networking and pure RF work:

- **Shared medium:** DOCSIS is fundamentally a shared-access technology. Upstream scheduling, noise ingress, and node utilisation are central operational concerns that don't exist in fibre-to-the-home or enterprise networking.
- **RF plant engineering:** You need to understand signal levels, noise floors, amplifier gain/tilt, and the physical characteristics of coaxial cable - concepts from RF engineering, not IP networking.
- **DOCSIS specifics:** DOCSIS is a complex suite of standards covering not just data, but QoS, security, voice, and increasingly, Remote PHY architectures. It's proprietary in culture (Cable Labs) but now mostly open.
- **Converging with IP:** Modern HFC networks increasingly look like IP networks at the edge (DOCSIS 3.1 OFDM, Remote PHY, DAA). An RF-coax engineer who can't work with IP routing, DHCP, and L2 is increasingly limited.

---

## Proposed Stage Overview

**Stage 1 - Foundation:**
NW-001 (OSI), IP-001 (IP addressing), IP-002 (Subnetting), AM-005 (Coax/DOCSIS basics), AM-008 (RF over optical/HFC)

**Stage 2 - RF Plant Engineering:**
RF-001 (RF fundamentals), AM-006 (Optical grey), AM-007 (Coloured optical - CWDM/DWDM for HFC trunks)

**Stage 3 - DOCSIS Deep Dive:**
DOCSIS 1.x/2.0/3.0 (channel bonding), DOCSIS 3.1 (OFDM/OFDMA, full-duplex), DOCSIS 4.0

**Stage 4 - CMTS & Network Architecture:**
CMTS configuration, IP address management for subscribers, DHCP at scale, QoS in DOCSIS (SFID, classifiers)

**Stage 5 - Remote PHY / DAA (Distributed Access Architecture):**
Fibre-deep architectures, Remote PHY Device (RPD), Converged Cable Access Platform (CCAP), CableLabs R-PHY spec

**Stage 6 - Operations & Provisioning:**
Subscriber provisioning (TFTP/HTTPS config files), signal level monitoring, upstream noise management, node utilisation and splitting decisions

---

## See Full Learning Path

[learning-paths/rf-coax-engineer.md](../../../learning-paths/rf-coax-engineer.md) *(pending - see TASK.md)*

## Call for Contributors

HFC engineering is a niche area. Engineers with hands-on CMTS experience (Cisco, Casa, Harmonic), plant RF experience, or DOCSIS 3.1/4.0 deployment experience are particularly needed.

Open a GitHub Issue with label `rf-coax-path`.
