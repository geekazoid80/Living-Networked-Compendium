---
title: "IP Subnetting & VLSM"
module_id: "IP-002"
domain: "fundamentals/ip"
difficulty: "intermediate"
prerequisites: ["NW-001", "IP-001"]
estimated_time: 60
version: "1.1"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [subnetting, vlsm, cidr, ip, network-design, addressing]
vendors: []
language: en
cert_alignment: "CCNA 200-301 — 1.6; CompTIA Network+ — 1.4; JNCIA-Junos — IP Addressing"
---

## The Analogy

Imagine a company moves into a large office building with 1000 rooms. You could give every department access to every room, but that's chaos — the finance team walking through the engineering lab, the sales team accidentally in the server room. Instead, you divide the building into wings: Finance Wing (floors 1–3), Engineering Wing (floors 4–7), and so on. Each wing has its own entrance and can't be accessed from another without going through reception (the router).

Subnetting is exactly this. You take a large block of IP addresses and carve it into smaller, isolated wings — **subnets** — each one its own broadcast domain, separated from others by a router.

VLSM (Variable Length Subnet Masking) takes it further: rather than giving every wing the same number of rooms, you allocate based on need. Finance gets 60 rooms, the server room gets 6. No waste.

| Building analogy | IP subnetting |
|---|---|
| The building (all 1000 rooms) | Your address block (e.g., 192.168.1.0/24) |
| A wing (floors 1–3) | A subnet |
| Wing boundary (fire door / stairwell) | Router interface |
| Room count per wing | Usable hosts per subnet |
| Wing numbering scheme | Subnet mask / prefix length |
| Reception (between wings) | Router (inter-subnet routing) |
| Assigning wings by size of department | VLSM — right-sizing each subnet |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** why subnetting is needed and what problem it solves
2. **Calculate** subnet addresses, broadcast addresses, and usable host ranges for any given network and mask
3. **Divide** a given network into a required number of subnets
4. **Apply** Variable Length Subnet Masking (VLSM) to design an efficient IP addressing scheme
5. **Verify** that two given IP addresses are on the same subnet

---

## Prerequisites

- [The OSI Model](../networking/osi-model.md) (`NW-001`) — Layer 3 context
- [IP Addressing Fundamentals](ip-addressing.md) (`IP-001`) — binary conversion, subnet masks, CIDR notation

You must be comfortable converting IP addresses between binary and dotted-decimal. If you can't do that yet, do `IP-001` first — this module builds directly on it.

---

## Why This Matters

Every network engineer subnets. Every day. Whether you're assigning addresses to a new office, designing a data centre, configuring VLANs, or troubleshooting a routing problem, you will need to know which subnet an address belongs to, how many hosts fit in a subnet, and how to divide address space efficiently.

Subnetting is also one of the most heavily tested topics on the CCNA exam. But more than that — getting subnetting wrong in production causes real problems: duplicate addresses, broken routing, wrong broadcast domains. It's one of those skills where "close enough" isn't good enough.

The maths isn't hard. There's a pattern to it, and once you see the pattern, subnetting becomes fast and mostly automatic.

---

## Core Content

### Why Subnet?

A subnet is a logical subdivision of an IP network. The original motivation was simple: one large flat network is inefficient and hard to manage.

**Problem 1: Broadcast traffic.** Every device on a network receives every broadcast packet. A /16 network with 65,534 hosts generates enormous broadcast traffic. Subnetting creates **broadcast domains** — smaller groups where broadcasts are contained.

**Problem 2: Security.** You want to separate departments. Finance shouldn't be on the same network segment as the guest Wi-Fi. Subnetting makes it possible to apply access control at network boundaries.

**Problem 3: Address efficiency.** If you have 30 hosts in one office and 6 in another, giving both a /24 (254 hosts each) wastes 218 addresses per subnet. VLSM lets you right-size each subnet.

**Problem 4: Routing.** Routers route by network prefix. Subnetting creates more specific routes, enabling routers to make smarter forwarding decisions and reducing routing table size through summarisation.

---

### The Subnetting Mechanic

Subnetting works by **borrowing bits** from the host portion of an IP address and reassigning them to the network portion. Each bit you borrow doubles the number of subnets but halves the number of hosts per subnet.

Start with: `192.168.1.0/24` — one network, 254 usable hosts.

Borrow 1 bit: `/25` — 2 subnets, 126 hosts each
Borrow 2 bits: `/26` — 4 subnets, 62 hosts each
Borrow 3 bits: `/27` — 8 subnets, 30 hosts each
Borrow 4 bits: `/28` — 16 subnets, 14 hosts each

The formula:
- **Number of subnets** = 2^(borrowed bits)
- **Hosts per subnet** = 2^(remaining host bits) − 2

---

### Finding Subnet Boundaries

The fastest way to subnet is to work out the **block size** — how big each subnet is.

Block size = 256 − the interesting octet of the subnet mask

**Example:** Mask is `255.255.255.192` (which is /26).

The "interesting octet" is the last one: 192. Block size = 256 − 192 = **64**.

That means subnets start at multiples of 64 in the last octet:
- `192.168.1.0` → hosts .1 to .62, broadcast .63
- `192.168.1.64` → hosts .65 to .126, broadcast .127
- `192.168.1.128` → hosts .129 to .190, broadcast .191
- `192.168.1.192` → hosts .193 to .254, broadcast .255

Four subnets, 62 usable hosts each. That's your /26.

#### The Block Size Method (Step by Step)

Given a network and mask, find:
1. **Block size** = 256 − (interesting octet of mask)
2. **Subnets** start at: 0, block size, 2×block size, 3×block size, ...
3. **Network address** = the start of the block
4. **Broadcast address** = (next subnet start) − 1
5. **First host** = network address + 1
6. **Last host** = broadcast address − 1

**Example:** What subnet is `10.4.77.200/20` in?

Step 1: /20 mask = `255.255.240.0`. Interesting octet is the **third** (240). Block size = 256 − 240 = **16**.

Step 2: Subnet boundaries in the third octet: 0, 16, 32, 48, 64, 80 → 77 falls between 64 and 80.

Step 3: Network address = `10.4.64.0`

Step 4: Broadcast address = `10.4.79.255` (next subnet is 10.4.80.0, so broadcast is .79.255)

Step 5: First host = `10.4.64.1`

Step 6: Last host = `10.4.79.254`

**Answer:** `10.4.77.200` is in subnet `10.4.64.0/20`, which goes from `10.4.64.1` to `10.4.79.254`.

---

### Determining if Two Hosts Are on the Same Subnet

Two hosts are on the same subnet if they share the same **network address** (IP address AND'd with subnet mask).

Shortcut: apply the block size method to both. If they fall in the same block, they're on the same subnet.

**Example:** Are `192.168.1.100` and `192.168.1.200` on the same subnet, if both use /25?

- Block size = 256 − 128 = 128
- Subnets: `192.168.1.0` (hosts .1–.126) and `192.168.1.128` (hosts .129–.254)
- `.100` → in `192.168.1.0/25`
- `.200` → in `192.168.1.128/25`
- **Different subnets.** These hosts cannot communicate directly — traffic between them must go through a router.

---

### Subnetting a Network: Design Approach

**Scenario:** You're given `192.168.10.0/24` and need 6 subnets, each with at least 20 hosts.

**Step 1:** Determine the required subnet size.

20 hosts needed → host bits needed = at least 5 (2^5 − 2 = 30 ≥ 20). So use 5 host bits.

A /24 with 5 host bits = 24 + (8−5) = /27. Block size = 256 − 224 = 32.

**Step 2:** How many subnets does /27 give?

From a /24, borrowing 3 bits → 2^3 = 8 subnets. We need 6. 8 ≥ 6 — this works.

**Step 3:** List the subnets:

| Subnet | Network Address | Broadcast | First Host | Last Host | Hosts |
|---|---|---|---|---|---|
| 1 | 192.168.10.0 | 192.168.10.31 | 192.168.10.1 | 192.168.10.30 | 30 |
| 2 | 192.168.10.32 | 192.168.10.63 | 192.168.10.33 | 192.168.10.62 | 30 |
| 3 | 192.168.10.64 | 192.168.10.95 | 192.168.10.65 | 192.168.10.94 | 30 |
| 4 | 192.168.10.96 | 192.168.10.127 | 192.168.10.97 | 192.168.10.126 | 30 |
| 5 | 192.168.10.128 | 192.168.10.159 | 192.168.10.129 | 192.168.10.158 | 30 |
| 6 | 192.168.10.160 | 192.168.10.191 | 192.168.10.161 | 192.168.10.190 | 30 |

Subnets 7 and 8 (192.168.10.192/27 and 192.168.10.224/27) exist but are unallocated — keep them for future use.

---

### Variable Length Subnet Masking (VLSM)

Fixed-size subnets waste addresses. If you have one department with 100 hosts and another with 10, giving both a /27 (30 hosts) fails for the first, and giving both a /25 (126 hosts) wastes 116 addresses in the second.

**VLSM** lets you use different-sized masks for different subnets within the same address space — giving each subnet exactly the size it needs.

**The rule:** Allocate largest subnets first. This prevents fragmentation.

**Scenario:** You have `172.16.0.0/24` and need:
- Site A: 60 hosts
- Site B: 28 hosts
- Site C: 12 hosts
- WAN link A–B: 2 hosts (point-to-point)
- WAN link A–C: 2 hosts

**Step 1:** Sort by size, largest first.

| Requirement | Hosts needed | Min host bits | Mask | Block size | Hosts provided |
|---|---|---|---|---|---|
| Site A | 60 | 6 | /26 | 64 | 62 |
| Site B | 28 | 5 | /27 | 32 | 30 |
| Site C | 12 | 4 | /28 | 16 | 14 |
| WAN A–B | 2 | 2 | /30 | 4 | 2 |
| WAN A–C | 2 | 2 | /30 | 4 | 2 |

**Step 2:** Assign subnets sequentially from the start of your address space.

| Subnet | Allocation | Network | Broadcast | Hosts |
|---|---|---|---|---|
| Site A | `172.16.0.0/26` | 172.16.0.0 | 172.16.0.63 | 62 |
| Site B | `172.16.0.64/27` | 172.16.0.64 | 172.16.0.95 | 30 |
| Site C | `172.16.0.96/28` | 172.16.0.96 | 172.16.0.111 | 14 |
| WAN A–B | `172.16.0.112/30` | 172.16.0.112 | 172.16.0.115 | 2 |
| WAN A–C | `172.16.0.116/30` | 172.16.0.116 | 172.16.0.119 | 2 |

Remaining address space: `172.16.0.120` through `172.16.0.255` — available for future use.

!!! tip "WAN links use /30"
    Point-to-point links between two routers only need 2 addresses. A /30 gives exactly 2 usable host addresses (2^2 − 2 = 2), with zero waste. Some engineers use /31 (RFC 3021) — no broadcast, both addresses usable — but /30 is more universally supported.

---

## Common Pitfalls

### Pitfall 1: Forgetting to subtract 2 for network and broadcast

The number of **usable** hosts is always 2^(host bits) − 2. New engineers regularly calculate the total hosts (2^n) without subtracting. A /28 gives 16 total addresses, not 14 usable — the network and broadcast addresses are not assignable.

### Pitfall 2: Not sorting by size in VLSM

If you assign small subnets first in VLSM, you may back yourself into a corner where you can't fit the large subnet without overlapping. Always allocate largest first.

### Pitfall 3: Overlapping subnets

Two subnets overlap if their address ranges intersect. This is catastrophic — routers will be confused about which subnet to use. Always double-check that your subnet boundaries don't cross.

**Check:** The broadcast address of one subnet must be less than the network address of the next. If `192.168.1.63` (broadcast of subnet 1) is followed by `192.168.1.64` (network of subnet 2), there's no overlap. If you see `.64` appear in two subnets, you have an error.

### Pitfall 4: The "interesting octet" is in the wrong place

For networks larger than /24 (like `10.0.0.0/8` or `172.16.0.0/16`), the interesting octet may be the second or third octet, not the fourth. Work out which octet is "partially masked" — that's your interesting octet. The fully-masked octets are fixed; the interesting octet is where the boundaries land.

---

## Practice Problems

1. How many subnets and usable hosts per subnet does `10.0.0.0/22` provide from a /8 starting point? Show the first three subnet ranges.

2. Given `172.16.32.0/20`, calculate: network address, broadcast address, first usable host, last usable host.

3. Design a VLSM addressing scheme for `192.168.5.0/24` with:
    - LAN A: 50 hosts
    - LAN B: 25 hosts
    - LAN C: 10 hosts
    - WAN link 1: 2 hosts
    - WAN link 2: 2 hosts

4. Are `10.1.4.200` and `10.1.5.10` on the same subnet if both use `255.255.254.0`?

5. A junior engineer tells you that `192.168.1.192/26` has 64 usable hosts. Are they correct? Explain.

??? supplementary "Answers"
    **1.** From `10.0.0.0/8`, a /22 borrows 22−8 = 14 bits. Subnets = 2^14 = 16,384. Host bits = 32−22 = 10. Usable hosts = 2^10 − 2 = 1,022.
    Block size in the third octet = 256 − 252 = 4.
    - `10.0.0.0/22` → hosts 10.0.0.1 to 10.0.3.254
    - `10.0.4.0/22` → hosts 10.0.4.1 to 10.0.7.254
    - `10.0.8.0/22` → hosts 10.0.8.1 to 10.0.11.254

    **2.** /20 mask = `255.255.240.0`. Interesting octet = third (240). Block size = 16.
    Boundaries in third octet: 0, 16, 32, 48. `32` is a boundary → network = `172.16.32.0`.
    Next boundary = 48 → broadcast = `172.16.47.255`.
    - Network: `172.16.32.0`
    - Broadcast: `172.16.47.255`
    - First host: `172.16.32.1`
    - Last host: `172.16.47.254`

    **3.** Sort largest first: LAN A (50→/26), LAN B (25→/27), LAN C (10→/28), WAN1 (2→/30), WAN2 (2→/30).
    - LAN A: `192.168.5.0/26` (hosts .1–.62, broadcast .63)
    - LAN B: `192.168.5.64/27` (hosts .65–.94, broadcast .95)
    - LAN C: `192.168.5.96/28` (hosts .97–.110, broadcast .111)
    - WAN1: `192.168.5.112/30` (hosts .113–.114, broadcast .115)
    - WAN2: `192.168.5.116/30` (hosts .117–.118, broadcast .119)

    **4.** `255.255.254.0` = /23. Interesting octet = third (254). Block size = 2.
    Boundaries in third octet: 0, 2, 4, 6...
    - `10.1.4.200` → third octet 4 → subnet `10.1.4.0/23` (covers .4.x and .5.x)
    - `10.1.5.10` → third octet 5 → same subnet `10.1.4.0/23`
    **Same subnet.** Both addresses fall within `10.1.4.0`–`10.1.5.255`.

    **5.** No, they're wrong. `/26` gives 2^6 = 64 **total** addresses, but 2 are reserved (network `.192` and broadcast `.255`). **62 usable hosts**, not 64.

---

## Lab

### Lab: Subnetting Design Exercise with Packet Tracer

**Tools needed:** Cisco Packet Tracer (free with Cisco Networking Academy registration)
**Estimated time:** 30 minutes

**Objective:** Design a subnetting scheme, configure it in Packet Tracer, and verify connectivity.

**Scenario:**
You are given the network `192.168.20.0/24`. Design a VLSM scheme for:
- Engineering LAN: 50 hosts
- Admin LAN: 20 hosts
- Point-to-point WAN: 2 hosts

**Step 1:** Work out your VLSM plan on paper before touching Packet Tracer.

**Step 2:** In Packet Tracer, build this topology:

```text
[PC1-PC50]---[Switch-Eng]---[Router-A Gi0/0]---[Router-B Gi0/0]---[Switch-Admin]---[PC51-PC70]
                                  Gi0/1
                                  |
                               (WAN link)
```

**Step 3:** Configure Router-A interfaces with the addresses from your design:

```cisco-ios
Router-A# configure terminal
Router-A(config)# interface GigabitEthernet0/0
Router-A(config-if)# ip address <engineering-first-host> <mask>
Router-A(config-if)# no shutdown
Router-A(config-if)# exit
Router-A(config)# interface GigabitEthernet0/1
Router-A(config-if)# ip address <WAN-first-host> <mask>
Router-A(config-if)# no shutdown
```

**Step 4:** Configure a PC in each subnet with an appropriate IP address and the router interface as its default gateway.

**Step 5:** Verify:
```cisco-ios
Router-A# show ip interface brief
Router-A# show ip route
```

**Step 6:** Test connectivity:
```
PC1> ping <PC-in-Admin-LAN>
```
This should fail until you add static routes or a routing protocol. That's expected — you'll fix it when you do the routing modules.

**Stretch goal:** Add a second WAN link and Admin LAN, subnetting the remainder of your /24 to fit.

---

## Summary & Key Takeaways

- Subnetting divides a network into smaller **broadcast domains**, improving security, efficiency, and routing
- **Block size** = 256 − (interesting octet of subnet mask) — the spacing between subnet boundaries
- For any IP and mask: find which block the host falls in → that's the subnet; subnet−1 = broadcast
- Number of subnets = 2^(borrowed bits); usable hosts = 2^(host bits) − 2
- **VLSM** uses different masks for different subnets — always allocate largest subnets first
- Point-to-point WAN links use /30 (2 usable addresses) or /31 (RFC 3021)
- Two hosts are on the same subnet if their network addresses (IP AND mask) are identical

---

<!-- XREF-START -->
## Where to Next

- **Continue the sequence:** [IPv6 Addressing](ipv6-addressing.md) (`IP-003`) — the long-term solution to IPv4 exhaustion
- **Apply what you've learned:** [Routing Fundamentals](../routing/routing-fundamentals.md) (`RT-001`) — how routers use subnet information to forward packets
- **Design context:** [Data Network Engineer Learning Path](../../applied/data-network-engineer/overview.md) — where subnetting sits in the full engineering curriculum

---

## References

- IETF — RFC 1918: Address Allocation for Private Internets
- IETF — RFC 4632: Classless Inter-domain Routing (CIDR)
- IETF — RFC 3021: Using 31-Bit Prefixes on IPv4 Point-to-Point Links
- Odom, Wendell — *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2020 — Chapters 13–14
- Lammle, Todd — *CompTIA Network+ Study Guide*, 5th ed., Sybex, 2021 — Chapter 3

---

## Attribution & Licensing

**Author:** @geekazoid80
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Claude used for initial draft structure and worked examples. All calculations verified manually. Technical content verified against Odom's CCNA Official Cert Guide and RFC 4632.
<!-- XREF-END -->
