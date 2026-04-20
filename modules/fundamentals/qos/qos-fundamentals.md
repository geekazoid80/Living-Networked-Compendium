---
module_id: QOS-001
title: "QoS Fundamentals - Delay, Jitter, Loss & Bandwidth"
description: "The four metrics that define network quality for different traffic types, and the QoS framework for managing them."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 35
prerequisites:
  - IP-001
  - RT-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - qos
  - delay
  - jitter
  - packet-loss
  - bandwidth
  - network-quality
created: 2026-04-19
updated: 2026-04-19
---

# QOS-001 - QoS Fundamentals - Delay, Jitter, Loss & Bandwidth
## Learning Objectives

After completing this module you will be able to:

1. Define the four key QoS metrics: delay, jitter, loss, and bandwidth.
2. Explain why different traffic types have different QoS requirements.
3. Describe the QoS framework: classify → mark → queue → schedule → police/shape.
4. Explain the trust boundary concept.
5. Describe DSCP and 802.1p as the primary marking mechanisms.
6. Identify ITU-T G.114 delay recommendations for voice.

---
## Prerequisites

- IP-001 - IP Addressing Fundamentals (IP header structure)
- RT-001 - Routing Fundamentals (packets and interfaces)

---
## The Problem

A network carries voice calls, video conferencing, bulk file transfers, and background backups simultaneously. All traffic shares the same physical links. When the link is lightly loaded, everything works. When it's congested, the router drops the newest arriving packet. Voice calls start sounding choppy; video freezes; file transfers slow down.

The problem is that all packets are treated identically - a 1500-byte backup chunk has the same priority as a 64-byte VoIP packet. But these traffic types have completely different requirements: VoIP needs low delay and zero loss; backup traffic needs bandwidth but tolerates long delay.

### Step 1: Measure what different traffic actually needs

VoIP: delay sensitive (one-way delay must be < 150ms), jitter sensitive (variance in delay must be < 30ms), loss sensitive (> 1% loss = unintelligible call). Bandwidth: small (64–128 kbps per call).

Bulk data: delay tolerant (a few extra seconds doesn't matter), jitter tolerant, loss tolerant (TCP retransmits), bandwidth hungry.

### Step 2: Mark traffic by type

Packets are tagged with a priority marker so every device in the network knows what kind of traffic it is - without inspecting the full packet. Layer 3 uses DSCP in the IP header; Layer 2 uses 802.1p PCP in the VLAN tag. This marking happens once (at the edge) and persists through the network.

### Step 3: Manage queues and bandwidth

Each router maintains separate queues per traffic class. Delay-sensitive traffic gets a dedicated high-priority queue that is served first. Bandwidth-guaranteed traffic gets a minimum reservation. Background traffic uses only what's left. When congestion occurs, the router drops from low-priority queues first - preserving voice and video quality.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Time for a packet to cross the network | Delay / latency |
| Variation in delay between packets | Jitter |
| Percentage of packets not delivered | Packet loss |
| Maximum data rate on a link | Bandwidth |
| Tagging packets by traffic type | Classification & marking |
| Separating traffic into priority groups | Queue management (QoS) |

---
## Core Content

### The Four QoS Metrics

**Delay (Latency):** The one-way time for a packet to travel from source to destination. Components:

| Component | Cause |
|---|---|
| Propagation delay | Speed of light × distance (irreducible) |
| Serialisation delay | Time to put bits on the wire (packet size ÷ link speed) |
| Processing delay | Time to make a forwarding decision (minimal on modern hardware) |
| Queuing delay | Time spent waiting in a queue (the main variable QoS controls) |

**ITU-T G.114:** Recommends one-way delay < 150ms for voice; 150–400ms is acceptable with degraded quality; > 400ms is unacceptable.

**Jitter:** The variation in delay between consecutive packets. Voice and video codecs buffer a small amount of audio/video (the jitter buffer) to smooth out variation - if jitter exceeds the buffer size, packets arrive too late to be used. Typically < 30ms target for voice.

**Packet loss:** Percentage of packets that don't arrive. TCP retransmits lost packets (adds delay). UDP (used by voice/video) does not retransmit - lost packets are permanently gone. > 1% loss on VoIP causes noticeable degradation; > 5% is typically unacceptable.

**Bandwidth:** The maximum data rate the link can carry. QoS cannot create more bandwidth - it can only allocate existing bandwidth more appropriately. If total demand exceeds link capacity, QoS determines who gets priority but cannot eliminate the shortfall.

### QoS Traffic Classes

A common starting framework (based on RFC 4594 and Cisco SRND):

| Class | Traffic type | Delay | Jitter | Loss | Priority |
|---|---|---|---|---|---|
| Voice (EF) | RTP audio | < 150ms | < 30ms | < 1% | Highest - strict priority |
| Interactive video | Videoconferencing | < 150ms | < 30ms | < 1% | High |
| Call signalling | SIP, H.323 | < 150ms | Moderate | Low | Medium-high |
| Transactional | ERP, database | < 500ms | Moderate | Low | Medium |
| Bulk data | File transfers, backups | Hours acceptable | Don't care | Low (TCP retransmits) | Low |
| Scavenger | Peer-to-peer, unknown | Don't care | Don't care | Don't care | Lowest |
| Network control | Routing protocols | < 500ms | Low | Low | High (but small volume) |

### The QoS Process

QoS is a pipeline applied at each router interface:

```
Ingress traffic
    ↓
[Classify] — identify traffic type (by DSCP, protocol, port, ACL)
    ↓
[Mark] — stamp the DSCP/PCP value (at trust boundary only)
    ↓
[Police/Shape] — limit rate inbound
    ↓
[Queue] — sort into priority queues
    ↓
[Schedule] — determine output order (strict priority / weighted fair)
    ↓
[Congestion avoidance] — WRED drops low-priority packets before queue fills
    ↓
Egress
```

### The Trust Boundary

Devices can self-mark their traffic. An IP phone marks its audio as EF (Expedited Forwarding, DSCP 46) - the highest priority. A workstation could mark all its packets EF to jump the queue. The **trust boundary** is where the network stops trusting the endpoint's marking and re-marks based on its own classification.

Typical trust boundary: the access switch port connected to the IP phone or PC. The switch re-classifies based on port or CoS (802.1p), assigns DSCP, and trusts nothing from the device itself.

Some environments trust IP phones but re-mark workstation traffic to CS0 (best effort).

### DSCP - Differentiated Services Code Point

DSCP uses the **6 most significant bits of the IP Type of Service (ToS) byte** (rebranded as the DS field, RFC 2474). 64 possible values (0–63), grouped into Per-Hop Behaviours (PHBs):

| PHB | DSCP value | Binary | Use case |
|---|---|---|---|
| CS0 (Best Effort) | 0 | 000000 | Default - no priority |
| CS1 | 8 | 001000 | Scavenger |
| AF11–AF13 | 10, 12, 14 | - | Low-priority elastic data |
| AF21–AF23 | 18, 20, 22 | - | High-priority elastic data |
| AF31–AF33 | 26, 28, 30 | - | Multimedia streaming |
| AF41–AF43 | 34, 36, 38 | - | Multimedia conferencing |
| CS6 | 48 | 110000 | Network control (routing protocols) |
| EF | 46 | 101110 | Expedited Forwarding - voice |

**EF (DSCP 46):** Guarantees low latency, low jitter, low loss. Used exclusively for VoIP media (RTP). Must be strictly policed - if non-voice traffic gets marked EF, it starves the voice queue or is dropped.

**AF classes (Assured Forwarding):** Four classes (AF1x–AF4x), three drop precedence levels within each (AFxy where y=1 low drop, y=2 medium drop, y=3 high drop). Under congestion, WRED drops AFx3 before AFx2 before AFx1.

### 802.1p / PCP

In Layer 2 networks, QoS is marked using the **3-bit PCP (Priority Code Point)** field in the 802.1Q VLAN tag. Values 0–7 (lower = less priority; 7 = highest).

Common mapping:
- 7: Network critical (STP, routing protocol control)
- 5–6: Voice and video
- 3–4: Call signalling, important data
- 0–2: Best effort, scavenger

PCP is only present in 802.1Q-tagged frames. On untagged links, DSCP carries the marking.

---
## Common Pitfalls

1. **Assuming QoS can create bandwidth.** QoS only prioritises existing bandwidth. If a 10 Mbps link is carrying 15 Mbps of traffic, QoS can ensure voice gets its 1 Mbps - but the remaining 9 Mbps must drop the 5 Mbps excess. QoS doesn't fix an undersized link.

2. **Marking everything EF.** If too many traffic flows are marked EF (Expedited Forwarding), the strict priority queue becomes the busiest queue - defeating its purpose. Police EF traffic at the edge; only VoIP RTP should use EF.

3. **Trusting endpoint markings.** A misconfigured or malicious endpoint marking all traffic EF can starve legitimate voice traffic. Enforce re-marking at the trust boundary (access switch).

4. **QoS inconsistently applied.** QoS must be configured consistently on every hop. A router with no QoS policy treats all packets equally - voice traffic waits behind bulk data in a single FIFO queue. Audit every interface in the voice path.

5. **Forgetting WAN interfaces.** QoS is most critical on the lowest-bandwidth link in the path (usually the WAN uplink). Configuring QoS only on LAN interfaces misses the actual bottleneck.

---
## Practice Problems

**Q1.** A VoIP call carries 64 kbps of audio. The one-way delay measured is 160ms. Is this within ITU-T G.114 recommendations?

??? answer
    Borderline - ITU-T G.114 recommends one-way delay < 150ms for voice. 160ms falls in the "acceptable with degraded quality" range (150–400ms). It may be noticeable to users. Investigate queuing delay in the path - that's the component QoS can reduce.

**Q2.** What DSCP value is used for VoIP RTP media traffic and why is it specially treated?

??? answer
    EF (Expedited Forwarding), DSCP 46. EF defines a "Low Latency, Low Loss, Low Jitter" Per-Hop Behaviour - routers that implement EF schedule it with the highest priority, minimal queuing delay. It's specifically designed for real-time voice traffic. It must be policed strictly: only VoIP RTP should carry DSCP 46.

**Q3.** Why is jitter more damaging to VoIP than to file transfers?

??? answer
    VoIP uses UDP (no retransmission) and has a small jitter buffer (typically 20–60ms). If packet arrival variance exceeds the buffer, late packets are discarded - causing audio gaps. File transfers use TCP, which retransmits any lost or delayed packets; jitter just means the transfer takes longer but all data arrives intact. VoIP is real-time - late data is useless.

---
## Summary & Key Takeaways

- The four QoS metrics: **delay** (latency), **jitter** (delay variance), **loss** (dropped packets), **bandwidth** (link capacity).
- QoS **cannot create bandwidth** - it only distributes existing capacity more effectively.
- VoIP requirements: delay < 150ms (ITU G.114), jitter < 30ms, loss < 1%.
- **DSCP** (6-bit in IP header) and **802.1p PCP** (3-bit in 802.1Q tag) are the standard marking mechanisms.
- **EF (DSCP 46):** Expedited Forwarding - for voice RTP only. Strict priority queue.
- **Trust boundary:** Where the network stops trusting endpoint markings and re-marks based on policy.
- QoS pipeline: Classify → Mark → Police/Shape → Queue → Schedule → Congestion Avoidance.

---
## Where to Next

- **QOS-002 - Classification & Marking:** How to classify traffic and mark DSCP/802.1p at the trust boundary.
- **QOS-003 - Queuing Mechanisms:** FIFO, WFQ, CBWFQ, LLQ - how routers schedule packets.
- **QOS-004 - Policing & Shaping:** Rate limiting mechanisms.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2474 | Definition of the Differentiated Services Field (DSCP) |
| RFC 2597 | Assured Forwarding PHB Group |
| RFC 3246 | Expedited Forwarding PHB |
| RFC 4594 | Configuration Guidelines for DiffServ |
| ITU-T G.114 | Maximum tolerable delay for voice applications |
| IEEE 802.1p | Priority Code Point (now part of 802.1Q) |
| Cisco CCNP Enterprise | QoS fundamentals, DSCP, marking, queuing |
| CompTIA Network+ | QoS concepts |

---
## References

- RFC 2474 - Definition of the Differentiated Services Field. [https://www.rfc-editor.org/rfc/rfc2474](https://www.rfc-editor.org/rfc/rfc2474)
- RFC 3246 - An Expedited Forwarding PHB. [https://www.rfc-editor.org/rfc/rfc3246](https://www.rfc-editor.org/rfc/rfc3246)
- RFC 4594 - Configuration Guidelines for DiffServ. [https://www.rfc-editor.org/rfc/rfc4594](https://www.rfc-editor.org/rfc/rfc4594)
- ITU-T G.114 - One-Way Transmission Time. [https://www.itu.int/rec/T-REC-G.114/en](https://www.itu.int/rec/T-REC-G.114/en)

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
| QOS-002 | Classification & Marking | DSCP marking - the implementation of QoS concepts |
| QOS-003 | Queuing Mechanisms | Queue scheduling - the enforcement mechanism |
| QOS-004 | Policing & Shaping | Rate control - the bandwidth enforcement |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | ToS/DSCP field in the IP header |
| RT-001 | Routing Fundamentals | QoS applied at router interfaces |
<!-- XREF-END -->
