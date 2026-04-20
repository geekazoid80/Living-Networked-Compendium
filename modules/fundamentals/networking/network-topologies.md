---
title: "Network Topologies"
module_id: "NW-002"
domain: "fundamentals/networking"
difficulty: "novice"
prerequisites: ["NW-001"]
estimated_time: 45
version: "1.1"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [topology, star, mesh, bus, ring, hybrid, duplex, mtu, mss, collision-domain, broadcast-domain, unicast, multicast, three-tier]
vendors: []
language: en
cert_alignment: "CCNA 200-301 - 1.2; CompTIA Network+ - 1.2; JNCIA-Junos - Networking Fundamentals"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Distinguish** simplex, half-duplex, and full-duplex, and explain why modern switches use full-duplex
2. **Explain** MTU and MSS, describe how an MTU mismatch causes failures, and identify where jumbo frames are used
3. **Define** collision domain and broadcast domain and explain how switches and routers create boundaries
4. **Identify** unicast, broadcast, and multicast traffic and describe how each is delivered
5. **Identify** the five topology shapes (bus, ring, star, mesh, hybrid) and state the trade-offs of each
6. **Describe** the three-tier enterprise model (access, distribution, core) and explain what each layer does

---
## Prerequisites

- [The OSI Model](osi-model.md) (`NW-001`) - specifically, understanding that topology decisions affect Layers 1 and 2

---
## The Problem

Two devices, one cable. You send a message. It arrives. Simple.

Before we add a third device and start talking about topology, two devices on a single cable already raise five fundamental questions. Answer them first - they explain *why* every topology decision matters.

### Step 1: Can you both talk at the same time?

You send a message. Alice starts replying before you finish. Both signals travel on the same wire simultaneously - they collide and cancel each other out. Neither message arrives.

The simplest fix: agree that only one person transmits at a time. Finish, signal "over," then the other replies. This is **half-duplex** - both directions are possible, but not simultaneously. Whoever transmits first wins; the other waits.

The limitation: while Alice is transmitting, your side of the wire sits idle. You're paying for capacity you can't use.

The better fix: use two separate wires - one in each direction. Now you can transmit and receive at the same time without interference. This is **full-duplex**. Both sides are always active.

A third case exists: a fire station loudspeaker. It only broadcasts outward. You hear it; you can't reply through it. That's **simplex** - one direction only, permanently.

| Mode | Directions | Simultaneous? | Real example |
|---|---|---|---|
| Simplex | One way only | N/A | Broadcast radio, TV, alarm siren |
| Half-duplex | Both ways | No - one at a time | Walkie-talkie, Wi-Fi, hub-based Ethernet |
| Full-duplex | Both ways | Yes | Telephone, switch-based Ethernet |

Modern switched Ethernet runs full-duplex on every port. Older hub-based Ethernet was half-duplex - and that difference shapes the entire history of why we switched from hubs to switches.

### Step 2: How much can you say in one go?

The wire between you and Alice can only carry a signal of limited length before it degrades. You agree: no message longer than 50 words per transmission. More to say? Break it into numbered pieces and send them in sequence.

That agreed maximum is the **MTU - Maximum Transmission Unit**. It is a property of the link itself, not of your content. Different media have different MTUs. A thin copper pair has a low MTU. A fibre optic cable has a high one.

But each message starts with overhead: "To: Alice, From: Bob, Piece 3 of 7." The actual content that fits within the 50-word limit - after subtracting that framing overhead - is the **MSS - Maximum Segment Size**. MSS is the useful payload per transmission.

A chatty sender on a low-MTU link burns most words on overhead and barely moves data. High MTU: fewer transmissions, more content per go, less overhead per useful byte.

The trap: your message passes through a relay who only handles 20-word limits, but you're sending 50-word chunks. That relay either fragments your chunks into smaller pieces (expensive, causes ordering problems downstream) or - if you've told it "do not fragment" - it drops the chunk entirely and sends back a tiny error message saying "send smaller." If a firewall blocks that error message, you get a **black hole**: the connection looks established, but large transfers silently die. This is one of the most frustrating problems in networking to diagnose.

### Step 3: What happens when more people join?

Add a third person to the wire. Now when anyone transmits, everyone on the wire receives it - including people it wasn't meant for. More critically: if two people transmit at the same time, their signals collide and both are destroyed.

The group of devices that share a medium and must take turns - where a simultaneous transmission causes a collision - is a **collision domain**.

On a hub (which simply repeats everything to all ports), every connected device is in the same collision domain. 20 devices on a hub = 20 devices competing for the same wire, taking turns, destroying each other's messages if they misjudge the timing.

On a switch, each port has its own dedicated wire pair. Device A and Device B can transmit simultaneously without ever interfering - each is its own collision domain. This is the fundamental reason switches replaced hubs.

```
Hub: one collision domain for all              Switch: one collision domain per port
                                               
 A ─┐                                           A ───[Port 1]┐
 B ─┤─ [Hub] ─── (all share)                    B ───[Port 2]│
 C ─┘                                           C ───[Port 3]├─ [Switch]
                                                D ───[Port 4]│
                                               (each port independent)
```

### Step 4: Some messages are meant for everyone

"Who has the key to the supply room?" You shout it. Every person in the room stops what they're doing and processes the question - even though only one person has the key, and 19 didn't need to be interrupted.

That's a **broadcast** - a message addressed to everyone. In networks, broadcasts are essential: "Who has IP address 192.168.1.1?" (ARP) or "I need an IP address, is there a server here?" (DHCP Discover) cannot be sent to a specific address because you don't know the address yet.

The group of devices that receives every broadcast - that all stop and process it - is a **broadcast domain**.

The problem scales badly. 10 devices: manageable. 500 devices on the same flat network: every ARP request, every DHCP discover, every routing protocol hello interrupts all 500. At some density, broadcast traffic alone saturates the network. This is a **broadcast storm**.

The solution: create boundaries. A **router** or **VLAN boundary** stops broadcasts dead. Traffic crosses the boundary only if it's specifically addressed to something on the other side. This is why we subnet, why we use VLANs, and why the three-tier network model exists - each layer creates and enforces broadcast domain boundaries.

```
Broadcast domain A          │  Broadcast domain B
                            │
 A ─┐                       │        E ─┐
 B ─┤─ [Switch] ─── [Router]│─── [Switch]├─ F
 C ─┘                       │        G ─┘
 D ─┘                       │
                            │
 Broadcast from A           │  Does NOT cross the router
 reaches B, C, D            │  E, F, G never see it
```

### Step 5: Not all messages go to everyone

Now that you understand broadcast domains, the three ways to address a message make sense:

**Unicast - tell one person.** "Alice, can you come here?" The switch looks up Alice's address and delivers the message to her port only. No one else is interrupted.

**Broadcast - tell everyone in the room.** "Who has the key?" Every device in the broadcast domain receives and processes it. Necessary but expensive. Used sparingly.

**Multicast - tell a specific interested group.** "Everyone on the project team, update in 5 minutes." Only devices that have explicitly joined the "project team" group receive it. Devices outside the group are not interrupted. Efficient for one-to-many delivery - video streams, routing protocol updates, stock tickers - where broadcast would be wasteful and unicast would require sending one copy per receiver.

| Delivery mode | Addressed to | Who receives it | Use case |
|---|---|---|---|
| Unicast | One specific device | That device only | Normal data transfer |
| Broadcast | Everyone in domain | All devices in broadcast domain | ARP, DHCP Discover |
| Multicast | A group | Subscribed devices only | Video stream, OSPF hellos (224.0.0.5) |
| Anycast | Nearest instance | One device (closest by routing) | DNS root servers, CDN |

### Step 6: Given all of that - how do we wire everything?

Now we have the vocabulary: duplex (who can transmit when), MTU/MSS (how much per transmission), collision domain (who shares a medium), broadcast domain (who receives broadcasts), and delivery modes (how traffic is addressed).

Topology is how we physically wire devices to manage all of these constraints. Add a third device - how do you connect it?

**Option 1 - Connect everyone to everyone directly:**

Three devices, three cables. Every device has a direct path to every other. Add a fourth: three more cables. The count grows with the square:

```
Cables = N × (N−1) / 2
```

10 devices = 45 cables. 100 devices = 4,950. Maximum resilience, maximum cost. This is **full mesh**.

**Option 2 - Connect everyone to one central device:**

100 devices → 100 cables. Adding one device costs one cable regardless of how many exist. Scales linearly. Trade-off: the central device failing takes everyone down. This is **star**.

**Option 3 - Run one cable and tap everyone in:**

No central point possible - devices are strung along a floor, a street, a mine shaft. One cable, everyone tapped in. All share the medium: half-duplex, one collision domain, one broadcast domain. This is **bus**.

**Option 4 - Connect each device to its two neighbours:**

Each device connects left and right, forming a loop. Traffic travels around the ring in one direction. One link breaks: traffic reverses on the surviving arc. One device fails: the ring breaks. This is **ring**.

**Real networks:** No production network uses a single topology end-to-end. They combine them by layer. This is **hybrid**.

### What You Just Built

Before choosing a topology, you must understand the constraints on any link. Topology is the physical shape of how devices are connected to manage those constraints. Every topology decision is a trade-off between cost, resilience, and broadcast/collision domain size.

| Concept | Technical term |
|---|---|
| One direction only | Simplex |
| Both directions, one at a time | Half-duplex |
| Both directions simultaneously | Full-duplex |
| Maximum frame size the link carries | MTU - Maximum Transmission Unit |
| Usable payload per frame (MTU minus header overhead) | MSS - Maximum Segment Size |
| Devices that compete for the same medium | Collision domain |
| Devices that receive all broadcasts | Broadcast domain |
| Message to one recipient | Unicast |
| Message to all in domain | Broadcast |
| Message to a subscribed group | Multicast |
| Everyone connected to everyone | Full mesh topology |
| Everyone connected to one central device | Star topology |
| All devices on one shared cable | Bus topology |
| Each device connected to two neighbours | Ring topology |
| Mix of topologies by layer | Hybrid topology |

---
## Core Content

### Duplex

**Simplex** - one direction only. The transmitter transmits; the receiver receives. No reverse path. Examples: broadcast radio, TV, an alarm siren.

**Half-duplex** - both directions possible, but not simultaneously. Devices must take turns. The protocol for managing turns is **CSMA/CD** (Carrier Sense Multiple Access with Collision Detection) for Ethernet on shared media: listen before transmitting, detect collisions, back off and retry with a random delay.

Half-duplex creates a shared collision domain. The more devices share the medium, the worse performance gets - not because of bandwidth, but because of wait time. 20 devices on a hub each get roughly 1/20 of the available transmission time in practice.

**Full-duplex** - both directions simultaneously on separate paths (separate wire pairs or wavelengths). No collision possible. No CSMA/CD needed. Each device transmits at the full link rate in both directions independently.

Modern 100 Mbps and faster Ethernet is always full-duplex when connected to a switch. The "100 Mbps" you see on a port means 100 Mbps transmit AND 100 Mbps receive - effectively 200 Mbps of total throughput on the link.

!!! warning "Duplex mismatch"
    A duplex mismatch - one side negotiating full-duplex, the other half-duplex - is one of the most common Ethernet performance problems. The half-duplex side uses CSMA/CD and waits; the full-duplex side transmits freely. The result: the half-duplex side sees constant collisions, performance drops to a fraction of nominal speed, and errors accumulate. The link works but badly. Fix: configure both sides explicitly to the same duplex setting, or ensure Auto-MDI/MDIX negotiation completes correctly on both ends.

---

### MTU and Frame Size

The **MTU (Maximum Transmission Unit)** is the largest payload an Ethernet frame can carry - by default, **1500 bytes**. This limit dates to the original 1980 Ethernet specification. The Ethernet frame itself (header + payload + FCS) is up to 1518 bytes, but the MTU refers to the payload portion only.

```
Standard Ethernet Frame:
┌────────────┬──────────┬──────┬──────────────────────┬─────┐
│ Dest MAC   │ Src MAC  │ Type │       Payload        │ FCS │
│   6 bytes  │  6 bytes │ 2 B  │    46–1500 bytes     │ 4 B │
└────────────┴──────────┴──────┴──────────────────────┴─────┘
                                         ↑
                                   MTU = 1500 bytes
```

**MSS (Maximum Segment Size)** is a TCP concept - the maximum data TCP puts in one segment. Derived from MTU:

```
MSS = MTU − IP header (20 bytes) − TCP header (20 bytes)
    = 1500 − 20 − 20 = 1460 bytes
```

TCP endpoints negotiate MSS during the three-way handshake. Each side advertises its MSS; the lower value wins. This prevents oversized segments at the endpoints - but doesn't protect against smaller MTUs in the middle of the path.

**MTU across different link types:**

| Link type | Typical MTU |
|---|---|
| Standard Ethernet LAN | 1500 bytes |
| Jumbo frames (data centre) | 9000 bytes |
| PPPoE (DSL, some broadband) | 1492 bytes |
| MPLS (label stack overhead) | Effective IP MTU reduced by label stack size |
| IPsec VPN tunnel | Lower than underlying link (ESP/AH header overhead) |

**Jumbo frames** - typically 9000-byte MTU - are used in data centres to reduce CPU overhead on high-throughput servers. Fewer, larger frames means fewer interrupts per megabyte of data. Critical requirement: every device on the path must be configured for jumbo frames. One switch with a standard 1500-byte MTU silently drops oversized frames.

**MTU mismatch** causes one of two symptoms:
- **Fragmentation** - the router breaks oversized packets into smaller pieces. Expensive (CPU overhead) and causes ordering delays.
- **Black hole** - if the IP packet has the **Don't Fragment (DF)** bit set, the router drops the packet and sends an ICMP "Fragmentation Needed" message back. If a firewall blocks that ICMP, the sender never learns to use smaller packets. TCP connections complete the handshake (small SYN/ACK packets fit), but data transfers silently fail because full-size data packets are dropped.

??? supplementary "Path MTU Discovery and MSS Clamping"
    **Path MTU Discovery (PMTUD, RFC 1191)** is the mechanism TCP uses to find the effective MTU across all links in the path. The sender sets the DF bit and sends full-size packets. Any router with a smaller MTU drops the packet and returns ICMP Type 3 (Fragmentation Needed). The sender reduces its packet size and retries.

    PMTUD works - when ICMP is not filtered. Overzealous firewalls that block all ICMP break PMTUD and cause black holes.

    **MSS clamping** (`ip tcp adjust-mss` on Cisco IOS) is the standard fix for VPN and PPPoE environments. The router rewrites the MSS field in TCP SYN packets to a safe value that accounts for tunnel overhead, preventing oversized segments from ever being sent. It is the correct solution when PMTUD cannot be relied upon.

---

### Collision Domain vs. Broadcast Domain

These two concepts define the two key "containers" that topology creates. Getting them confused is one of the most common misunderstandings in networking.

| | Collision Domain | Broadcast Domain |
|---|---|---|
| **Definition** | All devices that share a medium and must take turns | All devices that receive a Layer 2 broadcast |
| **Created by** | Shared medium (hub, coaxial bus, Wi-Fi radio) | Switch (contains broadcasts within a VLAN) |
| **Bounded by** | Switch (each port is its own collision domain) | Router or VLAN boundary |
| **Effect when too large** | Excessive collisions, poor throughput | Broadcast storms, high CPU on all devices |
| **Protocol for managing** | CSMA/CD (half-duplex) | IGMP snooping (limits multicast), VLANs, subnetting |

**A switch:**
- Breaks collision domains (each port = one collision domain, full-duplex)
- Does **not** break broadcast domains (a broadcast floods to all ports in the same VLAN)

**A router:**
- Does not reduce collision domains directly
- Breaks broadcast domains (does not forward Layer 2 broadcasts between interfaces)

**A VLAN:**
- Does not change the physical topology
- Logically segments a switch into multiple broadcast domains
- Requires a router or Layer 3 switch to route between VLANs

This is why the three-tier model uses switches at the access layer (collapse collision domains) and routers/Layer 3 switches at the distribution layer (collapse broadcast domains).

---

### Delivery Modes: Unicast, Broadcast, and Multicast

**Unicast** is the default. A frame or packet addressed to one specific MAC or IP address. The switch looks up the destination MAC in its forwarding table and delivers the frame to exactly that port. All other ports are silent.

**Broadcast** reaches every device in the broadcast domain. Layer 2 broadcast: destination MAC `FF:FF:FF:FF:FF:FF`. Layer 3 broadcast: destination IP `x.x.x.255` (directed) or `255.255.255.255` (limited). The switch forwards a broadcast out every port in the VLAN. Every device processes it.

Broadcasts are essential but expensive. Required uses:
- **ARP** - "Who has IP 192.168.1.1? Tell 192.168.1.50" - because you need the MAC before you can unicast
- **DHCP Discover** - "Is there a DHCP server? I need an address" - before you have an IP
- **Some routing protocol hellos** (e.g., RIPv1) - finding neighbours before adjacency is formed

**Multicast** delivers to a subscribed group only. Addressed to a Class D IP (224.0.0.0/4). Devices join a multicast group using **IGMP (Internet Group Management Protocol)**. A Layer 2 switch running **IGMP snooping** listens for IGMP join/leave messages and only forwards multicast frames to ports with subscribed receivers - not everywhere.

Without IGMP snooping, a switch treats multicast frames like broadcasts and floods them to all ports. With IGMP snooping, multicast is contained to interested ports only.

Multicast routing across subnets is a separate topic - covered in [Multicast Routing](../routing/multicast-routing.md) (`RT-011`).

**Anycast** is a Layer 3 concept: one IP address, multiple physical servers, traffic delivered to the nearest one by routing. Used in DNS (root servers), CDNs, and IPv6 router solicitation. Not a Layer 2 delivery mode.

---

### Topology Shapes

With the foundational concepts established, topology is the answer to: *how do we physically wire devices to manage collision domains, broadcast domains, and delivery modes at the required scale and resilience?*

#### Physical vs. Logical Topology

**Physical topology** - the actual cables and device connections.

**Logical topology** - how data flows, regardless of physical layout.

These often differ. Wi-Fi is physically a star (all devices to the AP) but logically a bus (all share the radio spectrum, half-duplex). Token Ring used a physical star (cables to a central MAU) but a logical ring (data passed device-to-device sequentially). Understand both when troubleshooting.

#### Bus Topology

```text
Device A ──┬── Device B ──┬── Device C ──┬── Device D
           │              │              │
        (tap)          (tap)          (tap)
              (shared coaxial cable, terminators at ends)
```

All devices share one cable. One collision domain. One broadcast domain. Half-duplex - CSMA/CD manages access. A break anywhere on the cable isolates everything downstream.

**Where it survives today:**
- Industrial control systems (Modbus, older RS-485 installations)
- CAN bus in automotive networks
- Logically: Wi-Fi (all clients share the same radio channel - conceptually a bus)
- Historically: 10BASE-2 coaxial Ethernet (obsolete in LAN)

#### Ring Topology

```text
    Device A
   /         \
Device D   Device B
   \         /
    Device C
```

Each device connects to exactly two neighbours. One collision domain per segment (in older Token Ring - tokens managed access). Resilient if the ring supports counter-rotation.

**Single ring:** one link or device failure can isolate downstream devices.

**Dual counter-rotating ring:** two rings, opposite directions. A break heals automatically - traffic wraps back on the surviving arc.

**Where it exists today:**
- Carrier metropolitan ring protection (ITU-T G.8032 / ERPS)
- SONET/SDH rings in telco core
- Historically: Token Ring (802.5), FDDI - now obsolete in LAN

??? supplementary "Token Ring and FDDI - Brief History"
    Token Ring (IEEE 802.5) was IBM's LAN technology of the 1980s–90s. A token - a special control frame - circulated the ring. Only the device holding the token could transmit, eliminating collisions entirely. FDDI extended the concept to 100 Mbps over dual fibre rings.

    Both were overtaken by switched Ethernet, which achieved collision-free operation (per port) without the complexity and single-token bottleneck. Ring protection, however, survived in carrier networks as a resilience mechanism.

#### Star Topology

```text
    Device A
        │
Device D ─ [Switch] ─ Device B
        │
    Device C
```

All devices connect to a central device (switch, hub, or access point). The central device forwards traffic. One cable per device - linear scaling. One collision domain per switch port (full-duplex). Broadcast domain = the VLAN configured on those ports.

**Trade-off:** central device failure isolates all connected devices. Mitigated by redundant central devices and uplinks.

**Modern reality:** switched star with full-duplex on every port is the universal LAN topology. Each port is its own collision domain. Broadcasts are bounded by VLAN.

??? supplementary "Hub vs. Switch - The Collision Domain Difference"
    A **hub** is a physical star but logical bus. Every frame received on any port is repeated to all other ports. One collision domain for all connected devices. Half-duplex. Every device sees every frame and decides whether to keep it.

    A **switch** learns which MAC addresses live on which ports and delivers frames only to the correct destination port (or floods only on first contact with an unknown MAC). Each port is its own collision domain. Full-duplex per port. Devices see only frames addressed to them (plus broadcasts).

    The performance difference is dramatic: a 24-port hub has 24 devices competing for one collision domain. A 24-port switch has 24 independent full-duplex paths operating simultaneously.

#### Mesh Topology

**Full mesh** - every device directly connected to every other.

```
A ──── B
│ ╲  ╱ │
│  ╳  │
│ ╱  ╲ │
C ──── D
```

Cables = N×(N−1)/2. 4 nodes = 6 cables. 10 nodes = 45. Maximum resilience - any single link or device failure is survived. Practical only for small N or where virtual paths (MPLS LSPs, VPNs) substitute for physical cables.

**Partial mesh** - selective direct connections between some pairs. Used everywhere in WAN design and data centre interconnect. Provides resilience on critical paths without the full cable count.

**Where mesh exists today:**
- WAN backbone topologies (core routers, BGP peering fabrics)
- Data centre interconnect (DCI) between sites
- Spine-leaf data centres (every leaf to every spine = partial mesh between layers)

#### Hybrid Topology and the Three-Tier Enterprise Model

No real network uses one topology end-to-end. The dominant campus model combines star at every layer with redundant uplinks creating partial mesh between layers.

**The three-tier model:**

The three layers form a hierarchy: access feeds into distribution, which feeds into core. Each tier serves a distinct purpose, and traffic only escalates upward when it needs to travel beyond the current layer's scope.

```
                        [Internet / WAN]
                               │
                   ┌───────────┴───────────┐
                [Core-A]             [Core-B]
               ╱       ╲             ╱       ╲
        [Dist-1]       [Dist-2] [Dist-3]    [Dist-4]
         ╱    ╲         ╱    ╲   ╱    ╲      ╱    ╲
      [Acc1][Acc2]  [Acc3][Acc4][Acc5][Acc6][Acc7][Acc8]
       |||   |||    |||   |||   |||   |||   |||   |||
      PCs   PCs    PCs   PCs   PCs   PCs   PCs   PCs

      ← ACCESS →   ←────── DISTRIBUTION ──────→   ← CORE →
         L2              L2/L3 boundary              L3
```

**Access layer - "the street"**

Where end devices connect: workstations, IP phones, printers, wireless APs. This layer operates primarily at Layer 2: Ethernet switching, MAC learning, and VLAN assignment. No routing happens here. A device in VLAN 10 wanting to reach VLAN 20 sends traffic upward to the distribution layer. Port-level features (PoE, authentication, security policies) and uplink redundancy are covered in [Switching Fundamentals](../switching/switching-fundamentals.md) (`SW-001`).

One access switch is one physical star. Multiple access switches feeding a distribution pair create a layer of stars aggregated upward.

**Distribution layer - "the main road"**

Aggregates multiple access switches. This is the **Layer 2 / Layer 3 boundary**: traffic between VLANs is routed here, crossing broadcast domain boundaries for the first time. Policy enforcement (ACLs, QoS marking, route summarisation) is applied at this layer rather than at the core, so the core can stay simple and fast.

**Core layer - "the motorway"**

The high-speed backbone. One job: move packets fast. Policy was applied at distribution; the core only forwards. It runs pure Layer 3 routing with no access lists or complex processing, using high-bandwidth links (10G, 40G, 100G) between core and distribution switches.

**Why this hierarchy?**

A flat network with 2,000 devices on one switch segment:
- Every ARP request, every DHCP discover, every routing hello interrupts all 2,000 devices - broadcast storm risk
- One switch failure takes down all 2,000
- No clear point to apply security policy

The three-tier model:
- Access layer: collapses collision domains (full-duplex per port), defines VLAN broadcast domain boundaries
- Distribution layer: collapses broadcast domains (routes between VLANs), enforces policy
- Core layer: fast, policy-free backbone

**Collapsed core (two-tier)**

Small sites - a single building with fewer than 10–15 access switches - often combine distribution and core into one pair of switches:

```
              [Internet / WAN]
                     │
         ┌───────────┴───────────┐
    [Collapsed-A]         [Collapsed-B]   ← Core + Distribution combined
      ╱    │    ╲             ╱    │    ╲
   [Acc] [Acc] [Acc]       [Acc] [Acc] [Acc]
    |||   |||   |||         |||   |||   |||
   PCs   PCs   PCs        PCs   PCs   PCs
```

Same principles, fewer devices. When the site grows, the combined layer splits back into two tiers.

**Spine-leaf (data centre)**

In data centres, a structured partial mesh emerged: every leaf switch connects to every spine switch. No leaf-to-leaf connections. No STP required. Every server-to-server path is exactly two hops: leaf → spine → leaf. Predictable, equal-cost, fast. Covered in [Data Centre Network Design](../datacentre/dc-network-design.md) (`DC-001`).

---
## Common Pitfalls

### Pitfall 1: Confusing physical and logical topology

Wi-Fi is physically a star (all devices connect to the AP) but logically a bus (all share the same radio channel, half-duplex). Troubleshooting RF interference means understanding the logical bus: collisions (in 802.11 terms: RTS/CTS, hidden node, co-channel interference) - not the physical star layout.

### Pitfall 2: Assuming star topology means resilience

A single switch is one device failure away from a total access outage. Resilience in a star requires redundant central devices - which means redundant uplinks to a second switch, which creates a partial mesh at the distribution layer. "We use a star topology" is not an answer to "how do you survive a switch failure."

### Pitfall 3: Treating a switch as eliminating broadcast domains

A switch breaks collision domains but does **not** break broadcast domains. A broadcast from Device A on VLAN 10 still reaches every port in VLAN 10. Only a router or Layer 3 switch (with a VLAN interface configured) stops a broadcast at a VLAN boundary. Forgetting this leads to oversized flat networks and broadcast storms.

### Pitfall 4: Duplex mismatch - the invisible performance killer

A link showing as "up/up" with terrible throughput and incrementing CRC errors is the classic duplex mismatch signature. One side is full-duplex (transmits freely), the other is half-duplex (using CSMA/CD, seeing the full-duplex side's continuous transmissions as collisions). The link functions but at a fraction of its rated speed. Always confirm duplex and speed settings match on both ends of a link.

### Pitfall 5: MTU mismatch - the black hole

A TCP session that completes the handshake but cannot transfer bulk data is the classic MTU black hole signature. The SYN, SYN-ACK, and ACK (small packets, ~60–80 bytes) fit through a bottleneck link. The first full-size data packet (1500 bytes) gets dropped silently because a firewall is blocking the ICMP "Fragmentation Needed" response. Diagnose with a ping of increasing sizes with the DF bit set: `ping -M do -s 1472 <destination>` (Linux) tests the 1500-byte MTU path.

---
## Practice Problems

1. A network has 48 workstations connected to a single hub. How many collision domains exist? How many broadcast domains? What happens if you replace the hub with a switch?

2. You are designing a network for a three-storey office building with 80 users per floor. Describe which topology you would use at each tier and why. How many broadcast domains should there be at minimum?

3. A junior engineer reports that a newly installed 1 Gbps link between two switches has terrible throughput (roughly 10–15 Mbps) but no link errors visible at Layer 1. What is the most likely cause, and how do you diagnose it?

4. A VPN tunnel between two sites is established (pings work, SSH connects), but SCP file transfers fail silently after the connection is established. What is the likely cause, and what are two ways to fix it?

5. You have 200 devices on a flat /24 network. A new security policy requires that Finance (30 hosts), Engineering (80 hosts), and Guest Wi-Fi (90 hosts) cannot communicate with each other. What network changes are needed?

??? supplementary "Answers"
    **1.** Hub: **1 collision domain** (all 48 devices compete for the same medium) and **1 broadcast domain** (all 48 receive every broadcast).
    Replace with a switch: **48 collision domains** (one per port, full-duplex) and still **1 broadcast domain** (unless VLANs are configured - a switch alone does not segment broadcast domains).

    **2.** Access layer: star (switch per floor, each workstation connected to its floor switch). Distribution layer: redundant pair of switches connecting all three floor switches; inter-VLAN routing here. Core: redundant pair connecting to WAN/internet. Minimum broadcast domains: at least 3 (one per floor / department) - ideally more, depending on security policy. Each VLAN = one broadcast domain.

    **3.** Most likely cause: **duplex mismatch**. One switch negotiated full-duplex; the other negotiated half-duplex (or was manually configured). Diagnose: `show interfaces` on both ends - look for incrementing CRC errors and late collisions on the half-duplex side. Fix: set both ends to the same duplex and speed explicitly, or ensure auto-negotiation is enabled on both (not forced on one side only).

    **4.** Most likely cause: **MTU black hole**. The tunnel adds header overhead (IPsec ESP = 50–60 bytes), reducing effective MTU. Full-size data packets hit the path with DF bit set, get dropped at the tunnel interface, but the ICMP "Fragmentation Needed" message is blocked by a firewall. The TCP handshake works (small packets); bulk data fails. Two fixes: (1) allow ICMP Type 3 Code 4 through the firewalls (enable PMTUD); (2) configure MSS clamping on the tunnel interface to reduce TCP segment size to a safe value (e.g., `ip tcp adjust-mss 1360` on Cisco).

    **5.** Create three VLANs (Finance, Engineering, Guest). Assign ports/SSIDs to the appropriate VLAN. Configure inter-VLAN routing on a Layer 3 switch or router at the distribution layer - then apply ACLs on the routed interfaces to block traffic between the three VLANs. Each VLAN is its own broadcast domain; the ACLs enforce the security policy at the point where the domains meet.

---
## Lab

### Lab: Collision Domains and Broadcast Domains in Packet Tracer

**Tools needed:** Cisco Packet Tracer
**Estimated time:** 25 minutes

**Objective:** Observe the difference between a hub (one collision domain, one broadcast domain) and a switch (per-port collision domains, configurable broadcast domains via VLANs) using simulation mode.

**Part 1 - Hub:**
1. Place a hub and connect four PCs (PC1–PC4) to it. Assign addresses `192.168.1.1–.4/24`.
2. In Packet Tracer simulation mode, send a ping from PC1 to PC3.
3. Observe: the frame is replicated to **all** ports - PC2 and PC4 receive it even though it's not for them. This is one collision domain and one broadcast domain in action.

**Part 2 - Switch:**
1. Replace the hub with a switch. Same four PCs, same addresses.
2. Repeat the ping. In simulation mode: the frame goes PC1 → Switch → PC3 only. PC2 and PC4 are silent.
3. Now send a broadcast ping (`ping 192.168.1.255` from PC1). Observe: the switch floods the broadcast to all ports - all four PCs receive it. The switch broke the collision domain but not the broadcast domain.

**Part 3 - VLANs (broadcast domain segmentation):**
1. Configure VLAN 10 on ports connected to PC1 and PC2. Configure VLAN 20 on ports connected to PC3 and PC4.
2. Send a broadcast from PC1. In simulation: it reaches PC2 (same VLAN) but not PC3 or PC4 (different VLAN). The switch now has two broadcast domains.
3. Attempt a ping from PC1 to PC3. It fails - no router to route between VLANs. This is expected.

**Stretch:** Add a router-on-a-stick (one trunk port to the switch, two sub-interfaces for VLAN 10 and 20). Now PC1 can reach PC3 via the router. The router is the broadcast domain boundary and the routing point between VLANs.

---
## Summary & Key Takeaways

Every topology is a tradeoff between cost, resilience, and scale. No single topology wins on all three, which is why every real network is a hybrid. The pattern that emerged as the industry standard is not arbitrary: star topologies at the access layer because they are cheap and easy to manage; partial mesh in the middle because critical paths need redundancy; a routed boundary between segments because routing is what keeps broadcast domains manageable as networks grow.

When something stops working, topology tells you where to look. A collision domain problem shows up as retransmissions and errors on a shared segment. A broadcast domain problem shows up as excessive background traffic or ARP flooding. A routing problem shows up as reachability failing at a subnet boundary. Knowing which layer owns each domain tells you immediately which device to inspect and which counter to check.

---
## Where to Next

- **Continue the sequence:** [Ethernet Standards & Cabling](ethernet-cabling.md) (`NW-003`) - the physical media that carries the signal
- **Apply to switching:** [Switching Fundamentals](../switching/switching-fundamentals.md) (`SW-001`) - how switches learn, forward, and create collision domain boundaries
- **Broadcast domain segmentation:** [VLANs & 802.1Q Trunking](../switching/vlans-trunking.md) (`SW-002`) - how VLANs create multiple broadcast domains on one switch
- **Topology at scale:** [Data Centre Network Design](../datacentre/dc-network-design.md) (`DC-001`) - spine-leaf as structured partial mesh

---
## Standards & Certifications

**Relevant standards:**
- IEEE 802.3 - Ethernet (star/bus physical and logical topology, duplex, frame size)
- IEEE 802.5 - Token Ring (ring topology, historical)
- ITU-T G.8032 - Ethernet Ring Protection Switching (carrier ring topology)
- IETF RFC 1191 - Path MTU Discovery
- IETF RFC 3021 - Using 31-Bit Prefixes on IPv4 Point-to-Point Links

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant section |
|---|---|---|
| CCNA 200-301 | Cisco | 1.2 - Network topology architectures |
| CompTIA Network+ | CompTIA | 1.2 - Topology concepts |
| JNCIA-Junos JN0-103 | Juniper | Networking fundamentals |

---
## References

- IEEE 802.3-2022 - Ethernet Standard
- IEEE 802.5 - Token Ring (historical)
- ITU-T G.8032/Y.1344 - Ethernet Ring Protection Switching
- IETF RFC 1191 - Path MTU Discovery
- Forouzan, Behrouz A. - *Data Communications and Networking*, 5th ed., McGraw-Hill, 2013 - Chapters 13–14
- Odom, Wendell - *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2020 - Chapters 2, 8

---
## Attribution & Licensing

**Author:** @geekazoid80
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Claude used for initial draft structure and prose. Technical claims verified against IEEE 802.3-2022, Forouzan's textbook, and Odom's CCNA Official Cert Guide.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| SW-001 | Switching Fundamentals | Prerequisite - star topology, collision domains, broadcast domains | 2026-04-17 |
| SW-002 | VLANs & 802.1Q Trunking | Prerequisite - broadcast domain segmentation via VLANs | 2026-04-17 |
| SW-003 | Spanning Tree Protocol | Prerequisite - redundant uplinks in hierarchical star create loops STP must manage | 2026-04-17 |
| DC-001 | Data Centre Network Design | Prerequisite - spine-leaf as structured partial mesh topology | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| NW-001 | The OSI Model | Prerequisite - topology decisions affect Layers 1 and 2 | 2026-04-17 |
| NW-003 | Ethernet Standards & Cabling | "Where to Next" forward reference | 2026-04-17 |
| SW-001 | Switching Fundamentals | "Where to Next" forward reference | 2026-04-17 |
| SW-002 | VLANs & 802.1Q Trunking | "Where to Next" forward reference | 2026-04-17 |
| DC-001 | Data Centre Network Design | "Where to Next" forward reference - spine-leaf | 2026-04-17 |
| RT-011 | Multicast Routing | Forward reference - multicast delivery across subnets | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Notes |
|---|---|---|
| Ethernet duplex and frame size | IEEE 802.3 | All vendors comply; duplex mismatch fix is vendor-agnostic |
| Path MTU Discovery | RFC 1191 | Supported on all IP stacks |
| Ethernet Ring Protection | ITU-T G.8032 | Carrier-grade ring resilience; Cisco/Juniper/Nokia all support |

### Maintenance Notes

- When SW-001 (Switching) is written, add a back-reference in that XREF section pointing here for collision domain and star topology context.
- When SW-002 (VLANs) is written, add a back-reference pointing here for broadcast domain context.
- When DC-001 (Data Centre) is written, update the "Modules That Reference This Module" table with spine-leaf context.
<!-- XREF-END -->
