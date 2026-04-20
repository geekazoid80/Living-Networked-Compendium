---
id: CT-003
title: "MPLS L2VPN — VPLS & Pseudowire"
description: "How MPLS Layer 2 VPN services (pseudowires and VPLS) deliver point-to-point and multipoint Ethernet connectivity over an MPLS backbone."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - CT-001
  - CT-002
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - mpls
  - l2vpn
  - vpls
  - pseudowire
  - ethernet
  - carrier
  - vfi
created: 2026-04-19
updated: 2026-04-19
---

# CT-003 — MPLS L2VPN — VPLS & Pseudowire

## The Problem

L3VPN (CT-002) delivers IP routing services — the provider terminates the customer's IP, participates in their routing, and forwards IP packets. But some customers need something different: they want their remote sites to behave as if they're on the *same Ethernet network* — the same broadcast domain. Their servers use ARP, DHCP broadcast, and Layer 2 clustering protocols that don't survive IP routing. They want a wire, not a router.

Can the MPLS backbone carry Layer 2 Ethernet frames transparently between two sites — as if a physical cable connected them?

### Step 1: Tunnel Ethernet frames point-to-point

Two PE routers are connected to one customer site each. The ingress PE takes an incoming Ethernet frame, wraps it in MPLS labels, and sends it across the backbone to the egress PE. The egress PE strips the labels and delivers the original frame to the remote CE — as if it came off a local interface. This is a **pseudowire** (also called an EoMPLS — Ethernet over MPLS): a point-to-point Layer 2 tunnel over MPLS.

### Step 2: Connect multiple sites — full mesh

A customer has six sites. They want all sites on the same Ethernet broadcast domain. Point-to-point pseudowires would require 15 pseudowires (n×(n-1)/2). Instead, each PE maintains a **MAC address table** per VPN service and forwards frames only to the PE where the destination MAC was learned. PEs signal MAC reachability to each other. Unknown unicast and broadcasts are flooded to all PEs in the VPN. This is **VPLS** (Virtual Private LAN Service): a multipoint Layer 2 VPN where the MPLS backbone emulates a virtual Ethernet switch connecting all sites.

### Step 3: Avoid loops in a mesh topology

With multiple PEs in a full mesh, every PE has a pseudowire to every other PE. A broadcast frame from CE1 arrives at PE1, which floods it to PE2 and PE3. PE2 receives it and floods to PE1 and PE3. PE3 receives from PE2 and floods back — a loop. VPLS uses a **split-horizon** rule: a PE never forwards a frame received from a pseudowire (from another PE) back out another pseudowire. Frames received from a CE can go to pseudowires; frames from a pseudowire go only to CEs.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Point-to-point Ethernet tunnel over MPLS | Pseudowire / EoMPLS |
| MPLS-encapsulated Ethernet frame | MPLS pseudowire PDU |
| Multipoint Layer 2 VPN across MPLS | VPLS (Virtual Private LAN Service) |
| Per-VPN logical switch on the PE | VFI (Virtual Forwarding Instance) |
| Rule preventing L2 loops in mesh | Split-horizon forwarding |
| MAC learning in VPLS | Data-plane MAC learning |
| H-VPLS hub PE | U-PE (user-facing) / N-PE (network-facing) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain pseudowire architecture — signalling, encapsulation, and use cases.
2. Describe VPLS architecture — VFI, MAC learning, flooding, split-horizon.
3. Explain LDP-based pseudowire signalling (martini draft) and BGP-based VPLS.
4. Describe Hierarchical VPLS (H-VPLS) and why it reduces PE state.
5. Explain the limitations of VPLS that motivated EVPN.
6. Configure basic pseudowire and VPLS on a PE router.

---

## Prerequisites

- CT-001 — MPLS Fundamentals (label switching, LDP)
- CT-002 — MPLS VPNs (L3VPN) (VRF and MP-BGP context)

---

## Core Content

### Pseudowire — Point-to-Point L2 Tunnel

A pseudowire emulates a point-to-point Layer 2 circuit. The most common type: Ethernet pseudowire (EoMPLS). Also available: Frame Relay, ATM, TDM (for legacy migration).

Pseudowire uses a two-label stack:
- **Outer label (transport):** LSP label, switched by P routers.
- **Inner label (VC label / pseudowire label):** Identifies the specific pseudowire on the egress PE.

Signalling: the VC label is negotiated between PE pairs using **LDP** (targeted LDP sessions — not link-local) or **BGP L2VPN** (BGP EVPN address family, covered in CT-006).

```
CE-A ─── [PE1] ─────── P1 ─────── P2 ─────── [PE2] ─── CE-B
           │  [outer][VC][Eth Frame]               │
           LDP T-LDP session to PE2 ───────────────┘
```

=== "Cisco IOS-XE"

    ```
    ! Pseudowire class (EoMPLS)
    pseudowire-class EoMPLS
     encapsulation mpls
     interworking none

    ! Interface assigned to pseudowire
    interface GigabitEthernet0/1
     no ip address
     xconnect 2.2.2.2 100 encapsulation mpls
     ! 2.2.2.2 = far-end PE loopback; 100 = VC ID (must match both ends)
    
    ! Verification
    show xconnect all
    show mpls l2transport vc
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l2_vpns/configuration/xe-17/mp-l2-vpns-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_l2_vpns/configuration/xe-17/mp-l2-vpns-xe-17-book.html)

=== "Juniper Junos"

    ```
    # Layer 2 circuit (pseudowire) using LDP
    set protocols l2circuit neighbor 2.2.2.2 interface ge-0/0/1.0 virtual-circuit-id 100

    # Interface configuration
    set interfaces ge-0/0/1 unit 0 encapsulation ethernet-ccc
    set interfaces ge-0/0/1 unit 0 family ccc

    # Verification
    show l2circuit connections
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/l2-circuit-config.html](https://www.juniper.net/documentation/us/en/software/junos/mpls/topics/topic-map/l2-circuit-config.html)

=== "Nokia SR-OS"

    ```
    # Spoke-SDP pseudowire
    configure service epipe 100 customer 1 create
        description "Pseudowire PE1 to PE2"
        endpoint "to-CE" create
        exit
        sap 1/1/1:100 create
        exit
        spoke-sdp 1:100 create
        exit
        no shutdown
    exit
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-l2-services-dataplane/epipe-service.html](https://documentation.nokia.com/sr/23-10/books/sr-l2-services-dataplane/epipe-service.html)

### VPLS — Multipoint Layer 2 VPN

VPLS creates a **VFI (Virtual Forwarding Instance)** on each PE — a logical Ethernet switch with:
- A MAC address table (learned from incoming frames).
- Attachment circuits (AC): CE-facing interfaces.
- Pseudowires: PE-to-PE tunnels for each remote site.

VPLS forwarding logic:
1. Frame arrives from CE on an AC.
2. PE looks up destination MAC in VFI MAC table.
3. If found → forward out the learned pseudowire (or AC).
4. If not found (unknown unicast) or broadcast/multicast → flood to all ACs and all pseudowires (except split-horizon: not to PW if frame came from a PW).

=== "Cisco IOS-XE"

    ```
    ! VPLS using LDP signalling
    l2 vfi VPLS-CUST-A manual
     vpn id 100
     neighbor 2.2.2.2 encapsulation mpls
     neighbor 3.3.3.3 encapsulation mpls

    ! Attach CE-facing interface to VFI
    interface GigabitEthernet0/1
     service instance 100 ethernet
      encapsulation untagged
      bridge-domain 100
     !
    
    ! Bridge domain ties interface to VFI
    bridge-domain 100
     member GigabitEthernet0/1 service-instance 100
     member vfi VPLS-CUST-A

    ! Verification
    show l2vpn vfi
    show mac address-table vfi
    ```

=== "Juniper Junos"

    ```
    # VPLS instance with BGP signalling
    set routing-instances VPLS-CUST-A instance-type vpls
    set routing-instances VPLS-CUST-A interface ge-0/0/1.0
    set routing-instances VPLS-CUST-A route-distinguisher 65001:200
    set routing-instances VPLS-CUST-A vrf-target target:65001:200
    set routing-instances VPLS-CUST-A protocols vpls site CE-A site-identifier 1
    set routing-instances VPLS-CUST-A protocols vpls site CE-A interface ge-0/0/1.0

    # Verification
    show vpls connections
    show vpls mac-table
    ```

=== "Nokia SR-OS"

    ```
    # VPLS service
    configure service vpls 200 customer 1 create
        description "VPLS Customer A"
        stp shutdown
        sap 1/1/1:200 create
        exit
        mesh-sdp 1:200 create
        exit
        mesh-sdp 2:200 create
        exit
        no shutdown
    exit
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-10/books/sr-l2-services-dataplane/vpls-service.html](https://documentation.nokia.com/sr/23-10/books/sr-l2-services-dataplane/vpls-service.html)

### VPLS Signalling — LDP vs BGP

| Method | Details |
|---|---|
| LDP (Martini / RFC 4762) | Targeted LDP sessions between all PE pairs; VFI configured manually listing all PEs; O(n²) sessions |
| BGP (Kompella / RFC 4761) | BGP L2VPN address family; BGP auto-discovers PEs and assigns VC labels; scales better than LDP |

BGP-based VPLS uses the same MP-BGP infrastructure as L3VPN — the same Route Reflectors can distribute both VPNv4 and L2VPN routes.

### Hierarchical VPLS (H-VPLS)

Standard VPLS requires every PE to maintain full-mesh pseudowires and MAC state for every VPLS instance. This scales poorly for access networks with many small sites.

H-VPLS introduces two tiers:
- **U-PE (User-facing PE):** Access PE. Connects to CEs via a single spoke pseudowire to the N-PE. Does not participate in the full mesh. Minimal state.
- **N-PE (Network-facing PE):** Core PE. Participates in the full-mesh VPLS. Receives all MAC state. Forwards between sites.

U-PEs are simple boxes; MAC learning and VPLS state is concentrated in the N-PEs.

### VPLS Limitations — Why EVPN Was Needed

VPLS has several limitations that motivated EVPN (CT-006):
1. **Flooding for unknown unicast:** Unknown destination MACs are flooded to all PEs in the VPLS, consuming bandwidth on all pseudowires — even to PEs with no matching CE.
2. **No multihoming:** A CE cannot connect to two PEs simultaneously for redundancy without running STP — STP blocks one link, wasting capacity.
3. **MAC/IP decoupling:** VPLS carries only MAC addresses; IP bindings (for ARP suppression or host mobility) are not distributed.
4. **Slow MAC withdrawal:** When a CE moves or fails, stale MACs age out or require explicit MAC withdrawal messages — convergence can be slow.

EVPN (RFC 7432) solves all four with a BGP control plane for MAC/IP advertisement, integrated multihoming (EVPN Ethernet Segment), and ARP/ND suppression.

---

## Common Pitfalls

1. **VC ID mismatch between PE pairs.** The pseudowire VC ID (circuit ID) must match on both ends. If PE1 uses VC ID 100 and PE2 uses VC ID 101, the targeted LDP session negotiates the label but the connection is rejected — the VC stays down. Always verify VC IDs are symmetric.

2. **Split-horizon not implemented.** A custom VPLS implementation or misconfiguration that forwards frames between pseudowires creates broadcast storms and forwarding loops. VPLS split-horizon is not optional — it is required for loop-free operation. Verify it is enabled (most implementations enforce it automatically).

3. **MTU mismatch on pseudowire.** MPLS adds at least 8 bytes (two 4-byte labels) to each frame. If the CE sends 1500-byte Ethernet frames and the backbone MTU is 1508 or less (not accounting for MPLS overhead), frames are silently dropped or fragmented. Configure MTU on PE-to-PE links to at least 1508 (for two labels) or 1512 (for padding). Also match AC MTU — pseudowire negotiation may reject mismatched MTUs.

4. **VPLS state scaling.** Each VFI on a PE stores one MAC entry per active host in that VPLS instance. A PE with 1000 VPLS instances each with 100 MACs holds 100,000 MAC entries. This can exhaust TCAM on platforms with limited hardware tables. Use H-VPLS to concentrate MAC state, or migrate to EVPN.

5. **STP interaction.** If the CE runs STP (or RSTP) across pseudowires, STP BPDUs are forwarded transparently. The VPLS backbone appears as a shared broadcast segment to STP — this can cause unexpected topology changes and port blocking. Most implementations tunnel STP BPDUs (provider bridge mode) or use BPDU filtering on CE-facing ACs.

---

## Practice Problems

**Q1.** What is the difference between a pseudowire (EoMPLS) and VPLS?

??? answer
    A pseudowire is **point-to-point** — it connects exactly two CE sites by tunnelling Layer 2 frames between two PE routers. It is the Ethernet equivalent of a leased line. VPLS is **multipoint** — it connects N CE sites in a single Ethernet broadcast domain using a mesh of pseudowires between PE routers, combined with MAC learning and split-horizon forwarding. VPLS is the Ethernet equivalent of a shared LAN switch. For two-site connections, a pseudowire is simpler and uses fewer resources. For three or more sites needing a shared broadcast domain, VPLS is the appropriate service.

**Q2.** Why does VPLS use split-horizon forwarding, and what problem does it prevent?

??? answer
    VPLS creates a full mesh of pseudowires between PEs. Without split-horizon, a broadcast or unknown unicast frame from CE-A received at PE1 would be flooded to PE2 and PE3. PE2 would forward to PE3, PE3 would forward back to PE1, PE1 back to PE2, and so on — an infinite broadcast loop. Split-horizon prevents this by prohibiting a PE from forwarding a frame received on a pseudowire out another pseudowire. Frames from a pseudowire (PE-to-PE) may only exit on CE-facing attachment circuits. This eliminates loops without running STP in the backbone.

**Q3.** A VPLS service is working, but hosts at two sites experience intermittent communication failures that resolve after 5-10 minutes. What might be the cause?

??? answer
    This is a MAC mobility / stale MAC issue. When a host moves from one site to another (or a CE device fails and MAC entries must be repopulated), the old MAC-to-pseudowire mapping remains in the VPLS MAC table until it ages out (typically 5 minutes). Traffic destined to the moved host is forwarded to the wrong PE, then dropped. The fix is faster MAC aging for the specific VFI, or configuring MAC withdrawal (where the PE explicitly removes stale MAC entries when a CE link goes down). This is one of the motivations for moving from VPLS to EVPN, which uses BGP MAC/IP advertisements with explicit MAC withdraw on link failure.

---

## Summary & Key Takeaways

- **Pseudowire (EoMPLS):** Point-to-point Layer 2 tunnel over MPLS — two-label stack (outer transport + inner VC label).
- **VPLS:** Multipoint Layer 2 VPN — VFI acts as a virtual Ethernet switch; MAC learning in data plane; flood-and-learn for unknown destinations.
- **Split-horizon:** Prevents broadcast loops in the PE mesh — frames from a PW never exit another PW.
- VPLS signalling: LDP (manual full-mesh) or BGP (auto-discovery, scales better).
- **H-VPLS:** Hierarchical model — U-PEs (access, spoke PW) offload state from N-PEs (core, full mesh).
- VPLS limitations: flooding, no native multihoming, slow MAC withdrawal — EVPN solves these.
- MTU: backbone links must support at least 1508 bytes (1500 + two 4-byte MPLS labels).

---

## Where to Next

- **CT-004 — Segment Routing SR-MPLS:** SR replaces LDP for pseudowire and VPLS transport.
- **CT-006 — EVPN Fundamentals:** Modern replacement for VPLS with BGP-based MAC/IP control plane.
- **CT-007 — EVPN-VXLAN:** EVPN extended to VXLAN data centres.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 4448 | Encapsulation Methods for Transport of Ethernet over MPLS (PWE3) |
| RFC 4762 | VPLS Using LDP Signalling |
| RFC 4761 | VPLS Using BGP |
| MEF 6.3 | Ethernet Virtual Connection (EVC) services |
| Cisco CCIE Service Provider | Pseudowire, VPLS, H-VPLS |
| Juniper JNCIE-SP | L2VPN, VPLS |

---

## References

- RFC 4448 — Ethernet over MPLS. [https://www.rfc-editor.org/rfc/rfc4448](https://www.rfc-editor.org/rfc/rfc4448)
- RFC 4762 — VPLS Using LDP. [https://www.rfc-editor.org/rfc/rfc4762](https://www.rfc-editor.org/rfc/rfc4762)
- RFC 4761 — VPLS Using BGP. [https://www.rfc-editor.org/rfc/rfc4761](https://www.rfc-editor.org/rfc/rfc4761)

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
| CT-004 | Segment Routing SR-MPLS | SR replaces LDP for pseudowire/VPLS transport |
| CT-006 | EVPN Fundamentals | EVPN is modern replacement for VPLS |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-001 | MPLS Fundamentals | Label switching and LDP as transport |
| CT-002 | MPLS VPNs — L3VPN | L3VPN context; BGP infrastructure shared |
<!-- XREF-END -->
