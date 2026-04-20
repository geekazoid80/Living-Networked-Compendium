---
title: "Routing Fundamentals"
module_id: "RT-001"
domain: "fundamentals/routing"
difficulty: "intermediate"
prerequisites: ["IP-001", "IP-002", "NW-001", "NW-002"]
estimated_time: 45
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["routing", "routing-table", "longest-prefix-match", "administrative-distance", "next-hop", "forwarding", "convergence"]
cert_alignment: "CCNA 200-301 - 3.1–3.3 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "MikroTik RouterOS"]
language: "en"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** what a router does and why Layer 2 switching alone is insufficient for inter-network communication
2. **Read** a routing table and identify the next-hop, exit interface, and route source for a given destination
3. **Apply** longest-prefix match to determine which routing table entry a router will use for a specific destination address
4. **Describe** administrative distance and explain how it determines which route is installed when multiple sources know a path to the same destination
5. **Distinguish** between the routing table (what the router knows) and the forwarding table (what it acts on)

---
## Prerequisites

- [IP Addressing Fundamentals](../ip/ip-addressing.md) (`IP-001`) - CIDR notation, network and host portions, subnet masks
- [IP Subnetting & VLSM](../ip/subnetting.md) (`IP-002`) - prefix lengths, address blocks, calculating overlaps
- [The OSI Model](../networking/osi-model.md) (`NW-001`) - Layer 2 vs Layer 3 distinction; why MAC addresses do not cross routers
- [Network Topologies](../networking/network-topologies.md) (`NW-002`) - broadcast domains; how routers bound them

---
## The Problem

Two office buildings. Building A has 50 devices - laptops, servers, printers - all on the same floor, all connected to the same switch. Building B has another 50 devices, connected to their own switch. A direct cable runs between the buildings.

Someone in Building A needs to send a file to someone in Building B. At the switch level, they're on different segments. The switch in Building A can't forward that frame directly - it doesn't know where Building B's devices are, and even if it did, Layer 2 doesn't cross between separate network segments without help.

Something needs to know the way between buildings. Something needs to make a decision.

### Step 1: Who knows the path?

The switch in Building A can deliver frames within the building. But it has no concept of "other buildings." It only knows MAC addresses on its own ports.

You need a device that understands **networks** rather than just individual addresses. A device that can look at a destination IP address, consult a map of the network, and decide: "This packet should go out this interface, toward that device."

That device is a **router**. The "map" it consults is its **routing table**.

### Step 2: The routing table - what's in the map?

The routing table is a list of known destinations and how to reach them. Each entry says:
- *"For packets going to network X..."*
- *"...send them out interface Y, toward next-hop address Z."*

```text
Network           Next-hop         Interface
10.0.0.0/8        192.168.1.1      eth0
172.16.0.0/12     10.1.1.1         eth1
0.0.0.0/0         203.0.113.1      eth2      ← default route: "everything else"
```

The router reads the destination IP address of each incoming packet, looks it up in this table, and forwards the packet accordingly. The sender doesn't choose the path - the **router** does, at each hop.

### Step 3: Two entries match - which one wins?

The file transfer from Building A reaches a router. The routing table has two matching entries for the destination `10.1.2.50`:

```text
10.0.0.0/8     →  via eth0
10.1.0.0/16    →  via eth1
```

Both match. Which does the router use?

The router always picks the **most specific match** - the entry with the longest prefix (highest number of fixed bits). `10.1.0.0/16` is more specific than `10.0.0.0/8`, so the router uses the /16 entry. This is called **longest-prefix match**.

This rule is what makes routing tables scalable: a router can have a general route for a large address block and a more specific route for a subset, and the right one always wins.

### Step 4: Multiple routes to the same destination - which source do you trust?

The routing table now has two routes to `10.1.0.0/16`: one learned from a static configuration, one learned from a routing protocol. They both point to the same destination but via different paths.

How does the router decide which one to install?

Each route source has a trustworthiness score - **Administrative Distance (AD)**. Lower AD = more trusted. The route with the lowest AD wins and is installed in the forwarding table. If the preferred route disappears, the next-best AD takes over.

| Source | Cisco AD | Juniper Preference |
|---|---|---|
| Connected | 0 | 0 |
| Static | 1 | 5 |
| OSPF | 110 | 10 |
| RIP | 120 | 100 |
| BGP (eBGP) | 20 | 170 |

### What You Just Built

A router - a device that maintains a routing table, applies longest-prefix match to choose a forwarding path, and uses administrative distance to prefer one route source over another.

| Scenario element | Technical term |
|---|---|
| The device that decides where packets go | Router |
| The map of known destinations | Routing table |
| "Most specific match wins" | Longest-prefix match (LPM) |
| Each intermediate router the packet passes through | Hop |
| Trustworthiness score for a route source | Administrative Distance (AD) |
| The next device a packet is sent toward | Next-hop |
| Route of last resort - "everything else" | Default route (0.0.0.0/0 or ::/0) |

---
## Core Content

### What Routing Is

**Routing** is the process of selecting a path for traffic to travel from its source network to its destination network. A router performs routing at Layer 3: it reads the destination IP address in the packet header and decides where to send the packet next.

Each **hop** is one router in the path from source to destination. A packet may cross many hops before it arrives. At each hop, the same process runs: read destination IP, look up routing table, forward.

```text
  PC-A             R1              R2             Server
  [10.0.1.5]  ——→  [10.0.1.1]  ——→  [10.0.2.1]  ——→  [10.0.2.10]
             hop 1              hop 2

At R1: destination 10.0.2.10 — which interface leads toward 10.0.2.0/24?
At R2: destination 10.0.2.10 — is 10.0.2.10 directly connected? Yes → deliver.
```

Routing is **per-hop** and **stateless** - each router makes an independent decision. No router sees the full path; each only knows its own next step.

### The Routing Table

The routing table is a database of known network destinations and how to reach them. Each entry (called a **route**) contains:

| Field | Meaning |
|---|---|
| Destination prefix | The network address and prefix length (e.g., `10.1.0.0/24`) |
| Next-hop | The IP address of the next router to send the packet toward |
| Exit interface | The local interface the packet leaves through |
| Route source | How the router learned this route (connected, static, OSPF, BGP, etc.) |
| Metric | The cost of using this route (lower is better; varies by protocol) |
| Administrative Distance | Trustworthiness of the source; used to select between competing sources |

**Types of routes:**

| Type | Source | When it appears |
|---|---|---|
| **Connected** | Interface configuration | Automatically when an interface with an IP is up |
| **Local** | Interface configuration | Router's own address on that interface (`/32` or `/128`) |
| **Static** | Manual config | Administrator enters it explicitly |
| **Dynamic** | Routing protocol (OSPF, BGP, RIP, IS-IS) | Learned automatically from neighbours |
| **Default** | Static or dynamic | Route of last resort - matches everything not more specifically matched |

**Sample routing table output (Cisco IOS-XE):**
```text
R1# show ip route
Codes: C - connected, S - static, O - OSPF, B - BGP, * - candidate default

     10.0.0.0/8 is variably subnetted
C       10.0.1.0/24 is directly connected, GigabitEthernet0/0
L       10.0.1.1/32 is directly connected, GigabitEthernet0/0
S       10.0.2.0/24 [1/0] via 10.0.1.2
O       10.0.3.0/24 [110/2] via 10.0.1.2, 00:05:23, GigabitEthernet0/0
B*      0.0.0.0/0 [20/0] via 203.0.113.1
```

Reading the output:
- `[1/0]` - `[AD/metric]`: AD=1 (static), metric=0
- `[110/2]` - AD=110 (OSPF), metric=2 (cost)
- `C` routes are directly connected - no next-hop needed, just deliver
- `*` marks the default route candidate

### Longest-Prefix Match

When a packet arrives, the router compares the destination IP address against every entry in the routing table. There may be multiple matches. The router always installs and uses the **most specific** (longest prefix) match.

```text
Routing table contains:
  10.0.0.0/8      via 10.99.0.1  (8-bit prefix — broad)
  10.1.0.0/16     via 10.99.0.2  (16-bit prefix — narrower)
  10.1.2.0/24     via 10.99.0.3  (24-bit prefix — most specific)

Packet destination: 10.1.2.50

Match candidates:
  10.0.0.0/8    ✓  (10.1.2.50 is in 10.0.0.0/8)
  10.1.0.0/16   ✓  (10.1.2.50 is in 10.1.0.0/16)
  10.1.2.0/24   ✓  (10.1.2.50 is in 10.1.2.0/24)

Winner: 10.1.2.0/24 — longest prefix wins
```

If **no** match is found at all - and no default route exists - the router **drops** the packet and may send an ICMP "Destination Unreachable" back to the source.

The default route (`0.0.0.0/0` for IPv4, `::/0` for IPv6) has a prefix length of zero - it matches everything. It is always the lowest-priority match, used only when nothing more specific exists.

??? supplementary "Why Longest-Prefix Match Enables Summarisation"
    Longest-prefix match is what makes **route summarisation** (aggregation) possible. A router can advertise a summary route like `10.0.0.0/8` to the rest of the network while keeping detailed `/24` routes internally.

    Packets arriving from outside see only `10.0.0.0/8` and forward toward this router. Once they arrive, the router applies LPM and routes internally to the correct `/24`. The external network carries fewer routes; the internal router has the detail. Both work correctly because LPM ensures the most specific match always wins.

    This is also why summarisation boundaries matter: if a more-specific route `10.1.2.0/24` is reachable via a different path than the summary `10.0.0.0/8`, a router that has both routes will always choose the /24 - even if you intended the /8 summary to catch everything.

### Administrative Distance

When two different route sources both know a path to the same destination, the router must choose one to install in the routing table. It uses **Administrative Distance (AD)** - a preference score assigned to each source. Lower AD = more trusted = preferred.

| Route Source | Cisco AD | Juniper Preference | Nokia Preference |
|---|---|---|---|
| Connected interface | 0 | 0 | 0 |
| Static route | 1 | 5 | 5 |
| eBGP | 20 | 170 | 170 |
| OSPF | 110 | 10 | 10 |
| IS-IS | 115 | 15 | 15 |
| RIP | 120 | 100 | 100 |
| iBGP | 200 | 170 | 170 |

Note that Cisco and Juniper/Nokia use **opposite conventions**: Cisco prefers lower AD; Juniper and Nokia also prefer lower preference numbers. The values differ but the logic is the same - the number signals trustworthiness.

AD only matters when two sources report a path to **the same prefix**. If only one source knows about a prefix, it is installed regardless of its AD.

??? supplementary "Floating Static Routes"
    A **floating static route** is a static route configured with an artificially high AD - higher than the routing protocol that normally handles that destination. Under normal operation, the routing protocol's route wins. If the routing protocol route disappears (neighbour down, link failure), the static route "floats" to the top and is installed as a backup.

    Example: OSPF AD = 110. A floating static with AD = 200 stays hidden while OSPF works. If OSPF fails, AD 200 beats nothing, and the static installs.

    This is a simple, protocol-independent backup mechanism - useful when you can't run a routing protocol on the backup link.

### Routing Table vs Forwarding Table

The distinction confuses many learners. In high-performance routers, there are actually two tables:

| Table | Also called | Purpose | Where it lives |
|---|---|---|---|
| **Routing Information Base (RIB)** | Routing table | All known routes; selects best route per prefix | Control plane (software) |
| **Forwarding Information Base (FIB)** | Forwarding table, CEF table | The winning routes only; used for actual packet forwarding | Data plane (hardware/ASIC) |

The **control plane** (the router's CPU/software) maintains the RIB, runs routing protocols, and selects best routes using AD and metric. It then programmes the **data plane** (ASICs, line cards) with the FIB - a fast-lookup structure optimised for line-rate forwarding.

On a simple router, you may interact only with the RIB (what `show ip route` shows). On a high-speed carrier router, the FIB is what actually handles every packet - the RIB just keeps it updated.

```text
                      ┌─────────────────────────┐
     Routing protocols│     CONTROL PLANE        │
     ─────────────────│  (routing protocols,     │
     Static config    │   RIB, best-route        │
                      │   selection)             │
                      └────────────┬────────────┘
                                   │ programs
                      ┌────────────▼────────────┐
     Packets ────────→│     DATA PLANE           │──→ Forwarded out
                      │  (FIB, hardware ASIC,    │    correct interface
                      │   line-rate forwarding)  │
                      └─────────────────────────┘
```

??? supplementary "CEF, Express Forwarding, and MPLS Forwarding"
    Cisco's **Cisco Express Forwarding (CEF)** is the data-plane forwarding mechanism on IOS/IOS-XE/IOS-XR. CEF pre-computes the FIB (forwarding decisions) and an **Adjacency Table** (next-hop Layer 2 rewrite information - MAC addresses, outgoing interface encapsulation). When a packet arrives, the hardware looks up the FIB, finds the adjacency, rewrites the Layer 2 header, and sends - all without CPU involvement.

    In **MPLS** networks, a third table enters: the **LFIB (Label Forwarding Information Base)**. Instead of looking up an IP destination, the router swaps or pops the MPLS label - a much faster operation. IP routing still happens at the ingress PE router (to determine which label to push); every intermediate P router only reads the label.

### How Routers Learn Routes

Routes enter the routing table from four sources:

1. **Connected** - when an interface is configured with an IP address and comes up, the router automatically knows the network on that interface.

2. **Static** - an administrator manually enters a route. Simple, predictable, but doesn't adapt to topology changes.

3. **Dynamic routing protocols** - routers exchange routing information with each other automatically. Examples:
   - **OSPF** - link-state, fast convergence, hierarchical areas (covered in RT-004)
   - **BGP** - path-vector, used between autonomous systems and as the internet's routing protocol (RT-007)
   - **RIP** - distance-vector, simple but slow to converge; mainly historical (RT-003)
   - **IS-IS** - link-state, used heavily in carrier and data-centre networks (RT-006)

4. **Default route** - a route that matches everything not more specifically matched. Usually a static `0.0.0.0/0` pointing toward the ISP, or injected by BGP.

**Convergence** - when the network topology changes (a link fails, a new link comes up), routers must update their routing tables to reflect the new reality. The time it takes for all routers to agree on the new correct view is called **convergence time**. Fast convergence is critical - packets are dropped until convergence completes.

---
## Vendor Implementations

The routing table structure and forwarding behaviour are defined by IETF standards (RFC 1812 for IPv4 router requirements). All compliant implementations perform longest-prefix match and administrative distance selection. Syntax and default AD values differ by vendor.

!!! success "Standard - RFC 1812 (IPv4 Router Requirements), RFC 8200 (IPv6)"
    All compliant routers perform longest-prefix match forwarding, support a default route, and separate control-plane and data-plane functions. Administrative distance is a local policy value - not standardised - so values differ between vendors.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! View the routing table
    show ip route

    ! View a specific prefix
    show ip route 10.1.2.0

    ! View FIB (CEF table)
    show ip cef 10.1.2.0

    ! Verify which route wins for a destination
    show ip route 10.1.2.50
    ```
    On Cisco IOS-XE, `show ip route` displays the RIB. `show ip cef` shows the hardware forwarding table. AD values are fixed by default; custom AD can be set per static route with `ip route X.X.X.X Y.Y.Y.Y <next-hop> <AD>`.

    Full configuration reference: [Cisco IP Routing Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bps/configuration/xe-16/irb-xe-16-book.html)

=== "Juniper Junos"
    ```junos
    # View the routing table (inet.0 = IPv4 unicast)
    show route

    # View routes for a specific prefix
    show route 10.1.2.0/24

    # View forwarding table
    show route forwarding-table destination 10.1.2.0/24

    # Show route detail including preference
    show route 10.1.2.0/24 detail
    ```
    Junos calls AD "preference." Lower preference = more trusted (same direction as Cisco, different values). Junos maintains separate routing tables per address family: `inet.0` (IPv4 unicast), `inet6.0` (IPv6 unicast), `inet.3` (MPLS/tunnelled paths).

    Full configuration reference: [Junos Routing Policy and Firewall Filters](https://www.juniper.net/documentation/us/en/software/junos/routing-overview/)

=== "Nokia SR-OS"
    ```nokia-sros
    # View the routing table
    show router route-table

    # View a specific prefix
    show router route-table 10.1.2.0/24

    # View FIB
    show router fib 1 10.1.2.0/24

    # Detail with preference
    show router route-table 10.1.2.0/24 longer
    ```
    SR-OS uses "preference" with the same convention as Juniper (lower = more trusted). Routes are organised per routing instance (default is router instance 1; VPRNs are separate instances).

    Full configuration reference: [Nokia SR-OS Routing Protocols Guide](https://documentation.nokia.com/sr/)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # View the routing table
    /ip route print

    # View detail for a specific route
    /ip route print detail where dst-address=10.1.2.0/24

    # Check which route is active for a destination
    /ip route check 10.1.2.50
    ```
    RouterOS uses "distance" (equivalent to AD). Default static distance = 1; connected = 0. Dynamic protocol distances are configurable per instance. The active route (lowest distance, then lowest metric) is marked with `A` in the route print output.

    Full configuration reference: [MikroTik Routing Reference](https://help.mikrotik.com/docs/display/ROS/IP+Routing)

---
## Common Pitfalls

### Pitfall 1: Assuming the route is symmetric

A packet from A to B may take a completely different path than the reply from B to A. Each router makes an independent decision based on its own routing table. Asymmetric routing is normal and expected. Troubleshooting tools that assume symmetric paths (e.g., traceroute to a destination but not back) can mislead you into thinking the forward path has a problem when the return path is broken.

### Pitfall 2: Confusing the routing table with the forwarding table

`show ip route` shows what the router *knows*. It doesn't show what is actually installed in the hardware for fast forwarding. If CEF is disabled or a software exception exists, a route visible in the RIB may not be in the FIB. On Cisco, check `show ip cef` to confirm the forwarding entry exists.

### Pitfall 3: Missing the more-specific route

A default route of `0.0.0.0/0` silently attracts all traffic that has no better match. If a specific prefix is unreachable and no more-specific route exists, traffic silently goes to the default route gateway instead of being dropped. This causes traffic to travel to an unexpected destination with no obvious error at the source. Always check for unexpected matches with `show ip route <destination>`.

### Pitfall 4: Same prefix, different AD sources - wrong one installs

If OSPF and a static route both advertise the same prefix, the lower AD wins. If an engineer manually adds a static route (AD=1) for a destination that OSPF is supposed to manage (AD=110), the static route silently takes over - and if the static route points to a wrong next-hop, traffic blackholes with no OSPF alarm raised. Always verify which source is active with `show ip route <prefix>` and check the AD in the output.

### Pitfall 5: Recursive route resolution failure

When a next-hop is not directly connected, the router must resolve the next-hop recursively - it looks up the next-hop address in the routing table to find an exit interface. If that recursive lookup fails (the next-hop is unreachable), the route appears in the RIB but is not installed in the FIB. On Cisco, this shows as `%not in table` or the route is simply absent from `show ip cef`. Always confirm the next-hop is reachable, not just that the route is present.

---
## Practice Problems

1. A router has these routes in its table:
   ```text
   192.168.0.0/16  via 10.0.0.1
   192.168.1.0/24  via 10.0.0.2
   192.168.1.128/25 via 10.0.0.3
   0.0.0.0/0       via 10.0.0.4
   ```
   A packet arrives with destination `192.168.1.200`. Which route is used? Which route is used for destination `192.168.2.50`?

2. Two routing protocols both know about `10.5.0.0/24`. OSPF reports it via 10.0.0.1 with metric 20. RIP reports it via 10.0.0.2 with metric 5. Which route does a Cisco router install, and why? What would change if OSPF went down?

3. A Cisco router has a static route `ip route 10.20.0.0 255.255.0.0 10.0.0.1`. An OSPF neighbour also advertises `10.20.0.0/16` via the same 10.0.0.1 next-hop. Only the static route appears in `show ip route`. Is this correct behaviour? Explain.

4. You add a new subnet `172.16.5.0/24` to your network. Hosts on it can ping their default gateway (the router interface at `172.16.5.1`) but cannot reach anything outside. What is the most likely cause, and what do you check first?

5. Traceroute from PC-A to a server reaches hop 3 and then times out. A colleague runs traceroute from the server back toward PC-A and it completes successfully. What does this tell you about the problem?

??? "Answers"
    **1.** For `192.168.1.200`:
    - Matches `192.168.0.0/16` (16-bit match) ✓
    - Matches `192.168.1.0/24` (24-bit match) ✓
    - Matches `192.168.1.128/25` (25-bit match) ✓ - 192.168.1.200 is in 192.168.1.128–255
    - Winner: `192.168.1.128/25` via 10.0.0.3 - longest prefix wins

    For `192.168.2.50`:
    - Matches `192.168.0.0/16` ✓
    - Does not match /24 or /25 (wrong third octet)
    - Matches `0.0.0.0/0` ✓
    - Winner: `192.168.1.0/24`? No - `192.168.2.50` is NOT in `192.168.1.0/24`. It IS in `192.168.0.0/16`. Winner: `192.168.0.0/16` via 10.0.0.1.

    **2.** Cisco AD: OSPF = 110, RIP = 120. OSPF has lower AD → **OSPF route installs** (via 10.0.0.1). Metric is irrelevant when comparing different protocols - AD wins first. If OSPF goes down, the OSPF route is withdrawn; RIP's route (AD 120) is then the only candidate and installs.

    **3.** Yes, this is correct. Static AD = 1; OSPF AD = 110. Static wins. The OSPF route is known to the router but not installed because a lower-AD source (static) already has a route to the same prefix. This is expected and intentional - static routes override dynamic ones by default.

    **4.** Most likely cause: the router has no route back to `172.16.5.0/24` - or more precisely, the router's routing table doesn't have the route to forward return traffic back. Check: does the router have a connected route for `172.16.5.0/24`? Run `show ip route 172.16.5.0` on the router. If the interface is up and the IP is configured, the connected route should be there. If not, the interface may be administratively down or the IP misconfigured.

    **5.** The **forward path** (PC-A → server) fails at or after hop 3. The **return path** (server → PC-A) works. This is **asymmetric routing** with a forward-path failure: the router at hop 3 either drops the packet (routing black hole, ACL, or no route) or the response packets from hop 3 onward take a different path back. The server's response reaches PC-A via a working alternate path. Start by checking the router at hop 3 for a missing route to the server's destination, or a firewall policy that blocks the traffic.

---
## Lab

### Lab: Reading and Understanding the Routing Table

**Tools:** GNS3 or Cisco Packet Tracer (any Cisco IOS image)
**Estimated time:** 20 minutes
**Objective:** Configure a small three-router topology, observe what appears in each router's routing table, and verify longest-prefix match behaviour.

**Topology:**
```text
[PC-A]         [R1]              [R2]              [R3]         [Server]
10.1.1.10  ——→ Gi0/0   Gi0/1 ——→ Gi0/0   Gi0/1 ——→ Gi0/0  ——→ 10.3.3.10
           10.1.1.1  10.0.12.1 10.0.12.2  10.0.23.1 10.0.23.2
                                                    Gi0/1
                                                   10.3.3.1
```

**Steps:**

1. Configure IP addresses on all interfaces (refer to topology). Add a static route on each router toward the next segment. On R1, add a default route via R2.

    ```cisco-ios
    ! On R1:
    ip route 10.3.3.0 255.255.255.0 10.0.12.2
    ! Or use default route:
    ip route 0.0.0.0 0.0.0.0 10.0.12.2
    ```

2. Check the routing table on R1 - identify connected, local, and static routes:

    ```text
    R1# show ip route
    C    10.1.1.0/24 is directly connected, Gi0/0
    L    10.1.1.1/32 is directly connected, Gi0/0
    C    10.0.12.0/24 is directly connected, Gi0/1
    L    10.0.12.1/32 is directly connected, Gi0/1
    S*   0.0.0.0/0 [1/0] via 10.0.12.2
    ```

3. Test longest-prefix match: add a more specific static route on R1 and verify it wins:

    ```cisco-ios
    ip route 10.3.3.0 255.255.255.0 10.0.12.2
    ```

    ```text
    R1# show ip route 10.3.3.5
    Routing entry for 10.3.3.0/24
      Known via "static", distance 1, metric 0
      Routing Descriptor Blocks:
      * 10.0.12.2
    ```

4. Ping from PC-A to Server and verify connectivity. Then remove the specific static route and confirm traffic falls back to the default route:

    ```cisco-ios
    no ip route 10.3.3.0 255.255.255.0 10.0.12.2
    ```

??? supplementary "Lab extension: Observe route installation failure"
    On R1, add a static route with a next-hop that is not reachable (e.g., `ip route 10.4.0.0 255.255.0.0 10.99.0.1`). Check `show ip route 10.4.0.0`: the route appears. Now check `show ip cef 10.4.0.0`: the next-hop may show as "no adj" or fail recursive resolution. Ping `10.4.0.1` - the packet is dropped.

    This illustrates the difference between a route that exists in the RIB (routing table) and one that is actually forwarding-capable (installed in FIB/CEF).

---
## Summary & Key Takeaways

- A router forwards packets between networks using a **routing table** - a map of destinations and how to reach them
- Each router makes an **independent, per-hop** decision; no single device sees the full path
- The routing table contains **connected**, **local**, **static**, and **dynamic** routes
- **Longest-prefix match** always wins: the most specific (longest) matching prefix is used for forwarding
- The **default route** (`0.0.0.0/0` / `::/0`) is the route of last resort - it matches everything with no better match
- If no match exists and there is no default route, the packet is **dropped**
- **Administrative Distance** determines which route source wins when multiple sources know the same prefix - lower AD = more trusted
- Default Cisco ADs: connected=0, static=1, OSPF=110, RIP=120, iBGP=200
- The **RIB** (routing table) is maintained by the control plane; the **FIB** (forwarding table) is what the data plane actually uses to forward packets - both must agree for traffic to flow
- **Convergence** is the time it takes all routers to agree on the new correct routing state after a topology change - packets are dropped until convergence completes

---
## Where to Next

- **Continue:** [Static Routing](static-routing.md) (`RT-002`) - how to configure routes manually, default routes, and floating static backups
- **Continue:** [RIP & Distance-Vector Concepts](rip-distance-vector.md) (`RT-003`) - first dynamic routing protocol; introduces the distance-vector problem and why it matters
- **Related:** [IP Subnetting & VLSM](../ip/subnetting.md) (`IP-002`) - longest-prefix match depends on accurate prefix-length understanding
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) - this module is Stage 3, position 11 in the DNE path

---
## Standards & Certifications

**Relevant standards:**
- [RFC 1812 - Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812)
- [RFC 4271 - BGP-4](https://www.rfc-editor.org/rfc/rfc4271) (for administrative distance context)
- [RFC 8200 - IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200) (forwarding requirements)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 3.1 Interpret the components of a routing table; 3.2 Determine how a router makes a forwarding decision |
| JNCIA-Junos JN0-103 | Juniper | Routing fundamentals; routing table; preference values |
| Nokia NRS I | Nokia | IP routing basics; routing table; preference |

---
## References

- IETF - [RFC 1812: Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812)
- Odom, W. - *CCNA 200-301 Official Cert Guide, Volume 2*, Cisco Press, 2019 - Ch. 17–18 (IP routing)
- Doyle, J.; Carroll, J. - *Routing TCP/IP, Volume I*, 2nd ed., Cisco Press, 2005 - Ch. 3 (Static routing and routing table fundamentals)

---
## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Draft written by Claude Sonnet 4.6. RFC citations verified against IETF RFC index. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-002](static-routing.md) | Static Routing | Builds directly on routing table and LPM concepts | 2026-04-17 |
| [RT-003](rip-distance-vector.md) | RIP & Distance-Vector | Distance-vector builds on routing table fundamentals | 2026-04-17 |
| [RT-004](ospf-fundamentals.md) | OSPF Fundamentals | OSPF installs routes into the table described here | 2026-04-17 |
| [RT-007](bgp-fundamentals.md) | BGP Fundamentals | BGP uses AD and LPM described here | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [NW-001](../networking/osi-model.md) | The OSI Model | Layer 2 vs Layer 3; why MAC addresses do not cross routers | 2026-04-17 |
| [NW-002](../networking/network-topologies.md) | Network Topologies | Broadcast domains; routers as domain boundaries | 2026-04-17 |
| [IP-001](../ip/ip-addressing.md) | IP Addressing Fundamentals | CIDR notation; network and host portions | 2026-04-17 |
| [IP-002](../ip/subnetting.md) | IP Subnetting & VLSM | Prefix lengths; address block calculation | 2026-04-17 |
| [IP-003](../ip/ipv6-addressing.md) | IPv6 Addressing | IPv6 default route (::/0); IPv6 routing table | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | MikroTik RouterOS |
|---|---|---|---|---|---|
| View routing table | RFC 1812 | `show ip route` | `show route` | `show router route-table` | `/ip route print` |
| View forwarding table | RFC 1812 | `show ip cef` | `show route forwarding-table` | `show router fib 1` | `/ip route print` |
| Verify LPM for destination | RFC 1812 | `show ip route X.X.X.X` | `show route X.X.X.X` | `show router route-table X.X.X.X` | `/ip route check X.X.X.X` |
| Administrative Distance (name) | Local policy | Administrative Distance | Preference | Preference | Distance |
| Static route AD | Local policy | 1 | 5 | 5 | 1 |
| OSPF AD | Local policy | 110 | 10 | 10 | 110 |

### Maintenance Notes

- When RT-002 (Static Routing) is written, add a back-reference there to this module for routing table and LPM context
- When RT-004 (OSPF) is written, add a back-reference for AD values and route installation
- When RT-007 (BGP) is written, add a back-reference for eBGP/iBGP AD values

<!-- XREF-END -->
