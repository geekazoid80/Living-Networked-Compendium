---
id: SW-002
title: "VLANs & 802.1Q Trunking"
description: "How switches segment broadcast domains with VLANs and carry multiple VLANs across shared links using 802.1Q tagging."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - SW-001
  - NW-002
learning_path_tags:
  - DNE
  - CE
difficulty: intermediate
tags:
  - switching
  - vlan
  - 802.1q
  - trunking
  - layer2
created: 2026-04-19
updated: 2026-04-19
---

# SW-002 — VLANs & 802.1Q Trunking

## The Problem

Two switches, each with twenty ports. Twenty computers — accounting on the left, engineering on the right. Every broadcast one accountant sends floods to every engineer, and vice versa. IT has decided these teams must not share a broadcast domain. You can't buy more switches right now.

### Step 1: What if we could label traffic?

You stamp every frame from accounting with an "A" and every frame from engineering with an "E." Switches only forward frames to ports carrying the same label. One physical switch, two isolated logical networks. You have just invented the **VLAN (Virtual LAN)** — a logical broadcast domain bounded by a label, not a physical port count.

### Step 2: The uplink problem

Two switches connected by one cable. Switch 1 has VLAN 10 (accounting) and VLAN 20 (engineering). Switch 2 has the same. You want accounting traffic to reach accounting across the uplink, and engineering to reach engineering — but you only have one wire between the switches.

Naive approach: run two cables, one per VLAN. Works, but doesn't scale — 10 VLANs means 10 cables.

Better: use the same wire for all VLANs but tag every frame before it crosses the link. The receiving switch reads the tag, knows which VLAN the frame belongs to, strips the tag, and delivers it to the right ports. You have just invented **trunking** — a link that carries multiple VLANs simultaneously. The tag format is **IEEE 802.1Q**.

### Step 3: What about frames with no tag?

Legacy devices and management interfaces often send untagged frames. The switch needs somewhere to put them. One VLAN is designated the **native VLAN** — untagged frames on a trunk are assumed to belong to it. Both ends of the trunk must agree on which VLAN is native; a mismatch causes VLAN leakage.

### Step 4: The default case

A simple access device — a printer, a desktop — should not need to know about VLANs. The switch port it connects to is configured as an **access port**: frames arrive untagged, the switch assigns them to a specific VLAN, and they leave untagged on the other side. The device never sees 802.1Q.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Logical broadcast domain on one switch | VLAN |
| Label carried in the Ethernet frame | 802.1Q VLAN tag |
| Link carrying multiple VLANs | Trunk port |
| VLAN receiving untagged frames on a trunk | Native VLAN |
| Port that adds/strips tags for end devices | Access port |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain what a VLAN is and how it limits broadcast scope.
2. Describe the 802.1Q frame structure and the fields in the VLAN tag.
3. Distinguish access ports from trunk ports and configure each correctly.
4. Identify the risks of native VLAN misconfiguration.
5. Trace a frame's journey from access port → trunk → access port across two switches.
6. Configure VLANs and trunks on at least two vendor platforms.

---

## Prerequisites

- SW-001 — Switching Fundamentals (MAC learning, flooding, broadcast domains)
- NW-002 — Network Topologies (broadcast domains, collision domains)

---

## Core Content

### What Is a VLAN?

A **VLAN (Virtual Local Area Network)** is a logical partition of a switch's broadcast domain. Frames tagged with VLAN ID 10 are invisible to ports assigned to VLAN 20. From a Layer 3 perspective each VLAN is a separate subnet — traffic between VLANs requires a router or Layer 3 switch.

Key properties:

- A VLAN is identified by a **12-bit VLAN ID** (VID), range 1–4094.
- VLAN 1 is the default VLAN on most platforms — all ports belong to it unless reconfigured.
- VLANs 1002–1005 are reserved on Cisco IOS for legacy (Token Ring / FDDI) and cannot be deleted.
- VLANs 1006–4094 are the **extended VLAN** range (requires VTP transparent mode or VTP version 3 on Cisco; most modern platforms support extended range natively).

??? supplementary "Why Not Just Buy More Switches?"
    Adding physical switches per department solves the broadcast problem but creates operational sprawl: more hardware, more power, more cabling, more management interfaces. VLANs let one switch serve many departments — especially valuable in multi-tenant environments, campus deployments, and any site where the number of logical segments exceeds the budget for physical switches.

### 802.1Q Frame Structure

IEEE 802.1Q inserts a **4-byte tag** between the Source MAC address and the EtherType field of a standard Ethernet frame.

```
Standard Ethernet frame:
 +-----------+-----------+-------+-------+------+-----+
 | Dst MAC   | Src MAC   | EType | ...   | Data | FCS |
 +-----------+-----------+-------+-------+------+-----+

802.1Q tagged frame:
 +-----------+-----------+-------+------+-------+------+-----+
 | Dst MAC   | Src MAC   | TPID  | TCI  | EType | Data | FCS |
 +-----------+-----------+-------+------+-------+------+-----+
                           <---4-byte tag--->
```

Tag fields:

| Field | Bits | Value | Purpose |
|---|---|---|---|
| TPID (Tag Protocol ID) | 16 | 0x8100 | Identifies the frame as 802.1Q tagged |
| PCP (Priority Code Point) | 3 | 0–7 | 802.1p CoS priority (0=lowest, 7=highest) |
| DEI (Drop Eligible Indicator) | 1 | 0 or 1 | Frame may be dropped under congestion |
| VID (VLAN ID) | 12 | 1–4094 | Which VLAN the frame belongs to |

??? supplementary "QinQ / 802.1ad — Double Tagging"
    Service providers sometimes need to carry customer 802.1Q traffic inside their own 802.1Q domain without consuming customer VLAN IDs. **IEEE 802.1ad (QinQ)** adds a second tag (TPID = 0x88A8, called the S-Tag or outer tag) on top of the customer tag (C-Tag). The provider network sees only the outer VLAN ID; the inner customer VID is transported transparently. This is foundational to MEF Carrier Ethernet E-Line and E-LAN services — see CT-008.

### Access Ports

An **access port** connects a single end device and belongs to exactly one VLAN. The switch:

1. Receives an untagged frame from the device.
2. Associates it with the port's access VLAN.
3. Forwards it (tagged internally) within that VLAN.
4. Strips the tag before delivering to another access port in the same VLAN.

The end device is VLAN-unaware — it sends and receives standard Ethernet frames.

Voice VLAN: many switches support a secondary "voice VLAN" on access ports, allowing an IP phone to share the port with a PC. The phone sends 802.1Q-tagged frames on the voice VLAN; the PC's traffic goes untagged on the data VLAN. The switch accepts both on one port.

### Trunk Ports

A **trunk port** carries frames for multiple VLANs simultaneously. The switch tags all frames with the appropriate VLAN ID before sending them out the trunk, and reads the tag to associate incoming frames with the correct VLAN.

Key trunk configuration parameters:

- **Allowed VLAN list** — which VLANs are permitted on this trunk. Default: all VLANs (1–4094). Best practice: restrict to only necessary VLANs.
- **Native VLAN** — the VLAN for untagged frames. Default VLAN 1 on most platforms. Both ends must match.

### Native VLAN and VLAN Hopping

The native VLAN is a critical security surface. **VLAN hopping** via double tagging:

1. Attacker sends a double-tagged frame: outer tag = native VLAN (1), inner tag = target VLAN (10).
2. First switch strips the outer tag (it's the native VLAN — untagged on the trunk).
3. Second switch sees the inner tag (VLAN 10) and forwards to VLAN 10 devices.
4. Attacker has injected traffic into VLAN 10 without authorisation.

Mitigation:
- Change the native VLAN to an unused, non-routable VLAN (e.g. VLAN 999).
- Tag the native VLAN explicitly (some platforms: `vlan dot1q tag native`).
- Prune unnecessary VLANs from trunks.
- Place unused ports in a quarantine VLAN and disable them.

??? supplementary "Switch Spoofing — DTP Attack"
    On Cisco IOS, trunk negotiation is performed by **DTP (Dynamic Trunking Protocol)** — a Cisco-proprietary protocol. A malicious device can send DTP frames to negotiate a trunk with the switch, gaining access to all VLANs. Mitigation: disable DTP on all access ports with `switchport nonegotiate` and explicitly set the port mode.

### Inter-VLAN Routing

By definition, VLANs cannot communicate at Layer 2. Traffic between VLANs requires Layer 3 forwarding. Two common approaches:

**Router-on-a-stick (ROAS):** A single physical link from the switch to a router, configured as a trunk. The router uses sub-interfaces, one per VLAN, each with an IP address in the VLAN's subnet. Frames arrive tagged; the router routes between subnets and sends the reply tagged for the destination VLAN.

**Layer 3 switch with SVIs (Switched Virtual Interfaces):** The switch itself performs routing. Each VLAN has an SVI — a virtual routed interface — in the VLAN's subnet. The switch routes internally between VLANs at wire speed using hardware (ASIC/TCAM). Much higher throughput than ROAS for large environments.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Create VLANs
    vlan 10
     name ACCOUNTING
    vlan 20
     name ENGINEERING

    ! Access port
    interface GigabitEthernet0/1
     switchport mode access
     switchport access vlan 10
     switchport nonegotiate

    ! Trunk port
    interface GigabitEthernet0/24
     switchport mode trunk
     switchport trunk encapsulation dot1q
     switchport trunk native vlan 999
     switchport trunk allowed vlan 10,20

    ! Verification
    show vlan brief
    show interfaces trunk
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/vlan/b_173_vlan_9300_cg.html](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/vlan/b_173_vlan_9300_cg.html)

=== "Juniper EX (Junos)"

    ```
    # Create VLANs
    set vlans ACCOUNTING vlan-id 10
    set vlans ENGINEERING vlan-id 20

    # Access port
    set interfaces ge-0/0/1 unit 0 family ethernet-switching interface-mode access
    set interfaces ge-0/0/1 unit 0 family ethernet-switching vlan members ACCOUNTING

    # Trunk port
    set interfaces ge-0/0/23 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/23 unit 0 family ethernet-switching vlan members [ACCOUNTING ENGINEERING]
    set interfaces ge-0/0/23 unit 0 family ethernet-switching native-vlan-id 999

    # Verification
    show vlans
    show ethernet-switching interface
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/multicast-l2/topics/topic-map/vlan-configuring-interfaces.html](https://www.juniper.net/documentation/us/en/software/junos/multicast-l2/topics/topic-map/vlan-configuring-interfaces.html)

=== "Arista EOS"

    ```
    ! Create VLANs
    vlan 10
       name ACCOUNTING
    vlan 20
       name ENGINEERING

    ! Access port
    interface Ethernet1
       switchport mode access
       switchport access vlan 10

    ! Trunk port
    interface Ethernet24
       switchport mode trunk
       switchport trunk native vlan 999
       switchport trunk allowed vlan 10,20

    ! Verification
    show vlan
    show interfaces trunk
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-vlan-configuration](https://www.arista.com/en/um-eos/eos-vlan-configuration)

=== "MikroTik RouterOS"

    ```
    # Create bridge for VLAN-aware switching
    /interface bridge
    add name=bridge1 vlan-filtering=yes

    # Add ports to bridge
    /interface bridge port
    add bridge=bridge1 interface=ether1 pvid=10   # access port, VLAN 10
    add bridge=bridge1 interface=ether24 pvid=1   # trunk port

    # Configure VLANs on bridge
    /interface bridge vlan
    add bridge=bridge1 tagged=ether24 untagged=ether1 vlan-ids=10
    add bridge=bridge1 tagged=ether24 vlan-ids=20

    # Verification
    /interface bridge vlan print
    /interface bridge host print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/Bridging+and+Switching](https://help.mikrotik.com/docs/display/ROS/Bridging+and+Switching)

---

## Common Pitfalls

1. **Native VLAN mismatch.** If one end of a trunk has native VLAN 1 and the other has native VLAN 999, untagged traffic enters VLAN 1 on one side and VLAN 999 on the other — silent misdelivery, no error message. Always verify both ends match with `show interfaces trunk` / `show vlans`.

2. **Forgetting to allow VLANs on the trunk.** Creating a VLAN and assigning ports to it is not enough — the VLAN must also be allowed on every trunk it needs to traverse. New VLANs added to a switch but not added to trunk allowed lists will silently fail to pass traffic.

3. **Leaving DTP enabled on access ports (Cisco).** An attacker or misconfigured device can negotiate a trunk. Always `switchport nonegotiate` on access ports.

4. **Using VLAN 1 as the native VLAN.** VLAN 1 is the default management VLAN on many platforms. Using it as the native VLAN conflates management traffic with the untagged trunking loophole. Move native VLAN to an unused ID.

5. **Forgetting that routing between VLANs requires Layer 3.** A common beginner error: configuring VLANs on a switch and expecting devices in different VLANs to communicate without a Layer 3 device (router, SVI, or L3 switch). L2 VLANs are isolated by design.

---

## Practice Problems

**Q1.** A switch port is configured as an access port in VLAN 10. A PC sends a broadcast. Which devices receive the frame?

??? answer
    Only devices whose switch ports are in VLAN 10 on the same switch, plus devices in VLAN 10 on switches connected via trunks that allow VLAN 10. Devices in VLAN 20 or any other VLAN do not receive the broadcast.

**Q2.** An 802.1Q frame arrives on a trunk port. The VID field contains 0x000 (zero). What does the switch do?

??? answer
    A VID of 0 means the frame carries priority information (PCP) but no VLAN assignment — it is treated as belonging to the native VLAN of the trunk port.

**Q3.** You create VLAN 30 on Switch A. You add an access port to VLAN 30. You connect Switch A to Switch B via a trunk, but forget to add VLAN 30 to the trunk's allowed list. What happens to VLAN 30 traffic destined for Switch B?

??? answer
    It is dropped at the trunk port. The trunk only forwards VLANs in its allowed list. VLAN 30 traffic never reaches Switch B, silently.

**Q4.** What is the double-tagging VLAN hopping attack and what assumption does it exploit?

??? answer
    The attacker crafts a frame with two 802.1Q tags: the outer tag matches the native VLAN, the inner tag targets a victim VLAN. The first switch strips the outer tag (treating the frame as native VLAN, untagged on the trunk). The second switch reads the now-exposed inner tag and forwards to the victim VLAN. The attack exploits the assumption that native VLAN frames are untagged — so the inner tag survives the first hop.

**Q5.** A router-on-a-stick has a sub-interface `GigabitEthernet0/0.10` with IP `192.168.10.1/24` and a sub-interface `.20` with `192.168.20.1/24`. A host in VLAN 10 wants to ping a host in VLAN 20. Describe the Layer 2 and Layer 3 steps.

??? answer
    1. Host (VLAN 10) sends IP packet to its default gateway (192.168.10.1) — frame tagged VLAN 10.
    2. Switch delivers the frame (tagged VLAN 10) out the trunk to the router.
    3. Router's sub-interface .10 receives the frame, strips the 802.1Q tag, processes the IP packet.
    4. Router performs a routing lookup: destination 192.168.20.x → sub-interface .20.
    5. Router encapsulates the packet in a new Ethernet frame, tags it VLAN 20, sends out the trunk.
    6. Switch receives the VLAN 20-tagged frame and delivers to the destination access port.

---

## Lab

**Objective:** Configure VLANs and a trunk between two simulated switches; verify that hosts in the same VLAN communicate and hosts in different VLANs do not (without a router).

**Topology:**
```
PC-A (VLAN 10) --- [SW1] --- trunk --- [SW2] --- PC-B (VLAN 10)
PC-C (VLAN 20) --- [SW1]               [SW2] --- PC-D (VLAN 20)
```

**Steps:**
1. Create VLAN 10 and VLAN 20 on both switches.
2. Assign PC-A and PC-B's ports as access VLAN 10; PC-C and PC-D as access VLAN 20.
3. Configure the inter-switch link as a trunk, native VLAN 999, allowed VLANs 10 and 20.
4. Verify: PC-A can ping PC-B (VLAN 10 → VLAN 10 across trunk). PC-A cannot ping PC-C or PC-D (different VLANs, no router).
5. Capture traffic on the trunk and observe 802.1Q tags.

**Extension:** Add a router-on-a-stick. Configure sub-interfaces for VLAN 10 and VLAN 20. Verify PC-A can now ping PC-C via the router. Observe the frame flow: tagged out access → trunk → router → trunk back → access destination.

---

## Summary & Key Takeaways

- A **VLAN** is a logical broadcast domain — one switch can host many isolated L2 segments.
- VLANs are identified by a 12-bit **VLAN ID** (1–4094).
- **802.1Q** inserts a 4-byte tag into the Ethernet frame carrying the VLAN ID, priority bits (PCP), and DEI.
- **Access ports** belong to one VLAN and strip tags from end-device traffic.
- **Trunk ports** carry multiple VLANs with explicit 802.1Q tags.
- **Native VLAN** is the VLAN for untagged frames on a trunk; both ends must match.
- VLANs do not route — inter-VLAN traffic requires a router or Layer 3 switch SVI.
- Security: always change native VLAN from VLAN 1, disable DTP on access ports, restrict trunk allowed VLAN lists.

---

## Where to Next

- **SW-003 — Spanning Tree Protocol (STP/RSTP/MSTP):** VLANs over redundant links create loops; STP prevents forwarding loops.
- **SW-004 — EtherChannel/LACP:** Bundle physical links for trunk bandwidth and redundancy.
- **SW-006 — Layer 3 Switching & SVIs:** Native inter-VLAN routing without an external router.
- **RT-004 — OSPF Fundamentals:** Routing across VLAN-segmented networks.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| IEEE 802.1Q-2018 | Defines the 802.1Q VLAN tag format, trunking, and VLAN operations |
| IEEE 802.1ad (QinQ) | Double-tagging for service provider use |
| IEEE 802.1p | Priority Code Point (PCP) / CoS marking within 802.1Q |
| Cisco CCNA | VLAN configuration, trunk configuration, inter-VLAN routing |
| Cisco CCNP Enterprise | Advanced VLAN design, VTP, voice VLANs, private VLANs |
| CompTIA Network+ | VLAN concepts, trunk vs access |
| Juniper JNCIA-Junos | EX series VLAN configuration |

---

## References

- IEEE 802.1Q-2018 — Bridges and Bridged Networks. [https://standards.ieee.org/ieee/802.1Q/6844/](https://standards.ieee.org/ieee/802.1Q/6844/)
- IEEE 802.1ad-2005 — Provider Bridges (QinQ). [https://standards.ieee.org/ieee/802.1ad/1456/](https://standards.ieee.org/ieee/802.1ad/1456/)

---

## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Vendor Feature Mapping

| Feature | Cisco IOS-XE | Juniper EX (Junos) | Arista EOS | MikroTik RouterOS |
|---|---|---|---|---|
| Create VLAN | `vlan <id>` | `set vlans <name> vlan-id <id>` | `vlan <id>` | `/interface bridge vlan add` |
| Access port | `switchport mode access` + `switchport access vlan` | `interface-mode access` + `vlan members` | `switchport mode access` + `switchport access vlan` | `pvid=<id>` on bridge port |
| Trunk port | `switchport mode trunk` | `interface-mode trunk` + `vlan members` | `switchport mode trunk` | `tagged=<if>` in bridge vlan |
| Native VLAN | `switchport trunk native vlan <id>` | `native-vlan-id <id>` | `switchport trunk native vlan <id>` | No direct equivalent; use untagged config |
| Allowed VLANs | `switchport trunk allowed vlan <list>` | `vlan members [list]` | `switchport trunk allowed vlan <list>` | `vlan-ids` per bridge vlan entry |

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| SW-003 | Spanning Tree Protocol | STP operates per-VLAN in PVST+; trunk links are the context |
| SW-004 | EtherChannel / LACP | EtherChannel bundles trunk uplinks |
| SW-005 | Port Security & DAI | Port security and DAI operate on access ports with VLAN context |
| SW-006 | Layer 3 Switching & SVIs | SVIs provide inter-VLAN routing |
| CT-008 | MEF Standards | E-Line/E-LAN services use 802.1Q or QinQ |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SW-001 | Switching Fundamentals | MAC learning and broadcast domains — prerequisite |
| NW-002 | Network Topologies | Broadcast domain concept |
| RT-004 | OSPF Fundamentals | Routing between VLAN subnets |
<!-- XREF-END -->
