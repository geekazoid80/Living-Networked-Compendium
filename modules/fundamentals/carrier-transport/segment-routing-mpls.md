---
id: CT-004
title: "Segment Routing — SR-MPLS"
description: "How Segment Routing distributes MPLS labels via the IGP (OSPF/IS-IS) instead of LDP, simplifies the control plane, and enables source-based traffic engineering."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - CT-001
  - RT-004
  - RT-006
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - segment-routing
  - sr-mpls
  - mpls
  - igp
  - ospf
  - isis
  - traffic-engineering
  - carrier
created: 2026-04-19
updated: 2026-04-19
---

# CT-004 — Segment Routing — SR-MPLS

## The Problem

Traditional MPLS requires two separate protocol stacks to work:
- **IGP (OSPF or IS-IS):** Distributes topology — which nodes exist, which links connect them, link costs.
- **LDP:** Distributes MPLS labels — which label maps to which destination prefix, on every hop.

Every router runs both. LDP sessions must be maintained between all directly connected routers. If a link fails and the IGP reconverges, LDP must also reconverge — this takes additional time and requires synchronisation (LDP-IGP sync) to prevent black holes during the gap. Every router in the network must know labels for every prefix.

What if the IGP could carry the label information directly — eliminating LDP entirely?

### Step 1: Let the IGP distribute labels

Segment Routing extends OSPF or IS-IS to carry label information in existing extensions. Each router advertises a **Node Segment** (a label for the router's loopback — "send to this router"). Each link can advertise an **Adjacency Segment** (a label that forces traffic onto a specific link — "go via this exact interface"). The label values are distributed with the topology, in one protocol.

LDP is no longer needed. The control plane becomes simpler: one protocol instead of two.

### Step 2: Source-based path encoding

In traditional MPLS, the path through the network is determined by the label each hop assigns — the ingress router imposes one label; each hop swaps it. The path follows the labels hop-by-hop, determined at each P router based on its label table.

With Segment Routing, the **ingress router** encodes the entire path as a **label stack** before sending the packet. A packet destined for router R8 via specific links gets a label stack `[100 (R3 adjacency), 200 (R6 node), 300 (R8 node)]`. Each label is popped in sequence; the stack encodes the explicit path. The ingress router — not intermediate routers — controls the path. Intermediate routers just pop labels.

### Step 3: Eliminate per-flow state from the core

Traditional MPLS-TE (RSVP-TE) requires every router in the path to maintain state for every Traffic Engineering tunnel — memory scales with the number of tunnels. Segment Routing has **no per-flow state** in the core. Intermediate routers pop labels based on their local label table (which lists only node and adjacency segments — O(N) entries, not O(tunnels)). Traffic engineering paths exist only as the label stack on packets at the ingress.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Label for a router's loopback (reachability) | Node Segment (Prefix SID) |
| Label for a specific interface/link | Adjacency Segment (Adj-SID) |
| Label identifying a service/VPN | Service Segment (BGP Prefix SID) |
| IGP-distributed label database | SRGB (Segment Routing Global Block) |
| Label stack encoding an explicit path | Segment List |
| Ingress router that imposes the label stack | Headend |
| No per-flow state in core P routers | Stateless core |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why Segment Routing replaces LDP and RSVP-TE.
2. Describe Node Segments (Prefix SID) and Adjacency Segments (Adj-SID).
3. Explain the Segment Routing Global Block (SRGB) and how SIDs map to MPLS labels.
4. Describe source-based path encoding using a segment list.
5. Explain Topology-Independent LFA (TI-LFA) for fast reroute without RSVP-TE.
6. Configure basic SR-MPLS with IS-IS or OSPF.

---

## Prerequisites

- CT-001 — MPLS Fundamentals (label forwarding basis)
- RT-004 — OSPF Fundamentals (OSPF as SR control plane)
- RT-006 — IS-IS Fundamentals (IS-IS as SR control plane; preferred for SR in carrier networks)

---

## Core Content

### Segments and SIDs

A **segment** is an instruction: "forward to this node", "use this link", "apply this service policy". Each segment is identified by a **SID (Segment Identifier)**.

**Node Segment (Prefix SID):**
- Identifies a destination node (loopback prefix).
- Globally significant — the same label value on all routers in the SR domain.
- The SID value is an *index* into the SRGB, not a raw label.
- Example: Router R1 advertises Prefix SID index 1. All routers with SRGB 16000–23999 map this to label 16001.
- A packet with label 16001 at any router in the domain means "send to R1 via shortest path (IGP best path)".

**Adjacency Segment (Adj-SID):**
- Identifies a specific interface (link) from one router to a neighbour.
- Locally significant — only meaningful at the advertising router.
- Used to force traffic onto a specific link (traffic engineering, bypass of congested link).
- Example: R2 advertises Adj-SID 24001 for the link R2→R4. A packet arriving at R2 with top label 24001 exits specifically via R2→R4, regardless of routing tables.

### SRGB — Segment Routing Global Block

The SRGB is the MPLS label range reserved for globally-significant Prefix SIDs. All routers in the domain must use the same SRGB. The default is 16000–23999 on most platforms.

SID index → Label: `label = SRGB_start + SID_index`

For SRGB 16000–23999 and Prefix SID index 5: label = 16000 + 5 = 16005.

Because the SRGB is the same on all routers, any router that sees a packet with label 16005 knows: "this means node SID index 5 — forward to that node via IGP best path."

### SR with IS-IS

IS-IS is the preferred IGP for SR in carrier networks because its extensions for SR are mature and widely deployed.

=== "Cisco IOS-XR"

    ```
    ! Enable Segment Routing with IS-IS
    router isis 1
     net 49.0001.0001.0001.0001.00
     address-family ipv4 unicast
      metric-style wide
      segment-routing mpls    ! Enable SR
     !

    ! Configure Prefix SID on loopback
    interface Loopback0
     address-family ipv4 unicast
      prefix-sid index 1      ! This router = SID index 1
     !

    ! SRGB
    segment-routing
     global-block 16000 23999
    
    ! Verification
    show isis segment-routing label table
    show mpls forwarding-table labels 16001-16010
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/segment-routing/b-segment-routing-cg-ncs5500.html](https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/segment-routing/b-segment-routing-cg-ncs5500.html)

=== "Juniper Junos"

    ```
    # IS-IS with Segment Routing
    set protocols isis interface lo0.0 level 2 metric 0
    set protocols isis interface ge-0/0/0.0 level 2 metric 10
    set protocols isis source-packet-routing srgb start-label 16000 index-range 8000

    # Prefix SID on loopback
    set interfaces lo0 unit 0 family iso address 49.0001.0001.0001.00
    set protocols isis interface lo0.0 level 2 prefix-sid-index 1

    # Verification
    show isis overview
    show route protocol isis table inet.3
    show mpls label usage
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/segment-routing-isis.html](https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/segment-routing-isis.html)

=== "Nokia SR-OS"

    ```
    # IS-IS with Segment Routing
    configure router isis 1
        level-capability level-2
        area-id 49.0001
        segment-routing
            prefix-sid-range global
            no shutdown
        exit
        interface "system"
            no shutdown
        exit
        interface "to-R2"
            no shutdown
        exit
        no shutdown
    exit

    # SRGB
    configure router mpls-labels sr-labels start 16000 end 23999

    # Prefix SID on system interface
    configure router isis 1 interface "system" prefix-sid-index 1
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-segment-routing/segment-routing-mpls.html](https://documentation.nokia.com/sr/23-10/books/sr-segment-routing/segment-routing-mpls.html)

### Traffic Engineering with SR — Segment Lists

A **segment list** is a sequence of SIDs imposed as a label stack at the headend. It encodes an explicit path through the network.

Example: Force traffic from R1 to R8 to traverse R3→R6→R8 (instead of IGP shortest path R1→R2→R8):

```
Label stack at R1: [Prefix-SID(R6), Prefix-SID(R8)]
```

R1 pops Prefix-SID(R8) at penultimate hop (PHP). R6 pops Prefix-SID(R6) (after it's the top label), sees Prefix-SID(R8) and forwards to R8 via its own IGP best path.

To force a specific link: include an Adj-SID:

```
Label stack: [Adj-SID(R3→R6), Prefix-SID(R8)]
```

Traffic is forwarded through R3 and forced onto the R3→R6 link, then follows IGP to R8.

This is implemented via **SR Policy** — a construct on the headend that maps traffic (by colour/endpoint or route-map) to a segment list:

### SR-TE Policies (Cisco IOS-XR)

```
! SR Traffic Engineering Policy
segment-routing
 traffic-eng
  policy FORCE-VIA-R6
   color 100 end-point ipv4 8.8.8.8
   candidate-paths
    preference 100
     explicit segment-list EXPLICIT-PATH
     !
  !
 !
!

segment-routing
 traffic-eng
  segment-list EXPLICIT-PATH
   index 10 mpls label 16003    ! R3 Prefix SID
   index 20 mpls label 16006    ! R6 Prefix SID
  !
```

### TI-LFA — Topology-Independent Loop-Free Alternates

RSVP-TE FRR (Fast Reroute) required pre-computed bypass tunnels for every protected LSP — complex and stateful. SR provides **TI-LFA** (Topology-Independent Loop-Free Alternates): the router automatically pre-computes a backup path for each next-hop using segment lists. On link failure, traffic is switched to the pre-computed backup segment list in sub-50ms — no per-tunnel state in the core.

TI-LFA is enabled per IS-IS or OSPF interface and works automatically. The backup path is any path that doesn't use the failed link — computed using the post-convergence topology.

---

## Common Pitfalls

1. **SRGB mismatch across routers.** If one router uses SRGB 16000–23999 and another uses 17000–24999, the same Prefix SID index maps to different labels. A packet arriving at the mismatched router with label 16001 is not forwarded to the correct destination — it may be dropped or forwarded incorrectly. Verify all routers in the SR domain share the same SRGB.

2. **Prefix SID index collision.** Two routers advertising the same Prefix SID index causes label collision — both resolve to the same label, and traffic for one node may be forwarded to the other. Assign Prefix SID indices from a managed table. Use a centralised controller (SR-PCE) to allocate SIDs and detect collisions.

3. **Adj-SIDs not considered in path computation.** Adj-SIDs are locally significant. A segment list that uses an Adj-SID from router R2 must ensure the packet reaches R2 first — the Adj-SID is meaningless at any other router. When building explicit paths with Adj-SIDs, always verify the preceding segment routes the packet to the correct advertising router.

4. **PHP removing the last SID before service label processing.** Penultimate Hop Popping (PHP) removes the top label at the penultimate hop. If the last SID in a segment list is a service/BGP label (for VPN termination), PHP removes it prematurely. Use **Explicit Null** labels or disable PHP for the final segment when a service label must be preserved to the egress PE.

5. **TI-LFA not enabled or no feasible backup.** TI-LFA requires the IGP to compute the post-convergence topology from the point of local repair. For some topologies (e.g., a single-link stub), no loop-free alternate exists — coverage is less than 100%. Check TI-LFA coverage per interface with `show isis fast-reroute coverage` and consider additional links or SR-TE backup policies for uncovered segments.

---

## Practice Problems

**Q1.** What is the advantage of SR-MPLS over LDP + RSVP-TE for a carrier backbone?

??? answer
    SR-MPLS collapses two protocol stacks (LDP for label distribution, RSVP-TE for traffic engineering) into one (IGP with SR extensions). Operational benefits: (1) Simpler control plane — one protocol to configure, monitor, and troubleshoot. (2) No per-LSP state in core P routers — state is only at headend (ingress PE); scales to any number of TE policies without adding memory load to P routers. (3) TI-LFA provides RSVP-FRR-equivalent protection (<50ms) without pre-signalling bypass tunnels for every protected path. (4) Faster convergence — IGP convergence directly provides label updates; no LDP-IGP sync delay.

**Q2.** Router R5 has Prefix SID index 5 and the SRGB is 16000–23999. What MPLS label represents R5 in the network, and what does that label mean to any router in the domain?

??? answer
    Label = 16000 + 5 = **16005**. Any router in the domain that receives a packet with top label 16005 interprets it as "forward to router R5 via the IGP best path." Each router pops (or swaps) this label according to its local LFIB entry derived from SR. The label value is the same on every router because the SRGB is the same — this is what makes Prefix SIDs globally significant. An intermediate router does not need to be told which label maps to R5 via a separate signalling protocol; it computes this locally from the SRGB and the Prefix SID index advertised in the IGP.

**Q3.** When would you use an Adjacency SID instead of a Prefix SID in a segment list?

??? answer
    A Prefix SID forwards traffic to a destination router via the IGP shortest path — you don't control which specific links are used. An Adjacency SID forces traffic onto a **specific link** regardless of the routing table. Use an Adj-SID when: (1) A specific link must be used (e.g., traffic engineering to avoid a congested link or to guarantee latency on a specific physical path). (2) Testing a specific path for troubleshooting. (3) Building an explicit path that must traverse a specific interface for policy or compliance reasons. Adj-SIDs are locally significant — they are only meaningful at the advertising router; the segment list must ensure the packet reaches that router first.

---

## Summary & Key Takeaways

- **Segment Routing** replaces LDP (label distribution) and RSVP-TE (traffic engineering) with IGP extensions — one protocol instead of two.
- **Prefix SID (Node Segment):** Globally significant label index — "send to this router via IGP best path." Label = SRGB_start + SID_index.
- **Adjacency SID (Adj-SID):** Locally significant — forces traffic onto a specific link.
- **SRGB** must be consistent across all routers in the SR domain.
- **Segment list** encodes an explicit path at the ingress (headend) — no per-flow state in the core.
- **TI-LFA:** Automatic fast reroute (<50ms) without RSVP-TE bypass tunnels — computed from post-convergence topology.
- SR integrates with L3VPN and EVPN — BGP Prefix SIDs carry service labels.
- IS-IS is the preferred SR control plane in carrier networks.

---

## Where to Next

- **CT-005 — SRv6:** Segment Routing using IPv6 addresses as SIDs — no MPLS labels.
- **CT-006 — EVPN Fundamentals:** EVPN over SR-MPLS for L2/L3 services.
- **CT-012 — Traffic Engineering:** SR-TE policies, PCE/PCEP, bandwidth optimisation.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 8402 | Segment Routing Architecture |
| RFC 8665 | OSPF Extensions for SR-MPLS |
| RFC 8667 | IS-IS Extensions for SR-MPLS |
| RFC 8664 | Path Computation Element Communication Protocol (PCEP) Extensions for SR |
| Cisco CCIE Service Provider | SR-MPLS, SR-TE, TI-LFA |
| Nokia SRC | Segment Routing |
| Juniper JNCIE-SP | SR-MPLS with IS-IS |

---

## References

- RFC 8402 — Segment Routing Architecture. [https://www.rfc-editor.org/rfc/rfc8402](https://www.rfc-editor.org/rfc/rfc8402)
- RFC 8667 — IS-IS Extensions for SR-MPLS. [https://www.rfc-editor.org/rfc/rfc8667](https://www.rfc-editor.org/rfc/rfc8667)
- RFC 8665 — OSPF Extensions for SR-MPLS. [https://www.rfc-editor.org/rfc/rfc8665](https://www.rfc-editor.org/rfc/rfc8665)

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
| CT-005 | SRv6 | SRv6 is IPv6-native evolution of SR-MPLS |
| CT-006 | EVPN Fundamentals | EVPN uses SR-MPLS as transport |
| CT-012 | Traffic Engineering | SR-TE replaces RSVP-TE |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-001 | MPLS Fundamentals | Label forwarding basis |
| RT-004 | OSPF Fundamentals | OSPF as SR control plane |
| RT-006 | IS-IS Fundamentals | IS-IS preferred SR control plane in carrier |
<!-- XREF-END -->
