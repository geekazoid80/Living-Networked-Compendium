---
title: "RIP & Distance-Vector Routing"
module_id: "RT-003"
domain: "fundamentals/routing"
difficulty: "intermediate"
prerequisites: ["RT-001", "RT-002"]
estimated_time: 35
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["rip", "distance-vector", "bellman-ford", "routing-loops", "split-horizon", "poison-reverse", "convergence", "hop-count"]
cert_alignment: "CCNA 200-301 - 3.4 (context) | JNCIA-Junos JN0-103"
vendors: ["Cisco IOS-XE", "MikroTik RouterOS"]
language: "en"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** how distance-vector routing works - what is shared, how often, and how routes propagate
2. **Describe** the counting-to-infinity problem and why it occurs in distance-vector protocols
3. **Explain** split horizon and poison reverse, and why they only partially solve the loop problem
4. **Describe** RIP's key characteristics - hop-count metric, 15-hop limit, update interval, and version differences
5. **Explain** why RIP is rarely used in modern networks and what limitations drove the development of link-state protocols

---
## Prerequisites

- [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) - routing table, metric, administrative distance, convergence
- [Static Routing](static-routing.md) (`RT-002`) - understanding of what problem dynamic routing replaces

---
## The Problem

Ten routers, each connected to a few others. Every router knows its directly connected networks. But Router A doesn't know about the networks behind Router J on the far side of the topology. You could type a static route on every router for every destination - but with 10 routers and 20 networks, that's 200 static routes to enter and maintain by hand. Add one new network, update 10 routers. A link fails, update again.

A more scalable routing mechanism is clearly needed.

### Step 1: Routers share what they know

What if each router told its neighbours what it knows? Router A knows about Network 1 (directly connected). It tells Router B: "I can reach Network 1." Router B now knows Network 1 is reachable via Router A. Router B tells Router C what it knows - including the route to Network 1. Router C tells Router D, and so on.

Within a few rounds of exchange, every router knows about every network in the topology. Nobody had to type anything. The routing tables self-populated.

This is the core of **distance-vector routing**: each router periodically sends its entire routing table to its directly connected neighbours. Neighbours update their own tables, then propagate to their neighbours. Knowledge spreads hop by hop.

### Step 2: How far is "far"?

But which path is better when there are multiple? Router C can reach Network 5 via Router B (2 hops) or via Router D (4 hops). The cost metric used in early distance-vector protocols was the simplest possible: **hop count** - how many routers does the packet pass through?

Fewer hops = shorter path = lower metric = preferred route.

Network 5 via Router B: 2 hops → metric = 2
Network 5 via Router D: 4 hops → metric = 4

Router B's route wins. The maximum hop count allowed is 15. A hop count of 16 means "unreachable" - the route is considered dead.

### Step 3: A link fails - and the problem begins

Router B, the only path to Network 5, goes down. Router C immediately loses its best route to Network 5. Router C's next advertisement will say "Network 5: unreachable" to Router D.

But wait - Router D heard about Network 5 *from* Router C. Router D still has it in its table (from the previous advertisement, saying 4 hops). Router D now tells Router C: "I can reach Network 5 - it's 5 hops via me." Router C thinks: "A new path! I'll use that." It updates its table to say Network 5 = 5 hops via Router D.

Next round: Router C tells Router D: "Network 5 = 6 hops via me." Router D updates: 7 hops. Next round: 8, 9, 10... the metric slowly counts up to 16 (infinity), then the route is declared unreachable. This process is called **counting to infinity**. Until it completes, both routers believe they have a valid path to a network that is actually unreachable. Packets loop between them until TTL expires.

### Step 4: Split horizon and poison reverse - partial fixes

Two mechanisms reduce (but don't eliminate) the counting-to-infinity problem:

**Split horizon:** "Never advertise a route back out the interface you learned it from." Router D learned about Network 5 from Router C. Under split horizon, Router D will not advertise Network 5 back to Router C. This breaks the immediate loop between two adjacent routers.

**Poison reverse:** Instead of silently not advertising, actively advertise the route with metric = 16 (infinity) back to the source. "I learned Network 5 from you - here it is with metric=16." This makes the poisoning explicit and faster.

These help for simple topologies. They don't fully solve the problem in larger, messier topologies with multiple paths.

### What You Just Built

RIP - the Routing Information Protocol. A distance-vector routing protocol that uses hop count as its metric, exchanges full routing tables periodically with neighbours, and uses split horizon and poison reverse to limit routing loops.

| Scenario element | Technical term |
|---|---|
| Routers sharing their routing tables with neighbours | Distance-vector routing |
| Number of router hops to a destination | Hop count (metric) |
| Metric value indicating "unreachable" | Infinity (16 in RIP) |
| Route count slowly increasing toward infinity after failure | Counting to infinity |
| Don't advertise a route back where you learned it | Split horizon |
| Advertise a dead route back with metric=∞ | Poison reverse |

---
## Core Content

### How Distance-Vector Routing Works

In a distance-vector protocol, each router maintains a **distance table** - essentially its routing table - containing the best known distance (metric) to every destination. Routers send their entire distance table to directly connected neighbours at regular intervals.

The process:

1. Each router starts knowing only its connected networks (distance = 0 or 1)
2. Every update interval (RIP default: 30 seconds), each router sends its table to all neighbours
3. When a router receives a neighbour's table, it processes each entry:
   - Destination reachable in N hops via this neighbour → add 1 → N+1 hops total
   - If N+1 is better than what the router currently knows → update the entry
4. Updated tables propagate outward, hop by hop, until stable (converged)

**Example - 3 routers in a line:**
```text
Round 0 (initial):
  R1 knows: N1=0 (connected)
  R2 knows: N2=0 (connected)
  R3 knows: N3=0 (connected)

Round 1 (after first exchange):
  R1 knows: N1=0, N2=1 (learned from R2)
  R2 knows: N1=1 (from R1), N2=0, N3=1 (from R3)
  R3 knows: N2=1 (from R2), N3=0

Round 2 (after second exchange):
  R1 knows: N1=0, N2=1, N3=2 (R2 told R1 that N3 is 1 hop from R2)
  R2 knows: N1=1, N2=0, N3=1
  R3 knows: N1=2, N2=1, N3=0

Converged — every router knows every network.
```

The convergence time scales with the network diameter (number of hops across the widest path) multiplied by the update interval. A 10-hop network with 30-second updates takes up to 300 seconds (5 minutes) to converge - very slow by modern standards.

### The Counting-to-Infinity Problem

When a route becomes unreachable, distance-vector protocols can create a routing loop before convergence completes.

```text
Topology:  R1 — R2 — R3
Networks:  N1 behind R1, N3 behind R3

R2 knows N3 = 1 hop (via R3)
R1 knows N3 = 2 hops (via R2)

R3 goes down. N3 is unreachable.

R2 removes N3 from its table — it knows N3 is gone.
Before R2 can send an update, R1 advertises: "N3 = 2 hops via me."
R2 thinks: "A new path! N3 = 3 hops via R1."
R2 tells R1: "N3 = 4 hops."
R1 updates: 5. R2: 6. R1: 7... → counting to infinity (16 = unreachable).

During this time, packets for N3:
  → Arrive at R2 → forwarded to R1 (R2 thinks R1 has a path)
  → R1 forwards to R2 (R1 thinks R2 has a path)
  → Loop until TTL=0
```

**Why this happens:** Each router only knows distances reported by neighbours, not the actual topology. They cannot detect that a reported path loops back through themselves.

### RIP Loop-Prevention Mechanisms

**Split Horizon:**
A router does not advertise a route back out the interface it learned the route from.

```text
R1 — R2 — R3

R2 learned N3 from R3 (via its Gi0/1 facing R3).
With split horizon: R2 does NOT advertise N3 back to R3 via Gi0/1.
R2 DOES advertise N3 to R1 via Gi0/0 (different interface — allowed).

Effect: R3 never hears from R2 that N3 is reachable via R2.
So when N3 fails, R3 cannot count-to-infinity with R2 — no loop between adjacent pair.
```

**Poison Reverse:**
Instead of silently omitting the route, advertise it back with metric = 16 (infinity) - explicitly poisoned.

```text
R2 learned N3 from R3 via Gi0/1.
With poison reverse: R2 DOES advertise N3 back to R3 via Gi0/1, but with metric=16.
R3 receives: "N3 = 16 hops via R2" = unreachable.
R3 ignores this (R3 already knows N3 directly = 0 hops).

When N3 fails:
R3 cannot use R2 as a backup (already marked 16) → no counting-to-infinity with R2.
```

**Triggered Updates:**
When a route changes (especially to unreachable), the router sends an immediate update rather than waiting for the next 30-second timer. This speeds up convergence.

**Holddown Timer:**
When a route is marked unreachable, the router ignores any new advertisement for that route for a holddown period (default 180 seconds). This prevents a stale advertisement from immediately restoring a broken route. The tradeoff: convergence is intentionally delayed to prevent instability.

??? supplementary "Why Split Horizon Doesn't Fix Everything"
    Split horizon prevents two-node loops (R1↔R2 looping). But in a triangle topology (R1-R2-R3 all connected to each other), it does not prevent a three-node counting-to-infinity loop.

    ```text
    R1 — R2
    |  ×  |
    R3 — —+

    R1 learns N4 (behind R3) from R3.
    R1 advertises N4 to R2 (different interface — split horizon allows it).
    R2 now has a path to N4 via R1.

    R3 goes down. N4 is unreachable.
    R3's direct route gone. R3 hears from R2: "N4 = 2 hops via me."
    R3 installs that. R2 hears from R3: "N4 = 3 hops." Counting begins.
    ```

    This is why distance-vector protocols with split horizon are fine for simple linear topologies but problematic in meshed networks. Link-state protocols (OSPF, IS-IS) solve this by sharing the full topology map rather than just distances.

### RIP Characteristics

| Characteristic | RIPv1 | RIPv2 | RIPng (IPv6) |
|---|---|---|---|
| Standard | RFC 1058 | RFC 2453 | RFC 2080 |
| Address family | IPv4 | IPv4 | IPv6 |
| Classful/Classless | Classful | Classless (CIDR) | Classless |
| Authentication | None | MD5 (plain text or MD5) | - (use IPsec) |
| Multicast updates | No (broadcast) | Yes (`224.0.0.9`) | Yes (`FF02::9`) |
| Metric | Hop count | Hop count | Hop count |
| Maximum hops | 15 (16 = infinity) | 15 (16 = infinity) | 15 (16 = infinity) |
| Update interval | 30 seconds | 30 seconds | 30 seconds |
| Invalid timer | 180 seconds | 180 seconds | 180 seconds |
| Holddown timer | 180 seconds | 180 seconds | 180 seconds |
| Flush timer | 240 seconds | 240 seconds | 240 seconds |

**Key limitations of hop count as a metric:**
- All hops are equal - a 1 Gbps link and a 9.6 kbps link both count as 1 hop
- RIP may choose a 10-hop path over 100 Mbps links rather than a 2-hop path over 56 kbps links
- No consideration of link bandwidth, delay, or congestion
- OSPF and IS-IS use cost (bandwidth-based) instead of hop count for this reason

### RIP's Place in Modern Networks

RIP is rarely deployed in new networks. It survives in some very small networks or embedded systems where simplicity outweighs performance concerns. Understanding it matters because:

1. It illustrates the core distance-vector algorithm - the same algorithm EIGRP and BGP are based on
2. The counting-to-infinity problem and its partial fixes motivate the design of link-state protocols (OSPF, IS-IS), which share the full topology rather than just distances
3. It appears in CCNA and professional certification exams as historical context
4. Legacy equipment still running RIPv1 or RIPv2 exists in older installations

OSPF (RT-004) is the standard for enterprise networks; IS-IS (RT-006) for carrier networks; BGP (RT-007) for inter-AS routing.

---
## Vendor Implementations

RIP is standardised in RFC 2453 (RIPv2) and RFC 2080 (RIPng). All implementations share the same algorithm and timers. Configuration is straightforward - RIP requires minimal parameters compared to link-state protocols.

!!! success "Standard - RFC 2453 (RIPv2), RFC 2080 (RIPng)"
    RIPv2 is fully standardised. Any compliant implementation interoperates with any other. Only configuration syntax differs.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Enable RIPv2 globally
    router rip
     version 2
     no auto-summary                    ! disable classful summarisation
     network 10.0.0.0                   ! enable RIP on interfaces in 10.0.0.0/8
     network 192.168.1.0                ! enable RIP on interfaces in 192.168.1.0/24
     passive-interface GigabitEthernet0/0  ! listen but don't send updates
     default-information originate      ! redistribute default route into RIP

    ! Verify
    show ip protocols
    show ip route rip
    debug ip rip
    ```
    `no auto-summary` is critical in IOS - without it, RIP summarises at classful boundaries and breaks VLSM. `network` statements use classful network addresses, not CIDR notation.

    Full configuration reference: [Cisco RIP Configuration](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_rip/configuration/xe-16/irip-xe-16-book.html)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # Enable RIP on interfaces
    /routing rip instance add name=default

    /routing rip interface-template add instance=default interfaces=ether1
    /routing rip interface-template add instance=default interfaces=ether2

    # Verify
    /routing rip neighbor print
    /ip route print where protocol=rip
    ```
    RouterOS uses instance-based RIP configuration. RIPv2 is the default in recent versions. Routes learned via RIP appear in the routing table with protocol=rip.

    Full configuration reference: [MikroTik RIP Reference](https://help.mikrotik.com/docs/display/ROS/RIP)

!!! warning "Proprietary - EIGRP (Cisco)"
    EIGRP (Enhanced Interior Gateway Routing Protocol) is a Cisco-originated distance-vector protocol that addresses most of RIP's limitations: it uses a composite metric (bandwidth + delay), supports VLSM, converges faster via the DUAL algorithm (no counting-to-infinity), and scales to larger networks. EIGRP was Cisco proprietary until RFC 7868 documented it in 2016, but interoperability with non-Cisco implementations remains limited in practice. EIGRP is covered in RT-010.

---
## Common Pitfalls

### Pitfall 1: Running RIPv1 by default on Cisco (no auto-summary)

Cisco IOS defaults to RIPv1 unless `version 2` is specified. RIPv1 sends broadcasts instead of multicasts, cannot carry subnet mask information (classful only), and does not support authentication. Always explicitly configure `version 2` and `no auto-summary`.

### Pitfall 2: Counting-to-infinity causes a long blackout after failure

When a link or router fails, RIP with default timers can take several minutes to converge, during which traffic is blackholed or loops. In a network where 3–5 minutes of outage is acceptable, this is tolerable. In any production network with SLAs, this is unacceptable. OSPF and IS-IS converge in seconds.

### Pitfall 3: 15-hop limit silently drops routes

A network larger than 15 hops in diameter simply cannot use RIP - routes beyond 15 hops are advertised with metric=16 (unreachable). There is no warning; packets to those destinations are silently dropped. Always verify that the maximum hop count in your network is below 15 before deploying RIP.

### Pitfall 4: All hops treated equally

RIP chooses the path with the fewest hops regardless of link speed. A 5-hop path over 10 Gbps links loses to a 3-hop path over 1 Mbps links. This is counterintuitive and causes performance problems in real networks. Use OSPF (cost = bandwidth-based) or IS-IS for any network where bandwidth varies significantly between links.

---
## Practice Problems

1. R1, R2, R3, and R4 are in a line (R1-R2-R3-R4). Network N5 is directly connected to R4. After RIP converges, what hop count does R1 report for N5? If R4 goes down, how many update cycles does it take for R1 to declare N5 unreachable (counting-to-infinity)?

2. In a simple R1-R2 topology, R2 learns network N1 from R1. With split horizon enabled: does R2 advertise N1 back to R1? What about with poison reverse enabled?

3. A network engineer deploys RIP on a new campus with 12 routers in series. After deployment, routes from the first router are visible on the last router. Six months later, three more routers are added in series. What problem do you anticipate?

4. Why does RIP use a 30-second update interval? What is the tradeoff of making the interval shorter? What would the consequence be of making it longer?

5. You have a 3-hop path over 10 Gbps links and a 2-hop path over a 128 kbps satellite link. Which does RIP choose? Is this the right choice? What protocol would make a better decision?

??? "Answers"
    **1.** N5 = 1 hop from R4. R3 learns it as 2 hops. R2 = 3 hops. R1 = **4 hops**.
    If R4 goes down: R3 loses N5. R3 hears from R2 (3 hops) → updates to 4. R2 hears from R3 (4) → 5. Then 6, 7... to 16. With 30-second updates, each round is 30 seconds. From 4 to 16 = 12 increments × 30 seconds = **approximately 6 minutes** (plus holddown timers - up to 3–5 minutes more in practice).

    **2.** Split horizon: **R2 does NOT advertise N1 back to R1** - it learned N1 from the interface facing R1. With poison reverse: **R2 DOES advertise N1 back to R1, but with metric=16** (explicitly unreachable). Poison reverse is the active form of split horizon.

    **3.** With 15 total routers in series, the maximum hop count from end to end = 14 hops. This is within the 15-hop limit. However, if any future expansion adds more routers in series, the 16th hop becomes unreachable. Also, with 15 update cycles needed for full convergence (one per hop at 30s each), convergence time approaches **7.5 minutes** - already problematic.

    **4.** 30 seconds balances convergence speed against bandwidth/CPU overhead. Shorter intervals: faster convergence, but more bandwidth consumed and CPU load on routers from processing updates. Longer intervals: less overhead, but slower convergence - routes take longer to propagate or be declared dead. In modern networks, 30 seconds is too slow; OSPF reacts in seconds using event-triggered updates rather than periodic full-table dumps.

    **5.** RIP chooses the **2-hop satellite path** - fewer hops. This is the wrong choice; the 128 kbps link is a massive bottleneck. OSPF uses a cost metric based on reference bandwidth ÷ link bandwidth - the 10 Gbps path would have a much lower cost (better) and win. IS-IS has a configurable metric system that can also account for bandwidth.

---
## Summary & Key Takeaways

- **Distance-vector routing** works by sharing routing tables (distances to all known destinations) with directly connected neighbours at regular intervals
- Knowledge spreads **hop by hop** - each router adds 1 to the metric as it forwards the information
- **RIP** uses **hop count** as its metric; max hop count = 15; hop count = 16 means unreachable
- When a link fails, distance-vector routers can enter **counting-to-infinity**: metrics increment toward 16 while packets loop between routers
- **Split horizon**: don't advertise a route back the interface it arrived from - breaks two-node loops
- **Poison reverse**: advertise a dead route back with metric=16 (explicit, faster than silent omission)
- **Triggered updates** send route changes immediately rather than waiting for the next 30-second timer
- **Holddown timers** delay reinstalling a failed route - prevents false convergence, but slows recovery
- RIP converges in **minutes**; modern link-state protocols (OSPF, IS-IS) converge in **seconds**
- RIP treats all hops equally regardless of bandwidth - cannot distinguish a 10 Gbps link from a 56 kbps link
- RIP is rarely used in new deployments; its value today is **conceptual** - understanding it explains why OSPF and IS-IS were designed the way they were

---
## Where to Next

- **Continue:** [OSPF Fundamentals](ospf-fundamentals.md) (`RT-004`) - link-state routing that solves the problems RIP introduced; shares full topology maps rather than just distances
- **Related:** [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) - routing table and metric concepts underlying RIP
- **Deep dive:** EIGRP (`RT-010`) - distance-vector with DUAL algorithm; resolves counting-to-infinity; Cisco-originated
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) - Stage 3, position 13 in the DNE path

---
## Standards & Certifications

**Relevant standards:**
- [RFC 1058 - Routing Information Protocol (RIPv1)](https://www.rfc-editor.org/rfc/rfc1058)
- [RFC 2453 - RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [RFC 2080 - RIPng for IPv6](https://www.rfc-editor.org/rfc/rfc2080)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | Historical context; distance-vector concepts |
| JNCIA-Junos JN0-103 | Juniper | Distance-vector routing principles |

---
## References

- IETF - [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- Bellman, R. - *Dynamic Programming*, Princeton University Press, 1957 - mathematical basis of the Bellman-Ford algorithm underlying distance-vector routing
- Odom, W. - *CCNA 200-301 Official Cert Guide, Volume 2*, Cisco Press, 2019 - Ch. 19 (RIP and distance-vector)
- Doyle, J.; Carroll, J. - *Routing TCP/IP, Volume I*, 2nd ed., Cisco Press, 2005 - Ch. 4 (RIP)

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
| [RT-004](ospf-fundamentals.md) | OSPF Fundamentals | OSPF motivation - solving problems introduced by distance-vector | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](routing-fundamentals.md) | Routing Fundamentals | Routing table, metric, convergence | 2026-04-17 |
| [RT-002](static-routing.md) | Static Routing | Static routing is what distance-vector replaces for dynamic learning | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | MikroTik RouterOS |
|---|---|---|---|
| Enable RIPv2 | RFC 2453 | `router rip; version 2` | `/routing rip instance add` |
| Advertise network | RFC 2453 | `network X.X.X.X` | `/routing rip interface-template add interfaces=X` |
| Disable classful summarisation | RFC 2453 | `no auto-summary` | Not applicable (RouterOS is classless by default) |
| View RIP routes | RFC 2453 | `show ip route rip` | `/ip route print where protocol=rip` |

### Maintenance Notes

- When RT-004 (OSPF Fundamentals) is written, add a forward reference here to that module as "how link-state solves counting-to-infinity"
- RT-010 (EIGRP) will describe the DUAL algorithm - add a reference here when written

<!-- XREF-END -->
