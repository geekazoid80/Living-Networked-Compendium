---
module_id: CT-006
title: "EVPN Fundamentals"
description: "How Ethernet VPN (EVPN) uses MP-BGP to distribute MAC and IP reachability information, replacing flood-and-learn VPLS with a control-plane-driven Ethernet forwarding model."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 60
prerequisites:
  - CT-003
  - CT-002
  - RT-007
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - evpn
  - bgp
  - l2vpn
  - mac-ip
  - multihoming
  - arp-suppression
  - carrier
  - datacenter
created: 2026-04-19
updated: 2026-04-19
---

# CT-006 - EVPN Fundamentals
## Learning Objectives

After completing this module you will be able to:

1. Explain EVPN architecture and its advantages over VPLS.
2. Describe the five EVPN route types and their functions.
3. Explain EVPN multihoming - Ethernet Segments, ESI, DF election.
4. Describe ARP/ND suppression using EVPN MAC/IP routes.
5. Explain EVPN for L3VPN (RT-5 IP Prefix Routes) as an alternative to traditional L3VPN.
6. Describe EVPN transport options - MPLS and VXLAN.

---
## Prerequisites

- CT-003 - MPLS L2VPN (VPLS): VPLS context and limitations that EVPN addresses
- CT-002 - MPLS VPNs (L3VPN): MP-BGP address families, Route Targets
- RT-007 - BGP Fundamentals: BGP sessions, address families, communities

---
## The Problem

VPLS (CT-003) works - but it has three fundamental limitations that become painful at scale:

1. **Flood-and-learn:** Unknown unicast and broadcast frames are flooded to every PE in the VPLS instance. At scale with hundreds of sites, a single ARP broadcast is replicated to every PE - even those with no hosts that need it.

2. **No multihoming:** A CE with two uplinks to two different PEs cannot use both simultaneously - STP blocks one link. Half the capacity is wasted; recovery when the active link fails takes seconds.

3. **Slow MAC mobility:** When a host moves from one CE to another (server migration, VM vMotion), the old MAC-to-PE mapping stays in the VPLS MAC table until it ages out. Traffic flows to the wrong PE for minutes.

What if MAC and IP reachability were distributed via the BGP control plane - so PEs know where every MAC is before the first packet arrives?

### Step 1: BGP as the MAC routing protocol

EVPN (RFC 7432) introduces a new BGP address family: **L2VPN EVPN**. PEs advertise MAC addresses (and optionally their associated IP addresses) via BGP routes - specifically **EVPN Route Type 2 (MAC/IP Advertisement Route)**. When PE1 learns that host H1 (MAC 00:11:22:33:44:55, IP 10.0.0.1) is attached to it, PE1 advertises this to all other PEs via BGP. Every PE now has a control-plane entry for H1 before a packet arrives.

### Step 2: Suppress flooding - ARP/ND proxy

Because PEs know MAC/IP bindings from BGP, they can answer ARP requests locally - without flooding the ARP broadcast to all PEs. PE2 receives an ARP request for 10.0.0.1; it checks its EVPN MAC/IP table, finds PE1 holds that binding, and sends a proxy ARP reply directly. The ARP broadcast never traverses the backbone.

### Step 3: Multihoming with EVPN Ethernet Segments

EVPN introduces **Ethernet Segments (ES)**: a logical identifier for a multi-homed connection. If CE-A connects to both PE1 and PE2, both PEs advertise the same ES identifier (ESI). EVPN elects a **Designated Forwarder (DF)** per VLAN to handle BUM (Broadcast, Unknown unicast, Multicast) traffic - avoiding duplication. Both links carry unicast traffic simultaneously. On failure, the non-DF PE takes over in sub-second time.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| BGP MAC/IP advertisement | EVPN RT-2 (MAC/IP Advertisement Route) |
| BGP route announcing an Ethernet segment | EVPN RT-1 (Ethernet Auto-discovery Route) |
| BGP route for IP prefix (L3VPN-like) | EVPN RT-5 (IP Prefix Route) |
| Logical identifier for multi-homed CE link | ESI (Ethernet Segment Identifier) |
| PE elected to forward BUM traffic per VLAN | DF (Designated Forwarder) |
| PE answering ARP on behalf of remote host | ARP proxy / ND proxy |
| VXLAN or MPLS data plane for EVPN | EVPN transport |
| EVPN instance (per VPN tenant) | EVI (EVPN Instance) |

---
## Core Content

### EVPN Route Types

EVPN defines five route types in the L2VPN EVPN BGP address family:

| Route Type | Name | Function |
|---|---|---|
| **RT-1** | Ethernet Auto-discovery | Announces ES membership; used for mass withdrawal on ES failure; carries aliasing info for multihoming |
| **RT-2** | MAC/IP Advertisement | Advertises a MAC address and optionally its IP binding; one route per host |
| **RT-3** | Inclusive Multicast Ethernet Tag (IMET) | Announces BUM tree membership; used to build flood list (or P2MP tree) for each EVI |
| **RT-4** | Ethernet Segment | Announces ES information; used for DF election |
| **RT-5** | IP Prefix | Advertises an IP prefix (L3VPN-style) for inter-subnet routing using EVPN |

RT-2 is the most fundamental: each connected host generates a separate RT-2 route containing its MAC (and optionally IP) and the PE's SID/label. This is the "MAC routing" that replaces VPLS flood-and-learn.

### EVI - EVPN Instance

An **EVI** (EVPN Instance) is the per-VPN context, analogous to a VPLS VFI or an L3VPN VRF. Each EVI has:
- A **Route Distinguisher** (to make RT-2 routes globally unique - same role as in L3VPN).
- **Route Targets** (import/export - same policy mechanism as L3VPN).
- An associated VLAN or VNI (VXLAN) or pseudowire label (MPLS).

Multiple EVIs on a PE map to different VPNs. The RT-2 routes from one EVI are imported only into PEs with a matching import RT - maintaining isolation between VPNs.

### EVPN Multihoming

A CE connects to two PEs (PE1 and PE2) via a LAG (or two separate links). Both PEs share the same **ESI (Ethernet Segment Identifier)** - a 10-byte value uniquely identifying this multi-homed connection.

**All-Active multihoming:** Both links carry traffic simultaneously. PE1 and PE2 both advertise RT-2 routes for hosts behind the CE - the remote PE uses ECMP across both PE1 and PE2 as next-hops for traffic destined to those hosts.

**Single-Active multihoming:** Only one PE forwards at a time (like STP active/standby). The backup PE takes over on failure.

**DF Election:** For BUM (Broadcast, Unknown unicast, Multicast) traffic, only one PE per VLAN (the **Designated Forwarder**) forwards to the CE - preventing duplicate BUM delivery. DF is elected via RT-4 route exchange between PEs sharing the same ESI.

**Mass withdrawal on ES failure:** When PE1's link to the CE fails, PE1 withdraws all RT-1 routes for that ESI. Remote PEs immediately redirect traffic to PE2 - without waiting for RT-2 MAC routes to age out. This is orders of magnitude faster than VPLS MAC aging.

### ARP/ND Suppression

PEs store `MAC + IP` bindings from RT-2 routes. When a host on PE2's segment sends an ARP request for an IP on PE1's segment:

1. PE2 receives the ARP broadcast.
2. PE2 checks its local EVPN MAC/IP table - RT-2 from PE1 has the binding.
3. PE2 generates a proxy ARP reply on behalf of PE1 - without flooding across the backbone.
4. The ARP broadcast never leaves PE2's local segment.

At scale (10,000+ VMs in a data centre), ARP suppression eliminates a significant flood load. The equivalent for IPv6 is ND (Neighbour Discovery) suppression - same mechanism, IPv6 specific.

### EVPN for L3 (RT-5 IP Prefix Routes)

EVPN RT-5 allows EVPN to carry IP prefix routes (not just MAC/IP host routes), enabling inter-subnet routing without a traditional L3VPN setup. An IRB (Integrated Routing and Bridging) interface on the PE acts as the gateway for hosts in the EVI. Routes from the IRB are advertised as RT-5 routes.

This allows EVPN to serve as a unified L2+L3 service - a single control plane (EVPN over BGP) handles both:
- L2 forwarding (RT-2 MAC routes within a VLAN)
- L3 routing (RT-5 IP prefix routes between subnets/VRFs)

In a data centre context, this is called **EVPN-VXLAN** with symmetric IRB or asymmetric IRB (covered in CT-007).

### Transport Options

EVPN is transport-agnostic - the BGP control plane works identically regardless of the data plane:

| Transport | Use case |
|---|---|
| **MPLS** (SR-MPLS or LDP) | Carrier WAN, SP edge |
| **VXLAN** | Data centre overlay (CT-007) |
| **SRv6** | Next-generation carrier and DC |
| **MPLS over UDP** | Interop with routers lacking MPLS hardware |

The RT-2 route carries the next-hop (PE loopback) and the encapsulation label/VNI. The receiving PE builds its forwarding table using the BGP next-hop and the label/VNI from the route's PMSI or encapsulation attribute.

=== "Cisco IOS-XE (MPLS transport)"

    ```
    ! EVPN instance
    l2vpn evpn instance 100 vlan-based
     rd 65001:100
     route-target export 65001:100
     route-target import 65001:100
     no auto-route-target

    ! EVI attached to bridge domain
    bridge-domain 100
     member evpn-instance 100 vni 10100
     member GigabitEthernet0/1 service-instance 100

    ! BGP — enable L2VPN EVPN address family
    router bgp 65001
     address-family l2vpn evpn
      neighbor 2.2.2.2 activate
      neighbor 2.2.2.2 send-community extended

    ! Verification
    show l2vpn evpn evi 100
    show bgp l2vpn evpn
    show l2vpn evpn mac-ip
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l2_vpns/configuration/xe-17/mp-l2-vpns-xe-17-book/mp-bgp-evpn.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l2_vpns/configuration/xe-17/mp-l2-vpns-xe-17-book/mp-bgp-evpn.html)

=== "Juniper Junos (MPLS transport)"

    ```
    # EVPN routing instance
    set routing-instances EVPN-CUST-A instance-type evpn
    set routing-instances EVPN-CUST-A vlan-id 100
    set routing-instances EVPN-CUST-A interface ge-0/0/1.0
    set routing-instances EVPN-CUST-A route-distinguisher 65001:100
    set routing-instances EVPN-CUST-A vrf-target target:65001:100
    set routing-instances EVPN-CUST-A protocols evpn

    # BGP L2VPN EVPN address family
    set protocols bgp group IBGP-EVPN type internal
    set protocols bgp group IBGP-EVPN family evpn signaling
    set protocols bgp group IBGP-EVPN neighbor 2.2.2.2

    # Verification
    show evpn instance
    show bgp summary
    show evpn mac-table
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-mpls.html](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-mpls.html)

=== "Nokia SR-OS (MPLS transport)"

    ```
    # EVPN service (VPLS with EVPN control plane)
    configure service vpls 300 customer 1 create
        description "EVPN L2 Service"
        bgp
            route-distinguisher 65001:300
            route-target export target:65001:300
            route-target import target:65001:300
        exit
        bgp-evpn
            mpls bgp 1
                no shutdown
            exit
            evi 300
        exit
        sap 1/1/1:300 create
        exit
        no shutdown
    exit
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-evpn/evpn-mpls.html](https://documentation.nokia.com/sr/23-10/books/sr-evpn/evpn-mpls.html)

---
## Common Pitfalls

1. **RT mismatch between EVIs.** EVPN uses the same RT import/export mechanism as L3VPN. If PE1's EVI exports RT `65001:100` but PE2's EVI imports only `65001:200`, RT-2 routes are received but not installed - the EVI MAC table stays empty. Always verify RTs match on both ends: `show bgp l2vpn evpn` to see received routes, `show l2vpn evpn evi` to see imported routes.

2. **Missing `send-community extended` on BGP neighbor.** Route Targets are extended communities. Without `send-community extended`, RTs are stripped - received routes have no RT and are not imported into any EVI. Essential for both EVPN and L3VPN.

3. **ESI misconfiguration in multihoming.** All PEs connected to the same CE (same LAG) must use the same ESI value. A mismatch causes the PEs to treat the connection as separate single-homed links - no DF election, possible MAC duplication, STP may block one link. ESI must be configured consistently.

4. **No RT-3 IMET routes - no flooding.** RT-3 IMET routes announce BUM flood list membership. If RT-3 routes are missing (config omitted, filtered), the PE is excluded from BUM flooding - broadcast and multicast traffic doesn't reach that PE. Unknown unicast also cannot be flooded. Hosts behind that PE are unreachable via broadcast-dependent protocols (ARP, DHCP) until MAC/IP routes are built via data-plane learning.

5. **EVPN and STP interaction.** EVPN with all-active multihoming bypasses STP (intentionally). If the CE still runs STP and sends BPDUs, EVPN may forward BPDUs in a way that interacts unexpectedly with the CE's topology. Configure BPDU handling (tunnel or filter) on CE-facing interfaces appropriately for the CE's STP mode.

---
## Practice Problems

**Q1.** How does EVPN eliminate the flood-and-learn problem of VPLS?

??? answer
    In VPLS, when a new host sends its first frame, the PE floods it to all other PEs because the destination MAC is unknown. EVPN replaces this with a BGP control plane: when a PE learns a new host's MAC (and IP), it immediately advertises an RT-2 MAC/IP Advertisement Route via BGP to all other PEs. Remote PEs install the MAC-to-PE mapping in their forwarding table before they receive any data-plane traffic for that host. Unknown unicast flooding is eliminated because PEs know where every MAC is from the control plane. Residual flooding (for genuinely unknown MACs and broadcast) uses the RT-3 IMET-based flood list, which is scoped and does not flood to unnecessary PEs.

**Q2.** A CE is connected to two PEs (PE1 and PE2) with the same ESI. Both PEs advertise RT-2 for hosts behind the CE. How does a remote PE (PE3) use both PE1 and PE2 for traffic to those hosts?

??? answer
    EVPN all-active multihoming advertises the same ESI from PE1 and PE2. When PE3 receives RT-2 routes for hosts behind the CE from both PE1 and PE2 (both with the same ESI), PE3 installs both PE1 and PE2 as equal-cost next-hops (ECMP) for those MAC routes. Traffic from PE3 to hosts behind the CE is load-balanced across both PE1 and PE2 simultaneously. This is called **aliasing** - RT-1 Ethernet Auto-discovery routes from PE1 and PE2 for the shared ESI signal to PE3 that both PEs reach the same CE, enabling PE3 to ECMP across both even before it has RT-2 routes from both.

**Q3.** What is the EVPN RT-5 IP Prefix Route used for, and how does it differ from RT-2?

??? answer
    RT-2 MAC/IP Advertisement Routes advertise individual host endpoints: `MAC + IP` bindings for a specific device connected to a PE. RT-5 IP Prefix Routes advertise IP network prefixes - subnets or summary routes - rather than individual hosts. RT-5 is used for inter-subnet routing (L3 forwarding between different IP subnets in an EVPN overlay): the IRB (Integrated Routing and Bridging) interface on the PE acts as the gateway, and its connected subnets (or learned routes) are redistributed as RT-5 routes to remote PEs. This allows EVPN to serve as a unified L2+L3 control plane: RT-2 for within-subnet L2 reachability, RT-5 for between-subnet L3 reachability.

---
## Summary & Key Takeaways

- **EVPN** replaces VPLS flood-and-learn with a BGP control plane for MAC/IP reachability.
- **RT-2 (MAC/IP):** Core route type - advertises `MAC + IP` per host; enables ARP suppression.
- **RT-1 (Ethernet Auto-discovery):** Multihoming membership; enables mass withdrawal and aliasing.
- **RT-3 (IMET):** BUM flood list - which PEs participate in broadcast/multicast for each EVI.
- **RT-4 (Ethernet Segment):** DF election between multihomed PEs.
- **RT-5 (IP Prefix):** Inter-subnet L3 routing - EVPN as a unified L2+L3 control plane.
- **Multihoming (all-active):** Both CE uplinks carry traffic simultaneously; DF handles BUM.
- **ARP suppression:** PEs answer ARP locally from the BGP MAC/IP table - no backbone flooding.
- EVPN transport is agnostic: MPLS, VXLAN, SRv6 all work with the same BGP control plane.
- RTs and `send-community extended` are mandatory for correct EVPN route import.

---
## Where to Next

- **CT-007 - EVPN-VXLAN:** EVPN with VXLAN data plane in data centre overlay networks.
- **CT-004 - Segment Routing SR-MPLS:** SR-MPLS as EVPN transport in carrier networks.
- **CT-005 - SRv6:** EVPN-SRv6 for next-generation unified transport.
- **SEC-006 - Network Segmentation & DMZ:** EVPN micro-segmentation in data centre.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 7432 | BGP MPLS-Based Ethernet VPN |
| RFC 8365 | A Network Virtualization Overlay Solution Using EVPN |
| RFC 9135 | Integrated Routing and Bridging in EVPN |
| Cisco CCIE Service Provider / Data Centre | EVPN, multihoming, RT-2/3/4/5 |
| Juniper JNCIE-SP / JNCIE-DC | EVPN-MPLS, EVPN-VXLAN |
| Nokia SRC | EVPN deployment |

---
## References

- RFC 7432 - BGP MPLS-Based Ethernet VPN. [https://www.rfc-editor.org/rfc/rfc7432](https://www.rfc-editor.org/rfc/rfc7432)
- RFC 8365 - EVPN with Network Virtualization Overlay. [https://www.rfc-editor.org/rfc/rfc8365](https://www.rfc-editor.org/rfc/rfc8365)
- RFC 9135 - Integrated Routing and Bridging in EVPN. [https://www.rfc-editor.org/rfc/rfc9135](https://www.rfc-editor.org/rfc/rfc9135)

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
| CT-007 | EVPN-VXLAN | EVPN control plane with VXLAN data plane |
| SEC-006 | Network Segmentation & DMZ | EVPN micro-segmentation in DC |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-003 | MPLS L2VPN (VPLS & Pseudowire) | EVPN replaces VPLS |
| CT-002 | MPLS VPNs - L3VPN | MP-BGP address family; RT mechanism |
| RT-007 | BGP Fundamentals | BGP sessions and address family foundation |
<!-- XREF-END -->
