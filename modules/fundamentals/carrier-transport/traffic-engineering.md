---
id: CT-012
title: "Traffic Engineering — RSVP-TE & SR-TE"
description: "How MPLS Traffic Engineering uses RSVP-TE and Segment Routing TE to explicitly control traffic paths, provide bandwidth guarantees, and protect against link and node failures."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - CT-001
  - CT-004
  - RT-004
  - RT-006
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - traffic-engineering
  - rsvp-te
  - sr-te
  - mpls
  - path-computation
  - fast-reroute
  - te-tunnel
  - carrier
created: 2026-04-19
updated: 2026-04-19
---

# CT-012 — Traffic Engineering — RSVP-TE & SR-TE

## The Problem

A carrier backbone has six inter-city links. The IGP shortest path routes all traffic between East and West over two of those links — they run at 95% utilisation while the other four links are nearly empty. Total capacity exists; it's just not being used.

Standard IP routing follows the shortest path (lowest metric). It cannot say "for this traffic class, use the longer path that has spare capacity." It has no concept of link bandwidth reservation or guaranteed delivery rate. When a link fails, reconvergence takes seconds — unacceptable for voice and real-time services.

### Step 1: Pre-compute and signal explicit paths

**MPLS Traffic Engineering (MPLS-TE)** establishes **TE tunnels** — MPLS LSPs with an explicitly defined path (not the IGP's shortest path). The headend router specifies which links the LSP must traverse. The path is chosen based on available bandwidth across the network — not just metric.

**RSVP-TE** (Resource Reservation Protocol with TE extensions) is the signalling protocol that establishes TE tunnels: it walks the path hop-by-hop, reserving bandwidth at each node and establishing MPLS forwarding state. If any link doesn't have enough available bandwidth, the setup is rejected.

### Step 2: Protect against failures with pre-computed backups

For each protected TE tunnel, RSVP-TE pre-establishes a **bypass tunnel** or a **detour** that avoids the protected link or node. On failure (detected via BFD in <50ms), the upstream node immediately switches traffic to the bypass — sub-50ms reroute without waiting for IGP reconvergence.

### Step 3: SR-TE — stateless traffic engineering

RSVP-TE maintains per-LSP state on every router in the path — memory scales with the number of tunnels. SR-TE (CT-004) eliminates this: the headend encodes the explicit path as a label stack; intermediate routers have no state. The path computation is the same; the data plane is fundamentally different.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Explicit path traversing specific links | TE tunnel / LSP |
| MPLS signalling protocol for TE | RSVP-TE (RFC 3209) |
| Bandwidth reserved on each link | Bandwidth constraint |
| Network-wide view of TE link states | TE database (TED) |
| Flooding of TE link attributes via IGP | OSPF-TE / IS-IS-TE |
| Pre-computed backup tunnel | Bypass tunnel (FRR) |
| Per-flow state at every router | RSVP-TE (stateful) |
| No per-flow state in core | SR-TE (stateless) |
| Centralised path computation | PCE (Path Computation Element) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why IGP shortest-path routing is insufficient for traffic engineering.
2. Describe RSVP-TE — PATH/RESV messages, explicit route objects, bandwidth reservation.
3. Explain the TE database (TED) and how IGP-TE extensions distribute link attributes.
4. Describe MPLS-TE Fast Reroute — facility backup, one-to-one protection, PLR.
5. Explain SR-TE policies — explicit segment lists, colour-based steering, PCEP.
6. Compare RSVP-TE and SR-TE — trade-offs in state, scale, and operations.

---

## Prerequisites

- CT-001 — MPLS Fundamentals (label switching, LSP)
- CT-004 — Segment Routing SR-MPLS (SR concepts, segment lists)
- RT-004 — OSPF Fundamentals (OSPF as TE control plane)
- RT-006 — IS-IS Fundamentals (IS-IS as TE control plane)

---

## Core Content

### The TE Database (TED)

Standard IGPs distribute topology (which links exist, what metric). For TE, routers also need to know **link attributes**:
- Maximum bandwidth (physical capacity)
- Maximum reservable bandwidth (portion available for TE)
- Unreserved bandwidth per priority class
- TE metric (separate from IGP metric — can be configured independently)
- SRLG (Shared Risk Link Group) — links sharing a physical path (e.g., same fibre bundle)

**IGP-TE extensions** flood these attributes in OSPF Opaque LSAs (RFC 3630) or IS-IS TE TLVs (RFC 5305). Every router builds a **TED (Traffic Engineering Database)** — a link-state map of the entire network with bandwidth attributes. Path computation uses the TED to find a path satisfying bandwidth and TE metric constraints.

**CSPF (Constrained Shortest Path First):** The algorithm used to compute TE tunnel paths. Standard SPF modified to: prune links that don't have sufficient available bandwidth, observe explicit include/exclude constraints (admin groups), minimise TE metric along the remaining graph.

### RSVP-TE — Tunnel Signalling

RSVP-TE (RFC 3209) establishes MPLS TE tunnels via a two-phase message exchange:

**PATH message (headend → tailend, hop-by-hop):**
- Originates at the headend with the Explicit Route Object (ERO) — the list of hops specifying the exact path.
- Carries Session Object (LSP ID, destination), Sender Template (source), TSPEC (bandwidth requirement).
- Each intermediate router processes the PATH message, records soft state, and forwards to the next hop specified in the ERO.

**RESV message (tailend → headend, reverse hop-by-hop):**
- Originates at the tailend when PATH is received.
- Carries LABEL object — the MPLS label assigned for this LSP by each hop.
- Each router processes the RESV, installs the MPLS forwarding entry (swap label, output interface), and forwards the RESV upstream.
- When the headend receives the RESV, the tunnel is established: traffic can be forwarded.

**Soft state:** RSVP-TE state must be refreshed periodically (PATH/RESV refresh messages every 30s by default). State expires if not refreshed — the tunnel tears down. In large networks, refresh messages consume significant bandwidth and CPU; RSVP extensions (RFC 2961 summary refresh, RFC 3473 bundle messages) reduce this overhead.

=== "Cisco IOS-XE (RSVP-TE)"

    ```
    ! Enable MPLS TE and RSVP on interfaces
    mpls traffic-eng tunnels
    interface GigabitEthernet0/0
     mpls traffic-eng tunnels
     ip rsvp bandwidth 100000    ! 100 Mbps available for TE

    ! OSPF TE extensions
    router ospf 1
     mpls traffic-eng router-id Loopback0
     mpls traffic-eng area 0

    ! TE tunnel definition
    interface Tunnel0
     ip unnumbered Loopback0
     tunnel mode mpls traffic-eng
     tunnel destination 4.4.4.4    ! tailend
     tunnel mpls traffic-eng bandwidth 50000    ! 50 Mbps reservation
     tunnel mpls traffic-eng path-option 10 explicit name EXPLICIT-PATH
     tunnel mpls traffic-eng path-option 20 dynamic    ! fallback

    ! Explicit path
    ip explicit-path name EXPLICIT-PATH enable
     next-address 2.2.2.2
     next-address 3.3.3.3
     next-address 4.4.4.4

    ! Verification
    show mpls traffic-eng tunnels
    show mpls traffic-eng link-management bandwidth-allocation
    show rsvp session
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_te/configuration/xe-17/mp-te-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_te/configuration/xe-17/mp-te-xe-17-book.html)

=== "Juniper Junos (RSVP-TE)"

    ```
    # MPLS and RSVP configuration
    set protocols mpls interface ge-0/0/0.0
    set protocols mpls label-switched-path TO-R4 to 4.4.4.4
    set protocols mpls label-switched-path TO-R4 bandwidth 50m
    set protocols mpls label-switched-path TO-R4 primary VIA-R2-R3
    set protocols mpls path VIA-R2-R3 2.2.2.2 strict
    set protocols mpls path VIA-R2-R3 3.3.3.3 strict
    set protocols mpls path VIA-R2-R3 4.4.4.4 strict

    set protocols rsvp interface ge-0/0/0.0 bandwidth 100m

    # OSPF TE
    set protocols ospf traffic-engineering
    set protocols ospf area 0.0.0.0 interface ge-0/0/0.0

    # Verification
    show mpls lsp detail
    show rsvp session
    show ted link
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/rsvp-te-config.html](https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/rsvp-te-config.html)

=== "Nokia SR-OS (RSVP-TE)"

    ```
    # RSVP-TE interface configuration
    configure router rsvp
        interface "to-R2"
            bandwidth 100000    ! kbps
            no shutdown
        exit
        no shutdown
    exit

    # MPLS TE tunnel (RSVP LSP)
    configure router mpls
        lsp "TO-R4"
            to 4.4.4.4
            bandwidth 50000
            primary "VIA-R2-R3"
                no shutdown
            exit
            path "VIA-R2-R3"
                hop 10 2.2.2.2 strict
                hop 20 3.3.3.3 strict
                hop 30 4.4.4.4 strict
                no shutdown
            exit
            no shutdown
        exit
        no shutdown
    exit

    # Verification
    show router mpls lsp detail
    show router rsvp session
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-unicast-routing-protocols/rsvp-te.html](https://documentation.nokia.com/sr/23-10/books/sr-unicast-routing-protocols/rsvp-te.html)

### MPLS-TE Fast Reroute (FRR)

FRR provides sub-50ms protection for TE tunnels by pre-computing and pre-signalling bypass tunnels.

**Facility backup (one-to-many, preferred):**
- A single bypass tunnel protects multiple TE tunnels sharing the same link.
- The bypass goes around the protected link or node.
- The **PLR (Point of Local Repair)** — the router upstream of the failure — switches all affected tunnels to the bypass simultaneously.
- Bypass tunnels are pre-established RSVP-TE LSPs with an explicit path avoiding the protected element.

**One-to-one protection (detour):**
- Each protected tunnel has its own dedicated detour path.
- More state, but allows bandwidth guarantees on the protection path.
- Used when the bypass must be guaranteed the same bandwidth as the primary.

**Protection types:**
- **Link protection:** Bypass avoids the protected link; the downstream node is still reachable via other paths.
- **Node protection:** Bypass avoids the protected link AND its downstream node — protects against node failure.

**Detection:** FRR relies on fast failure detection. BFD (Bidirectional Forwarding Detection) provides sub-second failure detection on RSVP-TE protected links — typical BFD timer: 50ms × 3 = 150ms detection. Combined with hardware-based FRR switching, total protection time can be <50ms (hardware detection + hardware forwarding switch).

### SR-TE — Segment Routing Traffic Engineering

SR-TE uses SR-MPLS label stacks at the headend to encode explicit paths — no per-hop state in the network core (as covered in CT-004). Key SR-TE concepts:

**SR-TE Policy:** Defined on the headend router. Attributes:
- **Headend:** The originating router.
- **Endpoint:** The destination (tailend address).
- **Colour:** An integer tag associating the policy with a specific service or traffic class. BGP routes can be steered into SR-TE policies by colour.
- **Candidate paths:** Ordered list of segment lists (explicit paths). Highest-preference valid path is active.

**PCEP — Path Computation Element Protocol (RFC 5440):** In large networks, computing TE paths locally may not scale or may not have a global view of the network. A **PCE (Path Computation Element)** is a centralised server with a full TED and sophisticated algorithms. **PCEP** is the protocol between the headend (**PCC — Path Computation Client**) and the PCE:
- PCC requests a path (constraints: bandwidth, latency, SRLG).
- PCE responds with a computed segment list.
- PCC instantiates the SR-TE policy with the PCE-provided path.

PCE-based TE enables centralised optimisation — the PCE can optimise across all tunnels simultaneously, re-routing tunnels when utilisation changes.

### RSVP-TE vs SR-TE

| Property | RSVP-TE | SR-TE |
|---|---|---|
| Per-path state | Yes — every router in path | No — only at headend |
| Signalling protocol | RSVP | None (IGP + BGP distribute segments) |
| Bandwidth reservation | Yes (per path) | No (best-effort from segment list) |
| Fast reroute | Pre-computed bypass tunnels | TI-LFA (IGP-computed, automatic) |
| Operational complexity | High — RSVP soft state, refresh, bypass tunnels | Low — no separate signalling to manage |
| Multi-domain TE | Complex (inter-AS RSVP) | Relatively simpler (BGP carries segment lists) |
| Scalability | Limited by state per router | Scales to large numbers of policies |

---

## Common Pitfalls

1. **Bandwidth over-subscription.** RSVP-TE bandwidth reservations are admission-controlled — but only for RSVP-TE tunnels. If an interface is also carrying non-TE (IP) traffic, the available bandwidth for RSVP may be less than the configured maximum. Configure reservable bandwidth conservatively (e.g., 80% of link capacity) to leave headroom for IGP, control plane, and non-TE traffic.

2. **ERO strict vs loose hops.** In an explicit path, **strict** hops require a direct link to the next hop; **loose** hops allow routing through any intermediate nodes. A path with all loose hops is equivalent to a dynamic path. Mixing strict and loose hops without understanding the topology can produce paths that don't traverse the intended links — always verify the actual path with `show mpls traffic-eng tunnels detail`.

3. **RSVP-TE state timer interaction.** RSVP uses soft state — PATH/RESV messages must be refreshed periodically. Default refresh interval is 30 seconds; state expires after ~3.5× refresh interval without refreshing. During heavy CPU load or link congestion, refresh messages may be delayed or dropped — causing tunnels to tear down unexpectedly. Implement RSVP summary refresh (RFC 2961) in large deployments to reduce refresh message volume.

4. **SR-TE colour and no-colour mismatch.** Traffic steering into an SR-TE policy uses colour + endpoint to match. BGP routes carry the SR-TE colour as a BGP community. If the BGP route is received without the expected colour community (stripped by a route reflector or policy), the SR-TE policy is not selected and traffic falls back to the IGP path. Always verify community propagation end-to-end.

5. **PCE reachability loss.** If the network loses reachability to the PCE, all PCE-computed paths remain until they are explicitly withdrawn or the local headend has a locally computed fallback. If no fallback is configured, losing PCE connectivity means no new TE paths can be established and failed paths cannot be re-routed. Configure a local fallback (dynamic SR-TE path) for all critical PCE-delegated LSPs.

---

## Practice Problems

**Q1.** Two parallel 10G links between the same pair of routers are each 70% utilised by IGP traffic. A new 5G voice TE tunnel must be established between these routers. Can RSVP-TE establish the tunnel, and why?

??? answer
    No — RSVP-TE cannot establish the tunnel on either link. RSVP-TE uses admission control based on **reservable bandwidth** on each link. If each 10G link has 70% utilisation from IGP traffic, the remaining reservable bandwidth is at most 3G (30% × 10G) per link — less than the 5G required for the voice tunnel. RSVP-TE will reject the PATH message with a "bandwidth not available" error. Resolution: (1) Re-route some IGP traffic via other paths (adjust IGP metrics) to free up bandwidth; (2) use SR-TE with policy-based steering to divert some existing traffic, then establish the voice tunnel; (3) add physical capacity.

**Q2.** What is the role of the PLR in MPLS-TE FRR, and what triggers the switch to the bypass tunnel?

??? answer
    The **PLR (Point of Local Repair)** is the router immediately upstream of the protected link or node — the last router that would normally forward traffic on the protected path before the failure point. The PLR pre-establishes the bypass tunnel during normal operation. When the PLR detects a failure (via BFD sub-second detection or interface down event), it immediately switches traffic from the primary TE tunnel to the bypass tunnel in hardware — without waiting for RSVP or IGP to reconverge. The bypass tunnel is already in the MPLS forwarding table, so the switch is a local hardware operation taking <50ms. The PLR also sends RSVP PATH Error messages upstream to notify the headend, which then re-routes the TE tunnel via a new path.

**Q3.** Why does SR-TE not require bandwidth reservation, and what does this mean for voice traffic?

??? answer
    SR-TE encodes an explicit path as a label stack but does not signal or reserve bandwidth at each hop — intermediate routers have no knowledge of SR-TE tunnels and perform best-effort forwarding. This means SR-TE cannot guarantee that the explicit path has sufficient bandwidth — if the selected path becomes congested, voice traffic experiences delay and loss. In practice, carriers address this by: (1) capacity planning to ensure sufficient headroom on all links; (2) combining SR-TE with QoS (marking voice traffic EF DSCP so it gets priority queuing regardless of path); (3) using PCE-computed SR-TE paths that consider current utilisation. For strict bandwidth guarantees, RSVP-TE remains the technically correct choice — but SR-TE's operational simplicity has made it dominant, relying on overprovisioning and QoS for service quality.

---

## Summary & Key Takeaways

- **MPLS-TE** enables explicit path control based on bandwidth constraints — traffic no longer forced onto IGP shortest path regardless of utilisation.
- **RSVP-TE:** Signals explicit paths hop-by-hop; reserves bandwidth; establishes per-path state at every router; FRR with pre-computed bypass tunnels (<50ms).
- **IGP-TE extensions** (OSPF-TE / IS-IS-TE) distribute link bandwidth attributes — the TED enables CSPF path computation.
- **RSVP-TE FRR:** PLR detects failure and switches to pre-established bypass; link or node protection modes.
- **SR-TE:** Stateless — headend imposes segment list; no per-path state in core; TI-LFA for automatic FRR.
- **PCE/PCEP:** Centralised path computation — enables network-wide optimisation, multi-domain TE.
- SR-TE is replacing RSVP-TE due to operational simplicity; RSVP-TE remains for strict bandwidth-guaranteed services.
- Pair SR-TE with QoS marking to compensate for lack of bandwidth reservation.

---

## Where to Next

- **CT-004 — Segment Routing SR-MPLS:** SR-TE foundation; TI-LFA fast reroute.
- **CT-005 — SRv6:** SRv6-TE for IPv6-native traffic engineering.
- **CT-011 — OTN:** OTN path provisioning coordinates with IP/MPLS TE for end-to-end path optimisation.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 3209 | RSVP-TE Extensions for LSP Tunnels |
| RFC 3630 | OSPF TE Extensions |
| RFC 5305 | IS-IS TE Extensions |
| RFC 5440 | PCEP |
| RFC 4090 | MPLS-TE FRR Facility Backup |
| Cisco CCIE Service Provider | RSVP-TE, SR-TE, PCE |
| Nokia SRC | SR-TE, PCE |
| Juniper JNCIE-SP | RSVP-TE, SR-TE |

---

## References

- RFC 3209 — RSVP-TE Extensions. [https://www.rfc-editor.org/rfc/rfc3209](https://www.rfc-editor.org/rfc/rfc3209)
- RFC 4090 — MPLS-TE FRR. [https://www.rfc-editor.org/rfc/rfc4090](https://www.rfc-editor.org/rfc/rfc4090)
- RFC 5440 — PCEP. [https://www.rfc-editor.org/rfc/rfc5440](https://www.rfc-editor.org/rfc/rfc5440)

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
| CT-005 | SRv6 | SRv6-TE for IPv6-native traffic engineering |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-001 | MPLS Fundamentals | Label switching and LSP base |
| CT-004 | Segment Routing SR-MPLS | SR-TE label-stack based path encoding |
| RT-004 | OSPF Fundamentals | OSPF-TE extensions for TED flooding |
| RT-006 | IS-IS Fundamentals | IS-IS-TE extensions for TED flooding |
<!-- XREF-END -->
