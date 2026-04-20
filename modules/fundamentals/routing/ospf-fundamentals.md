---
title: "OSPF Fundamentals"
module_id: "RT-004"
domain: "fundamentals/routing"
difficulty: "intermediate"
prerequisites: ["RT-001", "RT-002", "RT-003", "NW-002"]
estimated_time: 60
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["ospf", "link-state", "lsa", "spf", "dijkstra", "area", "dr-bdr", "neighbor", "adjacency", "cost", "ospfv3"]
cert_alignment: "CCNA 200-301 — 3.4 | JNCIA-Junos JN0-103 | Nokia NRS I | Huawei HCIA-Datacom"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "Arista EOS", "Huawei VRP", "MikroTik RouterOS"]
language: "en"
---

## The Problem

Ten routers. Each knows its directly connected links. A link between Router A and Router B fails. With RIP (distance-vector), the routers slowly count to infinity — several minutes of loops and blackholes before the network stabilises. That's unacceptable.

The problem with distance-vector is fundamental: each router only knows distances reported by neighbours. It has no picture of the actual topology — where the links are, what they connect, which ones are healthy. When something changes, it can only react to what neighbours tell it, and neighbours might be wrong.

What if every router had a complete, accurate map of the entire network?

### Step 1: Share the map, not just distances

Instead of broadcasting "I can reach X in N hops," each router broadcasts something different: "Here is what I directly know. I am connected to Router B via a link that costs 10. I am connected to Router C via a link that costs 1."

This information — a router's identity, its links, and their costs — is called a **Link State Advertisement (LSA)**. Every router generates its own LSA and floods it across the entire network. Every other router stores every LSA it receives in a **Link State Database (LSDB)**.

When every router has every other router's LSA, every router has an identical, complete picture of the entire network topology.

### Step 2: Calculate the best path yourself

With a complete map, each router can now calculate the best path to every destination independently — it doesn't need to trust neighbours' distance claims. It runs **Dijkstra's Shortest Path First (SPF) algorithm** on its local copy of the LSDB. This is pure mathematics: given the graph of links and costs, find the minimum-cost path from this router to every other router.

No counting-to-infinity. No dependency on what neighbours claim. Each router derives its own routing table from first principles, using the shared map.

### Step 3: But the map gets large — use areas

In a network with 500 routers, every router stores 500 LSAs and runs SPF over a 500-node graph. That's expensive — every link change causes every router to rerun SPF. And LSA flooding fills the network with chatter.

The solution: divide the network into **areas**. Routers within an area share full LSA detail with each other. Routers between areas exchange **summary routes** — compressed information. A router at the boundary of two areas (an **Area Border Router** or ABR) translates between the two.

All areas must connect to **Area 0** (the backbone area). Area 0 is the spine; all other areas hang off it. This hierarchy reduces SPF complexity to a manageable level per area while still allowing full connectivity.

### Step 4: Not everyone needs a full adjacency

On a multi-access network (an Ethernet segment) with 10 routers, each router could form an adjacency with every other — resulting in 45 adjacencies and 45 × 2 = 90 LSA exchanges. This doesn't scale. 

The solution: elect a **Designated Router (DR)** and a **Backup Designated Router (BDR)**. Every other router (called a DROther) forms a full adjacency only with the DR and BDR. The DR collects all link-state information and redistributes to all. LSA flood count drops from O(n²) to O(n). The BDR monitors the DR and takes over instantly if it fails.

### What You Just Built

OSPF — Open Shortest Path First. A link-state routing protocol where every router floods its LSA to the entire area, stores a complete topology map (LSDB), and independently calculates the best path using Dijkstra's SPF algorithm.

| Scenario element | Technical term |
|---|---|
| "Here is what I am connected to" | Link State Advertisement (LSA) |
| The complete topology map each router maintains | Link State Database (LSDB) |
| The algorithm that calculates best paths from the map | Dijkstra's SPF (Shortest Path First) |
| Dividing the network into manageable regions | OSPF Areas |
| The spine area all others connect to | Area 0 (backbone) |
| The router that translates between areas | Area Border Router (ABR) |
| Elected router that controls LSA flooding on a segment | Designated Router (DR) |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** how link-state routing differs from distance-vector and why it solves the counting-to-infinity problem
2. **Describe** the OSPF neighbour and adjacency formation process — the steps from "hello received" to "full adjacency"
3. **Read** an OSPF neighbour table and identify the state of each relationship
4. **Explain** OSPF cost and how it determines the best path
5. **Describe** the role of DR and BDR on multi-access segments and how they are elected
6. **Identify** the purpose of OSPF areas and explain why Area 0 is required

---

## Prerequisites

- [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) — routing table, metric, AD, RIB vs FIB
- [Static Routing](static-routing.md) (`RT-002`) — manual routing context; what OSPF automates
- [RIP & Distance-Vector](rip-distance-vector.md) (`RT-003`) — the problems OSPF was designed to solve
- [Network Topologies](../networking/network-topologies.md) (`NW-002`) — broadcast domains; multi-access vs point-to-point links

---

## Core Content

### Link State vs Distance Vector

| Property | Distance-Vector (RIP) | Link-State (OSPF) |
|---|---|---|
| What is shared | Distance table (routing table) | LSAs — direct topology facts |
| Who knows the full topology | Nobody — only local distances | Every router — LSDB is complete |
| Path calculation | Neighbour's claim → add 1 → trust it | SPF on local full map — no trust needed |
| Routing loops | Possible; counting-to-infinity | Not possible — full map prevents loops |
| Convergence time | Minutes (periodic updates) | Seconds (event-triggered flooding) |
| Scale | Limited — hop count max 15 | Large networks — areas allow scaling |
| CPU/memory cost | Low | Higher — SPF computation + LSDB storage |

The key insight: link-state is more complex and heavier, but it **cannot count to infinity** because no router trusts a neighbour's distance claim — it derives paths itself from the shared map.

### OSPF Neighbor and Adjacency Formation

Before exchanging LSAs, OSPF routers must become **neighbours** and then form a **full adjacency**. This happens through a state machine — a sequence of states from first contact to full database synchronisation.

**OSPF Hello packets** — the first contact mechanism:
- Sent every `hello-interval` seconds (default: 10s on point-to-point, 10s on broadcast, 30s on NBMA)
- Contains: router ID, area ID, hello/dead intervals, authentication, DR/BDR, neighbour list
- Received on `224.0.0.5` (all OSPF routers multicast)
- If parameters don't match → no neighbour relationship forms

**Parameters that must match to form adjacency:**
- Area ID
- Hello interval and dead interval
- Authentication type and key
- Stub area flags
- MTU (on some platforms/IOS versions)

**OSPF State Machine — from zero to full:**

| State | What it means |
|---|---|
| **Down** | No hellos received from this neighbour |
| **Init** | Hello received, but our Router ID is not yet in their neighbour list |
| **2-Way** | Our Router ID appears in their hello — bidirectional communication confirmed. DROther-DROther stops here |
| **ExStart** | Negotiate who is Master/Slave for DBD exchange; establish sequence numbers |
| **Exchange** | Exchange Database Description (DBD) packets — summaries of LSDB contents |
| **Loading** | Send Link State Requests (LSR) for LSAs the neighbour has that we don't; receive Link State Updates (LSU) |
| **Full** | LSDB is synchronised; routing table can be computed |

**On broadcast/Ethernet segments:**
- DROther routers reach **Full** only with DR and BDR
- DROther–DROther pairs stop at **2-Way**
- This is correct and expected — not a problem

```text
Neighbour table example (Cisco):
R1# show ip ospf neighbor

Neighbor ID  Pri  State      Dead Time  Address       Interface
10.0.0.2     1    FULL/DR    00:00:38   10.1.1.2     Gi0/0
10.0.0.3     1    FULL/BDR   00:00:35   10.1.1.3     Gi0/0
10.0.0.4     0    2WAY/DROTHER  00:00:37  10.1.1.4  Gi0/0
```

### OSPF Cost

OSPF uses **cost** as its metric. Lower cost = better path. Cost is **additive** — the total cost of a path is the sum of costs of all outgoing interfaces along the path.

**Cost formula (Cisco default):**
```text
Cost = Reference Bandwidth ÷ Interface Bandwidth

Default Reference Bandwidth = 100 Mbps = 100,000,000 bps

Interface         Bandwidth    Cost
GigabitEthernet   1 Gbps     100M ÷ 1000M = 0.1 → rounded to 1
FastEthernet      100 Mbps   100M ÷ 100M  = 1
10 Mbps Ethernet  10 Mbps    100M ÷ 10M   = 10
T1/E1             1.544 Mbps 100M ÷ 1.544M ≈ 64
```

**Problem:** The default reference bandwidth (100 Mbps) was designed in the 1990s. With the same formula, GigabitEthernet, 10GE, and 100GE all calculate to cost 1 — indistinguishable. OSPF cannot prefer a 100GE path over a 1GE path if both cost 1.

**Fix:** Set the reference bandwidth to something larger than your fastest link:
```text
auto-cost reference-bandwidth 100000    (Cisco — sets reference to 100 Gbps)
```
This must be configured consistently on ALL routers in the OSPF domain, or costs will be asymmetric and routing will be unpredictable.

??? supplementary "OSPF Cost — Manual Override and Policy"
    Cost can also be set manually per interface, overriding the formula:
    ```cisco-ios
    interface GigabitEthernet0/0
     ip ospf cost 50
    ```
    Manual cost is useful when:
    - You want to prefer one path over another independent of bandwidth
    - The formula produces equal costs across unequal links (bandwidth ties)
    - You need to influence inbound traffic from remote OSPF neighbours (requires changing cost on the remote side)

    Junos and Nokia set cost via `metric` under the routing protocol configuration, not the interface, by default — though interface-level settings are also possible.

### Designated Router (DR) and Backup Designated Router (BDR)

On any **multi-access network** (broadcast Ethernet, Frame Relay), OSPF elects a DR and BDR to reduce the number of adjacencies and LSA flood copies.

**Without DR/BDR:**
- N routers on a segment → N×(N-1)/2 adjacencies
- 10 routers → 45 adjacencies; each LSA copied 45 times

**With DR/BDR:**
- All routers form Full adjacency with DR and BDR only
- DROthers form 2-Way with each other — no exchange of LSAs between DROthers directly
- DR redistributes LSAs to all (`224.0.0.5`) after receiving them
- 10 routers → 9 adjacencies to DR + 9 to BDR = 18 total (vs 45)

**DR/BDR election:**
1. Highest OSPF **priority** wins (0–255; default = 1; priority 0 = ineligible)
2. Tie-break: highest **Router ID** (the OSPF Router ID — typically highest loopback IP or manually set)
3. Election is **non-preemptive** — once elected, the DR keeps its role until it fails or OSPF restarts; a higher-priority router that comes up later does not displace the current DR

```text
R1# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet address 10.1.1.1/24, Area 0
  OSPF Process ID 1, Router ID 1.1.1.1
  Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State DR, Priority 1
  Designated Router (ID) 1.1.1.1, Interface address 10.1.1.1
  Backup Designated Router (ID) 2.2.2.2, Interface address 10.1.1.2
  Timer intervals: Hello 10, Dead 40, Wait 40, Retransmit 5
  Neighbor Count is 2, Adjacent neighbor count is 2
```

**On point-to-point links** (serial, PPP, MPLS tunnels): no DR/BDR election — both routers form Full adjacency directly.

### OSPF Areas

OSPF uses a **two-level hierarchy** to scale:

```text
                    ┌──────────────────────────────┐
                    │         Area 0 (Backbone)     │
                    │  ABR ─────────────── ABR      │
                    └────┬──────────────────┬───────┘
                         │                  │
               ┌─────────┴──────┐   ┌───────┴────────┐
               │    Area 1      │   │    Area 2       │
               │ (non-backbone) │   │ (non-backbone)  │
               └────────────────┘   └─────────────────┘
```

- **Area 0** is mandatory — the backbone. All non-backbone areas must connect to Area 0.
- **Area Border Routers (ABRs)** sit at the boundary between areas. They have a full LSDB for each area they belong to. They generate **Type 3 LSAs** (summary LSAs) advertising networks from one area into another.
- Routers **within an area** have full LSA detail for all routers in their area.
- Routers in **different areas** only see summary routes (prefix + cost) for other areas — not the full topology detail.

**Why all areas must connect to Area 0:**
OSPF guarantees loop-free routing because within a single area, every router has the complete topology. Between areas, routing is based on distance-vector-like summary information — which could theoretically loop if areas were connected in a ring. Forcing all areas through Area 0 prevents inter-area loops by ensuring all inter-area traffic passes through a common spine.

**LSA Types:**

| LSA Type | Name | Generated by | Scope | Purpose |
|---|---|---|---|---|
| Type 1 | Router LSA | Every router | Within area | Router's own links and costs |
| Type 2 | Network LSA | DR | Within area | Multi-access segment (DR represents the segment) |
| Type 3 | Summary LSA | ABR | Into adjacent areas | Advertises networks from one area to another |
| Type 4 | ASBR Summary LSA | ABR | Backbone to other areas | Points to an ASBR (external route injector) |
| Type 5 | External LSA | ASBR | Domain-wide | External routes redistributed into OSPF |
| Type 7 | NSSA External LSA | ASBR in NSSA | NSSA area only | External routes in a Not-So-Stubby Area |

For CCNA/NRS I level: understand Type 1, 2, 3, and 5. Advanced area types (stub, NSSA) are covered in RT-005 (OSPF Advanced).

### OSPF Router ID

Every OSPF router has a **Router ID (RID)** — a 32-bit value written in dotted-decimal like an IPv4 address, but it is an identifier, not a routable address.

**RID selection order (Cisco):**
1. Manually configured RID: `router-id X.X.X.X`
2. Highest IP address on any **loopback** interface (loopbacks never go down unless OS-shutdown)
3. Highest IP address on any **non-loopback** interface

**Best practice:** always configure the RID manually using a loopback address:
```cisco-ios
interface Loopback0
 ip address 1.1.1.1 255.255.255.255

router ospf 1
 router-id 1.1.1.1
```

A loopback address used as a RID is also useful as a management address — always reachable as long as the router is up.

---

## Vendor Implementations

OSPF is standardised in RFC 2328 (OSPFv2 for IPv4) and RFC 5340 (OSPFv3 for IPv6). All compliant implementations share the same protocol behaviour — hello/dead intervals, state machine, LSA types, SPF algorithm. Syntax differences are in configuration only.

!!! success "Standard — RFC 2328 (OSPFv2), RFC 5340 (OSPFv3)"
    Any RFC-compliant OSPF implementation forms adjacencies with any other. Multi-vendor OSPF adjacencies are routine in real networks. Verify that hello intervals, dead intervals, area IDs, and MTU match across vendors.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Enable OSPF process 1 — process ID is local only; does not affect interop
    router ospf 1
     router-id 1.1.1.1
     auto-cost reference-bandwidth 100000   ! 100 Gbps reference — set on ALL routers

    ! Assign interfaces to an area
    interface GigabitEthernet0/0
     ip ospf 1 area 0      ! preferred — interface-level config
     ip ospf priority 100  ! increase to win DR election if needed
     ip ospf cost 10       ! manual cost override

    ! Alternatively, use network statements (classic syntax)
    router ospf 1
     network 10.1.1.0 0.0.0.255 area 0

    ! Verify
    show ip ospf neighbor
    show ip ospf interface brief
    show ip ospf database
    show ip route ospf
    ```
    Cisco supports both interface-level (`ip ospf <pid> area <area>`) and process-level (`network` statements) OSPF assignment. Interface-level is more explicit and preferred in modern configs. The OSPF process ID (e.g., `ospf 1`) is local — two routers with different process IDs can still form an adjacency.

    Full configuration reference: [Cisco OSPF Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/configuration/xe-16/iro-xe-16-book.html)

=== "Juniper Junos"
    ```junos
    # Configure OSPF area and interfaces
    set protocols ospf area 0.0.0.0 interface ge-0/0/0.0
    set protocols ospf area 0.0.0.0 interface lo0.0 passive

    # Set reference bandwidth (affects cost calculation)
    set protocols ospf reference-bandwidth 100g

    # Adjust interface cost manually
    set protocols ospf area 0 interface ge-0/0/0.0 metric 10

    # Set Router ID
    set routing-options router-id 1.1.1.1

    # Verify
    show ospf neighbor
    show ospf interface
    show ospf database
    show route protocol ospf
    ```
    In Junos, areas are written as dotted-decimal (Area 0 = `0.0.0.0`). The loopback interface should be added as `passive` — it advertises the address into OSPF but doesn't send hellos. The Router ID is set under `routing-options`, not under the OSPF stanza.

    Full configuration reference: [Juniper OSPF Configuration](https://www.juniper.net/documentation/us/en/software/junos/ospf/index.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # Configure OSPF (classic CLI)
    configure router ospf
        area 0.0.0.0
            interface "to-R2"
                interface-type point-to-point
                no shutdown
            exit
            interface "system"
                passive
                no shutdown
            exit
        exit
        no shutdown
    exit

    # Set reference bandwidth
    configure router ospf reference-bandwidth 100000000   ! in kbps = 100 Gbps

    # Verify
    show router ospf neighbor
    show router ospf interface
    show router ospf database
    show router route-table protocol ospf
    ```
    SR-OS uses "system interface" (loopback equivalent) as the Router ID source. The `passive` keyword suppresses hello messages on loopback/system interfaces. Interface types (broadcast, point-to-point) must be specified explicitly where needed.

    Full configuration reference: [Nokia SR-OS OSPF Guide](https://documentation.nokia.com/sr/)

=== "Arista EOS"
    ```arista-eos
    ! OSPF configuration (similar to Cisco IOS)
    router ospf 1
     router-id 1.1.1.1
     auto-cost reference-bandwidth 100000   ! 100 Gbps

    interface Ethernet1
     ip ospf 1 area 0.0.0.0
     ip ospf cost 10

    ! Verify
    show ip ospf neighbor
    show ip ospf interface
    show ip ospf database
    show ip route ospf
    ```
    Arista EOS OSPF syntax is nearly identical to Cisco IOS-XE. The main differences are in show command output format and some advanced feature syntax.

    Full configuration reference: [Arista EOS OSPF Configuration](https://www.arista.com/en/um-eos/eos-ospf-configuration)

=== "Huawei VRP"
    ```huawei-vrp
    # Enable OSPF process
    ospf 1 router-id 1.1.1.1

    # Configure area and network
    area 0
     network 10.1.1.0 0.0.0.255

    # Set interface cost
    interface GigabitEthernet0/0/0
     ospf cost 10

    # Set bandwidth-reference for cost calculation
    ospf 1
     bandwidth-reference 100000   ! 100 Gbps in Mbps

    # Verify
    display ospf peer
    display ospf interface
    display ospf lsdb
    display ip routing-table protocol ospf
    ```
    Huawei VRP uses `display` instead of `show`. The `network` command under the `area` stanza uses wildcard masks (same as Cisco). `bandwidth-reference` is in Mbps.

    Full configuration reference: [Huawei VRP OSPF Configuration](https://support.huawei.com/enterprise/en/doc/EDOC1100278578)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # Configure OSPF instance and area
    /routing ospf instance add name=default router-id=1.1.1.1
    /routing ospf area add name=backbone area-id=0.0.0.0 instance=default

    # Assign interfaces to area
    /routing ospf interface-template add area=backbone interfaces=ether1 type=broadcast
    /routing ospf interface-template add area=backbone interfaces=lo0 passive=yes

    # Set interface cost
    /routing ospf interface-template add area=backbone interfaces=ether1 cost=10

    # Verify
    /routing ospf neighbor print
    /routing ospf interface print
    /routing ospf lsa print
    /ip route print where protocol=ospf
    ```
    RouterOS v7 uses the new routing framework with instances, areas, and interface templates. Earlier RouterOS v6 used a different syntax. The `passive=yes` flag on loopback suppresses hellos while still advertising the prefix.

    Full configuration reference: [MikroTik OSPF Reference](https://help.mikrotik.com/docs/display/ROS/OSPF)

---

## Common Pitfalls

### Pitfall 1: Hello/dead interval mismatch

The most common reason two OSPF routers never form an adjacency. If Router A sends hellos every 10 seconds and Router B expects them every 30 seconds, they will not form a neighbour relationship — the routers will see each other's hellos but the parameters won't match. Check `show ip ospf interface` on both sides and verify the hello and dead intervals are identical.

### Pitfall 2: MTU mismatch blocking adjacency

On Cisco IOS, if two routers have different interface MTUs, OSPF may get stuck in the ExStart/Exchange state (trying to exchange DBD packets). The MTU in the DBD packet is checked — if it doesn't match, the exchange fails. Fix: set matching MTUs on both sides, or add `ip ospf mtu-ignore` on the interface to suppress the check (not recommended for production — it hides a real misconfiguration).

### Pitfall 3: Area 0 required for inter-area routing

A common design error: connecting two non-backbone areas to each other without going through Area 0. OSPF will not route between them — inter-area routes require Area 0 in the path. All non-backbone areas must have an ABR connected to Area 0. If physical connectivity to Area 0 is not possible, use a **virtual link** through a transit area — but this is a design workaround, not a first choice.

### Pitfall 4: DR election locking out the intended DR

OSPF DR election is non-preemptive. If Router B (priority 1) comes up before Router A (priority 255), Router B wins the DR election. When Router A comes up later with higher priority, it does not displace Router B. Fix: either configure priority before bringing up routers, or clear OSPF on the segment to force a new election (`clear ip ospf process`). In production, plan the priority assignment before deployment.

### Pitfall 5: reference-bandwidth not set consistently

If different routers have different reference-bandwidth values, cost calculations become inconsistent. Router A may see cost 1 to a network; Router B may see cost 10 for the same link — leading to asymmetric routing or suboptimal paths. Always set `auto-cost reference-bandwidth` to the same value on every router in the OSPF domain.

---

## Practice Problems

1. Two routers are directly connected. R1 has hello interval = 10, dead interval = 40. R2 has hello interval = 30, dead interval = 120. Do they form an OSPF adjacency? What would you change?

2. A Cisco router has reference-bandwidth = 100 Mbps (default). Calculate the OSPF cost for a 10 GigabitEthernet interface and a FastEthernet interface. What problem does this reveal?

3. Five routers are on an Ethernet segment. All have priority 1. Router IDs are 1.1.1.1, 2.2.2.2, 3.3.3.3, 4.4.4.4, 5.5.5.5. All come up simultaneously. Which becomes DR? Which becomes BDR? A sixth router with RID 6.6.6.6 and priority 255 joins later — does it become DR?

4. Draw (in words or ASCII) the OSPF adjacency state machine from Down to Full. At which state do DROther routers stop with other DROthers?

5. A multi-area OSPF network has Area 0, Area 1, and Area 2. Area 1 and Area 2 are both connected only to Area 0. Can a router in Area 1 reach a network in Area 2? What LSA type carries the route from Area 2 into Area 1?

??? "Answers"
    **1.** No adjacency — hello intervals must match (10 ≠ 30). Change R2 to hello=10, dead=40 (or change R1 to hello=30, dead=120, if 30s is acceptable). The dead interval should be at least 4× the hello interval.

    **2.** 10GE: 100M ÷ 10,000M = 0.01 → rounded to **1**. FastEthernet: 100M ÷ 100M = **1**. Both cost the same — OSPF cannot prefer the 10GE path over the FastEthernet path. Fix: set `auto-cost reference-bandwidth 10000` (10 Gbps) or higher so 10GE = 1 and FastEthernet = 100.

    **3.** Highest RID wins DR election when priority is tied. **DR = 5.5.5.5, BDR = 4.4.4.4**. When the sixth router (RID 6.6.6.6, priority 255) joins later — **it does not become DR**. DR election is non-preemptive; the current DR (5.5.5.5) keeps its role until it fails. The new router forms Full adjacency with the DR and BDR as a DROther.

    **4.** Down → Init → 2-Way → ExStart → Exchange → Loading → Full.
    DROther–DROther pairs stop at **2-Way**. This is correct; they exchange only hellos, not LSAs.

    **5.** Yes — Area 1 can reach Area 2 via Area 0. An ABR connected to Area 2 generates **Type 3 Summary LSAs** for Area 2 networks and floods them into Area 0. An ABR connected to Area 1 then generates Type 3 LSAs into Area 1 summarising the Area 2 networks. Routers in Area 1 see the prefix + cost but not the full Area 2 topology.

---

## Lab

### Lab: Configure a Two-Router OSPF Adjacency

**Tools:** GNS3 or Cisco Packet Tracer
**Estimated time:** 25 minutes
**Objective:** Configure OSPFv2 between two routers, verify neighbour adjacency reaches Full state, and observe cost-based path selection.

**Topology:**
```text
[R1] Lo0: 1.1.1.1/32               [R2] Lo0: 2.2.2.2/32
     Gi0/0: 10.12.0.1/30   ←———→   Gi0/0: 10.12.0.2/30
     Gi0/1: 10.1.0.1/24             Gi0/1: 10.2.0.1/24
```

**Steps:**

1. Configure loopbacks and all interface IPs. Enable OSPF on both routers:

    ```cisco-ios
    ! On both R1 and R2:
    router ospf 1
     auto-cost reference-bandwidth 100000

    ! On R1:
    router ospf 1
     router-id 1.1.1.1

    interface Loopback0
     ip ospf 1 area 0
    interface GigabitEthernet0/0
     ip ospf 1 area 0
    interface GigabitEthernet0/1
     ip ospf 1 area 0

    ! On R2:
    router ospf 1
     router-id 2.2.2.2

    interface Loopback0
     ip ospf 1 area 0
    interface GigabitEthernet0/0
     ip ospf 1 area 0
    interface GigabitEthernet0/1
     ip ospf 1 area 0
    ```

2. Verify neighbour adjacency reaches Full state (may take up to 40 seconds for dead timer):

    ```text
    R1# show ip ospf neighbor
    Neighbor ID  Pri  State    Dead Time  Address     Interface
    2.2.2.2      1    FULL/DR  00:00:38   10.12.0.2  Gi0/0
    ```

3. Verify OSPF routes in the routing table:

    ```text
    R1# show ip route ospf
    O    2.2.2.2/32 [110/2] via 10.12.0.2, Gi0/0
    O    10.2.0.0/24 [110/2] via 10.12.0.2, Gi0/0
    ```

4. Check the LSDB — both routers should have identical entries:

    ```text
    R1# show ip ospf database
    Router Link States (Area 0):
      Link ID    ADV Router  Age  Seq#       Checksum
      1.1.1.1    1.1.1.1     32   0x80000004 0x00xxxx
      2.2.2.2    2.2.2.2     30   0x80000003 0x00xxxx
    ```

5. Verify connectivity: ping R2's loopback from R1:

    ```text
    R1# ping 2.2.2.2 source 1.1.1.1
    !!!!!
    ```

??? supplementary "Lab extension: Change cost and observe path change"
    Add a second link between R1 and R2 (Gi0/2 on both) with a /30 address. OSPF installs both paths as ECMP (equal cost). Then manually set the cost on one link higher:
    ```cisco-ios
    interface GigabitEthernet0/2
     ip ospf cost 100
    ```
    Check `show ip route` — R1 now uses only the lower-cost path. OSPF has made a policy-based forwarding decision based purely on cost, without any manual route configuration.

---

## Summary & Key Takeaways

- OSPF is a **link-state** protocol: every router floods its LSA (its direct links and costs) to all routers in the area
- Every router builds an identical **LSDB** (Link State Database) — a full map of the area topology
- Each router independently runs **Dijkstra's SPF** algorithm on its LSDB to calculate the shortest path to every destination
- Because every router has the full map and derives paths independently, **routing loops cannot form** within an OSPF area
- OSPF neighbours must **match**: area ID, hello/dead intervals, authentication, and MTU (on Cisco)
- The neighbour state machine: Down → Init → 2-Way → ExStart → Exchange → Loading → **Full**
- On multi-access (Ethernet) segments, **DR and BDR** are elected to reduce adjacency count from O(n²) to O(n)
- **DR election** uses priority (higher wins), then Router ID (higher wins); it is **non-preemptive**
- **OSPF cost** = reference bandwidth ÷ interface bandwidth; set `auto-cost reference-bandwidth` consistently across all routers
- OSPF **areas** reduce LSDB size and SPF computation; all areas must connect to **Area 0** (backbone)
- ABRs advertise **Type 3 Summary LSAs** between areas; Type 5 External LSAs carry redistributed routes
- OSPFv3 (RFC 5340) is the IPv6 version — same algorithm, different address family

---

## Where to Next

- **Continue:** [BGP Fundamentals](bgp-fundamentals.md) (`RT-007`) — the routing protocol between autonomous systems; builds on OSPF understanding of path selection
- **Continue:** [OSPF Advanced](ospf-advanced.md) (`RT-005`) — multi-area design, stub areas, NSSA, redistribution, virtual links, route filtering
- **Related:** [IS-IS Fundamentals](isis-fundamentals.md) (`RT-006`) — another link-state protocol; widely used in carrier and DC networks; compare with OSPF
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) — Stage 3, position 14 in the DNE path

---

## Standards & Certifications

**Relevant standards:**
- [RFC 2328 — OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 5340 — OSPF for IPv6 (OSPFv3)](https://www.rfc-editor.org/rfc/rfc5340)
- [RFC 4940 — IANA Considerations for OSPF](https://www.rfc-editor.org/rfc/rfc4940)

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 3.4 — Configure and verify single-area OSPFv2 |
| JNCIA-Junos JN0-103 | Juniper | OSPF fundamentals; neighbour states; cost |
| Nokia NRS I | Nokia | OSPF link-state concepts; DR/BDR; areas |
| Huawei HCIA-Datacom | Huawei | OSPF neighbour states; DR election; LSA types |

---

## References

- IETF — [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- IETF — [RFC 5340: OSPF for IPv6](https://www.rfc-editor.org/rfc/rfc5340)
- Odom, W. — *CCNA 200-301 Official Cert Guide, Volume 2*, Cisco Press, 2019 — Ch. 20–22 (OSPF)
- Doyle, J.; Carroll, J. — *Routing TCP/IP, Volume I*, 2nd ed., Cisco Press, 2005 — Ch. 8–11 (OSPF)
- Dijkstra, E. W. — "A Note on Two Problems in Connexion with Graphs," *Numerische Mathematik*, vol. 1, 1959 — original SPF algorithm paper

---

## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Draft written by Claude Sonnet 4.6. RFC citations verified against IETF RFC index. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-005](ospf-advanced.md) | OSPF Advanced | Builds directly on this module — multi-area, stub areas, redistribution | 2026-04-17 |
| [RT-007](bgp-fundamentals.md) | BGP Fundamentals | BGP runs alongside OSPF in most enterprise networks; AD comparison | 2026-04-17 |
| [CT-001](../carrier-transport/mpls-fundamentals.md) | MPLS Fundamentals | OSPF is the most common IGP running under MPLS networks | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](routing-fundamentals.md) | Routing Fundamentals | Routing table, metric, AD, RIB vs FIB | 2026-04-17 |
| [RT-002](static-routing.md) | Static Routing | Context for what OSPF replaces; floating static still used alongside OSPF | 2026-04-17 |
| [RT-003](rip-distance-vector.md) | RIP & Distance-Vector | Problems OSPF was designed to solve | 2026-04-17 |
| [NW-002](../networking/network-topologies.md) | Network Topologies | Multi-access vs point-to-point; DR/BDR applies to broadcast segments | 2026-04-17 |
| [IP-003](../ip/ipv6-addressing.md) | IPv6 Addressing | OSPFv3 uses IPv6 link-local addresses for neighbour formation | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | Arista EOS | Huawei VRP | MikroTik RouterOS |
|---|---|---|---|---|---|---|---|
| Enable OSPF | RFC 2328 | `router ospf <pid>` | `set protocols ospf` | `configure router ospf` | `router ospf <pid>` | `ospf <pid>` | `/routing ospf instance add` |
| Set Router ID | RFC 2328 | `router-id X.X.X.X` | `set routing-options router-id` | `configure router router-id` | `router-id X.X.X.X` | Router ID in ospf stanza | `router-id=X.X.X.X` |
| View neighbours | RFC 2328 | `show ip ospf neighbor` | `show ospf neighbor` | `show router ospf neighbor` | `show ip ospf neighbor` | `display ospf peer` | `/routing ospf neighbor print` |
| View LSDB | RFC 2328 | `show ip ospf database` | `show ospf database` | `show router ospf database` | `show ip ospf database` | `display ospf lsdb` | `/routing ospf lsa print` |
| Interface cost | RFC 2328 | `ip ospf cost X` | `metric X` (under protocol) | Interface metric config | `ip ospf cost X` | `ospf cost X` | `cost=X` in template |
| Reference bandwidth | RFC 2328 | `auto-cost reference-bandwidth` | `reference-bandwidth` | `reference-bandwidth` | `auto-cost reference-bandwidth` | `bandwidth-reference` | Not configurable separately |

### Maintenance Notes

- When RT-005 (OSPF Advanced) is written, add a back-reference there to this module for all foundational concepts
- When RT-006 (IS-IS Fundamentals) is written, add a comparison reference — link-state concept is shared; implementation differs
- When CT-001 (MPLS Fundamentals) is written, add a reference: OSPF is the typical IGP in MPLS networks; LDP/RSVP-TE builds on OSPF adjacency

<!-- XREF-END -->
