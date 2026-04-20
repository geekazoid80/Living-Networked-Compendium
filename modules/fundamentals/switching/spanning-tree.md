---
id: SW-003
title: "Spanning Tree Protocol (STP / RSTP / MSTP)"
description: "How STP, RSTP, and MSTP prevent Layer 2 loops in switched networks while maintaining redundant paths."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - SW-001
  - SW-002
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - switching
  - stp
  - rstp
  - mstp
  - spanning-tree
  - layer2
  - loop-prevention
created: 2026-04-19
updated: 2026-04-19
---

# SW-003 — Spanning Tree Protocol (STP / RSTP / MSTP)

## The Problem

Two switches connected by two cables — one for redundancy, in case the primary fails. This seems like good engineering. But switches flood unknown unicast and broadcast frames to every port. With two paths between them, a broadcast creates a loop: Switch A floods to Switch B on path 1, Switch B floods back on path 2, Switch A floods again... This never stops. A **broadcast storm** consumes 100% of link bandwidth within seconds and brings the network to a halt.

### Step 1: You need redundant paths but can't allow loops

You need a way to keep the second cable available for failover without allowing it to actively forward traffic. The cable must exist but be logically blocked.

### Step 2: Elect one switch as the reference point

If every switch makes its own decision about which ports to block, they might disagree and either create loops or block too much. You need one switch to be the authority — the **root bridge**. Every other switch computes the shortest path to the root and blocks any port that would create an alternative path.

### Step 3: React when a path fails

When the active path breaks, the blocked port must unblock and become the new forwarding path. The transition must be orderly enough that loops don't form during the changeover — but it must also complete quickly enough that users notice minimal disruption.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Reference switch elected by all | Root bridge |
| Best port toward root on each non-root switch | Root port |
| Best port per segment (toward root) | Designated port |
| Blocked port preventing a loop | Alternate (blocking) port |
| Algorithm that selects this topology | Spanning Tree Protocol (STP) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why Layer 2 loops form and why they are catastrophic.
2. Describe the STP election process: root bridge, root port, designated port, and blocking port.
3. Explain STP port states and the role of timers.
4. Contrast 802.1D STP, 802.1w RSTP, and 802.1s MSTP.
5. Identify common STP misconfigurations and their symptoms.
6. Configure and verify STP/RSTP on at least two vendor platforms.

---

## Prerequisites

- SW-001 — Switching Fundamentals (MAC learning, flooding, broadcast domains)
- SW-002 — VLANs & 802.1Q Trunking (VLAN concept, trunk links)

---

## Core Content

### Why Loops Are Catastrophic

A Layer 2 network has no TTL equivalent — Ethernet frames have no hop-count field that decrements to zero and causes the frame to be discarded. In a looped topology:

1. A broadcast frame is sent once and arrives at all switches.
2. Each switch floods it to all ports except the one it arrived on.
3. The frame re-enters the network on another path and floods again.
4. Each iteration makes the frame count grow exponentially — a **broadcast storm**.
5. The **MAC table thrashes**: the switch sees the same MAC address arriving on different ports as the frame circulates, re-learning the MAC repeatedly, never converging.

The network becomes completely unusable within seconds.

### STP Overview (IEEE 802.1D)

**Spanning Tree Protocol** builds a loop-free logical topology over a physically redundant network. It does this by:

1. Electing a **root bridge** — the switch all others measure distance from.
2. Computing the shortest path from every switch to the root (using **path cost**).
3. Placing all non-shortest-path ports into a **blocking** state.

The result is a tree rooted at the root bridge, with exactly one active path between any two switches.

### Root Bridge Election

Every switch has a **Bridge ID (BID)** — an 8-byte value composed of:

```
[2 bytes: Bridge Priority] [6 bytes: MAC address]
```

Default priority: **32768** (0x8000). Lower BID wins the election.

The priority field is configurable in increments of 4096 (to accommodate the 12-bit VLAN ID embedded in 802.1D / 802.1w). Values: 0, 4096, 8192 ... 61440.

Election process:

1. Every switch starts believing it is the root and sends **BPDUs (Bridge Protocol Data Units)** claiming root status.
2. When a switch receives a superior BPDU (lower BID), it stops claiming root status and forwards the superior BPDU.
3. The switch with the lowest BID wins — no other switch will receive a superior BPDU to challenge it.

**Best practice:** Manually set the root bridge by lowering its priority (`priority 4096`). Do not rely on the lowest MAC address determining the root — this is arbitrary and may not be the most central switch.

??? supplementary "Bridge Priority and VLAN ID (Extended System ID)"
    In PVST+ (Cisco) and RPVST+ (Arista), each VLAN runs a separate STP instance. The bridge priority field embeds the VLAN ID in the lower 12 bits, so the actual configured priority is the base value + VLAN ID. If you configure priority 32768 on VLAN 10, the effective BID priority is 32778. Juniper and Nokia use different mechanisms for per-VLAN spanning tree.

### Path Cost

Path cost is an integer assigned to each port based on link speed. Lower cost = preferred path.

IEEE 802.1D (original) and IEEE 802.1w (Revised) cost values:

| Link speed | 802.1D cost | 802.1w (short) | 802.1t (long, recommended) |
|---|---|---|---|
| 10 Mbps | 100 | 2 000 000 | 2 000 000 |
| 100 Mbps | 19 | 200 000 | 200 000 |
| 1 Gbps | 4 | 20 000 | 20 000 |
| 10 Gbps | 2 | 2 000 | 2 000 |
| 100 Gbps | 1 | 200 | 200 |

The **root path cost** is accumulated hop by hop from root to each bridge. A switch adds the port cost when it receives a BPDU through that port.

### Port Roles

| Role | Description |
|---|---|
| **Root Port (RP)** | The one port on each non-root switch with the lowest cost path to the root bridge. Exactly one per non-root switch. |
| **Designated Port (DP)** | The port on each network segment (link) closest to the root. Exactly one designated port per segment. The root bridge's ports are always designated. |
| **Alternate Port** | A non-designated, non-root port — blocked. Provides the backup path to the root. |
| **Backup Port** | A port blocked because a better designated port exists on the same switch on the same segment (rare — two ports on the same switch connected to the same hub). |

### STP Port States (802.1D)

| State | Duration | Forwards traffic? | Learns MACs? |
|---|---|---|---|
| Blocking | Until elected RP or DP, or timeout | No | No |
| Listening | 15 s (Forward Delay) | No | No |
| Learning | 15 s (Forward Delay) | No | Yes |
| Forwarding | Indefinite | Yes | Yes |
| Disabled | Admin down | No | No |

Convergence time for 802.1D: **30–50 seconds** in typical failure scenarios (Max Age 20s + 2× Forward Delay 15s = 50s maximum).

### STP Timers (802.1D)

| Timer | Default | Description |
|---|---|---|
| Hello Time | 2 s | Interval between BPDU transmissions from root |
| Max Age | 20 s | How long a switch stores BPDU information before expiring it |
| Forward Delay | 15 s | Time spent in Listening and Learning states |

**Do not adjust timers in production** without understanding the topology diameter implications. Reducing timers on large networks can cause premature topology changes and instability.

### RSTP (IEEE 802.1w) — Rapid Spanning Tree

RSTP was designed to address 802.1D's slow convergence (30–50 seconds). Key improvements:

- **Convergence time: 1–2 seconds** in typical topologies.
- Three port roles instead of five states: **Discarding** (combined Blocking + Listening), **Learning**, **Forwarding**.
- **Rapid agreement mechanism**: instead of waiting for timers, switches negotiate directly with their peer using a Proposal/Agreement handshake (only on point-to-point links).
- **Alternate and Backup ports** are pre-computed and transition immediately when the root port fails — no timer wait.
- BPDUs sent from every switch every Hello interval (not just the root) — allows fast detection of loss.

Port types in RSTP:

| Port type | Link type | Rapid transition? |
|---|---|---|
| Edge port | Access port (end device) | Yes — immediately forwarding |
| Point-to-point | Full-duplex switch link | Yes — via Proposal/Agreement |
| Shared | Half-duplex (hub) | No — must wait for timer |

**PortFast / Edge ports:** Ports connected to end devices skip Listening and Learning and go directly to Forwarding. This is safe because end devices do not generate BPDUs and cannot create loops. Always enable PortFast on access ports; never on switch-to-switch links.

**BPDU Guard:** When enabled on PortFast/Edge ports, if a BPDU is received the port is immediately placed in err-disabled state. Protects against an attacker or misconfigured switch connected to an access port attempting to influence the STP topology.

### MSTP (IEEE 802.1s) — Multiple Spanning Tree

In a network with 100 VLANs, 802.1D runs 100 STP instances (PVST+) — one per VLAN. Each instance generates BPDUs, each requires CPU processing, and convergence events multiply. MSTP maps VLANs to a smaller number of **MST instances (MSTIs)**, sharing compute and convergence overhead.

Key concepts:

- **MST region:** A group of switches with identical MST configuration (region name, revision, VLAN-to-instance mapping). Switches in the same region share MST topology computation.
- **MSTI 0 (IST — Internal Spanning Tree):** The default instance. Carries all VLANs not explicitly mapped to another instance.
- **MSTIs 1–64:** User-defined instances. VLANs are mapped to them explicitly.
- Outside the region, MSTP appears as a single RSTP bridge to the rest of the network.

MSTP is preferred for large campus networks with many VLANs. For typical enterprise deployments with < 10 VLANs, RSTP per VLAN (RPVST+) is operationally simpler.

### Cisco-Specific: PVST+ and RPVST+

Cisco's implementation runs a separate spanning tree instance per VLAN:

- **PVST+** (Per-VLAN Spanning Tree Plus): based on 802.1D with Cisco extensions, one instance per VLAN.
- **RPVST+** (Rapid PVST+): based on 802.1w, one instance per VLAN. Current Cisco default on most platforms.

Benefits: different VLANs can use different root bridges, enabling load balancing across uplinks. VLANs 1–4094 can have different active paths.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Set switch as root for VLAN 10, secondary for VLAN 20
    spanning-tree vlan 10 priority 4096
    spanning-tree vlan 20 priority 8192

    ! Or use macro (sets priority automatically)
    spanning-tree vlan 10 root primary
    spanning-tree vlan 20 root secondary

    ! Enable RSTP (Rapid PVST+ is default on modern IOS)
    spanning-tree mode rapid-pvst

    ! Enable PortFast on access port
    interface GigabitEthernet0/1
     spanning-tree portfast

    ! Enable BPDU Guard on edge ports globally
    spanning-tree portfast bpduguard default

    ! Verification
    show spanning-tree vlan 10
    show spanning-tree summary
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/stp/b_173_stp_9300_cg.html](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/stp/b_173_stp_9300_cg.html)

=== "Juniper EX (Junos)"

    ```
    # Enable RSTP
    set protocols rstp

    # Set bridge priority (lower = preferred root)
    set protocols rstp bridge-priority 4096

    # Edge port (PortFast equivalent)
    set protocols rstp interface ge-0/0/1 edge

    # BPDU Guard on edge port
    set protocols rstp interface ge-0/0/1 no-root-port

    # Verification
    show spanning-tree bridge
    show spanning-tree interface
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/stp-l2/topics/topic-map/rstp-configuring.html](https://www.juniper.net/documentation/us/en/software/junos/stp-l2/topics/topic-map/rstp-configuring.html)

=== "Arista EOS"

    ```
    ! Enable Rapid PVST+
    spanning-tree mode rapid-pvst

    ! Set root for VLAN 10
    spanning-tree vlan 10 priority 4096

    ! Edge port with BPDU Guard
    interface Ethernet1
       spanning-tree portfast
       spanning-tree bpduguard enable

    ! Verification
    show spanning-tree vlan 10
    show spanning-tree detail
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-spanning-tree-protocols](https://www.arista.com/en/um-eos/eos-spanning-tree-protocols)

=== "MikroTik RouterOS"

    ```
    # Enable RSTP on the bridge
    /interface bridge
    set bridge1 protocol-mode=rstp priority=0x1000

    # Edge/fast port (PortFast equivalent)
    /interface bridge port
    set [find interface=ether1] edge=yes point-to-point=yes

    # Verification
    /interface bridge monitor bridge1
    /interface bridge port print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/Spanning+Tree+Protocol](https://help.mikrotik.com/docs/display/ROS/Spanning+Tree+Protocol)

---

## Common Pitfalls

1. **Root bridge not explicitly configured.** The switch with the lowest MAC address becomes root. This is often the oldest switch — potentially the least capable, most distant, or least redundant. Always set root bridge priority explicitly.

2. **PortFast on trunk ports.** Enabling PortFast on a switch-to-switch link means BPDUs are not expected there. If BPDU Guard is also enabled, the port will err-disable when a BPDU arrives — taking down the inter-switch link. Never enable PortFast on trunk ports.

3. **Topology change storms.** STP Topology Change Notifications (TCNs) cause all switches to flush their MAC tables, leading to flooding. A flapping access port triggers continuous TCNs. Use `spanning-tree portfast` on access ports (which suppresses TCN generation) and investigate flapping ports.

4. **Mismatched STP modes.** A Cisco PVST+ switch connected to a standard 802.1w RSTP switch may not interoperate cleanly for all VLANs. PVST+ only sends BPDUs on VLAN 1 by default on non-Cisco trunks. Verify interoperability when mixing vendors.

5. **Ignoring STP in VoIP deployments.** An IP phone rebooting triggers a PortFast transition; without PortFast, the phone waits 30 seconds before passing traffic. Always enable PortFast on switch ports connected to IP phones.

---

## Practice Problems

**Q1.** Three switches — SW1, SW2, SW3 — form a triangle. BIDs: SW1 = 32768.AA, SW2 = 32768.BB, SW3 = 4096.CC. Which switch becomes root?

??? answer
    SW3 — it has the lowest bridge priority (4096) regardless of MAC address. Priority is compared first; only if priorities are equal is MAC address used as tiebreaker.

**Q2.** A non-root switch has two paths to the root: Path A with accumulated cost 19, Path B with accumulated cost 4. Which port becomes the Root Port?

??? answer
    The port on Path B (cost 4). The Root Port is the port with the lowest accumulated path cost to the root bridge.

**Q3.** What happens when a PortFast-configured port receives a BPDU and BPDU Guard is enabled?

??? answer
    The port is immediately placed in err-disabled state. Traffic stops flowing until an administrator manually recovers the port (or auto-recovery is configured). This prevents an unauthorised switch from influencing the STP topology.

**Q4.** Why is RSTP faster than 802.1D STP on point-to-point links?

??? answer
    RSTP uses a Proposal/Agreement mechanism — the upstream switch proposes to become designated, the downstream switch agrees (after blocking its own non-edge ports), and the upstream port immediately transitions to Forwarding. No timer wait is required. This completes in milliseconds rather than 30 seconds.

**Q5.** What is the benefit of PVST+ over standard STP for a dual-uplink design?

??? answer
    PVST+ runs a separate STP instance per VLAN. You can configure SW1 as root for VLAN 10 and SW2 as root for VLAN 20. Half the VLANs use uplink 1, half use uplink 2 — load balancing across both links. Standard STP blocks one uplink entirely for all traffic.

---

## Lab

**Objective:** Observe STP election and convergence; trigger a topology change; verify RSTP rapid convergence.

**Topology:**
```
        [SW1]
       /     \
    [SW2]---[SW3]
```
Three switches connected in a triangle with three trunk links.

**Steps:**
1. Connect all three switches and observe the initial STP topology (`show spanning-tree`).
2. Identify which switch became root bridge (likely random based on MAC).
3. Set SW1 as root for VLAN 1 (`spanning-tree vlan 1 priority 4096`). Observe convergence.
4. Enable RSTP (`spanning-tree mode rapid-pvst` or equivalent). Re-run the test.
5. Disconnect the active link between SW1 and SW2. Measure time to convergence (ping SW2 from a host, observe loss duration).
6. Compare 802.1D timer-based convergence (max 50s) vs RSTP convergence (1–2s).

---

## Summary & Key Takeaways

- Layer 2 loops cause **broadcast storms** and **MAC table thrashing** — the network fails in seconds.
- STP (802.1D) prevents loops by electing a **root bridge** and blocking redundant paths.
- The **root bridge** is elected by lowest Bridge ID (priority + MAC). Always set explicitly.
- STP convergence: **30–50 seconds**. RSTP convergence: **1–2 seconds** via Proposal/Agreement.
- RSTP (802.1w) is backward-compatible with 802.1D and should be the default choice.
- MSTP (802.1s) maps multiple VLANs to fewer STP instances — preferred for large VLAN environments.
- **PortFast / Edge ports** skip the listening/learning states for end-device ports.
- **BPDU Guard** err-disables edge ports if a BPDU is received — prevents topology attacks.
- Always configure the root bridge explicitly; never rely on default MAC-based election.

---

## Where to Next

- **SW-004 — EtherChannel/LACP:** Aggregate multiple links to avoid STP blocking them altogether.
- **SW-005 — Port Security & DAI:** BPDU Guard, root guard, and storm control in security context.
- **SW-006 — Layer 3 Switching & SVIs:** L3 forwarding eliminates some STP scope.
- **CT-006 — EVPN Fundamentals:** EVPN-based loop prevention replaces STP in modern DC fabrics.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| IEEE 802.1D-2004 | Classic STP; largely superseded but foundational |
| IEEE 802.1w-2001 | RSTP — incorporated into 802.1D-2004 |
| IEEE 802.1s-2002 | MSTP — incorporated into 802.1Q-2005 and later |
| Cisco CCNA | STP election, RSTP, PortFast, BPDU Guard |
| Cisco CCNP Enterprise | MSTP, STP tuning, troubleshooting |
| CompTIA Network+ | STP concepts, loop prevention |
| Juniper JNCIA-Junos | EX series spanning tree |

---

## References

- IEEE 802.1D-2004 — Media Access Control (MAC) Bridges. [https://standards.ieee.org/ieee/802.1D/3588/](https://standards.ieee.org/ieee/802.1D/3588/)
- IEEE 802.1w-2001 — Rapid Reconfiguration. Incorporated into 802.1D-2004.
- IEEE 802.1s-2002 — Multiple Spanning Trees. Incorporated into 802.1Q-2005.

---

## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Vendor Feature Mapping

| Feature | Cisco IOS-XE (RPVST+) | Juniper EX (Junos) | Arista EOS | MikroTik RouterOS |
|---|---|---|---|---|
| STP mode | `spanning-tree mode rapid-pvst` | `set protocols rstp` | `spanning-tree mode rapid-pvst` | `protocol-mode=rstp` on bridge |
| Root priority | `spanning-tree vlan <id> priority <val>` | `set protocols rstp bridge-priority <val>` | `spanning-tree vlan <id> priority <val>` | `priority=0x<hex>` on bridge |
| Edge/PortFast | `spanning-tree portfast` (interface) | `set protocols rstp interface <if> edge` | `spanning-tree portfast` | `edge=yes` on bridge port |
| BPDU Guard | `spanning-tree portfast bpduguard default` | `no-root-port` | `spanning-tree bpduguard enable` | n/a (manual filtering) |
| Show topology | `show spanning-tree vlan <id>` | `show spanning-tree bridge` | `show spanning-tree vlan <id>` | `/interface bridge monitor` |

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| SW-004 | EtherChannel / LACP | EtherChannel is the alternative to STP-blocked redundant links |
| SW-005 | Port Security & DAI | Root Guard and BPDU Guard in security context |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SW-001 | Switching Fundamentals | Flooding and broadcast storms — why loops matter |
| SW-002 | VLANs & 802.1Q Trunking | STP operates on trunk links; PVST+ per-VLAN instances |
<!-- XREF-END -->
