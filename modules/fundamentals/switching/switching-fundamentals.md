---
title: "Switching Fundamentals"
module_id: "SW-001"
domain: "fundamentals/switching"
difficulty: "intermediate"
prerequisites: ["NW-001", "NW-002", "IP-001"]
estimated_time: 40
version: "1.0"
last_updated: "2026-04-19"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["switching", "mac-address", "cam-table", "flooding", "forwarding", "ethernet", "layer-2", "microsegmentation"]
cert_alignment: "CCNA 200-301 — 2.1–2.3 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Arista EOS", "MikroTik RouterOS"]
language: "en"
---

## The Problem

Ten computers in an office. They are all plugged into the same device in the middle. Someone sends a file to a colleague. How does the middle device know which port to send it out?

### Step 1: It doesn't know yet — so it floods

When a frame arrives and the switch has never seen the destination MAC address before, it has one option: send the frame out every port except the one it arrived on. This is **flooding**. Every device on the network receives the frame; only the intended recipient responds.

Flooding is expensive — every device is interrupted. But it solves the immediate problem: the frame reaches its destination.

### Step 2: It learns who is where

While the switch is forwarding frames, it does something useful: it reads the **source** MAC address of every incoming frame and records which port that address arrived on. This is **MAC learning**. The record is stored in the **MAC address table** (also called the CAM table — Content Addressable Memory).

```text
After a few exchanges:
MAC Address         Port   VLAN   Age
aa:bb:cc:dd:ee:01   Gi0/1  1      120s
aa:bb:cc:dd:ee:02   Gi0/2  1      90s
aa:bb:cc:dd:ee:03   Gi0/3  1      45s
```

Now when a frame arrives destined for `aa:bb:cc:dd:ee:02`, the switch looks up the MAC table, finds port Gi0/2, and sends the frame **only** out that port. No flooding needed. This is **unicast forwarding**.

### Step 3: The table gets stale — entries age out

Devices move, get replaced, or go offline. If the MAC table held entries forever, a moved device would never receive frames — the switch would still send to the old port. So each entry has an **aging timer** (default 300 seconds). If no frame is seen from that MAC within the timeout, the entry is removed. The next frame from that device re-triggers learning.

### What You Just Built

An Ethernet switch — a Layer 2 device that learns MAC addresses by observing source addresses, forwards known unicast frames to the correct port, and floods unknown unicast, broadcast, and multicast frames.

| Scenario element | Technical term |
|---|---|
| Send to all ports except source | Flooding |
| Recording source MAC + port | MAC learning |
| MAC address → port mapping table | MAC address table / CAM table |
| Send to specific port for known MAC | Unicast forwarding |
| Remove stale entries after timeout | MAC aging |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** the three core operations of an Ethernet switch: learn, flood, forward
2. **Read** a MAC address table and predict switch forwarding behaviour for a given frame
3. **Distinguish** between unicast, broadcast, and unknown-unicast flooding
4. **Explain** collision domains, broadcast domains, and how switches change both compared to hubs
5. **Describe** microsegmentation and why switches replaced hubs

---

## Prerequisites

- [The OSI Model](../networking/osi-model.md) (`NW-001`) — Layer 2 concepts; MAC addressing; Ethernet frame structure
- [Network Topologies](../networking/network-topologies.md) (`NW-002`) — collision and broadcast domains; star topology

---

## Core Content

### Ethernet Frame and MAC Addressing

A switch operates at **Layer 2** — it reads Ethernet frames, not IP packets. The Ethernet frame carries:

```text
Ethernet Frame:
┌──────────┬──────────┬──────┬─────────────────────┬─────┐
│ Dst MAC  │ Src MAC  │ Type │ Payload (IP packet)  │ FCS │
│ (6 bytes)│ (6 bytes)│(2B)  │ (up to 1500 bytes)  │(4B) │
└──────────┴──────────┴──────┴─────────────────────┴─────┘
```

MAC addresses are **48 bits** (6 bytes), written as `aa:bb:cc:dd:ee:ff`. The first 3 bytes are the OUI (Organisationally Unique Identifier — identifies the manufacturer); the last 3 bytes are assigned by the manufacturer.

**Special MAC addresses:**
- `ff:ff:ff:ff:ff:ff` — broadcast; all devices on the segment must process this
- `01:xx:xx:xx:xx:xx` — multicast (bit 0 of first byte = 1)
- All other addresses — unicast

### The Three Switch Operations

**1. Learn**
When a frame arrives on port X with source MAC `AA:BB:CC:DD:EE:01`:
- The switch creates or updates a MAC table entry: `AA:BB:CC:DD:EE:01 → port X`
- The aging timer resets
- Learning happens on every frame, every port

**2. Flood (when needed)**
The switch floods a frame when:
- The destination MAC is **unknown** (not in the MAC table) — unknown unicast flood
- The destination MAC is the **broadcast** address (`ff:ff:ff:ff:ff:ff`)
- The destination MAC is a **multicast** address (without IGMP snooping)

Flooding goes to all ports in the same VLAN, except the ingress port.

**3. Forward**
When the destination MAC is in the MAC table:
- The switch sends the frame **only** to the port listed in the table
- All other ports are silent — this is **microsegmentation**

```text
Frame arrives: Dst=AA:BB:CC:DD:EE:02, Src=AA:BB:CC:DD:EE:01, ingress=Gi0/1

MAC table lookup:
  AA:BB:CC:DD:EE:02 → Gi0/2  (found)

Action: forward out Gi0/2 only
Result: only the device on Gi0/2 receives the frame
```

### Hub vs Switch — Collision Domains

A **hub** is a Layer 1 repeater. Every frame received on any port is repeated out every other port. All devices share the same collision domain — only one can transmit at a time; simultaneous transmission causes a collision.

A **switch** creates a **separate collision domain per port**. Each port can transmit independently. On a full-duplex switch port (standard since Fast Ethernet), there are no collisions at all — the send and receive paths are electrically separate.

| Feature | Hub | Switch |
|---|---|---|
| Layer | Physical (L1) | Data Link (L2) |
| Collision domain | All ports share one | One per port |
| Bandwidth | Shared | Dedicated per port |
| Simultaneous transmission | No (CSMA/CD) | Yes (full-duplex) |
| MAC learning | None | Yes |
| Selective forwarding | No (always floods) | Yes |

### Broadcast Domain and Switches

Switches do **not** break broadcast domains by default. A broadcast frame (`ff:ff:ff:ff:ff:ff`) is flooded to every port in the same VLAN. All ports in the same VLAN are in the same broadcast domain.

To separate broadcast domains, you need either:
- A **router** (or Layer 3 switch with SVIs) — routes between subnets
- **VLANs** — separate the switch into multiple broadcast domains (covered in SW-002)

### MAC Table Behaviour — Edge Cases

**Unknown unicast flood:**
Frame arrives with a destination MAC not in the table. The switch floods it. This is normal during the initial learning phase, or when a device hasn't communicated recently (entry aged out).

**MAC move:**
A device unplugs from Gi0/1 and plugs into Gi0/3. The next frame from that device arrives on Gi0/3 with the same source MAC. The switch updates the table: `MAC → Gi0/3`. Frames to that device now go to Gi0/3.

**MAC flapping:**
If a MAC address appears on two different ports in rapid succession (milliseconds), it is recorded as a MAC flap. This indicates either a loop in the network, a misconfigured device, or a spoofing attack. Switches log MAC flaps; excessive flapping causes instability.

**Full MAC table:**
Switches have a finite MAC table size (a few thousand to hundreds of thousands of entries depending on hardware). When the table is full, new unknown source MACs cannot be learned — new frames with unknown destinations are flooded until old entries age out. An attacker can deliberately flood the table with fake MACs (MAC flooding attack) to force the switch into hub-like behaviour.

??? supplementary "Cut-Through vs Store-and-Forward Switching"
    Switches can forward frames in two modes:

    - **Store-and-forward**: the entire frame is received, error-checked (FCS), then forwarded. If the frame has errors, it is dropped. Adds latency equal to the frame transmission time but ensures no corrupt frames are forwarded.

    - **Cut-through**: the switch begins forwarding as soon as the destination MAC (first 6 bytes) is read — before the frame is fully received. Lower latency; corrupt frames may be forwarded (no FCS check until after forwarding begins).

    Most modern access switches use store-and-forward. Cut-through is used in low-latency data-centre environments (HFT, HPC) where the latency saving justifies the risk of forwarding some corrupt frames.

---

## Vendor Implementations

Ethernet switching behaviour is standardised in IEEE 802.1D (bridging) and IEEE 802.3 (Ethernet). All compliant switches implement the same MAC learning and forwarding logic. Configuration differences are in interface naming and command syntax.

!!! success "Standard — IEEE 802.1D (MAC Bridging), IEEE 802.3 (Ethernet)"
    All compliant switches implement learn/flood/forward identically. MAC aging defaults (300s) and flooding behaviour are standardised.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! View the MAC address table
    show mac address-table

    ! View entries for a specific VLAN
    show mac address-table vlan 1

    ! View entries for a specific MAC
    show mac address-table address aa:bb:cc:dd:ee:01

    ! Clear the dynamic MAC table
    clear mac address-table dynamic

    ! Configure MAC aging timer (seconds)
    mac address-table aging-time 300

    ! Configure a static MAC entry
    mac address-table static aa:bb:cc:dd:ee:ff vlan 1 interface GigabitEthernet0/1
    ```
    On Cisco IOS-XE, the MAC table is called `mac address-table`. Static entries never age out and are not overwritten by learning.

    Full configuration reference: [Cisco Layer 2 Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-3/configuration_guide/lyr2/b_173_lyr2_9300_cg.html)

=== "Juniper Junos"
    ```junos
    # View MAC table
    show ethernet-switching table

    # View for specific VLAN
    show ethernet-switching table vlan-name default

    # Clear dynamic entries
    clear ethernet-switching table

    # Configure MAC aging
    set vlans default mac-aging-time 300
    ```
    Junos EX switches use `ethernet-switching` commands. The MAC table is called the ethernet-switching table. VLANs are configured separately and referenced by name.

    Full configuration reference: [Juniper EX Series Switching](https://www.juniper.net/documentation/us/en/software/junos/layer-2-bridging/index.html)

=== "Arista EOS"
    ```arista-eos
    ! View MAC address table
    show mac address-table

    ! Clear dynamic entries
    clear mac address-table dynamic

    ! Set aging time
    mac address-table aging-time 300
    ```
    Arista EOS MAC table commands are nearly identical to Cisco IOS-XE.

    Full configuration reference: [Arista EOS Layer 2 Configuration](https://www.arista.com/en/um-eos/eos-layer-2-switching)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # View MAC table (bridge host table)
    /interface bridge host print

    # Clear dynamic entries
    /interface bridge host remove [find dynamic=yes]

    # Set bridge aging time
    /interface bridge set bridge1 ageing-time=5m

    # Configure bridge (required for L2 switching)
    /interface bridge add name=bridge1
    /interface bridge port add interface=ether1 bridge=bridge1
    /interface bridge port add interface=ether2 bridge=bridge1
    ```
    RouterOS implements switching via the **bridge** interface. Each bridge is a separate switching domain. Ports must be added to a bridge to participate in L2 switching. Hardware offload (`hw=yes`) is supported on platforms with switch chips.

    Full configuration reference: [MikroTik Bridge Reference](https://help.mikrotik.com/docs/display/ROS/Bridge)

---

## Common Pitfalls

### Pitfall 1: MAC flapping indicating a loop

MAC address `AA:BB:CC` flapping between port Gi0/1 and Gi0/2 repeatedly means the switch is receiving frames with that source MAC from two different ports — almost always a Layer 2 loop. Without STP, this causes a broadcast storm. Check physical cabling and STP state immediately.

### Pitfall 2: Unknown unicast flooding causing bandwidth issues

If a server MAC ages out (went silent for 300+ seconds) and then starts receiving traffic again, the switch floods until it learns the server's MAC from the server's response. In high-traffic environments, this momentary flood can saturate access ports. Fix: configure static MAC entries for critical servers, or reduce the aging time on ports connected to always-active servers.

### Pitfall 3: Full MAC table on a switch under attack

A MAC flooding attack (sending frames with thousands of different random source MACs) fills the CAM table, causing all traffic to be flooded. An attacker with a port mirroring connection can capture all traffic. Mitigation: Port Security (SW-005) — limits the number of MAC addresses allowed per port.

---

## Practice Problems

1. A switch has the following MAC table: `Gi0/1: AA:BB:CC:11:22:33`, `Gi0/2: AA:BB:CC:44:55:66`. A frame arrives on Gi0/1 with Dst=`AA:BB:CC:44:55:66`. What does the switch do?

2. Same switch. A frame arrives on Gi0/1 with Dst=`AA:BB:CC:99:99:99` (not in table). What does the switch do? What happens to port Gi0/1?

3. A frame arrives on Gi0/1 with Dst=`ff:ff:ff:ff:ff:ff`. What does the switch do? Is this normal?

4. What is the difference between a collision domain and a broadcast domain? How does a switch affect each?

5. Device A (on Gi0/1) unplugs and plugs into Gi0/3. Before any traffic is sent from Device A, a frame arrives destined for Device A's MAC. What happens?

??? "Answers"
    **1.** `AA:BB:CC:44:55:66` is in the table → port Gi0/2. Switch **forwards** the frame out Gi0/2 only.

    **2.** Destination unknown → switch **floods** out all ports except Gi0/1 (ingress). Port Gi0/1 is excluded from flooding; it receives no copy of its own frame.

    **3.** Broadcast address → switch **floods** out all ports except Gi0/1. This is normal — ARP requests, DHCP discovers, and other broadcast protocols rely on this behaviour.

    **4.** A **collision domain** is the set of devices that share a medium and must take turns (CSMA/CD). A switch creates one collision domain per port — devices don't compete with each other. A **broadcast domain** is the set of devices that receive broadcast frames. A switch does NOT break broadcast domains by default — all ports in the same VLAN are in the same broadcast domain. Only routers (or VLANs) separate broadcast domains.

    **5.** The MAC table still shows Device A → Gi0/1 (old entry, not yet aged out). The switch **forwards** the frame to Gi0/1 — the device is no longer there and the frame is dropped. This continues until the MAC table entry ages out (up to 300 seconds), at which point future frames are flooded — and Device A responds on Gi0/3, updating the table.

---

## Summary & Key Takeaways

- A switch operates at **Layer 2** — it reads MAC addresses, not IP addresses
- Three core operations: **learn** (source MAC → port), **flood** (unknown/broadcast/multicast), **forward** (known unicast → specific port)
- The **MAC address table** (CAM table) maps MAC addresses to ports; entries age out after ~300 seconds by default
- Switches create one **collision domain per port** — full-duplex ports have zero collisions
- Switches do **not** break broadcast domains — VLANs and routers do
- **Flooding** is the fallback for unknown destinations — normal during learning, problematic if it persists
- **MAC flapping** = same MAC seen on two ports rapidly = almost always a loop
- A full MAC table causes all traffic to be flooded — both a performance issue and a security risk (mitigated by Port Security)

---

## Where to Next

- **Continue:** [VLANs & 802.1Q Trunking](vlans-8021q.md) (`SW-002`) — segment the switch into multiple broadcast domains
- **Continue:** [Spanning Tree Protocol](spanning-tree.md) (`SW-003`) — prevent loops from forming in redundant switched networks
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) — Stage 2, position 6 in the DNE path

---

## Standards & Certifications

**Relevant standards:**
- [IEEE 802.1D — MAC Bridging and Spanning Tree](https://standards.ieee.org/ieee/802.1D/3958/)
- [IEEE 802.3 — Ethernet](https://standards.ieee.org/ieee/802.3/7071/)

**Benchmark certifications:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 2.1 — Describe and verify switching concepts |
| JNCIA-Junos JN0-103 | Juniper | Layer 2 bridging fundamentals |
| Nokia NRS I | Nokia | Ethernet switching basics |

---

## References

- IEEE — IEEE 802.1D-2004: Media Access Control (MAC) Bridges
- IETF — [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348) — background on why L2 scaling matters
- Odom, W. — *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2019 — Ch. 5–7 (Ethernet switching)

---

## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Draft written by Claude Sonnet 4.6. Technical accuracy to be verified by human reviewer.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [SW-002](vlans-8021q.md) | VLANs & 802.1Q | VLAN builds on MAC table and broadcast domain concepts | 2026-04-19 |
| [SW-003](spanning-tree.md) | Spanning Tree | STP builds on flooding and loop concepts | 2026-04-19 |
| [SW-005](port-security.md) | Port Security | Port security limits MAC learning per port | 2026-04-19 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [NW-001](../networking/osi-model.md) | The OSI Model | Layer 2 operation; MAC addresses | 2026-04-19 |
| [NW-002](../networking/network-topologies.md) | Network Topologies | Collision and broadcast domains | 2026-04-19 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Arista EOS | MikroTik RouterOS |
|---|---|---|---|---|---|
| View MAC table | IEEE 802.1D | `show mac address-table` | `show ethernet-switching table` | `show mac address-table` | `/interface bridge host print` |
| Clear MAC table | IEEE 802.1D | `clear mac address-table dynamic` | `clear ethernet-switching table` | `clear mac address-table dynamic` | Remove dynamic entries |
| MAC aging time | IEEE 802.1D | `mac address-table aging-time` | `set vlans X mac-aging-time` | `mac address-table aging-time` | `/interface bridge set ageing-time` |

<!-- XREF-END -->
