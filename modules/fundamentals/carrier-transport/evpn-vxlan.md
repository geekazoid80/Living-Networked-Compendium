---
id: CT-007
title: "EVPN-VXLAN"
description: "How EVPN control plane combined with VXLAN data plane creates a scalable, multitenant data centre overlay network with distributed gateway, ARP suppression, and multivendor interoperability."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 60
prerequisites:
  - CT-006
  - SW-002
learning_path_tags:
  - CE
  - DCE
difficulty: advanced
tags:
  - evpn
  - vxlan
  - datacenter
  - overlay
  - vni
  - vtep
  - irb
  - multitenant
created: 2026-04-19
updated: 2026-04-19
---

# CT-007 — EVPN-VXLAN

## The Problem

A cloud provider operates a data centre with 10,000 servers. Tenants need isolated Layer 2 networks — each tenant's VMs must be on the same broadcast domain regardless of which physical rack they land on. Traditional VLANs are limited to 4094 IDs — far too few for thousands of tenants. VLAN configuration must be pushed to every switch in the fabric each time a tenant network is created.

### Step 1: Extend VLANs beyond the network — VXLAN

VXLAN (RFC 7348) encapsulates Ethernet frames in UDP packets. A hypervisor or switch that supports VXLAN (a **VTEP — VXLAN Tunnel Endpoint**) can send Ethernet frames to any other VTEP across an IP network. VXLANs use a 24-bit **VNI (VXLAN Network Identifier)** — 16 million possible overlay networks, eliminating the 4094 VLAN limit.

The physical underlay is a standard routed IP network (spine-leaf fabric). The overlay is a virtual Ethernet network stretched across the fabric. Physical location of the server no longer constrains which virtual network it's in.

### Step 2: Distribute MAC/IP without flooding

Basic VXLAN (RFC 7348) still uses flood-and-learn: unknown destination VTEPs receive flooded copies of every unknown unicast and broadcast frame. At 10,000+ servers, this is impractical.

EVPN (CT-006) provides the control plane: BGP MAC/IP (RT-2) routes tell every VTEP where every MAC is — before the first packet is sent. The combination **EVPN-VXLAN** uses EVPN as the control plane and VXLAN as the data plane. No flooding for known unicasts. ARP requests are answered locally. VTEPs only send frames to the specific VTEP that holds the destination host.

### Step 3: Route between subnets at the edge

Traditional DC architectures route inter-subnet traffic through a centralised L3 gateway — all inter-VLAN traffic must traverse that device even if source and destination are on adjacent leaf switches. EVPN-VXLAN supports **distributed anycast gateways**: every leaf switch acts as the IP gateway for all subnets, using the same MAC address (anycast MAC). VMs can send traffic to their default gateway at the nearest leaf — inter-subnet routing happens locally.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Ethernet-in-UDP encapsulation | VXLAN |
| 24-bit overlay network identifier | VNI (VXLAN Network Identifier) |
| Device that originates/terminates VXLAN tunnels | VTEP (VXLAN Tunnel Endpoint) |
| L2 VNI mapping to a broadcast domain / VLAN | L2 VNI |
| L3 VNI mapping to a VRF / routing domain | L3 VNI |
| Same gateway MAC on all leaf VTEPs | Anycast gateway |
| L3 routing at the leaf for inter-subnet traffic | Distributed gateway / IRB |
| Symmetric vs asymmetric routing between VTEPs | Symmetric IRB / Asymmetric IRB |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain VXLAN encapsulation — VNI, VTEP, and UDP encapsulation format.
2. Describe how EVPN provides the control plane for VXLAN — RT-2 and RT-3 usage.
3. Explain L2 VNI and L3 VNI — their roles in bridging and routing.
4. Describe the distributed anycast gateway and symmetric IRB model.
5. Explain the underlay requirements for EVPN-VXLAN.
6. Configure basic EVPN-VXLAN on a leaf switch.

---

## Prerequisites

- CT-006 — EVPN Fundamentals (EVPN route types, RT-2, RT-3, multihoming)
- SW-002 — VLANs & 802.1Q (VLAN-to-VNI mapping)

---

## Core Content

### VXLAN Encapsulation

```
[Outer Ethernet][Outer IP][Outer UDP dst=4789][VXLAN Header 8B][Inner Ethernet Frame]
```

VXLAN header (8 bytes):
- Flags: bit I = 1 (VNI present)
- VNI: 24 bits (0–16,777,215)
- Reserved: 8 bits

The inner Ethernet frame is the original host frame — preserved intact. The outer Ethernet/IP/UDP headers carry it across the underlay IP fabric. UDP destination port 4789 (IANA assigned for VXLAN).

**VTEP:** Any device (leaf switch, server NIC, hypervisor vSwitch) that can encapsulate/decapsulate VXLAN. VTEPs are identified by their underlay IP address (typically a Loopback).

**Overhead:** VXLAN adds 50 bytes (14+20+8+8) for IPv4 underlay. Physical links need MTU ≥ 1550 bytes (for 1500-byte tenant frames).

### L2 VNI and L3 VNI

**L2 VNI (Layer 2 VNI):** Maps to a broadcast domain — equivalent to a VLAN. Hosts in the same L2 VNI can communicate at Layer 2. The VNI is included in RT-2 MAC/IP routes so remote VTEPs know which VXLAN tunnel to use for a given MAC.

**L3 VNI (Layer 3 VNI):** Maps to a VRF. Used for inter-subnet routing in the symmetric IRB model. When traffic between subnets is forwarded from a leaf (ingress VTEP) to another leaf (egress VTEP), the packet is first routed into the L3 VNI on the ingress leaf, encapsulated in VXLAN with the L3 VNI, and decapsulated at the egress leaf which then routes it into the correct L2 VNI for the destination subnet.

### Underlay Network Requirements

The underlay carries VXLAN UDP packets between VTEPs. Requirements:
- **Routed fabric:** All spine and leaf interconnects are routed (Layer 3) — each leaf has a unique loopback used as VTEP IP.
- **ECMP:** Spine-leaf topology provides multiple equal-cost paths; VXLAN over UDP uses UDP source port randomisation (from inner flow hash) to spread flows across all paths.
- **MTU ≥ 1550:** To accommodate VXLAN overhead on top of standard 1500-byte tenant frames.
- **Multicast or ingress replication for BUM:** EVPN-VXLAN with RT-3 IMET routes uses head-end replication (ingress VTEP sends BUM to each remote VTEP individually) — simpler than multicast and the standard for EVPN deployments.

### Symmetric IRB — Distributed Anycast Gateway

In the **symmetric IRB** model:
- Each leaf has an **IRB (Integrated Routing and Bridging)** interface for every subnet: a virtual gateway interface.
- All leaves share the same **anycast gateway IP** and **anycast MAC** for each subnet — every leaf appears as the same gateway to VMs.
- VM's ARP for the default gateway (e.g., 10.0.1.1) is answered locally by the leaf — no ARP floods the backbone.

Inter-subnet routing:
1. VM sends frame to anycast gateway MAC.
2. Ingress leaf routes the packet — looks up destination IP in VRF routing table.
3. Finds egress leaf as next-hop (via RT-5 IP prefix route or RT-2 MAC/IP route).
4. Encapsulates in VXLAN using the **L3 VNI** (not the source L2 VNI).
5. Egress leaf decapsulates, looks up destination MAC in the destination L2 VNI.
6. Delivers to destination VM.

Symmetric: both leaves perform routing (ingress routes into L3 VNI; egress routes out of L3 VNI). Each leaf must have the L3 VNI for any VRF it participates in.

=== "Cisco Nexus NX-OS"

    ```
    ! Enable features
    feature nv overlay
    feature vn-segment-vlan-based
    feature bgp

    ! VLAN to VNI mapping
    vlan 100
     vn-segment 10100    ! L2 VNI
    vlan 3967
     vn-segment 99999    ! L3 VNI (per VRF)

    ! VRF and L3 VNI
    vrf context TENANT-A
     vni 99999
     rd auto
     address-family ipv4 unicast
      route-target both auto evpn

    ! Anycast gateway
    interface Vlan100
     vrf member TENANT-A
     ip address 10.0.1.1/24
     fabric forwarding mode anycast-gateway

    ! NVE (VTEP) interface
    interface nve1
     no shutdown
     source-interface loopback0
     host-reachability protocol bgp
     member vni 10100
      ingress-replication protocol bgp
     member vni 99999 associate-vrf

    ! BGP EVPN
    router bgp 65001
     router-id 1.1.1.1
     neighbor 10.0.0.1 remote-as 65001
     neighbor 10.0.0.1 update-source loopback0
     address-family l2vpn evpn
      neighbor 10.0.0.1 activate
      neighbor 10.0.0.1 send-community extended

    ! Verification
    show nve peers
    show bgp l2vpn evpn
    show mac address-table
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/dcn/nx-os/nexus9000/103x/configuration/vxlan/cisco-nexus-9000-series-nx-os-vxlan-configuration-guide-103x.html](https://www.cisco.com/c/en/us/td/docs/dcn/nx-os/nexus9000/103x/configuration/vxlan/cisco-nexus-9000-series-nx-os-vxlan-configuration-guide-103x.html)

=== "Arista EOS"

    ```
    ! VLAN to VNI mapping
    vlan 100
    !
    interface Vxlan1
       vxlan source-interface Loopback0
       vxlan udp-port 4789
       vxlan vlan 100 vni 10100
       vxlan vrf TENANT-A vni 99999

    ! Anycast gateway
    ip virtual-router mac-address 00:1c:73:00:00:01    ! shared anycast MAC
    interface Vlan100
       vrf TENANT-A
       ip address virtual 10.0.1.1/24

    ! VRF
    vrf instance TENANT-A
    ip routing vrf TENANT-A

    ! BGP EVPN
    router bgp 65001
       router-id 1.1.1.1
       neighbor SPINES peer group
       neighbor SPINES remote-as 65000
       neighbor 10.0.0.1 peer group SPINES
       !
       address-family evpn
          neighbor SPINES activate
       !
       vlan 100
          rd 65001:10100
          route-target both 65001:10100
          redistribute learned
       !
       vrf TENANT-A
          rd 65001:99999
          route-target import evpn 65001:99999
          route-target export evpn 65001:99999

    ! Verification
    show vxlan vtep
    show bgp evpn
    show mac address-table
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-vxlan-and-evpn](https://www.arista.com/en/um-eos/eos-vxlan-and-evpn)

### Spine Role in EVPN-VXLAN

In a BGP-based EVPN-VXLAN fabric, spines act as **BGP Route Reflectors** (not VTEPs). Spines reflect EVPN routes (RT-2, RT-3, RT-5) between leaf VTEPs. Spines do not encapsulate/decapsulate VXLAN — all VXLAN tunnels are leaf-to-leaf. This keeps spines simple (pure L3 IP forwarding + BGP RR) and puts the service intelligence at the leaf.

### BUM Traffic Handling

EVPN-VXLAN uses **head-end replication** for BUM:
- Each VTEP maintains a BUM replication list (from RT-3 IMET routes).
- When a BUM frame arrives, the ingress VTEP sends a separate copy to each VTEP in the replication list.
- No multicast required in the underlay — simplifies underlay design.

ARP suppression (from EVPN RT-2 MAC/IP routes) dramatically reduces the BUM load — most "broadcast" traffic in practice is ARP, which is eliminated.

---

## Common Pitfalls

1. **Underlay MTU not increased.** VXLAN adds 50 bytes overhead. If underlay links have MTU 1500, a 1500-byte tenant frame becomes 1550 bytes and is fragmented or dropped. Set underlay link MTU to at least 1550 (preferably 9216 for jumbo frame support). Also set MTU on server-facing ports and tenant VLANs.

2. **Anycast gateway MAC not consistent.** All leaf switches acting as the distributed gateway for a subnet must use the same anycast MAC address for the IRB interface. A mismatch causes VMs to receive different ARP replies when their default gateway moves — ARP cache inconsistency, traffic disruption. Configure the virtual MAC globally (not per-interface) and verify it's identical across all leaves.

3. **L3 VNI missing or mismatched.** In symmetric IRB, the L3 VNI must be provisioned on every leaf participating in the same VRF — even leaves with no hosts in that VRF (they need it for transit). A leaf missing the L3 VNI cannot decapsulate inter-subnet VXLAN traffic for that VRF. Verify NVE config and VRF VNI binding on all leaves.

4. **BGP next-hop not reachable in underlay.** EVPN RT-2 routes use the VTEP loopback as the BGP next-hop. If the loopback is not reachable in the underlay IGP (or eBGP underlay), VXLAN tunnels cannot be established — the route is received but the next-hop is unresolvable. Verify `ping source Loopback0` between all leaf pairs.

5. **Missing `send-community extended` on spine BGP config.** Spines acting as Route Reflectors must be configured with `send-community extended` toward leaves. Without it, RT communities are stripped when reflecting routes — leaves receive EVPN routes with no RT and import nothing. This is a common silent failure.

---

## Practice Problems

**Q1.** Why does EVPN-VXLAN use L3 VNIs separate from L2 VNIs for inter-subnet routing?

??? answer
    L2 VNIs identify broadcast domains (VLANs). A packet in L2 VNI 10100 stays in that broadcast domain — it's bridged, not routed. When traffic must cross between subnets (e.g., L2 VNI 10100 = 10.0.1.0/24 and L2 VNI 10200 = 10.0.2.0/24), the ingress leaf routes the packet, then needs to encapsulate it in a VXLAN tunnel that identifies the tenant routing context — not the destination subnet. The L3 VNI identifies the VRF (tenant routing domain). The egress leaf receives a VXLAN packet with L3 VNI, looks up the destination IP in the associated VRF, and delivers to the correct L2 VNI for the destination subnet. Separating L2 and L3 VNIs is what enables distributed routing without the egress leaf needing to know every L2 VNI of the ingress leaf's subnets.

**Q2.** What is the role of the spine in an EVPN-VXLAN fabric?

??? answer
    In a standard EVPN-VXLAN fabric, spines serve as **BGP Route Reflectors** — they receive EVPN routes (RT-2, RT-3, RT-5) from each leaf and reflect them to all other leaves. Spines are not VTEPs — they do not encapsulate or decapsulate VXLAN traffic. All VXLAN tunnels are direct leaf-to-leaf (VTEP-to-VTEP). The spine only forwards IP packets using the underlay routing table. This design keeps spine hardware simple (no overlay state), scales to large fabrics, and makes the overlay control plane independent of the underlay forwarding.

**Q3.** How does the anycast gateway prevent ARP floods when a VM sends an ARP request for its default gateway?

??? answer
    Every leaf switch has an IRB interface for each subnet with the same IP address (e.g., 10.0.1.1/24) and the same anycast MAC address (e.g., 00:1c:73:00:00:01). When a VM sends an ARP request for 10.0.1.1, the request is received by the local leaf — which immediately responds because it is 10.0.1.1 (locally configured). The ARP request never enters the VXLAN tunnel or reaches any other leaf. The VM's ARP cache is populated with the anycast MAC, which is the same on every leaf — so if the VM migrates to a different leaf, its ARP cache entry for the gateway remains valid. No ARP re-learning is needed on migration.

---

## Summary & Key Takeaways

- **VXLAN** encapsulates Ethernet frames in UDP — 24-bit VNI supports 16M overlay networks vs 4094 VLANs.
- **EVPN** provides the control plane for VXLAN — BGP RT-2 routes distribute MAC/IP, eliminating flood-and-learn.
- **L2 VNI:** One per VLAN/broadcast domain. **L3 VNI:** One per VRF — used for inter-subnet routing in symmetric IRB.
- **Symmetric IRB:** Both ingress and egress leaves route; uses L3 VNI for inter-subnet VXLAN transit.
- **Anycast gateway:** All leaves share the same gateway IP and MAC per subnet — VMs always reach the nearest leaf as gateway; no traffic tromboning.
- **Spines = BGP Route Reflectors only** — not VTEPs. VXLAN tunnels are leaf-to-leaf.
- **BUM:** Head-end replication from RT-3 IMET routes — no underlay multicast needed.
- ARP suppression (RT-2 MAC/IP) eliminates most BUM traffic.
- Underlay MTU must be ≥ 1550 bytes (or 9216 for jumbo frames).

---

## Where to Next

- **CT-008 — MEF Standards:** Carrier Ethernet service definitions and attributes.
- **CT-006 — EVPN Fundamentals:** EVPN route types and multihoming detail.
- **SEC-006 — Network Segmentation & DMZ:** EVPN micro-segmentation for security zoning.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 7348 | VXLAN: A Framework for Overlaying Virtualised Layer 2 Networks |
| RFC 8365 | A Network Virtualisation Overlay Solution Using EVPN |
| RFC 9135 | Integrated Routing and Bridging in EVPN |
| Cisco CCIE Data Centre | EVPN-VXLAN fabric design |
| Arista ACE | EVPN-VXLAN on EOS |
| Juniper JNCIE-DC | EVPN-VXLAN with Junos |

---

## References

- RFC 7348 — VXLAN. [https://www.rfc-editor.org/rfc/rfc7348](https://www.rfc-editor.org/rfc/rfc7348)
- RFC 8365 — EVPN with Network Virtualisation Overlay. [https://www.rfc-editor.org/rfc/rfc8365](https://www.rfc-editor.org/rfc/rfc8365)
- RFC 9135 — IRB in EVPN. [https://www.rfc-editor.org/rfc/rfc9135](https://www.rfc-editor.org/rfc/rfc9135)

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
| SEC-006 | Network Segmentation & DMZ | EVPN micro-segmentation in data centre |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-006 | EVPN Fundamentals | EVPN control plane used by EVPN-VXLAN |
| SW-002 | VLANs & 802.1Q Trunking | VLAN-to-VNI mapping |
<!-- XREF-END -->
