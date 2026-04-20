---
id: QOS-003
title: "Queuing Mechanisms"
description: "How routers schedule packets for transmission — from FIFO to LLQ — and how each mechanism affects delay, jitter, and fairness."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - QOS-001
  - QOS-002
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - qos
  - queuing
  - llq
  - cbwfq
  - wfq
  - fifo
  - scheduling
created: 2026-04-19
updated: 2026-04-19
---

# QOS-003 — Queuing Mechanisms

## The Problem

A router's output interface is a single serialisation point — packets leave one at a time. When more packets arrive than the link can send, packets queue. A single queue (FIFO) serves packets in arrival order — no priority. A VoIP packet arriving just after a 1500-byte backup packet waits until the backup packet finishes serialising. At 1 Mbps, that's ~12 ms just for one packet — unacceptable when accumulated over several hops.

### Step 1: Multiple queues

Create a separate queue for each traffic class. When a packet arrives, it goes to its class's queue based on its DSCP marking (done in QOS-002). The scheduler cycles through queues to decide which one to serve next.

### Step 2: Strict priority for delay-sensitive traffic

One queue — voice — must be served first, always. Every time a scheduler cycle runs, if the voice queue has any packet, serve it before anything else. This is **strict priority** (PQ). Voice packets experience near-zero queuing delay.

Risk: if voice traffic is too heavy, it monopolises the link and starves all other queues. Police voice traffic to a maximum bandwidth to prevent this.

### Step 3: Weighted fair queuing for everything else

Remaining queues share the link according to weights — a queue configured for 20% of bandwidth gets roughly 20% even under congestion. This is **CBWFQ (Class-Based Weighted Fair Queuing)**. Higher-priority data classes get more weight; bulk traffic gets the minimum needed.

The combination of a strict priority queue for voice and weighted fair queuing for everything else is **LLQ — Low Latency Queuing** — the standard QoS architecture for enterprise WAN links.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Single queue, first-in first-out | FIFO |
| Fair queue per flow | WFQ (Weighted Fair Queuing) |
| Weighted queues by class | CBWFQ |
| Strict priority queue for voice | PQ (Priority Queuing) |
| PQ + CBWFQ combined | LLQ (Low Latency Queuing) |
| Proactive drop before queue fills | WRED (Weighted Random Early Detection) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain how queuing delay occurs and why it matters for voice.
2. Describe FIFO, WFQ, CBWFQ, and LLQ and when each is appropriate.
3. Explain why strict priority queuing requires policing.
4. Configure LLQ with CBWFQ using Cisco MQC.
5. Describe WRED and how it differentially drops packets before queue exhaustion.

---

## Prerequisites

- QOS-001 — QoS Fundamentals (delay, jitter, traffic classes)
- QOS-002 — Classification & Marking (DSCP values, MQC class-maps)

---

## Core Content

### Why Queuing Matters

Queuing delay occurs when the output link is busy and a packet must wait. At 1.5 Mbps (T1):
- A 1500-byte packet takes: `(1500 × 8) / 1,500,000 = 8ms` to serialise.
- If 10 such packets queue before a 64-byte VoIP packet, the VoIP packet waits 80ms in queue alone — before propagation delay.
- LLQ eliminates this by letting voice skip the queue.

### FIFO — First In, First Out

The default when no QoS policy is applied. A single queue; packets leave in arrival order. Simple but no differentiation. Under congestion, all flows share the same queue equally in order of arrival — a flood of bulk traffic delays all interactive sessions.

### WFQ — Weighted Fair Queuing

WFQ automatically creates per-flow queues (no configuration needed). Each flow gets a share of bandwidth inversely proportional to its IP precedence — lower-priority flows get less, higher-priority get more. Better than FIFO for fairness but doesn't provide the explicit class guarantees that enterprise QoS requires.

WFQ is the Cisco default on low-speed interfaces (< 2 Mbps) and a useful baseline, but CBWFQ/LLQ replaced it for most deployments.

### CBWFQ — Class-Based Weighted Fair Queuing

CBWFQ extends WFQ to operator-defined traffic classes. Each class gets:
- A **bandwidth guarantee**: minimum percentage or absolute kbps. Guaranteed even under congestion.
- A **maximum** (optional): limits how much a class can use above its guarantee.
- A **queue depth** (packets or bytes): determines how many packets buffer before tail-drop occurs.

The remaining bandwidth after guarantees are met is distributed fairly among classes. No strict priority — every class waits its turn in the weighted schedule.

### PQ — Priority Queuing (Legacy)

The original strict priority system: four queues (High, Medium, Normal, Low). High queue is served until empty, then Medium, etc. Voice in High gets served immediately but Low traffic can starve indefinitely. PQ has been superseded by LLQ for most use cases.

### LLQ — Low Latency Queuing

LLQ = **strict priority queue (PQ) for voice + CBWFQ for everything else**.

- The priority class is served first, every scheduling cycle. Near-zero queuing delay.
- The priority class must be **policed** — limit the bandwidth it can claim. Without policing, a burst of voice traffic (or misconfigured traffic marked EF) can starve all other classes. The policer ensures voice never exceeds its reserved bandwidth.
- Remaining classes use CBWFQ with bandwidth guarantees.

Standard LLQ architecture:

| Class | Queue type | Bandwidth |
|---|---|---|
| Voice (EF) | Strict priority (policed) | 10–20% of link |
| Video (AF41) | CBWFQ | 20% |
| Signalling (CS3) | CBWFQ | 5% |
| Transactional (AF21) | CBWFQ | 30% |
| Bulk (AF11) | CBWFQ | 10% |
| Best effort (CS0) | CBWFQ / default | Remainder |
| Scavenger (CS1) | CBWFQ | < 1% |

### WRED — Weighted Random Early Detection

WRED proactively drops packets before the queue fills completely, preventing tail-drop (where all new packets are dropped when the queue is full). It randomly drops packets from lower-priority classes (AF drop precedence 3 → 2 → 1) as the queue fills — signalling TCP to slow down before the queue reaches capacity.

Benefits:
- Prevents global synchronisation (all TCP flows backing off simultaneously and then simultaneously resuming).
- Differentiates between AF11 (low drop precedence) and AF13 (high drop precedence) — the network infrastructure enforces the drop differentiation defined by the AF classes.
- Not used on the strict priority queue (voice must not be randomly dropped).

---

## Vendor Implementations

=== "Cisco IOS-XE (LLQ with CBWFQ)"

    ```
    ! Class maps (assumed defined in QOS-002)
    ! Policy map with LLQ
    policy-map WAN-QOS
     class VOICE            ! EF traffic
      priority percent 15   ! Strict priority, policed at 15%
     class VIDEO            ! AF41 traffic
      bandwidth percent 20
     class SIGNALLING       ! CS3 traffic
      bandwidth percent 5
     class TRANSACTIONAL    ! AF21 traffic
      bandwidth percent 30
     class BULK             ! AF11 traffic
      bandwidth percent 10
      random-detect dscp-based
     class class-default
      fair-queue
      bandwidth percent 15

    ! Apply outbound on WAN interface
    interface Serial0/0/0
     service-policy output WAN-QOS

    ! Verification
    show policy-map interface Serial0/0/0
    show queue Serial0/0/0
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_plcshp/configuration/xe-17/qos-plcshp-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_plcshp/configuration/xe-17/qos-plcshp-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # Forwarding classes already defined (see QOS-002)
    # Scheduler — define per-class bandwidth and priority
    set class-of-service schedulers VOICE transmit-rate percent 15 priority strict-high
    set class-of-service schedulers VIDEO transmit-rate percent 20 priority high
    set class-of-service schedulers SIGNALLING transmit-rate percent 5 priority medium-high
    set class-of-service schedulers BULK transmit-rate percent 10 priority low
    set class-of-service schedulers DEFAULT transmit-rate remainder priority low

    # Scheduler map
    set class-of-service scheduler-maps WAN-SCHED forwarding-class voice scheduler VOICE
    set class-of-service scheduler-maps WAN-SCHED forwarding-class video scheduler VIDEO

    # Apply to interface
    set class-of-service interfaces ge-0/0/0 scheduler-map WAN-SCHED

    # Verification
    show class-of-service interface ge-0/0/0
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-schedulers-overview.html](https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-schedulers-overview.html)

---

## Common Pitfalls

1. **Priority queue not policed.** A strict priority queue without a policer can starve other queues if voice traffic (or mismarked traffic using the priority queue) exceeds its expected bandwidth. Always configure `priority percent <n>` — this sets both the priority scheduling AND the policer.

2. **Total bandwidth guarantees exceed 100%.** CBWFQ bandwidth guarantees must sum to ≤ 100% (accounting for the priority queue's share). If they exceed 100%, the configuration is rejected or behaves unpredictably.

3. **Queuing only on congested interfaces.** Queuing policies are only active when the interface is congested (output queue > 1 packet). On uncongested links, all packets flow immediately regardless of QoS config. This is expected behaviour — QoS is for congestion management.

4. **Wrong interface for service-policy.** LLQ is typically applied **output** on the WAN interface (the congestion point). Applying it on the wrong interface or direction has no effect on the intended traffic.

5. **WRED on priority queue.** WRED should never be configured on the strict priority voice queue — randomly dropping voice packets defeats the purpose. Apply WRED only to CBWFQ data classes (bulk/best-effort) where TCP can retransmit.

---

## Practice Problems

**Q1.** A WAN interface runs LLQ with voice at 15% strict priority. The 1 Mbps WAN link is 95% utilised. A burst of 200 kbps of traffic marked EF arrives. What happens?

??? answer
    The priority queue is policed at 15% of 1 Mbps = 150 kbps. The 200 kbps burst exceeds the policer — 50 kbps excess is dropped or remarked (depending on policer action). The remaining 150 kbps goes through the priority queue with near-zero queuing delay. The policer protects other classes from starvation.

**Q2.** What is the difference between CBWFQ bandwidth guarantee and strict priority?

??? answer
    A CBWFQ **bandwidth guarantee** ensures a class receives at minimum the configured percentage of bandwidth — but the class must wait its turn in the weighted schedule (round-robin among classes). There is a small queuing delay. A **strict priority** queue is served first at every scheduling cycle — packets in the priority queue never wait behind lower-priority packets. Strict priority gives near-zero queuing delay; CBWFQ gives fairness and throughput guarantees.

**Q3.** Why is WRED preferred over tail-drop for bulk data classes?

??? answer
    Tail-drop drops all new packets when the queue is full. All TCP flows on that interface simultaneously detect packet loss, simultaneously back off (halving window sizes), then simultaneously resume — **global synchronisation** creates oscillating congestion. WRED randomly drops individual packets from individual flows before the queue is full, spreading the congestion signal across flows at different times — preventing global synchronisation and maintaining higher sustained throughput.

---

## Summary & Key Takeaways

- Queuing delay is the variable QoS targets — it occurs when packets wait behind others at a congested output interface.
- **FIFO:** No differentiation; all packets equal; adequate only for lightly loaded links.
- **WFQ:** Per-flow fairness; automatic; good baseline for slow interfaces.
- **CBWFQ:** Explicit bandwidth guarantees per class; weighted round-robin scheduling.
- **LLQ:** Strict priority queue for voice (always served first, policed) + CBWFQ for everything else. The standard enterprise QoS architecture.
- The priority queue MUST be policed — otherwise it starves other classes under load.
- **WRED:** Proactive random early detection; drops lower-priority packets before queue exhaustion; prevents global TCP synchronisation.
- QoS is active only under congestion; no effect on a lightly loaded link.

---

## Where to Next

- **QOS-004 — Policing & Shaping:** Rate limiting to control ingress/egress bandwidth.
- **QOS-005 — QoS in MPLS Networks:** DSCP maps to MPLS EXP/TC bits for per-hop treatment across MPLS cores.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2309 | Recommendations on Queue Management and Congestion Avoidance (RED/WRED) |
| RFC 3246 | Expedited Forwarding PHB (LLQ rationale) |
| Cisco CCNP Enterprise | CBWFQ, LLQ, WRED configuration |

---

## References

- RFC 2309 — Recommendations on Queue Management and Congestion Avoidance in the Internet. [https://www.rfc-editor.org/rfc/rfc2309](https://www.rfc-editor.org/rfc/rfc2309)
- RFC 3246 — An Expedited Forwarding PHB. [https://www.rfc-editor.org/rfc/rfc3246](https://www.rfc-editor.org/rfc/rfc3246)

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
| QOS-004 | Policing & Shaping | Policing limits priority queue bandwidth |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| QOS-001 | QoS Fundamentals | Delay and jitter — why queuing matters |
| QOS-002 | Classification & Marking | DSCP markings used to assign packets to queues |
<!-- XREF-END -->
