---
title: "IS-IS Fundamentals"
module_id: "RT-006"
domain: "fundamentals/routing"
difficulty: "advanced"
prerequisites: ["RT-001", "RT-004"]
estimated_time: 60
version: "1.0"
last_updated: "2026-04-19"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["is-is", "link-state", "lsp", "net", "nsap", "level-1", "level-2", "dis", "tlv", "carrier", "spf", "clnp"]
cert_alignment: "CCNP ENCOR 350-401 | JNCIS-SP JN0-362 | Nokia NRS II | Huawei HCIP-Datacom"
vendors: ["Cisco IOS-XR", "Juniper Junos", "Nokia SR-OS", "Arista EOS"]
language: "en"
---

## The Problem

Two carrier engineers are designing the IGP for a 300-router backbone network. They know OSPF well. But as they sketch the design, constraints emerge that OSPF doesn't handle cleanly.

### Step 1: The IGP should be independent of IP

OSPF runs inside IP packets (protocol number 89). This creates a subtle dependency: if IP routing is broken, OSPF can't help you diagnose it — the protocol that should fix routing needs routing to work first.

At carrier scale, engineers want the IGP to run **below** IP — at the data-link layer — so it operates even when IP is partially misconfigured, and can carry routing information for multiple protocols (IPv4, IPv6, MPLS labels) without being tied to any one of them.

IS-IS does this. It runs directly in IEEE 802 frames, addressed using OSI network addresses. It is not encapsulated in IP. The routing protocol is more fundamental than the traffic it routes.

### Step 2: The area topology is too constrained

In OSPF, all non-backbone areas must connect to Area 0. This forces a specific topology: if Area 0 becomes partitioned, you need virtual links — workarounds. In large carrier networks, this rigidity is a design burden.

IS-IS uses a simpler model: **Level 1** routers handle routing within an area. **Level 2** routers handle routing between areas. The backbone is not a special topology or area ID — it is simply the set of all Level 2 routers. Any router running Level 2 IS-IS is part of the backbone. No specific connectivity pattern is required; the backbone forms wherever L2 routers are.

### Step 3: The protocol needs to carry new things as the network evolves

Networks change. MPLS was invented after IS-IS and OSPF. Then Traffic Engineering. Then Segment Routing. Then IPv6. Each time, OSPF needed new LSA types (opaque LSAs). IS-IS needed only new **TLVs (Type-Length-Value)** fields added to the same LSP structure.

Because IS-IS uses TLV encoding, older routers that receive a TLV they don't recognise simply skip it — the protocol continues to work. New capabilities are additive, not breaking. This extensibility is why IS-IS is the IGP of choice for carrier and data-centre networks deploying Segment Routing, TE, and multi-topology IPv6.

### Step 4: Addressing is different

OSPF uses a Router ID (a 32-bit dotted-decimal value). IS-IS uses a **NET (Network Entity Title)** — an OSI address that includes the area, the system ID (the router's unique identifier), and a selector byte.

```text
NET format:
  49.0001.0000.0000.0001.00
  ↑  ↑    ↑               ↑
  AFI  Area  System ID     N-SEL (always 00 for routers)

AFI 49 = locally administered (private)
Area: 0001
System ID: 0000.0000.0001 (often derived from loopback IP: 1.1.1.1 → 0100.0100.0001... 
           more commonly set directly as 6 hex bytes)
```

### What You Just Built

IS-IS — Intermediate System to Intermediate System. A link-state protocol that runs below IP, uses OSI NET addressing, organises routers into Level 1 (intra-area) and Level 2 (inter-area backbone), floods LSPs with TLV-encoded information, and calculates best paths using Dijkstra's SPF algorithm.

| Scenario element | Technical term |
|---|---|
| Protocol runs at Layer 2, not inside IP | IS-IS on data-link (ISO 10589) |
| Router's OSI address — area + system ID | NET (Network Entity Title) |
| IS-IS equivalent of an LSA | LSP (Link State PDU) |
| Within-area routing | Level 1 (L1) |
| Between-area routing (backbone) | Level 2 (L2) |
| Router participating in both levels | L1/L2 router |
| Extensible data fields in IS-IS PDUs | TLV (Type-Length-Value) |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** how IS-IS differs from OSPF in terms of transport layer, area hierarchy, and extensibility
2. **Describe** the NET address format and derive a NET from a given area ID and system ID
3. **Distinguish** between Level 1, Level 2, and L1/L2 routers and explain how they interact
4. **Describe** IS-IS adjacency formation and the role of the DIS
5. **Compare** IS-IS and OSPF as IGP choices for enterprise and carrier environments
6. **Explain** why IS-IS is the dominant IGP in modern service provider and data-centre networks

---

## Prerequisites

- [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) — routing table, metric, SPF context
- [OSPF Fundamentals](ospf-fundamentals.md) (`RT-004`) — link-state concepts; this module builds directly on OSPF understanding

---

## Core Content

### IS-IS vs OSPF — Key Differences

Before going deeper, a direct comparison clarifies where IS-IS differs from OSPF and why those differences matter.

| Property | OSPF | IS-IS |
|---|---|---|
| Transport | IP (protocol 89) | Data-link directly (ISO 10589 / IEEE 802) |
| Router identifier | Router ID (32-bit dotted-decimal) | NET — OSI NSAP address |
| Area backbone | Area 0 (mandatory; specific topology) | Level 2 (any set of L2 routers) |
| Area boundary router | ABR (Area Border Router) | L1/L2 router |
| Link state record | LSA (Link State Advertisement) | LSP (Link State PDU) |
| Elected segment router | DR / BDR (non-preemptible) | DIS (preemptible; no backup) |
| Protocol data unit flooding | IP multicast (`224.0.0.5`, `224.0.0.6`) | L2 multicast (AllISs: `09:00:2B:00:00:05`) |
| Metric range (wide) | 1–65535 per interface | 1–16777214 per interface |
| Extension mechanism | Opaque LSAs (RFC 5250) | TLVs — add new type, backward compatible |
| IPv6 support | OSPFv3 (separate process) | Multi-Topology IS-IS (same process, new TLVs) |
| Primary deployment | Enterprise | Carrier / service provider / data centre |

### NET (Network Entity Title)

The NET is IS-IS's equivalent of the OSPF Router ID — it identifies the router in the IS-IS domain. Unlike a Router ID, the NET encodes both the area and the system identifier.

**NET structure:**
```text
Format:  <AFI>.<Area ID>.<System ID>.<N-SEL>

49.0001.0000.0000.0001.00
↑   ↑    ↑─────────────↑  ↑
│   │    System ID (6B)   N-SEL = 00 (always for routers)
│   Area ID (variable length, 1–13 bytes)
AFI: 49 = locally administered
```

**AFI 49** is the conventional choice for IS-IS in private networks (equivalent to using RFC 1918 addresses for IP). The area ID and system ID are local policy — you choose them.

**Common practice:** Derive the System ID from the router's loopback IP address:

```text
Loopback: 10.0.0.1
Pad to 12 digits: 010.000.000.001
Remove dots:      010000000001
Group in 4s:      0100.0000.0001

NET: 49.0001.0100.0000.0001.00
```

A router can have multiple NETs (for area mergers), but should have only one System ID across all NETs.

### IS-IS Levels

IS-IS uses a two-level hierarchy to scale:

```text
                ┌──────────────────────────────────────┐
                │          Level 2 (Backbone)           │
                │   L2 ─────── L1/L2 ─────── L1/L2    │
                │          (any L2 routers)             │
                └──────┬────────────────────┬──────────┘
                       │                    │
              ┌────────┴────┐         ┌─────┴───────┐
              │   Area 1    │         │   Area 2    │
              │ (L1 routers)│         │ (L1 routers)│
              └─────────────┘         └─────────────┘
```

**Level 1 (L1) routers:**
- Route within their area only
- Know full topology of their area (run SPF on area LSPs)
- Send all inter-area traffic to the nearest L1/L2 router (default route toward the backbone)
- Only hold L1 LSPs in their LSDB

**Level 2 (L2) routers:**
- Route between areas — the backbone
- Know full topology of the entire Level 2 domain
- Do not know intra-area detail of L1 areas (summary information only)
- Only hold L2 LSPs in their LSDB

**L1/L2 routers:**
- Participate in both levels — the equivalent of OSPF ABRs
- Maintain two separate LSDBs: one L1, one L2
- Leak inter-area reachability from L2 into L1 (the default route, or specific prefixes via route leaking)
- By default, L1 routers in an area see only a default route toward L1/L2 routers — not the full L2 topology

**Key difference from OSPF:** There is no "Area 0" requirement. Level 2 connectivity forms wherever L2 routers exist. If all backbone routers are L2 or L1/L2, they automatically form the backbone without any special configuration.

### IS-IS Adjacency Formation

IS-IS adjacencies form when two routers exchange **IIH (IS-IS Hello)** PDUs and agree on parameters.

**Hello PDU types:**
- **LAN Hello (L1/L2):** sent on multi-access (broadcast) segments
- **P2P Hello:** sent on point-to-point links

**Parameters that must match to form adjacency:**
- Area ID (for L1 adjacencies; L2 adjacencies span areas — area ID need not match)
- Authentication (if configured)
- Circuit type (L1, L2, or L1/L2)
- MTU (implicit — PDU must fit in a frame)

IS-IS hello intervals and hold times do NOT need to match between neighbours (unlike OSPF). The hold timer in the hello specifies how long the receiver should wait before declaring the neighbour down — it is per-sender.

**Adjacency states (simpler than OSPF):**
- **Down** — no valid hello received
- **Initialising** — hello received, processing
- **Up** — hello acknowledged, adjacency active

After adjacency is Up, routers exchange CSNP (Complete Sequence Number PDU) to compare LSP inventory, then request missing LSPs via PSNP (Partial Sequence Number PDU).

```text
IS-IS show command (Cisco IOS-XR):
RP/0/0/CPU0:R1# show isis neighbors
IS-IS core neighbors:
System Id    Interface  SNPA              Level  State  Hold
R2           Gi0/0/0/0  *PtoP*            L2     Up     28
R3           Gi0/0/0/1  *PtoP*            L1L2   Up     24
```

### DIS — Designated Intermediate System

On multi-access (broadcast) segments, IS-IS elects a **DIS (Designated IS)** — the equivalent of OSPF's DR. But there are important differences:

| Property | OSPF DR | IS-IS DIS |
|---|---|---|
| Backup | BDR elected as backup | No backup DIS |
| Preemption | Non-preemptive (once elected, stays) | Preemptive — higher priority takes over |
| Adjacency with non-DR | 2-Way only | All routers form Full adjacency with each other |
| Purpose | Reduce adjacency count; control LSA flooding | Generate pseudo-node LSP; synchronise LSPs |
| Election | Priority → Router ID | Priority → MAC address (higher wins) |

The DIS generates a **pseudo-node LSP** — a virtual LSP that represents the multi-access segment itself. All routers on the segment announce adjacency to the pseudo-node, and the pseudo-node LSP lists all attached routers. This elegantly represents the broadcast segment as a single topology node without the complexity of OSPF's DR/BDR model.

Because there is no backup DIS, DIS failure causes a brief re-election. Since election is preemptive, a higher-priority router that joins the segment will immediately become DIS.

### IS-IS Metric

IS-IS uses a link metric — cost assigned to each interface. The total path cost is the sum of outgoing interface metrics along the path (same additive model as OSPF).

**Two metric styles:**

| Style | Range | TLV used | Status |
|---|---|---|---|
| Narrow (original) | 1–63 per interface; max path = 1023 | TLV 2, 128, 130 | Legacy — should not be used in new deployments |
| Wide | 1–16,777,214 per interface; max path = 0xFE000000 | TLV 22, 135, 236 | Standard — required for TE and modern deployments |

Wide metrics are required for Traffic Engineering extensions (RSVP-TE, SR-TE) because TE uses the metric space for TE metric, link delay, and other attributes. Always configure `metric-style wide` in new deployments.

```text
Default metric on most platforms: 10 per interface
To prefer a high-bandwidth path: set lower metric
To avoid a link: set higher metric
```

Unlike OSPF, IS-IS does not auto-calculate cost from bandwidth by default — metrics are manually set (or all default to 10). This gives operators explicit control but requires manual tuning.

### TLV Extensibility

IS-IS's primary architectural advantage over OSPF is its TLV (Type-Length-Value) encoding. Every piece of information in an IS-IS PDU is a TLV: IP prefixes, adjacencies, TE attributes, Segment Routing labels, IPv6 prefixes.

When a new capability is needed, a new TLV type is defined and added. Routers that understand the new TLV process it. Routers that don't recognise the TLV skip it — no protocol version bump, no backward-incompatibility.

This is why IS-IS has become the IGP of choice for Segment Routing deployments:
- **SR Node SID** — TLV 135 sub-TLV
- **SR Adjacency SID** — TLV 22 sub-TLV
- **SR Capabilities** — new TLV 242
- **IPv6 reachability** — TLV 236 (MT-IS-IS)

All of these are additive. An IS-IS network can carry SR information without any change to the base protocol.

??? supplementary "Multi-Topology IS-IS (MT-IS-IS) for IPv6"
    Classic IS-IS carries IPv4 reachability via TLV 128 and TLV 130 (narrow) or TLV 135 (wide, extended IP reachability). IPv6 is carried via TLV 236.

    The challenge: if a link supports IPv4 but not IPv6 (or vice versa), a single SPF tree may produce incorrect results — the IPv6 path might route through a link that doesn't carry IPv6.

    **Multi-Topology IS-IS (RFC 5120)** runs separate topology instances within the same IS-IS process — one for IPv4, one for IPv6. Each topology runs its own SPF, allowing the IPv4 and IPv6 topologies to be different. A single IS-IS process, two independent forwarding trees.

    Simpler alternative for single-topology networks: run a single topology and ensure all IS-IS links support both IPv4 and IPv6.

### IS-IS in Modern Networks

IS-IS is the dominant IGP in:
- **Service Provider cores** — Cisco IOS-XR on ASR9000/NCS, Juniper MX/PTX, Nokia 7750/7950
- **Data centre underlays** — IS-IS or BGP-unnumbered underlay for spine-leaf fabrics
- **Segment Routing deployments** — IS-IS-SR is the reference implementation for SR-MPLS and SRv6

Enterprise networks use OSPF almost exclusively. The decision is largely historical and based on existing skill sets — both protocols provide equivalent functionality at enterprise scale.

---

## Vendor Implementations

IS-IS is standardised in ISO 10589 (base) and RFC 1195 (IP extensions). Multi-vendor IS-IS adjacencies are routine in carrier networks. The key interoperability requirements: matching authentication, correct TLV support for wide metrics, and consistent area/level design.

!!! success "Standard — ISO 10589 / RFC 1195 / RFC 5308 (IS-IS for IPv6)"
    IS-IS is fully standardised. Any RFC-compliant implementation forms adjacencies with any other. Wide metrics, multi-topology, and SR extensions are defined in additional RFCs.

=== "Cisco IOS-XR"
    ```cisco-ios-xr
    ! IOS-XR IS-IS configuration (SP-class syntax)
    router isis core
     net 49.0001.0100.0000.0001.00
     address-family ipv4 unicast
      metric-style wide
      advertise passive-only       ! only advertise loopback/passive interfaces
     !
     interface GigabitEthernet0/0/0/0
      circuit-type level-2-only    ! this is a backbone interface
      point-to-point
      address-family ipv4 unicast
       metric 10
      !
     !
     interface Loopback0
      passive
      address-family ipv4 unicast
      !

    ! Verify
    show isis neighbors
    show isis database
    show isis topology
    show route isis
    ```
    IOS-XR uses a hierarchical configuration model. `circuit-type level-2-only` is critical — if omitted, the router defaults to L1L2 and generates both L1 and L2 LSPs unnecessarily. Always configure `metric-style wide`. `passive` on loopbacks prevents hello flooding while still advertising the prefix.

    Full configuration reference: [Cisco IOS-XR IS-IS Configuration Guide](https://www.cisco.com/c/en/us/td/docs/routers/xr12000/software/xr12k_r4-0/routing/configuration/guide/rc_xr12k40.html)

=== "Juniper Junos"
    ```junos
    # Junos IS-IS configuration
    set protocols isis interface ge-0/0/0.0 level 2 metric 10
    set protocols isis interface ge-0/0/0.0 point-to-point
    set protocols isis interface lo0.0 passive

    # Set NET
    set interfaces lo0 unit 0 family iso address 49.0001.0100.0000.0001.00

    # Wide metrics
    set protocols isis level 2 wide-metrics-only

    # Verify
    show isis adjacency
    show isis database
    show isis spf log
    show route protocol isis
    ```
    In Junos, the NET is configured on the loopback interface under `family iso`, not in the routing protocol stanza. `wide-metrics-only` should be enabled; Junos supports it per-level. `point-to-point` must be configured explicitly on p2p links to avoid DIS election.

    Full configuration reference: [Juniper IS-IS Configuration](https://www.juniper.net/documentation/us/en/software/junos/is-is/index.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # SR-OS IS-IS configuration (classic CLI)
    configure router isis 0
        level-capability level-2
        area-id 49.0001
        system-id 0100.0000.0001

        interface "to-R2"
            circuit-type point-to-point
            level 2
                metric 10
            exit
            no shutdown
        exit
        interface "system"
            passive
            no shutdown
        exit
        no shutdown
    exit

    # Verify
    show router isis adjacency
    show router isis database
    show router isis topology
    show router route-table protocol isis
    ```
    SR-OS configures area and system ID separately (not as a full NET string). `level-capability level-2` confines this router to L2 operations — appropriate for backbone routers. IS-IS process 0 is the default.

    Full configuration reference: [Nokia SR-OS IS-IS Guide](https://documentation.nokia.com/sr/)

=== "Arista EOS"
    ```arista-eos
    ! Arista EOS IS-IS configuration
    router isis core
       net 49.0001.0100.0000.0001.00
       is-type level-2
       address-family ipv4 unicast
          bfd all-interfaces

    interface Ethernet1
       isis enable core
       isis circuit-type level-2
       isis metric 10
       isis network point-to-point

    interface Loopback0
       isis enable core
       isis passive

    ! Verify
    show isis neighbors
    show isis database
    show isis topology
    show ip route isis
    ```
    Arista EOS IS-IS syntax combines elements from IOS-XE and IOS-XR styles. IS-IS is enabled per-interface with `isis enable <process>`. BFD integration is straightforward.

    Full configuration reference: [Arista EOS IS-IS Configuration](https://www.arista.com/en/um-eos/eos-is-is)

---

## Common Pitfalls

### Pitfall 1: Mixing L1 and L2 adjacencies incorrectly

A common mistake: configuring some routers as L1-only and others as L2-only on the same link. IS-IS forms L1 adjacencies only between routers in the same area; L2 adjacencies span areas. If a link should be a backbone link, both ends must run L2 (or L1/L2). If routers on the same link are in different areas and both run L1-only, no adjacency forms. Check `show isis neighbors` — "Adj" count 0 means no adjacency.

### Pitfall 2: Narrow metric left enabled

Narrow metrics silently cap at 63 per interface and 1023 total path cost. If any TE extensions (SR, RSVP-TE) are planned, narrow metric must be migrated to wide before enabling TE — otherwise TE TLVs cannot carry correct metric values. Always deploy with `metric-style wide` from day one.

### Pitfall 3: Missing `point-to-point` on p2p links

On a point-to-point link between two routers, if `point-to-point` is not configured, IS-IS runs broadcast mode — elects a DIS and generates a pseudo-node LSP for a two-router "segment." The extra LSP is harmless but wastes LSDB space and slightly slows SPF. More importantly, hello PDUs differ between p2p and broadcast mode: if one side is p2p and the other is broadcast, no adjacency forms. Confirm both sides match.

### Pitfall 4: L1 routers cannot reach across areas without route leaking

L1 routers only know routes within their own area plus a default route toward L1/L2 routers. If you need L1 routers to reach specific inter-area prefixes (not just a default), configure explicit route leaking from L2 into L1 on the L1/L2 routers. Without this, all inter-area traffic from L1 routers uses the default — suboptimal if multiple L1/L2 routers exist with different inter-area path lengths.

### Pitfall 5: NET System ID collision

Two routers with the same System ID in the same IS-IS domain cause a duplicate System ID condition — IS-IS flooding stops working correctly and the network destabilises. The System ID must be unique across the entire IS-IS domain (not just within an area). Derive from loopback IP or assign from a managed pool.

---

## Practice Problems

1. A router has loopback address `10.0.0.3/32`. Using the derivation method described, what is its IS-IS System ID? What would the full NET be if the area is `49.0002`?

2. Two IS-IS routers are connected. Router A is configured as Level 1 only (area 49.0001). Router B is configured as Level 2 only (area 49.0002). Do they form an IS-IS adjacency? Explain why or why not.

3. An IS-IS domain has narrow metrics configured. The maximum path metric is 1023. A new path is added with 15 × 10 = 150 total metric — within range. What problem occurs when SR-MPLS is later enabled on this domain?

4. On a broadcast Ethernet segment with 5 IS-IS routers, all running Level 2, what is a DIS? How many full adjacencies exist? How does this differ from OSPF?

5. Compare IS-IS and OSPF area boundary handling. In OSPF, what happens if Area 0 becomes partitioned? How does IS-IS handle the equivalent failure?

??? "Answers"
    **1.** Loopback `10.0.0.3` → pad to 12 digits: `010.000.000.003` → remove dots: `010000000003` → group in 4s: `0100.0000.0003`. System ID: `0100.0000.0003`. Full NET: `49.0002.0100.0000.0003.00`.

    **2.** No adjacency. IS-IS Level 1 adjacencies require the same area ID. Router A (L1, area 49.0001) and Router B (L2, area 49.0002) have different areas and different levels — no common level with matching area exists. For an adjacency to form, both routers would need to run Level 2 (area IDs need not match at L2), or be in the same area running Level 1.

    **3.** Narrow metric maximum = 63 per interface, 1023 total. SR-MPLS Segment Routing SIDs are encoded in TE TLVs that require wide metric format. Enabling SR with narrow metrics causes TLVs to be mishandled or not advertised — adjacency SIDs and node SIDs may not propagate correctly. Solution: migrate to `metric-style wide` before enabling SR.

    **4.** The DIS is elected for the segment (highest priority → highest MAC). The DIS generates a pseudo-node LSP. Unlike OSPF, **all 5 routers form full IS-IS adjacencies with each other** on the broadcast segment — IS-IS does not restrict adjacencies to only DIS and non-DIS. The pseudo-node approach reduces LSDB complexity (one node represents the segment) without reducing actual adjacency count. OSPF DROthers only reach Full with DR/BDR; IS-IS has no equivalent restriction.

    **5.** OSPF Area 0 partition: routers in split partitions of Area 0 cannot exchange inter-area routes; non-backbone areas become isolated or must use virtual links as workarounds — a design problem. IS-IS: if the Level 2 domain becomes partitioned (no L2 path between two groups of L2 routers), inter-area routing between those halves fails. But there is no special "backbone area" constraint — any restoration of L2 connectivity (new link, new router) heals the partition automatically. IS-IS is generally considered more resilient in partition scenarios.

---

## Summary & Key Takeaways

- IS-IS is a **link-state** protocol that runs **below IP** (directly on data-link), making it transport-independent and more fundamental than IP routing itself
- Router identity is the **NET (Network Entity Title)** — an OSI address encoding area ID + system ID
- **Level 1** routers handle intra-area routing; **Level 2** routers form the backbone; **L1/L2** routers are the boundary
- The IS-IS backbone is the set of L2 routers — no special Area 0 topology required
- LSPs are flooded throughout the level domain; each router runs **Dijkstra SPF** on its local LSDB
- **DIS** (Designated IS) is elected on broadcast segments — it is **preemptible** (unlike OSPF DR) and has no backup
- All routers on a broadcast segment form full IS-IS adjacencies with each other (no DR/BDR adjacency restriction)
- IS-IS uses **wide metrics** (up to 16 million) — always deploy with `metric-style wide`; narrow metrics (max 63/1023) are legacy
- **TLV encoding** makes IS-IS easily extensible: SR, TE, IPv6, delay metrics are all new TLVs with backward compatibility
- IS-IS is the IGP of choice in **carrier cores and data-centre spine-leaf** networks, particularly for Segment Routing deployments
- IS-IS hello intervals need not match between neighbours (unlike OSPF); area ID must match for L1 adjacencies

---

## Where to Next

- **Continue:** [BGP Fundamentals](bgp-fundamentals.md) (`RT-007`) — inter-AS routing; where IS-IS (the IGP) hands off to BGP (the EGP)
- **Related:** [OSPF Fundamentals](ospf-fundamentals.md) (`RT-004`) — compare the two link-state protocols side by side
- **Advanced:** [MPLS Fundamentals](../carrier-transport/mpls-fundamentals.md) (`CT-001`) — MPLS runs over IS-IS as the IGP; SR-MPLS builds directly on IS-IS TLV extensions
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) — CCNP-level module; deepens the IGP picture started in RT-004

---

## Standards & Certifications

**Relevant standards:**
- [ISO 10589 — IS-IS for IP (base standard)](https://www.iso.org/standard/30932.html)
- [RFC 1195 — Use of OSI IS-IS for Routing in TCP/IP and Dual Environments](https://www.rfc-editor.org/rfc/rfc1195)
- [RFC 5308 — Routing IPv6 with IS-IS](https://www.rfc-editor.org/rfc/rfc5308)
- [RFC 5120 — Multi-Topology IS-IS](https://www.rfc-editor.org/rfc/rfc5120)
- [RFC 8667 — IS-IS Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc8667)

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNP ENCOR 350-401 | Cisco | IS-IS fundamentals; neighbour adjacency; levels |
| JNCIS-SP JN0-362 | Juniper | IS-IS levels; NET; DIS; metric |
| Nokia NRS II | Nokia | IS-IS in SP context; levels; TLV extensions |
| Huawei HCIP-Datacom | Huawei | IS-IS fundamentals |

---

## References

- ISO — ISO/IEC 10589:2002: Information technology — IS-IS Routing Protocol
- IETF — [RFC 1195: Use of OSI IS-IS for Routing in TCP/IP](https://www.rfc-editor.org/rfc/rfc1195)
- IETF — [RFC 5308: Routing IPv6 with IS-IS](https://www.rfc-editor.org/rfc/rfc5308)
- Doyle, J.; Carroll, J. — *Routing TCP/IP, Volume II*, Cisco Press, 2001 — Ch. 3 (IS-IS)
- Savage, P.; Browne, G. — *IS-IS Network Design Solutions*, Cisco Press, 2003

---

## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Draft written by Claude Sonnet 4.6. RFC and ISO citations verified. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [CT-001](../carrier-transport/mpls-fundamentals.md) | MPLS Fundamentals | IS-IS is the most common IGP in MPLS/SR networks | 2026-04-19 |
| [RT-007](bgp-fundamentals.md) | BGP Fundamentals | IS-IS as the IGP that runs underneath BGP in carrier networks | 2026-04-19 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](routing-fundamentals.md) | Routing Fundamentals | Routing table, SPF, metric | 2026-04-19 |
| [RT-004](ospf-fundamentals.md) | OSPF Fundamentals | Link-state foundation; comparison basis | 2026-04-19 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XR | Juniper Junos | Nokia SR-OS | Arista EOS |
|---|---|---|---|---|---|
| Configure NET | ISO 10589 | `net <NET>` in router isis | `family iso address <NET>` on lo0 | `area-id` + `system-id` separate | `net <NET>` in router isis |
| View adjacencies | ISO 10589 | `show isis neighbors` | `show isis adjacency` | `show router isis adjacency` | `show isis neighbors` |
| View LSDB | ISO 10589 | `show isis database` | `show isis database` | `show router isis database` | `show isis database` |
| Wide metrics | RFC 3784 | `metric-style wide` | `wide-metrics-only` per level | Configured per interface | `isis metric-style wide` |
| Point-to-point link | ISO 10589 | `point-to-point` under interface | `point-to-point` under interface | `circuit-type point-to-point` | `isis network point-to-point` |

### Maintenance Notes

- When CT-001 (MPLS Fundamentals) is written, add a back-reference here for IS-IS as IGP in MPLS networks
- When SR modules are written, add references here to the TLV extensibility section for SR SID allocation

<!-- XREF-END -->
