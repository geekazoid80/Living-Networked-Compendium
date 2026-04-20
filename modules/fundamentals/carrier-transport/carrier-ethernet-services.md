---
module_id: CT-009
title: "Carrier Ethernet Services - Design & Operations"
description: "How to design, provision, and operate Carrier Ethernet services using MPLS and EVPN infrastructure - including CoS, OAM, resiliency, and multi-carrier interconnect."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 50
prerequisites:
  - CT-008
  - CT-003
  - CT-006
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - carrier-ethernet
  - mef
  - cos
  - oam
  - y1731
  - cfm
  - resiliency
  - operations
created: 2026-04-19
updated: 2026-04-19
---

# CT-009 - Carrier Ethernet Services - Design & Operations
## Learning Objectives

After completing this module you will be able to:

1. Describe CoS for Carrier Ethernet - mapping customer markings to backbone QoS.
2. Explain CFM (802.1ag) - MEP, MIP, MD levels, and CCM.
3. Describe Y.1731 OAM functions - delay measurement (DMM), loss measurement (LMM), AIS/RDI.
4. Explain resiliency options for Carrier Ethernet - linear protection, ring protection, MPLS FRR.
5. Describe multi-carrier interconnect via ENNI and the operational considerations.
6. Explain service activation testing and acceptance testing for new EVCs.

---
## Prerequisites

- CT-008 - MEF Standards (EVC types, UNI, bandwidth profiles)
- CT-003 - MPLS L2VPN (pseudowire and VPLS implementation)
- CT-006 - EVPN Fundamentals (EVPN-based service implementation)

---
## The Problem

You understand MEF service types (CT-008) and how to implement E-Line over pseudowire or E-LAN over VPLS. But a network engineer provisioning and operating these services day-to-day needs more than technology mapping:

- How do you mark and honour customer traffic classes across the provider backbone?
- How do you detect faults in an Ethernet service without access to the CE?
- How do you meet an SLA commitment when a fibre cuts and you need sub-50ms recovery?
- How do you hand off a service across a carrier boundary?

These operational realities - Class of Service end-to-end, OAM, resiliency design, and inter-carrier interconnect - are what make a paper design into a running service.

### Step 1: Classify and mark traffic at the boundary

The provider's backbone runs QoS policies based on MPLS EXP bits (TC bits) or DSCP. Customer traffic arrives with its own CoS markings (802.1p PCP or DSCP). At the UNI, the PE classifies traffic - either trusting customer markings (if agreed in the SLA) or re-marking based on the service class. All traffic in the backbone is forwarded according to the provider's CoS, not the customer's arbitrary markings.

### Step 2: Detect and isolate faults without customer equipment access

An E-Line service has two UNIs and a pseudowire between them. If the customer reports "the service is down", the provider needs to localise the fault: is it the UNI, the pseudowire, or the backbone? **OAM (Operations, Administration and Maintenance)** tools - specifically **CFM (Connectivity Fault Management, 802.1ag)** and **Y.1731** - provide per-EVC fault detection, localisation, and performance measurement. They operate entirely within the provider network without touching the customer's equipment.

### Step 3: Design for sub-50ms recovery

Single-link or single-node failures are inevitable. Service SLAs specify recovery time objectives (RTOs) that are often 50ms or less. This requires pre-computed protection paths activated by fast failure detection - not waiting for routing reconvergence.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Classifying and marking customer traffic at UNI | CoS mapping / ingress policing |
| Per-EVC fault detection between provider endpoints | CFM (802.1ag) - Connectivity Fault Management |
| Per-EVC performance measurement (delay, loss) | Y.1731 OAM |
| Layer 2 continuity check between MEPs | CCM (Continuity Check Message) |
| Fast fault notification to CE | AIS/RDI (Alarm Indication Signal / Remote Defect Indication) |
| Pre-computed path for fast reroute | Protection switching / FRR |
| MPLS-specific fast reroute | MPLS FRR (RSVP-TE) or TI-LFA (SR) |

---
## Core Content

### Class of Service for Carrier Ethernet

A Carrier Ethernet service may carry multiple traffic classes: voice (delay-sensitive), data (best-effort), management (low bandwidth). The provider must:

1. **Classify** at ingress UNI: which traffic class does this frame belong to?
2. **Mark** in the backbone: map customer marking to backbone CoS field.
3. **Queue** in the backbone: apply appropriate queuing and scheduling.
4. **Remark** at egress UNI: restore or translate CoS for customer equipment.

**802.1p PCP (Priority Code Point):** 3-bit field in the 802.1Q VLAN tag. Values 0–7. Standard mappings: 5–7 = high priority (voice/video); 3–4 = medium (data); 0–2 = low (best-effort).

**MPLS Traffic Class (TC / EXP):** 3-bit field in the MPLS label. The PE maps 802.1p PCP to MPLS TC at ingress. Backbone devices use MPLS TC for QoS. The egress PE maps MPLS TC back to 802.1p PCP.

**MEF CoS service attributes** (MEF 23.x):
- **CoS Name:** Logical class names (Gold, Silver, Bronze - or voice, video, data).
- **Ingress bandwidth profile per CoS:** Separate CIR/EIR per class.
- **Performance objectives per CoS:** Different FD/FDV/FLR targets for voice vs data.

### CFM - Connectivity Fault Management (802.1ag)

CFM provides per-EVC fault detection and localisation using a hierarchy of **Maintenance Domains (MDs)** and **Maintenance End Points (MEPs)**.

**Key concepts:**

| Term | Description |
|---|---|
| **MD (Maintenance Domain)** | Administrative scope - customer domain, provider domain, operator domain |
| **MD Level** | 0–7; higher = wider scope; customer uses level 7, provider uses 3–6, operator uses 0–2 |
| **MEP (Maintenance End Point)** | Originates and terminates OAM messages; typically at UNI or provider edge |
| **MIP (Maintenance Intermediate Point)** | Responds to but does not originate OAM; typically at intermediate nodes |
| **CCM (Continuity Check Message)** | Periodic hello (default 1s); if a MEP stops receiving CCMs from a peer, it raises a defect |

OAM functions:
- **CC (Continuity Check):** MEP-to-MEP periodic CCMs - detect link/path failures.
- **LB (Loopback):** MEP sends a loopback to a target MEP or MIP - identifies which segment is faulty (similar to ping).
- **LT (Linktrace):** Traces the path between MEPs - identifies intermediate MIPs (similar to traceroute).

CFM operates at Layer 2 (Ethernet) - it is transport-agnostic and works over pseudowire, VPLS, or EVPN.

### Y.1731 - Performance Measurement

Y.1731 extends CFM with per-EVC performance measurement:

| Function | ITU Name | Description |
|---|---|---|
| **Delay Measurement** | DMM/DMR | Measures one-way or round-trip frame delay |
| **Synthetic Loss Measurement** | SLM/SLR | Measures frame loss ratio between MEPs |
| **AIS (Alarm Indication Signal)** | ETH-AIS | Downstream MEP sends AIS when upstream failure detected - notifies CE without requiring CE OAM |
| **RDI (Remote Defect Indication)** | ETH-RDI | MEP receiving defective CCMs signals far-end MEP - bidirectional fault notification |

Y.1731 measurements feed directly into SLA monitoring dashboards - providers can prove (or disprove) SLA compliance with timestamped per-EVC measurement data.

=== "Cisco IOS-XE (CFM)"

    ```
    ! Enable CFM globally
    ethernet cfm global
    ethernet cfm ieee

    ! Define Maintenance Domain (MD level 5 = provider)
    ethernet cfm domain PROVIDER level 5
     service EVC-100 evc 100
      continuity-check
      continuity-check interval 1s

    ! MEP on CE-facing interface
    interface GigabitEthernet0/1
     service instance 100 ethernet
      cfm mep domain PROVIDER mpid 1

    ! Verification
    show ethernet cfm maintenance-points local
    show ethernet cfm errors
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cether/configuration/xe-17/ce-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cether/configuration/xe-17/ce-xe-17-book.html)

=== "Juniper Junos (CFM)"

    ```
    # CFM / OAM configuration
    set protocols oam ethernet connectivity-fault-management maintenance-domain PROVIDER level 5
    set protocols oam ethernet connectivity-fault-management maintenance-domain PROVIDER maintenance-association EVC-100 continuity-check
    set protocols oam ethernet connectivity-fault-management maintenance-domain PROVIDER maintenance-association EVC-100 mep 1 interface ge-0/0/1.100 direction down

    # Verification
    show oam ethernet connectivity-fault-management mep-database
    show oam ethernet connectivity-fault-management continuity-check errors
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/oam-ethernet/topics/topic-map/oam-ethernet-cfm.html](https://www.juniper.net/documentation/us/en/software/junos/oam-ethernet/topics/topic-map/oam-ethernet-cfm.html)

### Resiliency Design for Carrier Ethernet

**Linear protection (1+1 or 1:1):** Two paths provisioned per EVC - working and protection. Traffic switches to the protection path on failure. 1+1 = traffic sent on both simultaneously (hitless or near-hitless switching); 1:1 = protection path carries traffic only on failure (allows protection path to carry low-priority traffic).

**Ring protection (ERP - G.8032):** Provider network forms a ring topology. Under normal operation, one link is blocked (ring protection link - RPL). On failure, the RPL is unblocked and traffic reroutes around the ring. Recovery is typically 50ms or less. Simpler than STP; deterministic; designed for carrier rings.

**MPLS FRR (with RSVP-TE):** Pre-computed bypass LSPs protect against link or node failure. On failure, traffic is switched to the bypass tunnel in hardware - sub-50ms. Bypass tunnels are maintained as RSVP-TE state.

**TI-LFA (with SR-MPLS):** As described in CT-004 - automatically pre-computed loop-free alternates, sub-50ms recovery, stateless in the core.

**Pseudowire redundancy:** Two pseudowires provisioned per EVC - primary and backup - to different PE routers. If the primary PE or pseudowire fails, the backup becomes active. Negotiated via LDP status signalling or BGP.

### ENNI - Multi-Carrier Interconnect

When an E-Line spans two providers, an ENNI (External NNI) connects their networks. Each provider:
- Manages their own portion of the EVC.
- Exposes an ENNI with negotiated attributes (S-VLAN, frame size, CoS mapping).
- Runs CFM OAM at the ENNI to detect cross-carrier faults.
- Specifies per-segment SLA objectives that add up to the end-to-end SLA.

Inter-carrier CoS harmonisation is critical - if Provider A marks voice as 802.1p=5 and Provider B expects 802.1p=7, re-marking at the ENNI is required.

### Service Activation Testing

Before a new EVC is handed to the customer:

1. **Physical layer test:** Optical power levels, bit error rate (BER) on the access fibre.
2. **Connectivity test:** CFM LB (loopback) between MEPs - verifies end-to-end L2 connectivity.
3. **Bandwidth profile test:** RFC 2544 or Y.1564 throughput test - verify CIR, EIR, and policer behaviour.
4. **Latency/jitter/loss test:** Y.1731 DMM + SLM measurements against SLA targets.
5. **Failover test:** Deliberately fail the working path; measure recovery time.
6. **CoS test:** Send marked traffic and verify correct queue treatment in the backbone.

**Y.1564** (ITU-T) is the preferred service activation test methodology - it tests each traffic class independently and verifies SLA parameters before service is accepted.

---
## Common Pitfalls

1. **CFM MD level conflicts.** The customer's CFM domain (if they run it) should be at a higher MD level than the provider's. If both use level 5, CCMs from the customer propagate into the provider's management domain - OAM messages interfere, and the customer can see provider network topology. Always configure provider MD at a lower level than the customer MD level.

2. **CoS trust boundary misconfiguration.** If the provider trusts customer CoS markings (802.1p) without enforcing bandwidth profiles per CoS, a misbehaving customer can mark all traffic as high priority, starving other customers' high-priority traffic. Always enforce ingress bandwidth profiles per CoS at the UNI - trust markings only up to the contracted CIR for that class.

3. **Protection switching but no OAM for detection.** A protection mechanism (G.8032 ERP, pseudowire redundancy) is useless without fast failure detection. BFD (Bidirectional Forwarding Detection) or CFM CCMs detect failures in sub-second intervals - without them, failure detection relies on slow IGP convergence. Pair every protection scheme with an appropriate fast-detection protocol.

4. **ENNI CoS mismatch.** Two providers may define CoS classes differently. Provider A's "Gold" class (MPLS TC=5) may not match Provider B's "Premium" class (MPLS TC=7). Without explicit CoS re-marking and negotiation at the ENNI, priority inversion occurs - voice traffic gets best-effort treatment across the far-side provider.

5. **Y.1731 measurements not aligned with SLA time periods.** SLA FD/FLR objectives apply over a specific measurement interval (e.g., worst 30-minute average over a month). Point-in-time measurements show instantaneous performance but may not reflect the SLA measurement methodology. Ensure monitoring platforms accumulate measurements over the correct intervals and apply the correct aggregation (mean, 99th percentile) as specified in the SLA.

---
## Practice Problems

**Q1.** A customer reports intermittent voice quality issues on their E-Line service. You run a CFM loopback (LB) from PE1 to PE2 - it succeeds. What does this tell you, and what should you check next?

??? answer
    CFM LB success confirms end-to-end Layer 2 connectivity at the MEP level - the EVC path is up and frames can traverse it. The problem is likely not a hard fault (complete path failure) but a performance issue. Next steps: (1) Run Y.1731 DMM (delay measurement) - measure one-way delay and jitter between MEPs. Voice is sensitive to delay >150ms and jitter >30ms. (2) Run Y.1731 SLM (loss measurement) - even 0.1% frame loss on a voice call causes audible quality issues. (3) Check ingress bandwidth profile - if voice traffic is not marked correctly at the UNI (wrong 802.1p PCP), it may be treated as best-effort and queued behind data traffic. (4) Check backbone CoS - confirm voice traffic is in the correct MPLS TC queue.

**Q2.** What is the difference between G.8032 ERP and MPLS FRR for Carrier Ethernet resiliency?

??? answer
    G.8032 ERP (Ethernet Ring Protection) operates at Layer 2 - it protects a ring of Ethernet/VPLS links by blocking one ring protection link (RPL) normally, and unblocking it on failure. Recovery is ~50ms. It requires a physical ring topology and works without MPLS. MPLS FRR operates at the MPLS forwarding layer - it protects MPLS LSPs (including pseudowires and VPLS tunnels) by pre-computing bypass LSPs around protected links or nodes. Recovery is also ~50ms (hardware switching). MPLS FRR works on any topology (not just rings) and protects the entire MPLS LSP, not just the Ethernet segment. In practice: G.8032 for metro Ethernet rings or access rings; MPLS FRR (or TI-LFA with SR) for provider backbone protection.

**Q3.** Why is Y.1564 preferred over RFC 2544 for Carrier Ethernet service activation testing?

??? answer
    RFC 2544 was designed for testing network equipment in a lab - it finds maximum throughput using a binary search algorithm that sends traffic at rates that exceed the service's CIR/EIR. This can trigger the provider's bandwidth policer, causing false failures, and the test is not representative of real SLA verification. Y.1564 was designed specifically for Ethernet service acceptance testing: it tests each traffic class independently at the configured CIR and EIR rates, measures FD/FDV/FLR simultaneously, and validates the bandwidth profile (green/yellow/red colouring) explicitly. Y.1564 results directly map to the SLA parameters in the service contract - RFC 2544 results do not.

---
## Summary & Key Takeaways

- **CoS mapping at the UNI** translates customer 802.1p PCP to backbone MPLS TC - enforce per-class bandwidth profiles to prevent priority abuse.
- **CFM (802.1ag):** Per-EVC OAM - CC for fault detection, LB for localisation, LT for path tracing. MD levels separate customer and provider domains.
- **Y.1731:** Performance measurement - DMM (delay), SLM (loss), AIS/RDI (fault notification). Feeds SLA monitoring.
- **Resiliency options:** G.8032 ERP (ring, L2), MPLS FRR (any topology, MPLS), TI-LFA (SR-MPLS, stateless). Pair with BFD/CFM for sub-second detection.
- **ENNI:** Multi-carrier handoff - requires CoS harmonisation, OAM at the boundary, per-segment SLA.
- **Y.1564:** Standard service activation test - validates CIR/EIR, FD/FDV/FLR per traffic class before service acceptance.

---
## Where to Next

- **CT-010 - SDH/SONET & OTN Basics:** Physical transport layer beneath Carrier Ethernet.
- **CT-012 - Traffic Engineering:** SR-TE and RSVP-TE for explicit path control across the backbone.
- **QOS-003 - Queuing Mechanisms:** Backbone queuing design underlying CoS commitments.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| IEEE 802.1ag | Connectivity Fault Management (CFM) |
| ITU-T Y.1731 | OAM for Ethernet-Based Networks |
| ITU-T Y.1564 | Ethernet Service Activation Test Methodology |
| ITU-T G.8032 | Ethernet Ring Protection Switching |
| MEF 23.x | Carrier Ethernet Class of Service |
| Cisco CCIE Service Provider | CFM, Y.1731, Carrier Ethernet OAM |
| MEF CECP | Carrier Ethernet Certified Professional |

---
## References

- IEEE 802.1ag - Connectivity Fault Management. [https://standards.ieee.org/ieee/802.1ag/](https://standards.ieee.org/ieee/802.1ag/)
- ITU-T Y.1731 - OAM for Ethernet-Based Networks. [https://www.itu.int/rec/T-REC-Y.1731](https://www.itu.int/rec/T-REC-Y.1731)
- ITU-T Y.1564 - Ethernet Service Activation Test Methodology. [https://www.itu.int/rec/T-REC-Y.1564](https://www.itu.int/rec/T-REC-Y.1564)
- ITU-T G.8032 - Ethernet Ring Protection. [https://www.itu.int/rec/T-REC-G.8032](https://www.itu.int/rec/T-REC-G.8032)

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
| CT-010 | SDH/SONET & OTN Basics | Physical transport beneath Carrier Ethernet |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-008 | MEF Standards | MEF service types and attributes being implemented |
| CT-003 | MPLS L2VPN (VPLS & Pseudowire) | VPLS/pseudowire implementing MEF services |
| CT-006 | EVPN Fundamentals | EVPN implementing MEF E-LAN services |
<!-- XREF-END -->
