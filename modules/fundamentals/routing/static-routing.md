---
title: "Static Routing"
module_id: "RT-002"
domain: "fundamentals/routing"
difficulty: "intermediate"
prerequisites: ["RT-001", "IP-001", "IP-002"]
estimated_time: 40
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["static-routing", "default-route", "floating-static", "next-hop", "exit-interface", "null0", "summarisation"]
cert_alignment: "CCNA 200-301 - 3.3 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "MikroTik RouterOS"]
language: "en"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Configure** static routes using next-hop address, exit interface, or both, on a router CLI
2. **Explain** the difference between configuring a next-hop address and an exit interface, and when each is appropriate
3. **Configure** a default route and explain how longest-prefix match causes it to be used only when no better match exists
4. **Configure** a floating static route and explain the AD mechanism that keeps it dormant while a routing protocol is healthy
5. **Identify** when static routing is appropriate and when dynamic routing is required

---
## Prerequisites

- [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) - routing table structure, longest-prefix match, administrative distance
- [IP Addressing Fundamentals](../ip/ip-addressing.md) (`IP-001`) - CIDR notation, subnet masks
- [IP Subnetting & VLSM](../ip/subnetting.md) (`IP-002`) - prefix lengths, address blocks

---
## The Problem

You have three routers. Router A connects to the office LAN. Router B connects to the data centre. Router C is in the middle, connecting the two. Each router only knows about its directly connected networks - it can't see beyond its own interfaces.

A PC on the office LAN sends a packet to a server in the data centre. The packet reaches Router A. Router A looks in its routing table. No entry for the data centre network. Packet dropped.

The networks are connected by cables. The routers just don't know it yet.

### Step 1: Tell the router where things are

You sit at Router A's CLI and type: "For packets going to the data centre network `10.2.0.0/24`, send them toward Router C at `10.0.12.2`." You enter this as a configuration command. The route appears immediately in the routing table. Now Router A knows.

You do the same on Router C: point toward Router B for the data centre. You do it on Router B: point back toward the office for the return path. The full path in both directions now exists.

This is **static routing** - a human manually programs the routing table. The router does exactly what it's told, nothing more.

### Step 2: The map is frozen

Three months later, the cable between Router A and Router C fails. The static route on Router A still says "send data centre packets toward Router C at `10.0.12.2`." Router A still sends packets that way - toward a dead interface. They're dropped silently. Nobody told Router A the path is gone.

Dynamic routing protocols detect failures and recalculate. Static routes don't. A static route is a fact you enter; it stays until you remove it, regardless of whether the path still works.

### Step 3: You can't know all routes - add a default

A new office is added. Then another. Then a partner company's network. Entering a static route for every possible destination is impractical. But most of the time, traffic that doesn't match a specific known destination should go toward the internet or the core network.

Instead of enumerating every destination, you add a single route that matches everything: destination `0.0.0.0/0`. This is the **default route**. It has the shortest possible prefix (zero bits), so it always loses to any more-specific match. It's the route of last resort - "send everything else here."

### Step 4: The backup that stays hidden

You have a primary path via a dynamic routing protocol and a backup link via a serial connection. You want the backup to activate only when the primary fails. If you add a static route for the backup with a normal AD of 1, it will win over OSPF (AD=110) and the backup becomes the primary - backwards.

You configure the static route with an artificially high AD - say, 200. Now OSPF's route (AD=110) wins. The static backup sits in the config, known but not installed. When OSPF fails and its route disappears, the only candidate is the static at AD=200. It installs. Traffic flows via the backup. When OSPF recovers, its route (AD=110) wins again and the static hides. This is a **floating static route**.

### What You Just Built

Static routing - a manually configured routing table entry that persists until removed, combined with default routes for catch-all forwarding and floating statics for protocol-independent backup paths.

| Scenario element | Technical term |
|---|---|
| Manually entered routing table entry | Static route |
| Route of last resort - matches everything | Default route (`0.0.0.0/0` or `::/0`) |
| Static route that stays hidden while a routing protocol works | Floating static route |
| Static route pointing to a dead interface that isn't removed | Static route with no failure detection |

---
## Core Content

### Static Route Syntax and Variants

A static route tells the router: "for packets to network X, use next-hop Y (or go out interface Z)."

Three equivalent forms exist:

| Form | What you specify | When to use |
|---|---|---|
| **Next-hop address** | IP address of the next router | Most common on point-to-multipoint or Ethernet links |
| **Exit interface** | Local interface name | Only correct for true point-to-point (serial/PPP) links |
| **Both** | Next-hop address + exit interface | Avoids recursive lookup; recommended on Ethernet where next-hop is on same subnet |

**Next-hop address (most common):**
```text
Destination: 10.2.0.0/24
Next-hop: the IP of the next router (10.0.12.2)
```

When the router receives a packet for `10.2.0.0/24`, it finds the next-hop `10.0.12.2` in the routing table, then resolves which interface leads to that next-hop (a recursive lookup). This is clean and readable, but adds one lookup step.

**Exit interface only (point-to-point links only):**
```text
Destination: 10.2.0.0/24
Exit interface: Serial0/0
```

On a point-to-point serial link, only one device is on the other end - no ambiguity. The router sends the packet out Serial0/0 and it arrives at the peer. On Ethernet, this form causes issues: the router sends ARP requests for every destination address, which is wrong and breaks.

**Both next-hop and interface (recommended on Ethernet):**
```text
Destination: 10.2.0.0/24
Next-hop: 10.0.12.2
Exit interface: GigabitEthernet0/1
```

No recursive lookup needed; the interface is explicit. The router knows exactly where to send it. This is the most precise form and avoids a potential issue where recursive lookup fails if the next-hop isn't directly resolvable.

### Default Route

The default route matches everything that has no more-specific match. In IPv4: `0.0.0.0/0`. In IPv6: `::/0`. Prefix length = 0 - the shortest possible - so it always loses to any real route under longest-prefix match.

```text
Routing table with default route:
  10.1.0.0/24  via 10.0.0.1   (specific — wins for 10.1.x.x)
  10.2.0.0/24  via 10.0.0.2   (specific — wins for 10.2.x.x)
  0.0.0.0/0    via 10.0.0.3   (default — wins for everything else)

Packet to 10.1.0.55:   → uses 10.1.0.0/24 (more specific)
Packet to 8.8.8.8:     → uses 0.0.0.0/0 (no specific match)
Packet to 10.2.0.100:  → uses 10.2.0.0/24 (more specific)
```

A default route is typically:
- Configured on edge routers pointing toward the ISP
- Redistributed by a routing protocol to propagate it through the organisation
- Or configured on every router pointing toward the "core" direction

Without a default route, any traffic to an unknown destination is silently dropped. With an incorrect default route, traffic disappears toward the wrong gateway with no error at the source - one of the most common silent failures in network troubleshooting.

### Floating Static Routes

A floating static route uses a manually inflated AD to stay dormant while a routing protocol runs, and only activates when the primary protocol-learned route disappears.

```text
Normal static route: AD = 1  → wins over OSPF (AD=110) — wrong for backup use
Floating static:     AD = 200 → loses to OSPF (AD=110) — stays hidden while OSPF works

When OSPF route is present:  OSPF (AD=110) wins → static (AD=200) is not installed
When OSPF route disappears:  Static (AD=200) is the only candidate → installs
When OSPF recovers:          OSPF (AD=110) wins again → static hides
```

The floating static must point to the backup path (different next-hop than OSPF's path). If it points to the same next-hop, it provides no actual redundancy.

??? supplementary "IP SLA + Floating Static: Tracked Routes"
    A standard floating static route activates when the routing protocol route disappears - but this only happens when the routing protocol neighbour relationship drops. If the link is up but the far-end device is broken (or an intermediate segment fails), OSPF may still be up while the actual data path is broken.

    Cisco IOS supports **IP SLA** (Service Level Agreement) tracking: the router probes a remote address (ICMP echo, TCP connect) on a schedule. If the probe fails, an associated static route is removed from the routing table. This lets you track end-to-end reachability, not just protocol neighbour state.

    ```cisco-ios
    ip sla 1
     icmp-echo 10.2.0.1 source-interface GigabitEthernet0/0
     frequency 10
    ip sla schedule 1 start-time now life forever

    track 1 ip sla 1 reachability

    ip route 10.2.0.0 255.255.0.0 10.0.0.2 track 1
    ```
    When the SLA probe fails, the tracked route is removed - even if the interface is physically up.

### Null0 - The Black Hole Route

`Null0` is a virtual interface that discards all traffic sent to it. Static routes pointing to `Null0` are used to:

1. **Prevent routing loops with summarisation:** If a router advertises a summary route `10.0.0.0/8` but only has specific /24 subnets internally, traffic for gaps in the summary (addresses not covered by any specific route) would fall to the default route and loop back. A `Null0` route for `10.0.0.0/8` catches these packets and drops them cleanly.

2. **Traffic filtering:** Drop specific destinations explicitly without an ACL.

```text
Routing table with Null0:
  10.0.0.0/8     Null0           ← summary; catches gaps
  10.0.1.0/24    via 10.99.0.1   ← specific; wins over Null0
  10.0.2.0/24    via 10.99.0.2   ← specific; wins over Null0
  0.0.0.0/0      via 10.99.0.254 ← default

Packet to 10.0.1.5:   → 10.0.1.0/24 wins (more specific) → forwarded
Packet to 10.0.99.1:  → 10.0.0.0/8 wins → Null0 → dropped
Packet to 8.8.8.8:    → 0.0.0.0/0 → forwarded to default gateway
```

### When to Use Static Routing

Static routing is appropriate when:

| Scenario | Why static works |
|---|---|
| Stub network with one exit point | Only one path exists; no routing protocol needed |
| Default route toward ISP | Simple: "everything else goes here" |
| Small network (< 5–10 routers) | Complexity is manageable; dynamic protocol overhead not worth it |
| Specific policy path control | You need traffic to take a specific path regardless of topology |
| Backup path (floating static) | Complement to a dynamic protocol; activates on failure |

Static routing is **not** appropriate when:
- The network has multiple paths between points (no automatic failover)
- The network has many prefixes (configuration burden scales badly)
- Topology changes frequently (every change requires manual updates on every affected router)
- You need sub-second failover (static routes don't detect failures)

---
## Vendor Implementations

Static routes are a local router configuration - no standard wire protocol. Syntax varies; behaviour (LPM, AD selection) is consistent across all RFC-compliant implementations.

!!! success "Standard - RFC 1812 (IPv4), RFC 8200 (IPv6)"
    Static routes are programmed locally and behave identically across vendors: lowest-AD route installs, LPM selects the forwarding entry. The `0.0.0.0/0` default route is universally supported.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Static route — next-hop only
    ip route 10.2.0.0 255.255.0.0 10.0.12.2

    ! Static route — exit interface + next-hop (preferred on Ethernet)
    ip route 10.2.0.0 255.255.0.0 GigabitEthernet0/1 10.0.12.2

    ! Default route
    ip route 0.0.0.0 0.0.0.0 203.0.113.1

    ! Floating static (AD=200, dormant while OSPF AD=110 is present)
    ip route 10.2.0.0 255.255.0.0 10.0.99.2 200

    ! Null0 black hole
    ip route 10.0.0.0 255.0.0.0 Null0

    ! IPv6 static route
    ipv6 route 2001:db8:2::/64 2001:db8:12::2

    ! Verify
    show ip route static
    show ip route 10.2.0.0
    ```
    The AD is the last numeric parameter on the `ip route` command. If omitted, default is 1. `Null0` is written as a single word (capital N, zero - not the letter O).

    Full configuration reference: [Cisco IOS Static Routing Configuration](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bps/configuration/xe-16/irb-xe-16-book/irb-static-routes.html)

=== "Juniper Junos"
    ```junos
    # Static route — next-hop address
    set routing-options static route 10.2.0.0/16 next-hop 10.0.12.2

    # Default route
    set routing-options static route 0.0.0.0/0 next-hop 203.0.113.1

    # Floating static — set preference higher than OSPF (preference 10)
    set routing-options static route 10.2.0.0/16 next-hop 10.0.99.2 preference 200

    # Discard (equivalent to Null0)
    set routing-options static route 10.0.0.0/8 discard

    # IPv6 static route
    set routing-options rib inet6.0 static route 2001:db8:2::/64 next-hop 2001:db8:12::2

    # Verify
    show route protocol static
    show route 10.2.0.0/16
    ```
    In Junos, `discard` drops the packet silently (no ICMP); `reject` drops and sends ICMP unreachable. Both serve the Null0/black-hole purpose; `discard` is used for loop prevention.

    Full configuration reference: [Juniper Static Routes](https://www.juniper.net/documentation/us/en/software/junos/static-routing/index.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # Static route (classic CLI)
    configure router static-route 10.2.0.0/16 next-hop 10.0.12.2

    # Default route
    configure router static-route 0.0.0.0/0 next-hop 203.0.113.1

    # Floating static — set preference
    configure router static-route 10.2.0.0/16 next-hop 10.0.99.2 preference 200

    # Black hole
    configure router static-route 10.0.0.0/8 black-hole

    # Verify
    show router static-route
    show router route-table 10.2.0.0/16
    ```
    SR-OS uses `black-hole` (equivalent to Null0/discard). Preference default for static routes is 5; set higher to float below a routing protocol.

    Full configuration reference: [Nokia SR-OS IP Routing Guide](https://documentation.nokia.com/sr/)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # Static route — next-hop
    /ip route add dst-address=10.2.0.0/16 gateway=10.0.12.2

    # Default route
    /ip route add dst-address=0.0.0.0/0 gateway=203.0.113.1

    # Floating static — set distance higher than routing protocol
    /ip route add dst-address=10.2.0.0/16 gateway=10.0.99.2 distance=200

    # Black hole
    /ip route add dst-address=10.0.0.0/8 type=blackhole

    # IPv6 static route
    /ipv6 route add dst-address=2001:db8:2::/64 gateway=2001:db8:12::2

    # Verify
    /ip route print
    /ip route print where dst-address=10.2.0.0/16
    ```
    RouterOS uses `distance` instead of AD (same concept). Default static distance = 1. Set `type=blackhole` for Null0 equivalent.

    Full configuration reference: [MikroTik Static Routing](https://help.mikrotik.com/docs/display/ROS/IP+Routing)

---
## Common Pitfalls

### Pitfall 1: Exit-interface static routes on Ethernet segments

Configuring `ip route 10.2.0.0 255.255.0.0 GigabitEthernet0/0` without a next-hop on an Ethernet interface causes the router to ARP for every destination address in `10.2.0.0/16` - thousands of ARP requests per second as traffic arrives. The route works but scales horribly. On Ethernet, always include the next-hop address.

### Pitfall 2: Static route present but traffic not forwarding

The static route is visible in `show ip route` but traffic is still dropped. Possible causes:
- The next-hop is not reachable (recursive lookup fails → route not installed in FIB; check `show ip cef`)
- A return path is missing (you configured the forward route but forgot the reverse)
- An ACL or policy is dropping the traffic after the routing decision

Always verify both directions and check the FIB, not just the RIB.

### Pitfall 3: Floating static with wrong AD value

Setting the floating static AD to a value lower than the routing protocol's AD means it always wins - defeating the purpose. AD must be **higher** than the routing protocol's AD to float below it. OSPF = 110 → floating static must be > 110 (e.g., 200). Confirm with `show ip route X.X.X.X` - the floating static should not appear while the protocol route is present.

### Pitfall 4: Default route attracts traffic that should be dropped

A default route catches everything with no specific match - including traffic to RFC 1918 addresses that should never leave the local network, and traffic to bogon/unallocated prefixes. A misconfigured default route can cause traffic to be forwarded toward the ISP when it should be dropped locally. Consider explicit null routes for RFC 1918 space that is not locally used, to prevent accidental leakage.

### Pitfall 5: Forgetting the return path

Network engineers frequently configure a static route in one direction and forget the return. The forward path works; ICMP or TCP replies are dropped at the far end. Symptom: one-way connectivity - pings are sent, but no reply arrives. Always ask: "does the router at the other end also have a route back to my source?"

---
## Practice Problems

1. A router has `ip route 0.0.0.0 0.0.0.0 10.0.0.1` configured. An engineer also adds `ip route 192.168.0.0 255.255.0.0 10.0.0.2`. A packet arrives with destination `192.168.1.50`. Which route is used?

2. You need a static route for `10.5.0.0/24` that stays dormant while OSPF is active (OSPF AD = 110) but activates if OSPF fails. What AD should the floating static use? Write the Cisco IOS command.

3. A router has two statics for `10.8.0.0/16`:
   - `ip route 10.8.0.0 255.255.0.0 10.0.0.1 1`
   - `ip route 10.8.0.0 255.255.0.0 10.0.0.2 1`
   What happens? How many routes appear in the routing table? How is traffic distributed?

4. An engineer configures `ip route 172.16.0.0 255.255.0.0 GigabitEthernet0/0` on a router with a multi-access Ethernet segment on Gi0/0. What problem will occur? What is the fix?

5. A router advertises the summary `10.0.0.0/8` via OSPF. Internally it has specific routes for `10.0.1.0/24`, `10.0.2.0/24`, and `10.0.3.0/24`. A packet arrives for `10.0.99.1`. What happens without a Null0 route? What happens with `ip route 10.0.0.0 255.0.0.0 Null0`?

??? "Answers"
    **1.** `192.168.1.50` matches both `192.168.0.0/16` (16-bit) and `0.0.0.0/0` (0-bit). Longest-prefix match: **`192.168.0.0/16` wins** → forwarded via `10.0.0.2`.

    **2.** AD must be greater than 110 (OSPF). A common choice is 200.
    `ip route 10.5.0.0 255.255.255.0 <backup-next-hop> 200`

    **3.** Both statics have the same prefix and the same AD (1). The router installs **both routes** as **ECMP (Equal-Cost Multipath)**. Both appear in the routing table. Traffic is load-balanced across both next-hops - typically per-destination (CEF per-flow) by default, not per-packet.

    **4.** Without a next-hop address, the router sends an ARP request for every unique destination in `172.16.0.0/16` that arrives. This generates massive ARP traffic and fills the ARP table with bogus entries. Fix: `ip route 172.16.0.0 255.255.0.0 GigabitEthernet0/0 <next-hop-IP>` - always include the next-hop on Ethernet.

    **5.** Without Null0: The packet for `10.0.99.1` matches `10.0.0.0/8` (no specific /24 exists). If there's a default route pointing upstream, the packet follows it - and may loop back if the upstream router also sends it back toward this router. A routing loop until TTL=0.
    With `ip route 10.0.0.0 255.0.0.0 Null0`: The Null0 route matches `10.0.0.0/8` as the longest prefix for `10.0.99.1` (more specific than the default). The packet is **silently dropped** - no loop. Specific routes (10.0.1.0/24, etc.) are more specific than Null0 and still win for valid subnets.

---
## Lab

### Lab: Static Routes, Default Route, and Floating Static

**Tools:** GNS3 or Cisco Packet Tracer
**Estimated time:** 20 minutes
**Objective:** Configure static routes between three routers, add a default route, then demonstrate floating static failover.

**Topology:**
```text
[R1]           [R2]          [R3]
Gi0/0   Gi0/1  Gi0/0  Gi0/1  Gi0/0
10.1.1.1  10.12.0.1  10.12.0.2  10.23.0.1  10.23.0.2
                                             Gi0/1
                                            10.3.3.1
                     (backup link)
[R1] ─────────────────────────────────────→ [R3]
  10.13.0.1                             10.13.0.2
```

**Steps:**

1. Configure IP addresses on all interfaces. Verify connected routes appear on each router.

2. Add static routes so R1 can reach `10.3.3.0/24` (via R2 → R3) as primary:

    ```cisco-ios
    ! On R1: primary path via R2
    ip route 10.3.3.0 255.255.255.0 10.12.0.2

    ! On R2: forward to R3
    ip route 10.3.3.0 255.255.255.0 10.23.0.2

    ! On R3: return path toward R1
    ip route 10.1.1.0 255.255.255.0 10.23.0.1
    ```

3. Add a floating static on R1 via the backup link (direct R1→R3):

    ```cisco-ios
    ! Floating static — AD=200, only activates if primary (AD=1) disappears
    ip route 10.3.3.0 255.255.255.0 10.13.0.2 200
    ```

4. Verify only the primary static appears (AD=1 wins over AD=200):

    ```text
    R1# show ip route 10.3.3.0
    Routing entry for 10.3.3.0/24
      Known via "static", distance 1, metric 0
      via 10.12.0.2
    ```

5. Simulate failure: shut down R1's Gi0/1 (the link to R2). Check that the floating static now installs:

    ```cisco-ios
    interface GigabitEthernet0/1
     shutdown
    ```

    ```text
    R1# show ip route 10.3.3.0
    Routing entry for 10.3.3.0/24
      Known via "static", distance 200, metric 0
      via 10.13.0.2      ← floating static took over
    ```

??? supplementary "Lab extension: Add a default route and Null0"
    Add a default route on R1: `ip route 0.0.0.0 0.0.0.0 10.12.0.2`. Ping an unknown address (e.g., `8.8.8.8`) from R1 - it should now be forwarded rather than dropped.

    Then add a Null0 route: `ip route 10.0.0.0 255.0.0.0 Null0`. Add a specific route inside that block (e.g., `ip route 10.99.0.0 255.255.255.0 10.12.0.2`). Ping `10.99.0.1` - uses specific route. Ping `10.55.0.1` - hits Null0, dropped. Ping `8.8.8.8` - uses default. This demonstrates all three behaviours together.

---
## Summary & Key Takeaways

- **Static routes** are manually configured routing table entries; they persist until removed and do not adapt to topology changes
- Three forms: **next-hop only** (most common), **exit interface only** (point-to-point only), **both** (most precise on Ethernet)
- On Ethernet segments, always include a **next-hop address** - exit-interface-only causes an ARP storm for every destination
- The **default route** (`0.0.0.0/0`) matches everything with no more-specific match; it is always the lowest-priority entry under LPM
- A missing return path causes one-way connectivity - always verify both directions
- **Floating static routes** use a high AD to stay dormant while a routing protocol works, then activate on failure
- AD must be **higher** than the primary protocol's AD for a floating static to work correctly (OSPF=110 → floating static ≥ 111)
- **Null0 routes** discard traffic matching a prefix - used to prevent routing loops under summary advertisements
- Static routing is appropriate for stub networks, simple topologies, and backup paths; it does not scale or self-heal

---
## Where to Next

- **Continue:** [RIP & Distance-Vector Concepts](rip-distance-vector.md) (`RT-003`) - the first dynamic routing protocol; automates what static routing does manually
- **Related:** [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) - routing table, LPM, and AD are all used here
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) - Stage 3, position 12 in the DNE path

---
## Standards & Certifications

**Relevant standards:**
- [RFC 1812 - Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812)
- [RFC 4861 - Neighbor Discovery for IPv6](https://www.rfc-editor.org/rfc/rfc4861) (default route via RA)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 3.3 - Configure and verify IPv4 and IPv6 static routing |
| JNCIA-Junos JN0-103 | Juniper | Static routing; preference; default route |
| Nokia NRS I | Nokia | Static route configuration; black hole routes |

---
## References

- IETF - [RFC 1812: Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812)
- Odom, W. - *CCNA 200-301 Official Cert Guide, Volume 2*, Cisco Press, 2019 - Ch. 17 (Static routing)
- Doyle, J.; Carroll, J. - *Routing TCP/IP, Volume I*, 2nd ed., Cisco Press, 2005 - Ch. 3 (Static routing)

---
## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Draft written by Claude Sonnet 4.6. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-003](rip-distance-vector.md) | RIP & Distance-Vector | Context for why dynamic routing was invented over static | 2026-04-17 |
| [RT-004](ospf-fundamentals.md) | OSPF Fundamentals | Floating static complement to dynamic protocols | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](routing-fundamentals.md) | Routing Fundamentals | Routing table, LPM, AD - prerequisites for static routing | 2026-04-17 |
| [IP-001](../ip/ip-addressing.md) | IP Addressing Fundamentals | CIDR notation; subnet masks | 2026-04-17 |
| [IP-002](../ip/subnetting.md) | IP Subnetting & VLSM | Prefix lengths; Null0 summarisation logic | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | MikroTik RouterOS |
|---|---|---|---|---|---|
| Static route (next-hop) | RFC 1812 | `ip route X.X.X.X M.M.M.M <nh>` | `set routing-options static route X/Y next-hop <nh>` | `static-route X/Y next-hop <nh>` | `/ip route add gateway=<nh>` |
| Default route | RFC 1812 | `ip route 0.0.0.0 0.0.0.0 <nh>` | `static route 0.0.0.0/0 next-hop <nh>` | `static-route 0.0.0.0/0 next-hop <nh>` | `dst-address=0.0.0.0/0` |
| Floating static | Local policy | Last param = AD value | `preference <value>` | `preference <value>` | `distance=<value>` |
| Null0 / discard | Local policy | `Null0` interface | `discard` | `black-hole` | `type=blackhole` |

### Maintenance Notes

- When RT-003 is written, add a back-reference there to this module as the "manual alternative" that dynamic protocols replace
- When OSPF module (RT-004) is written, verify floating static AD example matches OSPF AD discussion there

<!-- XREF-END -->
