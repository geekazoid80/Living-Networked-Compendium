---
id: QOS-004
title: "Traffic Policing & Shaping"
description: "How policing (drop/re-mark) and shaping (delay/buffer) enforce rate limits on traffic flows, and when to use each mechanism."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 35
prerequisites:
  - QOS-001
  - QOS-003
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - qos
  - policing
  - shaping
  - token-bucket
  - rate-limiting
  - congestion-management
created: 2026-04-19
updated: 2026-04-19
---

# QOS-004 — Traffic Policing & Shaping

## The Problem

You have a 10 Mbps WAN link and you've sold an enterprise customer 5 Mbps. If that customer bursts to 9 Mbps, other customers' traffic suffers. You need a mechanism to enforce the customer's contracted rate.

Two choices: drop excess immediately or delay it. Dropping is fast and stateless — it works well for protecting other traffic but causes TCP retransmissions. Delaying smooths the burst into a consistent flow — better for applications that don't tolerate sudden loss, but requires a buffer.

### Step 1: The token bucket model

Imagine a bucket that fills with tokens at a steady rate (one token per bit of contracted bandwidth, per time interval). To send a packet, a sender must remove tokens equal to the packet size. If enough tokens exist, the packet is sent — permitted. If the bucket is empty (no tokens), the packet is either dropped (policing) or held until tokens arrive (shaping).

Burst allowance: the bucket has a maximum depth — it can accumulate tokens up to a burst size (Bc), allowing a short burst above the average rate.

### Step 2: Policing vs shaping

**Policing:** Packets arriving when the bucket is empty are dropped or re-marked (change DSCP to a lower value — e.g., AF11 → AF13). No buffering. Instantaneous enforcement. Used for inbound rate enforcement and at the LLQ priority queue.

**Shaping:** Packets arriving when the bucket is empty are buffered and sent when tokens become available. Traffic is smoothed — no sudden drops. Used for outbound WAN to match the ISP's committed rate. Requires memory for the shaping buffer.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Token accumulation model | Token bucket |
| Drop or re-mark excess packets | Policing |
| Delay excess packets in a buffer | Shaping |
| Contracted average rate | CIR (Committed Information Rate) |
| Allowed burst size | Bc (Committed Burst) |
| Optional excess burst | Be (Excess Burst) |
| Dual-rate policer (CIR + PIR) | Two-rate three-colour marker (RFC 2698) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain the token bucket model and its parameters (CIR, Bc, Be).
2. Distinguish policing and shaping — mechanism, use case, and effect on traffic.
3. Describe single-rate and dual-rate policing (two-rate three-colour).
4. Configure traffic policing and shaping using Cisco MQC.
5. Identify when to use policing vs shaping in a network design.

---

## Prerequisites

- QOS-001 — QoS Fundamentals (bandwidth, delay concepts)
- QOS-003 — Queuing Mechanisms (LLQ priority policing context)

---

## Core Content

### Token Bucket Parameters

| Parameter | Abbreviation | Description |
|---|---|---|
| Committed Information Rate | CIR | Average rate the bucket fills at (the contracted rate) |
| Committed Burst | Bc | Maximum burst allowed at or below CIR (token bucket depth) |
| Excess Burst | Be | Additional burst allowed above CIR (only for single-rate shaping) |
| Peak Information Rate | PIR | Second token bucket rate (dual-rate / two-colour) |

Interval: `Tc = Bc / CIR`. At each interval, `Bc` tokens are added. If the bucket is full, tokens overflow and are lost.

### Single-Rate Two-Colour Policing

Two outcomes: conform (tokens available → permit) or exceed (no tokens → drop or re-mark).

```
! Cisco: police at 5 Mbps CIR, drop excess
police rate 5000000 bps burst 10000 byte conform-action transmit exceed-action drop
```

**Re-mark exceed action:** Instead of dropping, lower the DSCP — e.g., AF11 → AF13. The packet is sent but has high drop precedence. WRED will drop AF13 first under congestion — the packet may survive if the network is lightly loaded, but it's sacrificed first when congestion occurs. This is "soft policing" — more user-friendly than hard drop.

### Two-Rate Three-Colour Policing (RFC 2698)

Two token buckets: CIR bucket and PIR (Peak Information Rate) bucket. Three outcomes:

- **Conform** (green): within CIR — transmit at original DSCP.
- **Exceed** (yellow): between CIR and PIR — re-mark to lower DSCP.
- **Violate** (red): above PIR — drop.

Useful for ISP bandwidth tiers: a customer pays for 5 Mbps committed (CIR) but the contract allows up to 10 Mbps (PIR) with lower priority. Traffic between 5–10 Mbps is yellow and will be dropped before green traffic under congestion.

```
! Two-rate three-colour
police rate 5000000 bps burst 100000 byte
        peak-rate 10000000 bps peak-burst 200000 byte
        conform-action transmit
        exceed-action set-dscp-transmit af12
        violate-action drop
```

### Traffic Shaping

Shaping uses a token bucket but instead of dropping excess packets, it queues them. The shaping buffer (holding queue) accumulates excess traffic and releases it when tokens become available — smoothing bursts into a consistent stream at the CIR.

**When to use shaping:**
- Outbound to an ISP that polices your traffic: send at exactly the ISP's CIR to avoid the ISP's policer dropping your traffic.
- Frame Relay or ATM circuits with a CIR (legacy, but the concept applies to any constrained link).
- Avoid sudden TCP retransmissions triggered by policing drops.

**Cost:** Memory for the shaping buffer. If the buffer fills (sustained overload), packets are tail-dropped from the shaping queue.

**Generic Traffic Shaping (GTS) / Class-Based Shaping:** Cisco supports class-based shaping within a policy-map using `shape average` — shapes each class independently.

```
policy-map WAN-SHAPING
 class VOICE
  shape average 1500000    ! Shape voice to 1.5 Mbps
 class class-default
  shape average 3500000    ! Shape rest to 3.5 Mbps
```

### Hierarchical QoS (HQoS)

For WAN with multiple customers or VCs, a parent policy shapes the aggregate and a child policy applies per-class queuing within the shaped limit:

```
policy-map PARENT-SHAPE
 class class-default
  shape average 5000000
  service-policy LLQ-CHILD    ! Apply child LLQ within shaped bandwidth
```

The child policy (LLQ-CHILD) performs priority queuing and CBWFQ within the 5 Mbps window. This ensures voice gets strict priority AND the total link usage doesn't exceed the ISP's CIR.

### Policing vs Shaping — Decision Guide

| Scenario | Use |
|---|---|
| Limit customer traffic rate (inbound to your network) | Policing |
| Limit voice priority queue (LLQ) | Policing |
| Match ISP's CIR for outbound traffic | Shaping |
| Smooth bursty TCP application | Shaping |
| ISP interface with hard rate limit | Shaping (or both: shape then police) |
| Re-mark excess traffic to lower DSCP | Policing with re-mark exceed-action |

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Policing with re-mark
    policy-map POLICE-CUSTOMERS
     class CUSTOMER-TRAFFIC
      police rate 5000000 bps burst 100000 byte
              conform-action transmit
              exceed-action set-dscp-transmit af12
              violate-action drop

    ! Shaping
    policy-map SHAPE-TO-ISP
     class class-default
      shape average 10000000    ! 10 Mbps CIR

    ! HQoS — shape + child LLQ
    policy-map PARENT-SHAPE
     class class-default
      shape average 10000000
      service-policy LLQ-CHILD

    ! Apply
    interface GigabitEthernet0/0
     service-policy input POLICE-CUSTOMERS     ! Police inbound
    interface Serial0/0
     service-policy output SHAPE-TO-ISP        ! Shape outbound

    ! Verification
    show policy-map interface GigabitEthernet0/0
    show traffic-shape interface Serial0/0
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_plcshp/configuration/xe-17/qos-plcshp-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_plcshp/configuration/xe-17/qos-plcshp-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # Policing
    set firewall policer CUSTOMER-POLICER if-exceeding bandwidth-limit 5m
    set firewall policer CUSTOMER-POLICER if-exceeding burst-size-limit 100k
    set firewall policer CUSTOMER-POLICER then discard

    # Apply policer in firewall filter
    set firewall family inet filter RATE-LIMIT term POLICE from ...
    set firewall family inet filter RATE-LIMIT term POLICE then policer CUSTOMER-POLICER

    # Traffic shaping — via scheduler with transmit-rate
    set class-of-service schedulers SHAPED-CLASS transmit-rate 10m
    set class-of-service scheduler-maps SHAPED-MAP forwarding-class default scheduler SHAPED-CLASS
    set class-of-service interfaces ge-0/0/0.0 scheduler-map SHAPED-MAP
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-policers-overview.html](https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-policers-overview.html)

---

## Common Pitfalls

1. **Shaping inbound traffic (applying shaping on ingress).** Shaping buffers excess packets and releases them at the CIR — this requires the device to receive the packets first. You cannot shape traffic arriving from outside your network (you receive it at whatever rate the sender uses). Only police inbound; shape outbound.

2. **Burst size too small.** A very small Bc means the shaper or policer triggers on any short burst — including normal TCP acknowledgement bursts. Set Bc to at least 1.5× the largest expected packet size, typically `Bc = CIR × Tc` where Tc is 100–200ms.

3. **Shaping without LLQ inside the shaped class.** If you shape the entire output but don't apply a child LLQ, voice and data share the shaped queue equally — voice still experiences queuing delay from bulk traffic. Always apply a child QoS policy within the shaping.

4. **Two-rate policing with PIR < CIR.** PIR must always be ≥ CIR. Configuring PIR < CIR results in most traffic being in the "violate" (red) bucket and dropped.

5. **Applying both policing and shaping on the same interface in the same direction.** This is possible (and sometimes intentional with HQoS) but requires careful design. Shaping then policing (or policing then queuing into a shaped class) creates complex interactions. Document the intent clearly.

---

## Practice Problems

**Q1.** A policer is configured at CIR = 5 Mbps, exceed-action = drop. A customer sends a 7 Mbps burst for 100ms. What happens?

??? answer
    The initial burst up to Bc tokens is transmitted. Once tokens are exhausted (very quickly at 7 Mbps > 5 Mbps), the excess 2 Mbps above the token replenishment rate is dropped. The customer sees ~5 Mbps of throughput sustained; ~2 Mbps of traffic is dropped (TCP retransmissions occur for dropped TCP segments).

**Q2.** Why is shaping preferred over policing on the outbound WAN interface when connecting to an ISP?

??? answer
    The ISP's ingress policer will drop traffic exceeding the contracted CIR. If your router sends a burst to the ISP, the ISP drops it — causing TCP retransmissions and higher application-layer latency. If your router shapes to the ISP's CIR, it absorbs bursts in its shaping buffer and releases traffic smoothly at the CIR — the ISP's policer never triggers, and TCP performs better.

**Q3.** What is the difference between a two-colour and three-colour policer?

??? answer
    A **two-colour policer** (single-rate) has two outcomes: conform (within CIR → transmit) and exceed (above CIR → drop or re-mark). A **three-colour policer** (two-rate, RFC 2698) has two token buckets (CIR and PIR) and three outcomes: conform/green (within CIR → transmit), exceed/yellow (between CIR and PIR → re-mark to lower DSCP), and violate/red (above PIR → drop). The yellow traffic survives if network capacity allows but is dropped first under congestion.

---

## Summary & Key Takeaways

- **Token bucket model:** tokens fill at CIR; packets consume tokens; empty bucket = conform/exceed/violate.
- **Policing:** drops or re-marks excess packets immediately. Fast, stateless. Use for inbound rate enforcement.
- **Shaping:** buffers excess packets, releases at CIR. Smooth output, no sudden TCP drops. Use outbound toward ISP or constrained links.
- **Bc (burst):** must be large enough to allow normal packet-level bursts without false triggering.
- **Two-rate three-colour:** CIR + PIR; green/yellow/red; yellow re-marked and conditionally dropped under congestion.
- Apply **shaping + child LLQ** (HQoS) on shaped WAN interfaces so voice gets priority within the shaped bandwidth window.
- Shape outbound; police inbound. You cannot shape traffic you haven't received yet.

---

## Where to Next

- **QOS-005 — QoS in MPLS Networks:** DSCP maps to MPLS TC (EXP) bits for per-hop QoS in MPLS cores.
- **CT-001 — MPLS Fundamentals:** MPLS label header includes TC (EXP) bits for QoS.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2697 | Single Rate Three Colour Marker |
| RFC 2698 | Two Rate Three Colour Marker |
| RFC 4115 | Differentiated Services Two-Rate, Three-Color Marker |
| Cisco CCNP Enterprise | Policing, shaping, HQoS configuration |

---

## References

- RFC 2697 — Single Rate Three Colour Marker. [https://www.rfc-editor.org/rfc/rfc2697](https://www.rfc-editor.org/rfc/rfc2697)
- RFC 2698 — Two Rate Three Colour Marker. [https://www.rfc-editor.org/rfc/rfc2698](https://www.rfc-editor.org/rfc/rfc2698)

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
| QOS-005 | QoS in MPLS Networks | MPLS TC bits carry QoS marking through the core |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| QOS-001 | QoS Fundamentals | CIR, bandwidth, token bucket concepts |
| QOS-003 | Queuing Mechanisms | LLQ strict priority requires policing |
<!-- XREF-END -->
