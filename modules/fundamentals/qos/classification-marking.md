---
id: QOS-002
title: "QoS Classification & Marking"
description: "How routers identify traffic types using classification (ACL, DSCP, NBAR) and mark them with DSCP and 802.1p values for consistent QoS treatment downstream."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 35
prerequisites:
  - QOS-001
  - SEC-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - qos
  - classification
  - marking
  - dscp
  - 802.1p
  - nbar
  - mls-qos
created: 2026-04-19
updated: 2026-04-19
---

# QOS-002 — QoS Classification & Marking

## The Problem

Traffic arrives on a router interface. The router doesn't know if it's a VoIP call, a video stream, or a bulk backup. Without knowing the type, every packet gets the same queue. Classification is the act of identifying what the traffic is; marking is the act of stamping that identity into the packet header so every subsequent device can act on it without re-classifying.

### Step 1: Identify traffic at the edge

The first device in the network — the access switch or ingress router — inspects arriving packets. It matches traffic based on: source/destination IP, protocol and port number, DSCP value already set (if trusted), or application fingerprint. Each match maps to a traffic class.

### Step 2: Re-mark DSCP

The edge device stamps the DSCP field of each packet with the value appropriate for its class (EF for voice, AF41 for video, etc.). This mark travels with the packet through the entire network — every downstream device reads it and applies the right QoS treatment without re-inspecting the payload.

### Step 3: At the trust boundary, stop trusting endpoints

An IP phone marks its own traffic EF — that's fine if we trust IP phones. A workstation might also mark EF — that's not acceptable. The trust boundary policy: trust the phone (it's managed); re-mark the workstation to CS0 (best effort).

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Identifying traffic type | Classification |
| Stamping the DSCP value | Marking |
| Matching by IP/port/protocol | ACL-based classification |
| Matching by application fingerprint | NBAR (Network-Based Application Recognition) |
| Where re-marking occurs | Trust boundary |
| MQC — policy framework on Cisco | Modular QoS CLI (class-map + policy-map) |

---

## Learning Objectives

After completing this module you will be able to:

1. Describe classification methods: ACL match, DSCP match, NBAR.
2. Configure Cisco MQC class-maps and policy-maps for classification and marking.
3. Explain the trust boundary and configure `mls qos trust` on access switches.
4. Map between 802.1p PCP values and DSCP values.
5. Configure DSCP marking on at least two vendor platforms.

---

## Prerequisites

- QOS-001 — QoS Fundamentals (DSCP values, traffic classes, trust boundary concept)
- SEC-001 — ACLs (ACL syntax used in class-map match rules)

---

## Core Content

### Classification Methods

**1. ACL / Prefix-list match:** Match source/destination IP, protocol, port. The most common and explicit method. Requires maintenance as services change IPs or ports.

**2. DSCP match:** Trust the existing DSCP marking if the source is trusted (managed device, upstream QoS-enabled network). Simpler — classify once at the edge, trust everywhere else.

**3. Protocol / Port match:** Match by well-known port number (TCP 5060 = SIP, UDP 5004/5005 = RTP). More specific than ACL IP matching but still brittle if applications use non-standard ports.

**4. NBAR (Network-Based Application Recognition):** Deep packet inspection classifies applications by their payload signature, regardless of port. Recognises thousands of applications (Cisco proprietary capability). Used for dynamic port applications (RTP media port negotiated by SIP; Skype; QUIC).

### Cisco MQC — Modular QoS CLI

Cisco uses a three-stage configuration model:

**1. class-map:** Define a match condition.
```
class-map match-all VOICE-RTP
 match dscp ef
```

or:
```
class-map match-all VOICE-RTP
 match protocol rtp audio    ! NBAR match
```

**2. policy-map:** Define the action for each class.
```
policy-map CLASSIFY-AND-MARK
 class VOICE-RTP
  set dscp ef
 class BULK-DATA
  set dscp af11
 class class-default
  set dscp default
```

**3. service-policy:** Apply to an interface.
```
interface GigabitEthernet0/1
 service-policy input CLASSIFY-AND-MARK
```

**match-all:** All match conditions must be true (AND).
**match-any:** Any match condition being true is sufficient (OR).

### DSCP ↔ 802.1p Mapping

When a packet crosses between Layer 3 and Layer 2 domains, DSCP must be mapped to 802.1p (and vice versa). Routers and switches use a default or configured mapping table:

| 802.1p PCP | DSCP | Traffic class |
|---|---|---|
| 7 | CS7 (56) | Reserved / Network critical |
| 6 | CS6 (48) | Network control (routing) |
| 5 | EF (46) | Voice |
| 4 | AF41 (34) | Video conferencing |
| 3 | AF31 (26) | Call signalling |
| 2 | AF21 (18) | Transactional data |
| 1 | AF11 (10) | Bulk data |
| 0 | CS0 (0) | Best effort |

This mapping is bidirectional: packets entering an 802.1Q trunk from a DSCP-marked WAN link get PCP set; packets leaving toward the WAN get DSCP set from PCP.

### Trust Configurations on Access Switches

Access switches sit at the trust boundary. A switch port connected to an IP phone can be set to trust the phone's DSCP or 802.1p values:

```
! Cisco: trust DSCP markings from the IP phone
interface GigabitEthernet0/1
 mls qos trust dscp

! Trust CoS (802.1p) from the phone — convert to DSCP using default map
interface GigabitEthernet0/1
 mls qos trust cos

! Trust nothing — re-mark based on port class (most restrictive)
interface GigabitEthernet0/1
 mls qos trust cos
 mls qos cos 0    ! Override all CoS to 0 (best effort)
```

For ports connected to PCs (untrusted endpoints):
```
! Re-mark all traffic from PC to DSCP 0 (best effort)
interface GigabitEthernet0/2
 mls qos cos 0
```

### Egress Marking on Routers

At the WAN edge, traffic leaving to the internet must be marked with DSCP values the ISP has agreed to honour. Unmarked traffic (DSCP 0) may still be carried but the ISP's network treats it all as best effort.

Before the WAN policy is applied, classify inbound LAN traffic and mark DSCP at the ingress of the WAN interface (or at the edge of the LAN). If the ISP uses a different DSCP scheme (re-marking at their ingress), the marking may be overridden — check ISP QoS SLA documentation.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Class maps
    class-map match-any VOICE
     match dscp ef
    class-map match-any VIDEO
     match dscp af41
    class-map match-any SIGNALLING
     match dscp cs3 af31
    class-map match-any BULK
     match dscp af11 af12 af13 cs1

    ! Policy map (classification and marking)
    policy-map EDGE-MARK
     class VOICE
      set dscp ef
     class VIDEO
      set dscp af41
     class SIGNALLING
      set dscp cs3
     class BULK
      set dscp af11
     class class-default
      set dscp default

    ! Apply inbound on access interface
    interface GigabitEthernet0/1
     service-policy input EDGE-MARK

    ! Trust DSCP on uplink interface
    interface GigabitEthernet0/24
     mls qos trust dscp

    ! Verification
    show policy-map interface GigabitEthernet0/1
    show mls qos interface GigabitEthernet0/24
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_classn/configuration/xe-17/qos-classn-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_classn/configuration/xe-17/qos-classn-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # Define forwarding classes
    set class-of-service forwarding-classes class voice queue-num 5 priority high
    set class-of-service forwarding-classes class video queue-num 4 priority medium-high

    # DSCP classifier
    set class-of-service classifiers dscp DSCP-CLASSIFIER forwarding-class voice loss-priority low code-points ef
    set class-of-service classifiers dscp DSCP-CLASSIFIER forwarding-class video loss-priority low code-points af41

    # Rewrite rule (mark outbound)
    set class-of-service rewrite-rules dscp DSCP-REWRITE forwarding-class voice loss-priority low code-point ef

    # Apply to interface
    set class-of-service interfaces ge-0/0/1 classifiers dscp DSCP-CLASSIFIER
    set class-of-service interfaces ge-0/0/1 rewrite-rules dscp DSCP-REWRITE

    # Verification
    show class-of-service interface ge-0/0/1
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-classifiers-overview.html](https://www.juniper.net/documentation/us/en/software/junos/cos/topics/topic-map/cos-classifiers-overview.html)

=== "MikroTik RouterOS"

    ```
    # Mangle rule for classification and marking
    /ip firewall mangle
    add chain=prerouting protocol=udp dst-port=5004-5005 action=mark-packet new-packet-mark=voice passthrough=no comment="Voice RTP"
    add chain=prerouting protocol=tcp dst-port=5060 action=mark-packet new-packet-mark=signalling passthrough=no comment="SIP"

    # Queue tree uses packet marks
    /queue tree
    add name=voice parent=global packet-mark=voice priority=1 max-limit=5M
    add name=signalling parent=global packet-mark=signalling priority=2 max-limit=1M

    # Verification
    /ip firewall mangle print stats
    /queue tree print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/Mangle](https://help.mikrotik.com/docs/display/ROS/Mangle)

---

## Common Pitfalls

1. **Classifying too late.** Classification and marking should happen at the very first device the packet touches (access switch or ingress router). Marking in the core of the network means all the queuing decisions before the marking point were made without QoS information.

2. **Over-trusting endpoint markings.** Trusting PC DSCP markings allows any application to mark itself EF and bypass QoS policies. Only trust markings from managed, controlled sources (IP phones, WAN edges with agreed QoS SLAs).

3. **class-default not set.** If `class-default` has no action, traffic not matching any class-map gets default treatment (usually best effort). Always explicitly set `class class-default` → `set dscp default` or `set dscp cs0` to ensure consistent marking.

4. **NBAR performance impact.** NBAR deep packet inspection adds CPU load — significant on high-throughput interfaces. Use NBAR at access/edge; rely on DSCP trust in the core.

5. **Mismatched DSCP ↔ 802.1p mapping tables.** Default tables vary by platform. A mismatch means a packet marked EF at Layer 3 might get PCP 0 (best effort) at Layer 2 on a different vendor's switch — losing priority at the trunk. Verify mapping tables explicitly at all Layer 2/Layer 3 boundaries.

---

## Practice Problems

**Q1.** A class-map is configured with `match-all` and two match conditions: `match dscp ef` and `match protocol rtp`. A VoIP RTP packet arrives marked DSCP EF. Does it match?

??? answer
    Yes — it matches both conditions (DSCP EF AND protocol RTP). With `match-all`, both conditions must be true. If either doesn't match, the packet doesn't match the class-map and falls to the next class or `class-default`.

**Q2.** An IP phone port on a switch is set to `mls qos trust cos`. The phone sends 802.1Q-tagged frames with PCP 5. What happens?

??? answer
    The switch trusts the 802.1p PCP value of 5 and maps it to the corresponding DSCP value (typically EF or AF41 depending on the CoS-to-DSCP map). The packet is placed in the appropriate QoS queue. The switch does not re-mark or override the phone's CoS marking.

---

## Summary & Key Takeaways

- **Classification** identifies traffic type; **marking** stamps DSCP into the packet header.
- Mark once at the edge (**trust boundary**); all downstream devices act on the DSCP value.
- Cisco MQC uses: **class-map** (match conditions) → **policy-map** (actions) → **service-policy** (interface binding).
- DSCP key values: **EF (46)** = voice, **AF4x** = video, **CS6 (48)** = routing control, **CS0** = best effort.
- Trust only managed, controlled devices; re-mark untrusted endpoints to CS0.
- **NBAR** identifies applications by payload signature — use at the edge, not in the core.

---

## Where to Next

- **QOS-003 — Queuing Mechanisms:** How classified traffic is scheduled in queues.
- **QOS-004 — Policing & Shaping:** Rate control at the trust boundary.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2474 | Differentiated Services Field (DSCP) |
| RFC 2597 | Assured Forwarding PHB Group |
| RFC 3246 | Expedited Forwarding PHB |
| IEEE 802.1p | 802.1p PCP (Priority Code Point) |
| Cisco CCNP Enterprise | MQC, class-map, policy-map, NBAR, trust |

---

## References

- RFC 2474 — Definition of the Differentiated Services Field. [https://www.rfc-editor.org/rfc/rfc2474](https://www.rfc-editor.org/rfc/rfc2474)
- RFC 2597 — Assured Forwarding PHB Group. [https://www.rfc-editor.org/rfc/rfc2597](https://www.rfc-editor.org/rfc/rfc2597)
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
| QOS-003 | Queuing Mechanisms | Queuing uses DSCP class to determine queue assignment |
| QOS-004 | Policing & Shaping | Policing applied to classified traffic |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| QOS-001 | QoS Fundamentals | DSCP values, trust boundary concept |
| SEC-001 | Access Control Lists | ACL match syntax used in class-map |
<!-- XREF-END -->
