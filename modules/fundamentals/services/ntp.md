---
module_id: SV-004
title: "NTP - Network Time Protocol"
description: "How NTP synchronises clocks across network devices using a stratum hierarchy, and why accurate time is critical for network operations."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 30
prerequisites:
  - IP-001
  - RT-001
learning_path_tags:
  - DNE
difficulty: beginner
tags:
  - ntp
  - time-synchronisation
  - services
  - layer7
created: 2026-04-19
updated: 2026-04-19
---

# SV-004 - NTP - Network Time Protocol
## Learning Objectives

After completing this module you will be able to:

1. Explain why accurate time matters for network operations and security.
2. Describe the NTP stratum hierarchy and how accuracy degrades with each hop.
3. Distinguish NTP client mode, server mode, and peer mode.
4. Configure an NTP client and NTP server on router platforms.
5. Verify NTP synchronisation status.
6. Explain PTP/IEEE 1588 and when it is needed over NTP.

---
## Prerequisites

- IP-001 - IP Addressing Fundamentals
- RT-001 - Routing Fundamentals (reachability to NTP servers)

---
## The Problem

A router logs an event at 03:47:12 and a firewall logs a related event at 14:23:05. These timestamps are meaningless for correlation - the clocks drifted. Security incidents, routing protocol adjacency timers, Kerberos authentication tickets, log correlation, and certificate validation all require clocks to agree within seconds. Hardware clocks drift. Without synchronisation, every device tells its own time.

### Step 1: One device knows the correct time

An authoritative time source - a GPS receiver, an atomic clock, a radio clock - provides the reference time. Every other device sets its clock from this source.

### Step 2: Hierarchy for scale

One reference clock can't serve millions of devices directly. A **stratum hierarchy** distributes the load: the atomic clock is stratum 0 (it's not a network device), the server connected to it is stratum 1 (the most accurate network-reachable source), the servers synchronising from stratum 1 are stratum 2, and so on. Each level adds a small amount of error but distributes query load across many servers.

### Step 3: Continuous adjustment, not one-time sync

Clocks drift continuously. NTP doesn't just set the clock once - it periodically re-queries the server and applies **slew corrections** (gradual adjustments) to keep the clock accurate without disrupting time-sensitive applications. Only if the clock is very far off does NTP **step** (jump) the clock.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Atomic clock / GPS time source | Stratum 0 reference clock |
| Network device directly connected to stratum 0 | Stratum 1 server |
| Layer in the NTP hierarchy | Stratum level |
| Gradual clock adjustment | Slew |
| Instantaneous clock correction | Step |
| Client that both receives and provides time | NTP peer |

---
## Core Content

### Why Time Matters

| Use case | Time requirement |
|---|---|
| Log correlation (syslog, SNMP) | Seconds - events must be cross-referenced across devices |
| Kerberos authentication | ±5 minutes - tickets rejected if clocks differ more |
| TLS/X.509 certificates | Days - valid-from/valid-to dates checked against current time |
| OSPF/BGP hold timers | Seconds - not clock-based, but protocol state may log with timestamps |
| TACACS+/RADIUS accounting | Accurate timestamps in accounting records for billing/compliance |
| Forensics and incident response | Sub-second correlation across dozens of devices |
| RSVP-TE / circuit provisioning | Synchronised activation windows |

### The Stratum Hierarchy

```
[Atomic clock / GPS]  ← Stratum 0 (not a network device)
       |
[NTP stratum 1 server]  ← directly attached to reference clock
       |
[NTP stratum 2 server]  ← syncs from stratum 1
       |
[NTP stratum 3 client]  ← e.g., your routers and switches
```

- Stratum 0: Physical reference (GPS, cesium clock, CDMA). Not a network entity - it's the input to a stratum 1 server.
- Stratum 1: The first network-accessible tier. Examples: time.google.com, time.cloudflare.com, pool.ntp.org.
- Stratum 2–15: Synchronised from the layer above. Error accumulates slightly per level; stratum 3–4 is sufficient for enterprise networking.
- Stratum 16: Unsynchronised - clock is not reliable.

### NTP Modes

| Mode | Description |
|---|---|
| **Client** | Queries one or more servers, adjusts its own clock. Does not serve time. |
| **Server** | Receives queries from clients, provides time. Must be synchronised itself. |
| **Peer** | Two devices mutually synchronise - used between distribution and core devices for resilience. |
| **Broadcast/Multicast** | Server sends periodic time announcements; clients apply without querying. Less accurate. |

### NTP Authentication

NTP traffic can be spoofed - a fake NTP server could cause a device to adopt incorrect time, breaking Kerberos, certificates, and logging. **NTP authentication** uses a shared key (MD5 or SHA-1) to verify that responses come from a trusted server.

NTP version 4 (RFC 5905, current standard) supports authentication and IPv6.

### PTP / IEEE 1588 - When NTP Is Not Enough

NTP achieves accuracy of **1–50 milliseconds** over the internet, **< 1 ms** on a LAN. This is sufficient for most network operations.

**PTP (Precision Time Protocol / IEEE 1588)** achieves **sub-microsecond accuracy** by using hardware timestamping at the physical layer. Required for:

- Financial trading (sub-millisecond regulatory requirements).
- Mobile networks (5G RAN synchronisation - requires ±1.5 µs).
- Industrial control systems, power grid synchronisation (SyncE + PTP).
- Telecom carrier nodes where ITU-T G.8265/G.8275 standards apply.

PTP uses a **Grandmaster Clock** (analogous to NTP's stratum 1) and requires network devices to support **transparent clock** or **boundary clock** modes for accurate hardware timestamping at each hop.

---
## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Configure NTP servers (prefer a local stratum 2 server)
    ntp server 10.0.0.10 prefer
    ntp server 1.1.1.1

    ! Set time zone
    clock timezone SGT 8

    ! Configure device as an NTP server for downstream clients
    ntp master 3          ! Device acts as stratum 3 server if upstream unreachable
                          ! (use only if you have a real upstream reference)

    ! NTP authentication
    ntp authenticate
    ntp authentication-key 1 md5 MySecretKey
    ntp trusted-key 1
    ntp server 10.0.0.10 key 1

    ! Verification
    show ntp status
    show ntp associations
    show clock detail
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/bsm/configuration/xe-17/bsm-xe-17-book/bsm-time-ntp.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/bsm/configuration/xe-17/bsm-xe-17-book/bsm-time-ntp.html)

=== "Juniper (Junos)"

    ```
    set system ntp server 10.0.0.10 prefer
    set system ntp server 1.1.1.1
    set system time-zone Asia/Singapore

    # NTP authentication
    set system ntp authentication-key 1 type md5 value "MySecretKey"
    set system ntp server 10.0.0.10 key 1
    set system ntp trusted-key 1

    # Verification
    show ntp status
    show ntp associations
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/ntp-edit-system.html](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/ntp-edit-system.html)

=== "MikroTik RouterOS"

    ```
    # NTP client
    /system ntp client set enabled=yes servers=10.0.0.10,1.1.1.1

    # Time zone
    /system clock set time-zone-name=Asia/Singapore

    # NTP server (for downstream devices)
    /system ntp server set enabled=yes

    # Verification
    /system ntp client print
    /system clock print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/NTP](https://help.mikrotik.com/docs/display/ROS/NTP)

---
## Common Pitfalls

1. **`ntp master` without a real upstream reference.** On Cisco, `ntp master` makes the device act as a stratum server for downstream clients even if it has no valid time source. Used in isolation, it lets the device's drifting hardware clock become the authoritative time source for the network - silently degrading accuracy. Only use `ntp master` with a real upstream NTP reference.

2. **NTP blocked by firewall.** NTP uses **UDP port 123**. If the ACL or firewall doesn't permit UDP 123 to NTP servers, clients will never synchronise. Check with `debug ntp events` or verify `show ntp status` shows `unsynchronised`.

3. **Not configuring NTP authentication.** An attacker who can insert NTP responses can shift a device's clock by hours - defeating Kerberos authentication and invalidating log timestamps. Always enable NTP authentication with a shared key on production devices.

4. **All devices pointing to external NTP servers.** In large networks, all devices querying external public NTP servers creates unnecessary external traffic and adds latency. Configure 2–3 internal NTP servers (stratum 2) that synchronise from external sources, then point all devices to the internal servers.

5. **Clock jumping and syslog correlation errors.** A sudden clock step (jump) can cause syslog timestamps to go backward or forward, breaking log correlation tools. NTP uses **slew** (gradual adjustment at ≤0.5 ms/s) for small corrections and only steps for large offsets. Verify that your NTP implementation is slewing, not stepping, under normal operation.

---
## Practice Problems

**Q1.** A device shows `stratum 16` in `show ntp status`. What does this mean and how do you fix it?

??? answer
    Stratum 16 means the device is not synchronised - it has no valid time reference. The device either can't reach its configured NTP servers (check connectivity and UDP 123 firewall rules) or the servers haven't been configured. Fix by verifying reachability to NTP servers and checking `show ntp associations` for the association state.

**Q2.** Your Kerberos authentication is failing intermittently. What NTP-related issue could cause this?

??? answer
    Kerberos rejects authentication tickets if the clock difference between client and KDC exceeds 5 minutes (the default max skew). If NTP is not configured or clocks have drifted, authentication will fail. Verify NTP synchronisation on all Kerberos clients and the KDC.

**Q3.** What is the difference between NTP slew and NTP step?

??? answer
    NTP **slew** gradually adjusts the clock rate (up to ±0.5 ms per second) to bring it into sync without a sudden jump - suitable for small offsets. NTP **step** jumps the clock immediately - used when the offset is too large for slew (typically > 128 ms in many implementations). Stepping can disrupt time-sensitive processes but is necessary when clocks are far out of sync.

---
## Summary & Key Takeaways

- Accurate time is critical for log correlation, Kerberos, certificate validation, billing, and forensics.
- NTP uses a **stratum hierarchy**: stratum 1 (connected to reference clock) → stratum 2 → stratum 3...
- Stratum 16 means **unsynchronised**.
- NTP uses **UDP port 123**.
- NTP **slews** (gradually adjusts) for small offsets; **steps** (jumps) for large offsets.
- Use **NTP authentication** (shared key) to prevent spoofed time sources.
- For sub-millisecond accuracy (5G, financial trading, carrier), use **PTP/IEEE 1588** instead.
- Run 2–3 internal NTP servers; point all devices to them rather than to external sources directly.

---
## Where to Next

- **SV-005 - SNMP & Syslog:** Network monitoring - both rely on accurate timestamps.
- **SEC-004 - AAA (TACACS+ & RADIUS):** Kerberos authentication requires synchronised clocks.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 5905 | Network Time Protocol Version 4 |
| IEEE 1588-2019 | Precision Clock Synchronization Protocol (PTP) |
| ITU-T G.8275.1 | Telecom profile for PTP in packet networks |
| Cisco CCNA | NTP configuration and verification |
| CompTIA Network+ | NTP concepts, time synchronisation importance |

---
## References

- RFC 5905 - Network Time Protocol Version 4: Protocol and Algorithms Specification. [https://www.rfc-editor.org/rfc/rfc5905](https://www.rfc-editor.org/rfc/rfc5905)

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
| SV-005 | SNMP & Syslog | Accurate timestamps depend on NTP |
| SEC-004 | AAA - TACACS+ & RADIUS | Kerberos requires NTP for ticket validation |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | NTP uses UDP/IP for transport |
| RT-001 | Routing Fundamentals | Reachability to NTP servers |
<!-- XREF-END -->
