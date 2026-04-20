---
module_id: CT-005
title: "SRv6 - Segment Routing over IPv6"
description: "How SRv6 uses IPv6 addresses as Segment Identifiers, embeds the segment list in the IPv6 Segment Routing Header, and eliminates the MPLS label plane entirely."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 50
prerequisites:
  - CT-004
  - IP-003
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - srv6
  - segment-routing
  - ipv6
  - srh
  - carrier
  - traffic-engineering
created: 2026-04-19
updated: 2026-04-19
---

# CT-005 - SRv6 - Segment Routing over IPv6
## Learning Objectives

After completing this module you will be able to:

1. Explain SRv6 SID structure - locator, function, and argument.
2. Describe the Segment Routing Header (SRH) and how the active segment is processed.
3. Explain common SRv6 endpoint behaviours (End, End.X, End.DT4, End.DX2).
4. Describe how SRv6 replaces MPLS-based L3VPN and pseudowire.
5. Explain the trade-offs between SRv6 and SR-MPLS.
6. Describe the role of the IGP in SRv6 SID advertisement.

---
## Prerequisites

- CT-004 - Segment Routing SR-MPLS (SR concepts - segments, SIDs, segment lists)
- IP-003 - IPv6 Addressing (IPv6 address structure, routing)

---
## The Problem

SR-MPLS (CT-004) requires an MPLS forwarding plane - all routers must understand MPLS label operations. Optical transport equipment, host servers, and some access technologies do not support MPLS. Every new node added to the network must support MPLS before it can participate in SR paths. Integrating SR services with non-MPLS-capable endpoints (servers, VMs, containers) requires extra encapsulation layers.

What if you could do everything MPLS does - traffic engineering, VPN services, service chaining - using only IPv6? Every modern router, server, and VM already speaks IPv6.

### Step 1: Use IPv6 addresses as Segment IDs

In SR-MPLS, a Segment ID is a 20-bit MPLS label. In SRv6, a **SID is a 128-bit IPv6 address** - specifically a structured IPv6 address that encodes both a node/function identifier and an argument. The address space is large enough that each node can have millions of SIDs. No new label space needed - IPv6 addresses *are* the SIDs.

### Step 2: Carry the segment list in the IPv6 header

SR-MPLS encodes the segment list as a stack of MPLS labels. SRv6 encodes the segment list in an **IPv6 extension header: the Segment Routing Header (SRH)**. The SRH contains an ordered list of IPv6 SIDs. The current segment (active destination) is also the IPv6 destination address - standard IPv6 forwarding delivers the packet to the node identified by the current SID.

### Step 3: Functions encoded in SIDs

An SRv6 SID is not just a routing address - it encodes a **function** (behaviour). When a packet arrives at a node whose SRv6 SID matches an interface address, the node executes the behaviour specified by the SID: forward to next segment, decapsulate and deliver to a VRF, apply a service policy, or hand off to a VNF. Functions are local to the node; they can be anything the node's software supports - without requiring a new protocol.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| IPv6 address used as a Segment ID | SRv6 SID |
| IPv6 extension header carrying the segment list | Segment Routing Header (SRH) |
| Current active SID copied to IPv6 destination | Active segment |
| Function executed when SID is matched | SRv6 Endpoint Behaviour |
| SID that forwards to next segment | End (Node SID) |
| SID that decapsulates and routes in a VRF | End.DT4 / End.DT6 |
| SID for cross-connect (L2 pseudowire) | End.DX2 |
| First 64 bits of an SRv6 SID (node part) | Locator |
| Last 64 bits of an SRv6 SID (function + args) | Function + Argument |

---
## Core Content

### SRv6 SID Structure

```
|<---------- 128 bits -------------------->|
|<-- Locator (N bits) -->|<-- Func -->|<-Arg->|
```

- **Locator:** Routable IPv6 prefix identifying the node (or a function block). Advertised in the IGP (IS-IS/OSPF) - all routers know how to reach it. Typically /32 to /48.
- **Function:** Identifies which behaviour to execute when the packet arrives. Example: 1 = End (forward to next segment), 2 = End.DT4 (decapsulate + lookup in VRF for IPv4), 3 = End.DX2 (cross-connect to L2 interface).
- **Argument:** Optional parameter passed to the function (e.g., which VRF, which interface).

Example SRv6 SID: `2001:db8:1::/48` is the locator for node R1. R1 allocates functions:
- `2001:db8:1::1` - End (node SID, forward to next segment)
- `2001:db8:1::2:0` - End.DT4 (decapsulate, route in VRF 2)
- `2001:db8:1::3:0` - End.DX2 (cross-connect to interface eth0)

### SRH - Segment Routing Header

The SRH (RFC 8754) is an IPv6 extension header (Next Header = 43, Routing Type = 4):

```
IPv6 Header: Destination = Active SID (current segment)
  Extension: SRH {
    Segment Left: N-1   (pointer to active segment)
    Segment List: [SID-N, SID-(N-1), ..., SID-1]  (in reverse order)
  }
```

Processing at each hop:
1. Packet arrives with IPv6 destination = current SID.
2. Router matches SID, executes the SID's behaviour.
3. If the behaviour is "forward to next segment": decrement Segment Left, copy next SID to IPv6 destination, forward.
4. At the final SID (Segment Left = 0): execute terminal behaviour (deliver locally, decapsulate into VRF, etc.).

### SRv6 Endpoint Behaviours

Common behaviours (RFC 8986):

| Behaviour | Name | Function |
|---|---|---|
| `End` | Node SID | Forward packet; advance to next segment |
| `End.X` | Adjacency SID | Forward out a specific interface; advance to next segment |
| `End.DT4` | L3VPN decap (IPv4) | Remove outer IPv6+SRH, route inner IPv4 in specified VRF |
| `End.DT6` | L3VPN decap (IPv6) | Remove outer IPv6+SRH, route inner IPv6 in specified VRF |
| `End.DT46` | L3VPN decap (dual-stack) | Remove outer, route inner IPv4 or IPv6 in VRF |
| `End.DX2` | L2 cross-connect | Remove outer, deliver Ethernet frame to L2 interface (pseudowire) |
| `End.DX4` | L3 cross-connect (IPv4) | Remove outer, forward inner IPv4 out specific interface |
| `End.B6.Encaps` | Binding SID (headend) | Insert a new SRH, used by SR policies |

### SRv6 L3VPN - Replacing MPLS L3VPN

In MPLS L3VPN, the egress PE uses the inner VPN label to select the VRF. In SRv6, the egress PE's SID encodes the VRF selection: `End.DT4` with argument 2 → decapsulate and route in VRF 2. No MPLS labels needed.

The ingress PE:
1. Receives IPv4 packet from CE.
2. Encapsulates in IPv6 with destination = egress PE's End.DT4 SID.
3. Optionally adds SRH if an explicit path through the network is needed.
4. Forwards based on standard IPv6 routing (or SR path).

The egress PE:
1. Receives IPv6 packet destined to its End.DT4 SID.
2. Executes End.DT4: strips outer IPv6, looks up inner IPv4 in the specified VRF, forwards to CE.

No VPN label stack. No LDP. No RSVP. Only IPv6.

=== "Cisco IOS-XR"

    ```
    ! Enable SRv6
    segment-routing srv6
     locators
      locator MAIN
       micro-segment behavior unode psp-usd
       prefix 2001:db8:1::/48
      !
     !
    !
    
    ! IS-IS advertising the locator
    router isis 1
     address-family ipv6 unicast
      segment-routing srv6
       locator MAIN
      !
     !

    ! VRF with SRv6 transport
    router bgp 65001
     vrf CUST-A
      rd 65001:100
      address-family ipv4 unicast
       segment-routing srv6
        locator MAIN
        alloc mode per-vrf
       !
      !
     !
    !

    ! Verification
    show segment-routing srv6 sid
    show bgp vrf CUST-A
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/segment-routing/b-segment-routing-cg-ncs5500/m-srv6-usid.html](https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/segment-routing/b-segment-routing-cg-ncs5500/m-srv6-usid.html)

=== "Juniper Junos"

    ```
    # SRv6 locator and SID block
    set routing-options source-packet-routing srv6 locator MAIN prefix 2001:db8:1::/48

    # IS-IS advertising SRv6 locator
    set protocols isis source-packet-routing srv6 locator MAIN

    # BGP with SRv6 service programming
    set routing-instances CUST-A instance-type vrf
    set routing-instances CUST-A protocols bgp group CE-peers family inet unicast transport srv6 locator MAIN

    # Verification
    show spring-traffic-engineering lsp detail
    show route table CUST-A.inet.0
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/segment-routing-srv6.html](https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/segment-routing-srv6.html)

=== "Nokia SR-OS"

    ```
    # SRv6 locator
    configure router segment-routing segment-routing-v6
        base-routing-instance
            locator "MAIN"
                prefix 2001:db8:1::/48
                function-bits 16
                argument-bits 0
            exit
        exit
        no shutdown
    exit

    # IS-IS advertising locator
    configure router isis 1
        segment-routing-v6
            locator "MAIN"
            no shutdown
        exit
    exit
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-segment-routing/srv6.html](https://documentation.nokia.com/sr/23-10/books/sr-segment-routing/srv6.html)

### Micro-SID (uSID)

A standard SRv6 SID is 128 bits - a 40-byte SRH for a 3-SID path. In hardware with limited packet editing width, this is a concern. **Micro-SID (uSID)** packs multiple function identifiers into a single 128-bit IPv6 address (16-bit slots within a 32-bit or 64-bit block), reducing header overhead significantly. Cisco's implementation is widely deployed with uSID.

### SRv6 vs SR-MPLS Trade-offs

| Property | SR-MPLS | SRv6 |
|---|---|---|
| Data plane | MPLS | Native IPv6 |
| Label size | 20-bit | 128-bit IPv6 address |
| Header overhead | 4 bytes per segment | 40 bytes per SID (standard), 16 bytes (uSID) |
| Hardware support | Mature, universal | Growing; older hardware may lack SRH support |
| Integration with servers/VMs | Requires MPLS-capable fabric | Any IPv6 host can participate |
| Service encoding | Requires separate VPN label | Encoded in SID itself (End.DT4, End.DX2) |
| Deployment maturity | Widely deployed | Deployed by major carriers; growing |

---
## Common Pitfalls

1. **Hardware SRH support gaps.** Not all routers and line cards support SRH processing in hardware. Without hardware support, SRv6 packets are processed in software - at a fraction of MPLS line-rate throughput. Verify hardware support before deploying SRv6 on high-bandwidth paths.

2. **Locator prefix not in the IGP.** SRv6 locators must be advertised in the IGP so all nodes know how to route to them. If the locator prefix (`2001:db8:1::/48`) is not redistributed into the IGP, remote nodes cannot reach the SIDs - packets are dropped. Verify `show route 2001:db8:1::/48` is reachable from all nodes.

3. **MTU issues with SRH overhead.** A standard 3-SID SRH adds 56 bytes to each packet (40-byte SRH + 16-byte IPv6 header). If path MTU is 1500 bytes, packets larger than 1444 bytes are fragmented (or black-holed if DF is set). Configure MTU on all backbone interfaces to accommodate SRH overhead, or use uSID to reduce it.

4. **Function allocation conflicts.** Multiple functions allocated to the same SID address cause ambiguous behaviour. Maintain a SID allocation table and validate no two functions share the same IPv6 address on the same node.

5. **Transit nodes not SRv6-aware.** Standard IPv6 transit nodes (non-SR-capable) can forward SRv6 packets if the SRH doesn't require them to process it. But if a segment list routes through a transit node with its own SID, that node must be SRv6-capable to execute the behaviour. Plan transit capability requirements carefully.

---
## Practice Problems

**Q1.** What is the fundamental difference between how SR-MPLS and SRv6 encode the segment list?

??? answer
    SR-MPLS encodes the segment list as a **stack of 20-bit MPLS labels** prepended to the packet. Each label is 4 bytes; the stack is in the MPLS label space. SRv6 encodes the segment list as a **list of 128-bit IPv6 addresses** in the IPv6 Segment Routing Header (SRH), an extension header. The active segment is simultaneously the IPv6 destination address - standard IPv6 routing delivers the packet to the current SID without requiring MPLS awareness. SRv6 operates entirely in the IPv6 forwarding plane; SR-MPLS requires an MPLS forwarding plane.

**Q2.** A PE router receives an IPv4 packet from a CE and must forward it across an SRv6 backbone to a remote PE for delivery to a VRF. What does the ingress PE do?

??? answer
    The ingress PE encapsulates the original IPv4 packet in an outer IPv6 packet. The outer IPv6 destination is set to the egress PE's **End.DT4 SID** - the SID that identifies both the PE and the specific VRF to use. If an explicit path through the network is required, an SRH is added listing intermediate SIDs; otherwise, only the outer IPv6 header is needed. The packet is forwarded normally via IPv6 routing. When it arrives at the egress PE, the PE matches the End.DT4 SID, strips the outer IPv6 header (and SRH if present), and routes the inner IPv4 packet in the specified VRF - exactly like MPLS L3VPN but without any MPLS labels.

**Q3.** What is Micro-SID (uSID) and why was it developed?

??? answer
    Standard SRv6 SIDs are 128-bit IPv6 addresses. A 3-SID segment list in the SRH adds 40 bytes of overhead per packet. On 100G+ network hardware, processing large variable-length SRHs can require multiple memory accesses or pipeline stalls, reducing forwarding throughput. Micro-SID (uSID) packs multiple 16-bit function identifiers into a single 128-bit IPv6 address (using a carrier prefix for the locator block and 16-bit slots for functions). This reduces SRH overhead significantly - a 6-function path fits in a single 128-bit address instead of six 128-bit SIDs. uSID improves hardware processing efficiency and reduces per-packet overhead while retaining SRv6's IP-native model.

---
## Summary & Key Takeaways

- **SRv6** implements Segment Routing over native IPv6 - no MPLS label plane required.
- **SRv6 SID = IPv6 address** with structured fields: Locator (routing) + Function (behaviour) + Argument (parameter).
- **SRH (Segment Routing Header):** IPv6 extension header carrying the segment list.
- Common behaviours: **End** (forward), **End.DT4/DT6** (L3VPN decapsulate + VRF lookup), **End.DX2** (L2 pseudowire).
- Any IPv6-capable node (router, server, VM) can act as an SRv6 endpoint - no MPLS needed at the host.
- **uSID** reduces overhead by packing multiple functions into one 128-bit address.
- Advantage over SR-MPLS: integration with IPv6-native hosts; disadvantage: larger header overhead, hardware support still maturing.
- Locators must be advertised in the IGP for routing reachability.

---
## Where to Next

- **CT-006 - EVPN Fundamentals:** EVPN can run over SRv6 transport (EVPN-SRv6).
- **CT-012 - Traffic Engineering:** SRv6-TE policies for explicit path control.
- **IP-003 - IPv6 Addressing:** IPv6 fundamentals underlying SRv6 SID structure.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 8754 | IPv6 Segment Routing Header |
| RFC 8986 | SRv6 Network Programming (behaviours) |
| RFC 8402 | Segment Routing Architecture |
| Cisco CCIE Service Provider | SRv6, End behaviours, SRv6 VPNs |
| Nokia SRC | SRv6 deployment |
| Juniper JNCIE-SP | SRv6 with IS-IS |

---
## References

- RFC 8754 - IPv6 Segment Routing Header. [https://www.rfc-editor.org/rfc/rfc8754](https://www.rfc-editor.org/rfc/rfc8754)
- RFC 8986 - SRv6 Network Programming. [https://www.rfc-editor.org/rfc/rfc8986](https://www.rfc-editor.org/rfc/rfc8986)
- RFC 8402 - Segment Routing Architecture. [https://www.rfc-editor.org/rfc/rfc8402](https://www.rfc-editor.org/rfc/rfc8402)

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
| CT-006 | EVPN Fundamentals | EVPN-SRv6 uses SRv6 as transport |
| CT-012 | Traffic Engineering | SRv6-TE for explicit path control |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-004 | Segment Routing SR-MPLS | SR concepts; SRv6 is IPv6-native evolution |
| IP-003 | IPv6 Addressing | IPv6 address structure underlying SRv6 SIDs |
<!-- XREF-END -->
