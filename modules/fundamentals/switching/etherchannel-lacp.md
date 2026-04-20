---
id: SW-004
title: "EtherChannel / LAG (LACP)"
description: "How multiple physical links between switches can be bonded into a single logical channel for increased bandwidth and redundancy."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - SW-001
  - SW-002
  - SW-003
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - switching
  - etherchannel
  - lacp
  - lag
  - link-aggregation
  - layer2
created: 2026-04-19
updated: 2026-04-19
---

# SW-004 — EtherChannel / LAG (LACP)

## The Problem

Two switches connected by a single 1 Gbps uplink. Traffic between them saturates the link during peak hours. You install a second 1 Gbps cable. STP sees two paths between the same two switches — a loop — and blocks one of them. You now have a 1 Gbps active path and a 1 Gbps idle standby. You doubled your cabling cost and got no extra bandwidth.

### Step 1: What if the two switches agreed the cables are one logical link?

Instead of running STP over two separate interfaces, the switches negotiate to treat both cables as a single logical interface — one 2 Gbps pipe from STP's perspective. STP sees one path, not two, and does not block anything. You now have 2 Gbps of usable bandwidth and built-in redundancy: if one cable fails, traffic continues on the remaining cable without STP reconvergence.

### Step 2: Who decides which frames go on which cable?

The logical channel must distribute traffic across member links. The switch computes a **hash** from some combination of source/destination MAC, IP address, or port number — the same flow always uses the same physical link (so frames arrive in order), but different flows are distributed across links (so both cables carry traffic).

### Step 3: How do both ends agree to form the channel?

Without negotiation, a misconfigured channel causes a loop: one end thinks both links are in the channel, the other doesn't. A negotiation protocol ensures both ends agree before any member link is added. **LACP (Link Aggregation Control Protocol)** is the IEEE standard for this negotiation.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Group of physical links acting as one | Link Aggregation Group (LAG) / EtherChannel |
| Negotiation protocol | LACP (IEEE 802.3ad) |
| Formula for assigning frames to links | Load-balancing hash |
| Logical interface representing the group | Port-channel / bond / ae interface |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why EtherChannel/LAG provides both increased bandwidth and redundancy.
2. Describe the LACP negotiation modes (active / passive) and when negotiation fails.
3. Explain load-balancing hash methods and their implications for traffic distribution.
4. Identify EtherChannel configuration requirements (mismatches that prevent the channel from forming).
5. Configure and verify EtherChannel on at least two vendor platforms.
6. Distinguish LACP (802.3ad) from Cisco PAgP (proprietary).

---

## Prerequisites

- SW-001 — Switching Fundamentals
- SW-002 — VLANs & 802.1Q Trunking (trunk configuration on port-channels)
- SW-003 — Spanning Tree Protocol (why STP blocks redundant links without LAG)

---

## Core Content

### What Is EtherChannel / LAG?

**EtherChannel** (Cisco) or **Link Aggregation Group (LAG)** (IEEE) bonds 2, 4, or 8 physical links between two directly-connected switches into a single logical interface. From the network's perspective:

- STP sees one link (one BID, one cost).
- The logical interface has the combined bandwidth of all member links.
- If any member link fails, traffic redistributes to remaining members — no STP reconvergence required, sub-second failover.
- VLAN and STP configuration is applied to the port-channel interface, not individual member ports.

### IEEE 802.3ad / 802.1AX — LACP

**LACP (Link Aggregation Control Protocol)** is the standard negotiation protocol for LAG formation. It operates by exchanging **LACPDUs** (LACP Data Units) on each member link.

LACP port modes:

| Mode | Behaviour |
|---|---|
| **Active** | Sends LACPDUs; will form a LAG with any passive or active partner |
| **Passive** | Responds to LACPDUs but does not initiate; forms LAG only if partner is active |
| **On (static)** | No LACP — assumes partner is in the same group. No negotiation; risk of misconfiguration causing a loop |

At least one side must be **Active**. Two passive sides never form a channel. Use active/active or active/passive — avoid `on` except in strictly controlled environments.

### Cisco PAgP — Proprietary Alternative

**PAgP (Port Aggregation Protocol)** is Cisco's proprietary LAG negotiation protocol, predating LACP. Modes:

- **Desirable** — equivalent to LACP Active.
- **Auto** — equivalent to LACP Passive.

PAgP only interoperates between Cisco devices. In multi-vendor environments, always use LACP.

### Load-Balancing Hashing

The switch distributes frames across member links using a **hash function**. The input to the hash determines which flows go where:

| Hash input | Behaviour |
|---|---|
| Source MAC | All frames from the same source MAC always use the same link |
| Destination MAC | Common for switches; distributes based on next-hop MAC |
| Source + Destination MAC | Better distribution; accounts for both ends |
| Source + Destination IP | L3 hash; better for routed traffic |
| Source + Destination IP + L4 port | Best distribution; differentiates between multiple flows between same hosts |

The hash produces an index that maps to a specific member link. The same hash input always produces the same output — flow ordering is preserved.

**Limitation:** A single large flow (e.g., one FTP transfer) can only use one member link. LAG improves aggregate throughput across many flows, not the throughput of any single flow.

??? supplementary "Unequal Load Distribution"
    Hash-based load balancing can produce uneven distribution in practice. If most traffic has the same source MAC (e.g., a router with one MAC forwarding all traffic), all flows hash to the same link. Choosing src+dst-IP as the hash method helps; some vendors support adaptive hashing or per-packet round-robin (though per-packet can reorder frames within a flow and is rarely used for TCP).

### EtherChannel Configuration Requirements

Both sides of an EtherChannel must match exactly. A mismatch prevents the channel from forming and typically causes STP to see the individual links as separate paths — potentially causing a loop or blocking:

| Parameter | Must match? |
|---|---|
| LACP mode (both active or active/passive) | Yes |
| Speed and duplex | Yes |
| VLAN configuration (access VLAN or trunk/native VLAN/allowed list) | Yes |
| STP settings | Yes |
| MTU | Yes |
| Number of links | Yes (up to max group size) |

If the channel fails to form, check these parameters first. Mismatched VLANs are a frequent cause — applying trunk config to the port-channel but leaving member ports in default VLAN 1 access mode.

### Layer 3 EtherChannel

EtherChannel can also function at Layer 3 — the port-channel interface is a routed interface with an IP address, not a switched interface. This is common for:

- Switch-to-router links.
- Data centre spine-leaf links (L3 underlay).
- Connections between Layer 3 switches.

Configuration: create the port-channel as a routed interface (`no switchport` on Cisco) and assign the IP to the port-channel, not the physical interfaces.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Create EtherChannel (LACP active on both sides)
    interface range GigabitEthernet0/1 - 2
     channel-group 1 mode active
     no shutdown

    ! Configure the port-channel as trunk
    interface Port-channel1
     switchport mode trunk
     switchport trunk native vlan 999
     switchport trunk allowed vlan 10,20

    ! Optional: set load-balancing hash
    port-channel load-balance src-dst-ip

    ! Verification
    show etherchannel summary
    show lacp neighbor
    show interfaces port-channel 1
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/lag/b_173_lag_9300_cg.html](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/lag/b_173_lag_9300_cg.html)

=== "Juniper EX (Junos)"

    ```
    # Create aggregated ethernet interface
    set chassis aggregated-devices ethernet device-count 4

    # Configure member links
    set interfaces ge-0/0/0 ether-options 802.3ad ae0
    set interfaces ge-0/0/1 ether-options 802.3ad ae0

    # Configure the LAG (ae0) interface
    set interfaces ae0 aggregated-ether-options lacp active
    set interfaces ae0 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ae0 unit 0 family ethernet-switching vlan members [ACCOUNTING ENGINEERING]

    # Verification
    show interfaces ae0 detail
    show lacp interfaces
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/interfaces-ethernet-switches/topics/topic-map/switches-interface-lag.html](https://www.juniper.net/documentation/us/en/software/junos/interfaces-ethernet-switches/topics/topic-map/switches-interface-lag.html)

=== "Arista EOS"

    ```
    ! Create port-channel
    interface Port-Channel1
       switchport mode trunk
       switchport trunk native vlan 999
       switchport trunk allowed vlan 10,20

    ! Configure member interfaces
    interface Ethernet1
       channel-group 1 mode active
    interface Ethernet2
       channel-group 1 mode active

    ! Verification
    show port-channel summary
    show lacp peer
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-port-channel-interfaces](https://www.arista.com/en/um-eos/eos-port-channel-interfaces)

=== "MikroTik RouterOS"

    ```
    # Create bonding interface (LACP)
    /interface bonding
    add name=bond1 mode=802.3ad slaves=ether1,ether2 \
        lacp-rate=fast transmit-hash-policy=layer-2-and-3

    # Add bond to bridge
    /interface bridge port
    add bridge=bridge1 interface=bond1

    # Verification
    /interface bonding monitor bond1
    /interface bonding print detail
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/Bonding](https://help.mikrotik.com/docs/display/ROS/Bonding)

---

## Common Pitfalls

1. **Mismatched LACP modes (passive/passive).** If both sides are set to passive, neither side sends LACPDUs and the channel never forms. Use active on at least one side; active/active is preferred.

2. **Configuring VLANs on member interfaces instead of the port-channel.** VLAN (trunk/access) configuration must be on the logical port-channel interface. Applying it to physical member interfaces produces inconsistent results and may cause the channel to not form.

3. **Mixing member link speeds.** All member links in a LAG must have the same speed and duplex. Mixing 1 GE and 10 GE members is not supported.

4. **Assuming LAG doubles single-flow throughput.** A single TCP connection can only use one hash bucket — one physical link. LAG improves aggregate bandwidth for many parallel flows, not per-flow throughput.

5. **Forgetting STP sees the port-channel, not the members.** Once a port-channel is formed, STP configuration (priority, PortFast, BPDU Guard) must be applied to the port-channel interface.

---

## Practice Problems

**Q1.** Switch A has LACP mode `active` and Switch B has LACP mode `passive`. Does a LAG form?

??? answer
    Yes. Active initiates LACPDUs; passive responds. Active/passive is a valid combination and forms a LAG successfully.

**Q2.** Two switches have two 1 Gbps links bonded in a LAG using src-dst-MAC hashing. A single server sends all traffic to a single router (one src MAC, one dst MAC). How much bandwidth does the server use?

??? answer
    1 Gbps — all frames from this server to this router hash to the same link (same src/dst MAC pair → same hash output → same physical link). The second link carries no traffic from this flow. Consider using src+dst-IP or L4 hash if most traffic has the same MAC pair.

**Q3.** You create a port-channel on both switches. On Switch A, you configure the port-channel as a trunk. On Switch B, you forget and leave the port-channel as a default access VLAN 1 port. What happens?

??? answer
    The LAG may form (LACP negotiates at the physical layer, not the VLAN layer), but traffic will be misconfigured: Switch A sends tagged frames on the trunk; Switch B treats all frames as untagged VLAN 1. VLAN 10 and 20 traffic will be dropped. The mismatch is silent from an LACP perspective — use `show interfaces trunk` and `show etherchannel summary` to detect.

**Q4.** What is the difference between LACP `active/active` and `on/on`?

??? answer
    With active/active, LACP continuously exchanges LACPDUs to verify the channel state — if a link fails or the partner disconnects, LACP detects it quickly and removes that member. With `on/on` (static), there is no negotiation — the switch assumes all configured links are in the channel regardless of the partner's state. A misconfigured or failed partner may result in a loop or dropped traffic without detection.

---

## Lab

**Objective:** Configure a 2-link LACP EtherChannel between two switches; verify traffic distribution and failover.

**Steps:**
1. Connect two switches with two cables on interfaces Gi0/1 and Gi0/2.
2. Configure both as LACP active mode on both switches.
3. Create the port-channel as a trunk (VLANs 10 and 20).
4. Verify: `show etherchannel summary` shows both links as (P) — bundled; `show spanning-tree` shows one port-channel link, not two separate ones.
5. Generate traffic between hosts in VLAN 10 on both switches. Observe which physical interface is active.
6. Disconnect one cable. Verify traffic continues (brief interruption) and the remaining link carries all traffic.
7. Reconnect the cable. Verify it rejoins the LAG.

---

## Summary & Key Takeaways

- **EtherChannel/LAG** bonds multiple physical links into one logical interface — STP sees one link, not a loop.
- **LACP (IEEE 802.3ad)** is the standard negotiation protocol. Use it in multi-vendor environments.
- LACP modes: **Active** (initiates) and **Passive** (responds). At least one side must be active.
- **Load-balancing hash** distributes flows across member links — same flow always uses same link.
- LAG improves **aggregate** bandwidth (more parallel flows); it does not improve **per-flow** throughput.
- All member links must match in speed, duplex, VLAN config, MTU, and STP settings.
- Apply VLAN and STP configuration to the **port-channel interface**, not the physical members.
- **Cisco PAgP** is proprietary — use LACP in multi-vendor environments.

---

## Where to Next

- **SW-005 — Port Security & DAI:** Securing access ports; MAC limiting; ARP inspection.
- **SW-006 — Layer 3 Switching & SVIs:** L3 EtherChannel for routed uplinks.
- **DC-001 — Data Centre Network Design:** Spine-leaf uses L3 LAGs extensively.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| IEEE 802.3ad-2000 / IEEE 802.1AX-2020 | LACP and Link Aggregation standard |
| Cisco CCNA | EtherChannel configuration, LACP/PAgP |
| Cisco CCNP Enterprise | LAG troubleshooting, L3 port-channel |
| CompTIA Network+ | Link aggregation concepts |
| Juniper JNCIA-Junos | Aggregated Ethernet configuration |

---

## References

- IEEE 802.1AX-2020 — Link Aggregation. [https://standards.ieee.org/ieee/802.1AX/7155/](https://standards.ieee.org/ieee/802.1AX/7155/)

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
| Create LAG | `channel-group <n> mode active` | `ether-options 802.3ad ae<n>` | `channel-group <n> mode active` | `/interface bonding add mode=802.3ad` |
| LAG interface | `interface Port-channel<n>` | `interface ae<n>` | `interface Port-Channel<n>` | `interface bond<n>` |
| LACP active | `mode active` | `lacp active` | `mode active` | `mode=802.3ad` |
| Load-balance hash | `port-channel load-balance <method>` | (set on chassis/per-aggregated) | `port-channel load-balance <method>` | `transmit-hash-policy=layer-2-and-3` |
| Show summary | `show etherchannel summary` | `show lacp interfaces` | `show port-channel summary` | `/interface bonding monitor` |

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| SW-006 | Layer 3 Switching & SVIs | L3 port-channel for routed uplinks |
| DC-001 | Data Centre Network Design | Spine-leaf L3 LAGs |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SW-001 | Switching Fundamentals | MAC learning on port-channel |
| SW-002 | VLANs & 802.1Q Trunking | Trunk config on port-channel |
| SW-003 | Spanning Tree Protocol | STP treats port-channel as one link |
<!-- XREF-END -->
