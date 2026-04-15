---
title: "Applied: RF Mobile / Cellular Network Engineer — Overview"
module_id: "RME-000"
domain: "applied/rf-mobile-engineer"
difficulty: "advanced"
prerequisites: ["NW-001", "IP-001", "IP-002", "RF-001", "RF-002", "RF-003", "AM-010"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, mobile, cellular, 4g, lte, 5g, ran, backhaul, core-network]
---

## The Analogy

Think of a cellular network like a city of hexagonal neighbourhoods, each with a town hall in the middle. Your phone constantly listens for the loudest town hall nearby and stays connected to it. When you walk from one neighbourhood into the next, your call seamlessly hands off from one town hall to the next — so smoothly you don't notice.

Every town hall communicates back to a regional government centre, which connects to the national capital. The regional centres manage resources (which neighbourhood uses which frequency), handle handoffs between neighbourhoods, and connect calls to the rest of the world.

The challenge of mobile engineering: thousands of overlapping neighbourhoods, millions of moving phones, all sharing limited radio spectrum — orchestrated in real time.

**Mapping:**
| Analogy | Technical Term |
|---|---|
| Hexagonal neighbourhood | Cell (coverage area) |
| Town hall in the centre | Base station / eNB (4G) / gNB (5G) |
| Walking between neighbourhoods | Handover / Handoff |
| Regional government centre | EPC (4G core) / 5GC (5G core) |
| National capital | Internet Gateway / PDN-GW |
| Which neighbourhood uses which frequency | Frequency reuse planning / spectrum management |
| Town hall ↔ regional centre link | Backhaul (microwave, fibre, satellite) |

---

## What Is an RF Mobile / Cellular Network Engineer?

A mobile network engineer plans, deploys, and optimises the radio and core infrastructure that delivers cellular connectivity. The role spans:

- **Radio Access Network (RAN):** Base station planning, RF optimisation, antenna configuration, coverage and capacity planning
- **Backhaul:** Microwave, fibre, and satellite links connecting base stations to the core network
- **Core Network:** EPC (4G) or 5G Core (5GC) — the packet core that handles authentication, mobility management, and internet connectivity
- **Network Slicing (5G):** Carving virtual networks from shared physical infrastructure for different service types
- **Roaming:** How your phone works in a foreign operator's network (SS7/DIAMETER signalling between operators)

**Where you'll find these engineers:** Mobile network operators (Singtel, StarHub, M1 in Singapore; the major regional operators across SEA), tower companies (IHS Martel, ATC), equipment vendors (Ericsson, Nokia, Huawei, ZTE — the dominant four), and network planning consultancies.

---

## Why This Is a Distinct Path

Mobile engineering sits at the intersection of RF physics, IP networking, and highly specialised telecom standards:

- **3GPP is the standards body.** Unlike the IETF (internet) or IEEE (LAN), mobile networks are standardised by 3GPP. Understanding which release defines what is essential. LTE is Release 8+. 5G NR is Release 15+.
- **The air interface is the hardest part.** OFDM, MIMO, beamforming, interference coordination — these are RF and signal processing concepts that most IP engineers have never encountered.
- **The core is its own world.** The 4G EPC and 5G Core are complex distributed systems with their own protocols (GTP, DIAMETER, HTTP/2, SBA in 5G) that overlap with but are not the same as enterprise networking.
- **Backhaul connects RAN to core.** This is where RF backhaul engineers, IP transport engineers, and satellite engineers all intersect. A base station in a remote area may use microwave or VSAT backhaul — topics that span this path and the RF/satellite path.

---

## Proposed Stage Overview

**Stage 1 — Foundation (RF + IP):**
RF-001 (RF fundamentals), RF-002 (Modulation — OFDM is central to LTE/5G), RF-003 (Antennas — MIMO), AM-010 (Mobile networks 2G→5G overview), IP-001, IP-002, RT-001

**Stage 2 — Radio Access Network:**
LTE RAN architecture (eNB, S1, X2 interfaces), 5G NR concepts (gNB, Massive MIMO, beamforming), Cell planning (coverage, capacity, interference), SON (Self-Organising Networks)

**Stage 3 — Backhaul:**
Microwave point-to-point links, Ethernet/MPLS transport for backhaul, Timing/synchronisation (PTP/IEEE 1588 — critical for LTE/5G), Satellite backhaul (link to RSE path)

**Stage 4 — Packet Core:**
4G EPC (MME, SGW, PGW, HSS, PCRF), 5G Core SBA (AMF, SMF, UPF, UDM, PCF), GTP tunnelling, DIAMETER (4G) vs HTTP/2 (5G), Network slicing concepts

**Stage 5 — Operations & Optimisation:**
KPI monitoring (RSRP, RSRQ, SINR, throughput), RAN optimisation techniques, Interference management, SON algorithms, Drive testing

**Stage 6 — Emerging Topics:**
Private 5G (enterprise campus 5G), Open RAN (O-RAN Alliance), Network slicing for vertical industries, Edge computing (MEC — Multi-access Edge Computing)

---

## See Full Learning Path

[learning-paths/rf-mobile-engineer.md](../../../learning-paths/rf-mobile-engineer.md) *(pending)*

## Call for Contributors

Open a GitHub Issue with label `rf-mobile-path`. Engineers with 4G/5G core, RAN optimisation, or backhaul experience especially welcome.
