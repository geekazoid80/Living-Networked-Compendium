---
module_id: CT-002
title: "MPLS VPNs - L3VPN & VRF"
description: "How MPLS L3VPN uses VRFs, route distinguishers, route targets, and the BGP VPNv4 address family to deliver isolated Layer 3 VPN services across a shared MPLS backbone."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 60
prerequisites:
  - CT-001
  - RT-007
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - mpls
  - l3vpn
  - vrf
  - bgp
  - vpnv4
  - route-distinguisher
  - route-target
  - carrier
created: 2026-04-19
updated: 2026-04-19
---

# CT-002 - MPLS VPNs - L3VPN & VRF
## Learning Objectives

After completing this module you will be able to:

1. Explain the MPLS L3VPN architecture - CE, PE, P routers and their roles.
2. Describe VRFs and why they are needed on PE routers.
3. Explain Route Distinguishers and Route Targets - their roles and the difference between them.
4. Describe the MP-BGP VPNv4 address family and how it carries customer routes.
5. Explain the two-label stack used in MPLS VPN forwarding.
6. Configure a basic L3VPN (VRF, RD, RT, MP-BGP, CE-PE routing).

---
## Prerequisites

- CT-001 - MPLS Fundamentals (label switching, LDP, LSP)
- RT-007 - BGP Fundamentals (BGP sessions, address families, communities)

---
## The Problem

A service provider has one MPLS backbone and 50 enterprise customers. Each customer has multiple branch sites connected to the provider's routers (PE routers). Customer A's branches need to reach each other. Customer B's branches need to reach each other. But Customer A must never see Customer B's traffic or routing table - they're separate businesses, some of which use the same private IP address ranges (all using 10.0.0.0/8 internally).

One physical network. Many logical private networks. Complete isolation between customers. Same address space reused by multiple customers simultaneously.

### Step 1: Separate routing tables per customer

On a PE router connected to both Customer A and Customer B, a single global routing table cannot hold their overlapping prefixes. The router needs a separate routing table per customer - a **VRF (Virtual Routing and Forwarding)** instance. Each VRF has its own routes, its own interfaces, and forwards independently. A packet arriving on Customer A's interface looks up only Customer A's VRF.

### Step 2: Carry customer routes across the backbone

The backbone P routers only forward MPLS labels - they don't need to know about customer routes. Only the PE routers (at the edges) need to exchange customer routes with each other. They do this via **MP-BGP** (Multi-Protocol BGP) using the **VPNv4 address family**.

But if both customers use 10.0.0.0/8, how does the receiving PE know which customer a route belongs to? Each customer route is tagged with a **Route Distinguisher (RD)** - an 8-byte value prepended to the prefix that makes it globally unique: `65001:100:10.0.0.0/8` is Customer A's route; `65001:200:10.0.0.0/8` is Customer B's. The RD disambiguates - nothing more.

### Step 3: Control which VRFs import which routes

The receiving PE must know: import Customer A's routes into Customer A's VRF, and Customer B's routes into Customer B's VRF. This is controlled by **Route Targets (RT)** - BGP extended communities attached to VPNv4 routes. Each VRF has an export RT (tag routes leaving this VRF) and an import RT (accept routes tagged with this value). Customer A VRFs on all PEs share the same RT: `65001:100`. They export with `65001:100`; they import `65001:100`. Customer B uses `65001:200`. No route crosses the boundary.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Separate routing table per customer on PE | VRF (Virtual Routing and Forwarding) |
| BGP extension to carry multiple address families | MP-BGP |
| BGP address family for VPN routes | VPNv4 (IPv4 VPN) / VPNv6 |
| Prefix + 8-byte tag to make VPN routes unique | Route Distinguisher (RD) |
| BGP extended community for VRF import/export policy | Route Target (RT) |
| PE router - connects customer to MPLS backbone | PE (Provider Edge) |
| P router - backbone label switching only | P (Provider core) |
| CE router - customer router connecting to PE | CE (Customer Edge) |
| MPLS label forwarding between PE and PE | Label Switched Path (LSP) |

---
## Core Content

### L3VPN Architecture

```
     CE-A1 ─── PE1 ─────── P ─────── PE2 ─── CE-A2
                │    MPLS backbone    │
     CE-B1 ─── ┘                     └─── CE-B1
```

- **CE (Customer Edge):** Customer router. Connects to the PE via a routing protocol (BGP, OSPF, EIGRP, or static). Does not run MPLS - sees the L3VPN as a standard IP network.
- **PE (Provider Edge):** Service provider edge router. Maintains VRFs per customer, runs MP-BGP to other PEs, applies MPLS labels.
- **P (Provider core):** Label-switching only. No VRF awareness. Forwards based on MPLS labels.

### VRF Configuration

A VRF is a separate routing and forwarding instance. Each CE-facing interface is assigned to a VRF.

=== "Cisco IOS-XE"

    ```
    ! Create VRF for Customer A
    vrf definition CUST-A
     rd 65001:100
     address-family ipv4
      route-target export 65001:100
      route-target import 65001:100
     exit-address-family

    ! Assign interface to VRF
    interface GigabitEthernet0/1
     vrf forwarding CUST-A
     ip address 10.0.1.1 255.255.255.252
    
    ! Verification
    show vrf
    show ip route vrf CUST-A
    show ip bgp vpnv4 vrf CUST-A
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l3_vpns/configuration/xe-17/mp-l3-vpns-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l3_vpns/configuration/xe-17/mp-l3-vpns-xe-17-book.html)

=== "Juniper Junos"

    ```
    # Create routing instance (VRF) for Customer A
    set routing-instances CUST-A instance-type vrf
    set routing-instances CUST-A interface ge-0/0/1.0
    set routing-instances CUST-A route-distinguisher 65001:100
    set routing-instances CUST-A vrf-target target:65001:100
    set routing-instances CUST-A vrf-table-label

    # Verification
    show route table CUST-A.inet.0
    show bgp summary
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/mpls-l3vpn-configuring.html](https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/mpls-l3vpn-configuring.html)

=== "Nokia SR-OS"

    ```
    # Create VPRN (VRF) service
    configure service vprn 100 customer 1 create
        route-distinguisher 65001:100
        vrf-target target:65001:100
        interface "to-CE-A1" create
            address 10.0.1.1/30
            sap 1/1/1:100 create
            exit
        exit
        bgp-ipvpn
            mpls
                route-distinguisher 65001:100
                vrf-target target:65001:100
                auto-bind-tunnel
                    resolution any
                exit
                no shutdown
            exit
        exit
        no shutdown
    exit
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-unicast-routing-protocols/mpls-l3vpn.html](https://documentation.nokia.com/sr/23-10/books/sr-unicast-routing-protocols/mpls-l3vpn.html)

### MP-BGP VPNv4 Address Family

PE routers establish BGP sessions with each other (directly, or via Route Reflectors) using the VPNv4 address family. These are iBGP sessions within the provider AS.

=== "Cisco IOS-XE"

    ```
    ! MP-BGP between PE1 and PE2 (or Route Reflector)
    router bgp 65001
     bgp router-id 1.1.1.1
     no bgp default ipv4-unicast

     neighbor 2.2.2.2 remote-as 65001
     neighbor 2.2.2.2 update-source Loopback0

     address-family vpnv4
      neighbor 2.2.2.2 activate
      neighbor 2.2.2.2 send-community extended
     exit-address-family

    ! CE-facing routing — BGP from CE into VRF
    router bgp 65001
     address-family ipv4 vrf CUST-A
      neighbor 10.0.1.2 remote-as 65002    ! CE router AS
      neighbor 10.0.1.2 activate
      redistribute connected
     exit-address-family
    ```

=== "Juniper Junos"

    ```
    # BGP group for VPNv4 peers (internal)
    set protocols bgp group IBGP-VPN type internal
    set protocols bgp group IBGP-VPN local-address 1.1.1.1
    set protocols bgp group IBGP-VPN family inet-vpn unicast
    set protocols bgp group IBGP-VPN neighbor 2.2.2.2
    ```

### The Two-Label Stack

MPLS L3VPN uses two labels:

```
[Outer label (transport/tunnel label)] [Inner label (VPN label)] [IP packet]
```

- **Outer label (transport label):** Assigned by LDP (or RSVP-TE). Used by P routers to switch the packet along the LSP from ingress PE to egress PE. This label is swapped at every P hop.
- **Inner label (VPN label):** Assigned by MP-BGP. Identifies the destination VRF on the egress PE. P routers ignore it. Egress PE reads the inner label to determine which VRF to look up for the final IP forwarding.

At the egress PE (or the penultimate P router with PHP - Penultimate Hop Popping), the outer label is removed. The egress PE uses the inner label to select the VRF, then strips the inner label and does a normal IP lookup in that VRF.

### Route Distinguisher vs Route Target

These are often confused. Their roles are distinct:

| Property | Route Distinguisher (RD) | Route Target (RT) |
|---|---|---|
| Format | 8 bytes: `ASN:number` or `IP:number` | BGP extended community: `ASN:number` |
| Purpose | Make VPN routes globally unique (disambiguation) | Control which VRFs import which routes (policy) |
| Applied at | Route origination on PE (per-VRF, static) | Route advertisement and import (dynamic policy) |
| Can routes with same RD reach different VRFs? | No - RD is tied to origin VRF | Yes - RT controls import regardless of RD |
| Can two VRFs share an RD? | Technically yes, but bad practice | Yes - shared RT is normal (hub-and-spoke, etc.) |

**Hub-and-spoke VPN topology:** Site-A (spoke) exports `65001:110`, imports `65001:100`. Hub exports `65001:100`, imports `65001:110`. Spokes cannot reach each other directly - all traffic flows through the hub. Achieved purely through RT policy, no physical path changes required.

### CE-PE Routing

The CE router does not need to run MPLS. It exchanges routes with the PE using:
- **BGP (eBGP):** Most common; per-customer AS numbers; clean isolation.
- **OSPF:** CE and PE as OSPF neighbours in a separate OSPF domain per VRF; complex sham-link may be needed for backdoor links.
- **Static routes:** Simple but no failure detection.
- **EIGRP:** Supported but Cisco-specific.

---
## Common Pitfalls

1. **RD and RT configured on different sides.** RD must be unique per VRF per PE. RT export on PE1 must match RT import on PE2. A misconfigured RT means routes are learned by MP-BGP but not imported into the correct VRF - the VRF routing table stays empty while the VPNv4 BGP table shows the routes.

2. **Missing `send-community extended` on BGP neighbor.** Route Targets are BGP extended communities. Without `send-community extended`, RT attributes are stripped from VPNv4 advertisements - the receiving PE receives the route with no RT and imports it into no VRF.

3. **MPLS not enabled on PE-to-P interfaces.** L3VPN requires MPLS to be running on all PE-to-P and P-to-P links (LDP or RSVP-TE). If MPLS is not enabled on the PE's uplink interface, the outer label stack cannot be imposed - VPN traffic will not be forwarded.

4. **Overlapping address space without VRF.** If a CE-facing interface is not assigned to a VRF, its routes go into the global routing table. Overlapping customer prefixes in the global table cause route conflicts and incorrect forwarding. Every CE-facing interface must be in a VRF.

5. **BGP session between PEs using data-plane address.** PE-to-PE iBGP sessions should use Loopback addresses - these are reachable via the MPLS backbone's IGP (OSPF/IS-IS), remain up even if one physical link fails, and are the source address for the MPLS LSP. Using a physical interface address as the BGP source means the session may drop on link failure even though an alternate path exists.

---
## Practice Problems

**Q1.** Two PE routers have a VPNv4 BGP session. PE2 receives a route `65001:100:10.0.0.0/24` in the VPNv4 table but the route does not appear in VRF CUST-A's routing table. What is the most likely cause?

??? answer
    The RT on the received VPNv4 route does not match the RT import policy of VRF CUST-A on PE2. The route is in the BGP VPNv4 table (BGP learned it), but import into the VRF is controlled by the Route Target community. Check: (1) the RT export on PE1's VRF - what RT is stamped on outgoing routes; (2) the RT import on PE2's VRF - what RT values it accepts. They must match exactly. Also confirm `send-community extended` is configured on the BGP neighbor statement.

**Q2.** What is the purpose of the inner (VPN) label in the MPLS L3VPN label stack?

??? answer
    The inner label (VPN label) is assigned by the egress PE via MP-BGP and identifies the destination VRF on that PE. P routers in the backbone only look at the outer (transport) label - they never touch the inner label. When the packet reaches the egress PE (after the outer label is popped), the PE reads the inner label to determine which VRF to use for the final IP lookup. Without the inner label, the egress PE would not know which of its VRFs to forward the packet into.

**Q3.** Customer A has a hub site and four spoke sites. Spoke sites must not reach each other directly - all traffic must pass through the hub. How do you implement this with Route Targets alone?

??? answer
    Use asymmetric RTs: Hub VRF exports `65001:100` (hub export RT) and imports `65001:110` (spoke export RT). Each spoke VRF exports `65001:110` (spoke export RT) and imports `65001:100` (hub export RT). Spokes receive only hub routes (RT 65001:100); they do not import each other's routes (RT 65001:110). The hub receives all spoke routes. Traffic from spoke A to spoke B must traverse the hub because spoke A has no route to spoke B in its VRF - only to the hub. This is implemented entirely through RT policy on the PEs; no physical topology change required.

---
## Summary & Key Takeaways

- **MPLS L3VPN** delivers isolated Layer 3 VPN service over a shared backbone - multiple customers, overlapping IP, complete isolation.
- **VRF** provides per-customer routing table isolation on PE routers.
- **Route Distinguisher (RD):** Makes VPN routes globally unique - disambiguates overlapping prefixes from different VRFs.
- **Route Target (RT):** Controls which VRFs import which routes - the policy mechanism for VPN topology (full mesh, hub-and-spoke, extranet).
- **MP-BGP VPNv4** carries customer routes between PEs; P routers carry only MPLS labels.
- **Two-label stack:** Outer (transport) for PE-to-PE forwarding; inner (VPN) for egress VRF identification.
- PE-to-PE BGP uses Loopback addresses - not physical interfaces.
- `send-community extended` must be enabled on all VPNv4 BGP neighbors.

---
## Where to Next

- **CT-003 - MPLS L2VPN (VPLS & Pseudowire):** Layer 2 connectivity over MPLS backbone.
- **CT-004 - Segment Routing SR-MPLS:** Label distribution via IGP instead of LDP.
- **CT-006 - EVPN Fundamentals:** Modern replacement for VPLS with MAC/IP routes.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 4364 | BGP/MPLS IP Virtual Private Networks (VPNs) |
| RFC 4271 | BGP-4 (BGP fundamentals) |
| RFC 4760 | Multiprotocol Extensions for BGP-4 (MP-BGP) |
| Cisco CCIE Service Provider | L3VPN, VRF, MP-BGP |
| Nokia SRC | MPLS VPN service architecture |
| Juniper JNCIE-SP | MPLS L3VPN |

---
## References

- RFC 4364 - BGP/MPLS IP VPNs. [https://www.rfc-editor.org/rfc/rfc4364](https://www.rfc-editor.org/rfc/rfc4364)
- RFC 4760 - Multiprotocol Extensions for BGP-4. [https://www.rfc-editor.org/rfc/rfc4760](https://www.rfc-editor.org/rfc/rfc4760)

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
| CT-003 | MPLS L2VPN (VPLS & Pseudowire) | L2VPN complements L3VPN for same backbone |
| CT-004 | Segment Routing SR-MPLS | SR-MPLS can replace LDP-based L3VPN transport |
| CT-006 | EVPN Fundamentals | EVPN extends L3VPN concept to MAC/IP advertisement |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-001 | MPLS Fundamentals | Label switching, LDP, LSP as transport layer |
| RT-007 | BGP Fundamentals | MP-BGP carries VPNv4 routes between PEs |
<!-- XREF-END -->
