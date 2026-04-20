---
id: CT-008
title: "MEF Standards & Carrier Ethernet Framework"
description: "How MEF defines Carrier Ethernet service types, attributes, and performance metrics — E-Line, E-LAN, E-Tree, E-Access — standardising the commercial and technical vocabulary for Ethernet services."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - CT-003
  - SW-002
learning_path_tags:
  - CE
difficulty: intermediate
tags:
  - mef
  - carrier-ethernet
  - e-line
  - e-lan
  - e-tree
  - evc
  - cen
  - service-attributes
created: 2026-04-19
updated: 2026-04-19
---

# CT-008 — MEF Standards & Carrier Ethernet Framework

## The Problem

An enterprise customer wants a WAN Ethernet service between their sites. They contact three service providers. Each provider describes the service differently:

- Provider A: "Point-to-point Ethernet over our MPLS backbone"
- Provider B: "Virtual private LAN service, full mesh"
- Provider C: "Any-to-any Ethernet service with CIR/EIR bandwidth"

The customer cannot compare these services technically or contractually — the vocabulary is inconsistent. What bandwidth guarantee means, what service attributes are included, how performance is measured, what failover behaviour looks like — all differ by provider and sometimes by salesperson.

**MEF** (MEF Forum, formerly Metro Ethernet Forum) solves this by defining standard service types, attributes, and performance parameters for Carrier Ethernet services — giving providers and customers a common vocabulary.

### Step 1: Define service connectivity types

MEF defines four **Ethernet Virtual Connection (EVC)** types based on connectivity topology:
- **E-Line:** Point-to-point (two UNIs). A virtual circuit between exactly two sites.
- **E-LAN:** Multipoint-to-multipoint (any-to-any). All sites can communicate with all others.
- **E-Tree:** Rooted multipoint. One hub (root) communicates with all spokes (leaves); leaves cannot communicate directly with each other.
- **E-Access:** Wholesale access. An access provider delivers connectivity to a service provider's network.

### Step 2: Standardise the interface and attributes

The **UNI (User-Network Interface)** is the demarcation point between the customer's equipment and the provider's network. MEF specifies UNI attributes: speed, frame format, COS (Class of Service) identification, and bandwidth profiles.

### Step 3: Define performance metrics

MEF specifies standardised performance metrics (delay, jitter, frame loss) for each EVC. Providers can advertise exact performance guarantees that customers can independently verify.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Provider's standardised Ethernet service framework | MEF (MEF Forum) standards |
| Virtual circuit between UNIs | EVC (Ethernet Virtual Connection) |
| Demarcation point between customer and provider | UNI (User-Network Interface) |
| Point-to-point EVC | E-Line |
| Any-to-any multipoint EVC | E-LAN |
| Hub-and-spoke EVC | E-Tree |
| Committed information rate (guaranteed bandwidth) | CIR |
| Excess information rate (burst rate) | EIR |
| Committed burst size | CBS |
| Excess burst size | EBS |

---

## Learning Objectives

After completing this module you will be able to:

1. Describe the four MEF EVC types and their connectivity models.
2. Explain UNI and its key attributes.
3. Describe MEF bandwidth profiles — CIR, EIR, CBS, EBS, and their token bucket model.
4. Explain MEF service attributes — frame delivery, multiplexing, bundling.
5. Describe MEF performance parameters — FD, FDV, FLR.
6. Map MEF service types to underlying MPLS/Ethernet technologies.

---

## Prerequisites

- CT-003 — MPLS L2VPN (VPLS & Pseudowire): underlying technology for MEF services
- SW-002 — VLANs & 802.1Q Trunking: CE-VLAN and S-tag (802.1ad) framing

---

## Core Content

### MEF EVC Types

**E-Line (MEF 6.x):**
Point-to-point connection between exactly two UNIs. Equivalent to a leased line or pseudowire.

```
Site A ─── UNI-A ─── [Provider Network] ─── UNI-Z ─── Site Z
```

Variants:
- **EPL (Ethernet Private Line):** Dedicated, non-multiplexed — one EVC per UNI port. Full transparency of Ethernet frames including VLAN tags.
- **EVPL (Ethernet Virtual Private Line):** Multiplexed — multiple EVCs per UNI (multiple customers or services per port). Uses CE-VLAN ID to identify each EVC.

**E-LAN (MEF 6.x):**
Multipoint-to-multipoint — all UNIs can communicate with all others. Equivalent to VPLS.

```
Site A ─── UNI-A ─┐
Site B ─── UNI-B ─┤ Any-to-any
Site C ─── UNI-C ─┘
```

Variants:
- **EP-LAN (Ethernet Private LAN):** One EVC per port. Full transparency.
- **EVP-LAN (Ethernet Virtual Private LAN):** Multiplexed EVCs per port using CE-VLAN.

**E-Tree (MEF 6.x):**
Rooted multipoint — one root UNI, multiple leaf UNIs. Root can communicate with all leaves; leaves cannot communicate with each other. Used for point-to-multipoint services (IPTV, internet access from a hub).

**E-Access (MEF 51.x):**
Wholesale access service. An access provider (separate from the service provider) delivers connectivity from a UNI at the customer site to an ENNI (External Network-to-Network Interface) at the service provider edge. E-Access is the Carrier Ethernet equivalent of a local loop.

### UNI — User-Network Interface

The UNI is the physical and logical interface between the customer equipment (CE) and the provider's network (CEN — Carrier Ethernet Network). Key UNI attributes:

| Attribute | Description |
|---|---|
| **Physical speed** | 10 Mbps, 100 Mbps, 1 GbE, 10 GbE, 100 GbE |
| **Frame format** | Standard Ethernet; 802.1Q tagged or untagged |
| **CE-VLAN ID preservation** | Whether customer VLAN tags are preserved transparently |
| **Max frame size** | Maximum frame size accepted (default 1522 bytes for tagged) |
| **UNI multiplexing** | Whether multiple EVCs share the UNI |
| **Bundling** | Multiple CE-VLANs mapped to one EVC |

### MEF Bandwidth Profiles

MEF defines bandwidth profiles using a **dual token bucket model** (two rate, three colour):

| Parameter | Description |
|---|---|
| **CIR (Committed Information Rate)** | Guaranteed throughput — green traffic |
| **CBS (Committed Burst Size)** | Maximum burst at CIR rate — green bucket depth |
| **EIR (Excess Information Rate)** | Best-effort additional bandwidth — yellow traffic |
| **EBS (Excess Burst Size)** | Maximum excess burst — yellow bucket depth |

Traffic colouring:
- **Green (≤ CIR + CBS bucket):** Forwarded with lowest drop probability.
- **Yellow (≤ EIR + EBS bucket, exceeds CIR):** Forwarded if bandwidth is available; dropped first under congestion.
- **Red (exceeds both):** Dropped at the UNI.

Bandwidth profiles can be applied per-UNI (ingress policing for all traffic entering the UNI) or per-EVC (per-service policing for multiplexed services).

### MEF Performance Attributes

MEF specifies performance attributes per EVC with objective values the provider commits to in the SLA:

| Attribute | MEF Term | Definition |
|---|---|---|
| One-way frame delay | FD | Maximum delay for a frame from UNI-A to UNI-Z |
| Frame delay variation | FDV (jitter) | Maximum variation in delay between successive frames |
| Frame loss ratio | FLR | Ratio of lost frames to total transmitted frames |
| Availability | Availability | Percentage of time the service meets FD and FLR objectives |
| Mean time to restore | MTTR | Average recovery time after a fault |

These parameters map directly to ITU-T Y.1731 OAM measurements — providers use Y.1731 to measure and report these values.

### 802.1ad (QinQ) — Provider Bridging

For services that carry customer VLAN tags (CE-VLAN) transparently, the provider wraps an additional VLAN tag (S-VLAN, service VLAN) around the customer's frame using **802.1ad (QinQ)**:

```
[Provider S-VLAN 802.1ad tag][Customer C-VLAN 802.1Q tag][Ethernet payload]
```

- **S-VLAN:** Provider-assigned, identifies the EVC.
- **C-VLAN:** Customer-assigned, preserved transparently.

This allows the provider to carry thousands of customer VLANs without VLAN ID conflicts (customer VLANs in different EVCs can have the same number — they're in different S-VLAN tunnels).

### ENNI — External Network-to-Network Interface

The **ENNI** is the interface between two provider networks. Used in multi-carrier deployments where E-Line or E-LAN services span multiple providers (inter-carrier Ethernet). The ENNI defines how operators interconnect their networks to deliver end-to-end EVCs.

### Technology Mapping

| MEF Service | Common implementation |
|---|---|
| E-Line / EPL | Pseudowire (EoMPLS), dedicated physical circuit |
| E-Line / EVPL | MPLS pseudowire with VLAN-based mux, QinQ |
| E-LAN / EP-LAN | VPLS (RFC 4762/4761), EVPN (RFC 7432) |
| E-LAN / EVP-LAN | VPLS with CE-VLAN bridging, EVPN-VXLAN |
| E-Tree | VPLS with split-horizon, EVPN E-Tree (RFC 8317) |
| E-Access | NNI hand-off from access provider to service provider |

---

## Common Pitfalls

1. **Confusing CIR with link speed.** CIR is the guaranteed bandwidth for the EVC — it may be much less than the UNI physical speed. An enterprise may have a 1 GbE UNI but only a 100 Mbps CIR for their E-Line service. Traffic above CIR is yellow (best-effort) up to EIR, then red (dropped). Many customers assume their service is as fast as the physical port.

2. **CE-VLAN bundling vs multiplexing.** Bundling maps multiple CE-VLANs to one EVC (e.g., CE-VLANs 10–20 all in one EVC, losing VLAN distinction at the far end). Multiplexing creates separate EVCs per CE-VLAN (each VLAN gets its own bandwidth profile and QoS). These are different services — verify which the customer needs before ordering.

3. **EVPL without CE-VLAN preservation.** Some EVPL implementations do not preserve CE-VLAN tags — they strip and re-tag at the far end. This breaks customer protocols that rely on VLAN identity. Verify the provider's CE-VLAN ID preservation attribute in the service specification.

4. **Misunderstanding E-Tree leaf isolation.** In E-Tree, leaves cannot communicate with each other — traffic between two leaf sites must flow through the root. If an enterprise needs any-to-any connectivity between all sites, they need E-LAN, not E-Tree. E-Tree is for hub-and-spoke architectures (internet breakout from hub, content delivery from root to leaves).

5. **Applying bandwidth profiles in the wrong direction.** MEF bandwidth profiles are typically applied on ingress at the UNI (policing traffic entering the provider network from the customer). Applying them on egress (toward the customer) means the provider is policing traffic it is delivering — this should instead be a scheduling/shaping commitment, not a policer.

---

## Practice Problems

**Q1.** A customer has 20 branches and a single head office. All branch traffic must pass through the head office before reaching other branches. Which MEF EVC type is appropriate, and why?

??? answer
    **E-Tree**: The head office is the root; branches are leaves. E-Tree enforces hub-and-spoke connectivity: leaves can communicate with the root but not directly with each other. This matches the customer's requirement exactly and is more efficient than E-LAN (which would allow direct branch-to-branch communication that the customer doesn't need and the IT team would need to block with firewalls anyway). E-Tree also simplifies security: only the head office firewall provides internet access and inter-branch routing.

**Q2.** An enterprise orders a 500 Mbps CIR E-Line with EIR 200 Mbps on a 1 GbE UNI. They burst to 800 Mbps for 10 seconds. What happens to their traffic?

??? answer
    Traffic up to 500 Mbps is green — forwarded with guaranteed delivery and lowest drop priority. Traffic from 500 Mbps to 700 Mbps (CIR + EIR) is yellow — forwarded on a best-effort basis; dropped first if the provider network is congested. Traffic above 700 Mbps is red — dropped at the UNI ingress policer. During the 800 Mbps burst: 500 Mbps guaranteed delivery, up to 200 Mbps additional is best-effort (may or may not get through depending on provider network load), and the remainder (up to 100 Mbps) is dropped. The 1 GbE physical port allows up to 1 GbE of physical throughput but the bandwidth profile enforces the CIR/EIR limits regardless.

**Q3.** What is the difference between EPL and EVPL?

??? answer
    **EPL (Ethernet Private Line):** Dedicated UNI — one EVC per UNI port. All frames entering the UNI belong to the single EVC. The full UNI bandwidth is dedicated to this service. Provides complete Ethernet frame transparency including CE-VLAN tags (the customer's VLAN structure is preserved end-to-end). **EVPL (Ethernet Virtual Private Line):** Multiplexed UNI — multiple EVCs share one UNI port, distinguished by CE-VLAN ID. Each CE-VLAN maps to a different EVC (different bandwidth profile, different far-end UNI). Allows multiple services over one physical port. The trade-off: EVPL requires VLAN-based multiplexing at the UNI, and the number of EVCs is limited by CE-VLAN ID space.

---

## Summary & Key Takeaways

- **MEF** standardises Carrier Ethernet service types, attributes, and performance metrics — enabling comparable, contractual service definitions between providers and customers.
- **EVC types:** E-Line (point-to-point), E-LAN (any-to-any), E-Tree (hub-and-spoke), E-Access (wholesale).
- **EPL vs EVPL:** Dedicated UNI vs multiplexed (multiple EVCs per UNI via CE-VLAN).
- **Bandwidth profile:** CIR (guaranteed green), EIR (best-effort yellow), red (dropped) — dual token bucket.
- **Performance attributes:** FD (frame delay), FDV (jitter), FLR (frame loss ratio) — independently measurable via Y.1731.
- **802.1ad (QinQ):** Provider S-VLAN wraps customer C-VLAN — allows overlapping customer VLANs across the provider network.
- EVPL requires CE-VLAN preservation to be contractually specified; verify before ordering.
- Technology map: E-Line → pseudowire; E-LAN → VPLS or EVPN; E-Tree → VPLS split-horizon or EVPN E-Tree.

---

## Where to Next

- **CT-009 — Carrier Ethernet Services:** Operational design and deployment of MEF services on MPLS/EVPN infrastructure.
- **CT-003 — MPLS L2VPN:** VPLS and pseudowire implementation of MEF E-Line and E-LAN.
- **CT-006 — EVPN Fundamentals:** EVPN implementation of MEF E-LAN and E-Tree.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| MEF 6.3 | Ethernet Virtual Connection Services |
| MEF 51.x | E-Access Services |
| MEF 10.4 | Ethernet Services Attributes |
| MEF 23.x | Bandwidth Profile |
| ITU-T Y.1731 | OAM for Ethernet — performance measurement |
| MEF CECP | Carrier Ethernet Certification Programme |
| Cisco CCIE Service Provider | MEF services, E-Line, E-LAN |

---

## References

- MEF 6.3 — Ethernet Virtual Connection Services. Available via MEF membership: [https://www.mef.net/resources/mef-6-3/](https://www.mef.net/resources/mef-6-3/)
- MEF 10.4 — Ethernet Service Attributes. [https://www.mef.net/resources/mef-10-4/](https://www.mef.net/resources/mef-10-4/)
- ITU-T Y.1731 — OAM Functions and Mechanisms for Ethernet-Based Networks. [https://www.itu.int/rec/T-REC-Y.1731](https://www.itu.int/rec/T-REC-Y.1731)

---

## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| CT-009 | Carrier Ethernet Services | Operational deployment of MEF-defined services |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-003 | MPLS L2VPN (VPLS & Pseudowire) | VPLS implements MEF E-LAN services |
| SW-002 | VLANs & 802.1Q Trunking | CE-VLAN and 802.1ad (QinQ) for MEF services |
<!-- XREF-END -->
