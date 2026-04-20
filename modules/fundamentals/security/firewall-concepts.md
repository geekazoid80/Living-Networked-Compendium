---
id: SEC-002
title: "Firewall Concepts"
description: "How stateful firewalls track connection state to make per-packet decisions, and how zone-based policy models organise security policy at scale."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - SEC-001
  - IP-001
  - RT-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - firewall
  - security
  - stateful-inspection
  - zone-based
  - packet-filtering
created: 2026-04-19
updated: 2026-04-19
---

# SEC-002 — Firewall Concepts

## The Problem

You have an ACL permitting TCP traffic from the internet to your web server on port 443. But TCP port 443 can carry malformed packets, packets with unusual flag combinations, and packets that don't belong to any established session. An ACL can only match what's in the packet header — it can't tell if a packet is part of a legitimate session or a crafted attack.

Additionally: your users can initiate TCP connections outbound to any internet server. The responses come back inbound. To permit responses, your ACL needs a rule permitting all TCP traffic with ACK set inbound — but the `established` keyword is a blunt instrument. An attacker can set ACK on any packet.

### Step 1: Track the connection

Instead of evaluating each packet in isolation, the router tracks the state of every TCP connection and UDP flow. When a user inside initiates a TCP connection, the firewall records: "session exists between 192.168.1.5:52000 and 93.184.216.34:443." When a response arrives, the firewall verifies it matches a known session — correct source, correct destination, correct TCP sequence number range. Unsolicited inbound packets that don't match any session are dropped. This is **stateful inspection**.

### Step 2: Zone-based policy

As the network grows — internal users, servers, VoIP phones, partners, guest WiFi, internet — writing individual interface-based ACL rules for every combination becomes unmaintainable. Instead, group interfaces into **security zones** (trust, untrust, DMZ, voice). Write policies between zones: "trust → untrust: permit HTTP/HTTPS" rather than per-interface rules. A new interface assigned to an existing zone inherits the zone's policies automatically.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Tracking TCP/UDP session state per-flow | Stateful inspection |
| Firewall drops packets not matching a session | Default deny (stateful) |
| Logical grouping of interfaces | Security zone |
| Policy applied between zones | Zone policy |
| Server segment exposed to limited internet access | DMZ |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain the difference between stateless ACL filtering and stateful inspection.
2. Describe what information a stateful firewall tracks in its session table.
3. Explain zone-based security models and how policies are applied between zones.
4. Describe the DMZ and why it is architecturally separate from the internal network.
5. Identify common firewall evasion techniques (fragmentation, application-layer tunnelling).
6. Describe the role of NGFW capabilities (application awareness, IPS, TLS inspection).

---

## Prerequisites

- SEC-001 — Access Control Lists (stateless filtering — the prerequisite)
- IP-001 — IP Addressing Fundamentals
- RT-001 — Routing Fundamentals (firewall sits at routing boundaries)

---

## Core Content

### Stateless vs Stateful

| Property | Stateless (ACL) | Stateful (Firewall) |
|---|---|---|
| Evaluates each packet | Independently | In context of its session |
| Tracks TCP sequence numbers | No | Yes |
| Automatically permits return traffic | No (needs explicit rule) | Yes (session tracking) |
| Detects invalid flag combinations | No | Yes |
| Memory required | None (no state) | Per-session state table |
| Performance | Very fast | Slightly higher overhead |
| Attack surface | TCP flag spoofing, ACK bypass | Session table exhaustion (SYN flood) |

A stateful firewall maintains a **session table** (also: connection table, state table) that records:
- Source IP:port
- Destination IP:port
- Protocol (TCP/UDP/ICMP)
- Current TCP state (SYN-sent, established, FIN-wait)
- Timeout value
- Associated security policy

Inbound packets are checked against the session table first. If they match an existing session and the TCP state is valid, they are forwarded without further policy lookup. Unmatched packets go through policy evaluation.

### TCP State Tracking

For TCP sessions, the firewall verifies:

- **SYN:** New connection initiated from the permitted direction.
- **SYN-ACK:** Response from the server — expected direction, matches session.
- **Established:** Ongoing data exchange.
- **FIN / RST:** Session teardown — firewall removes the session table entry after appropriate timeout.
- **Invalid:** Packets with nonsense flag combinations (SYN+FIN, no flags set, etc.) are dropped.

This prevents a class of attacks where attackers send packets with unexpected flag combinations to bypass ACL rules.

### UDP and ICMP State

UDP is connectionless — there's no handshake. Stateful firewalls handle it by:
- Creating a pseudo-session when an outbound UDP packet is seen.
- Permitting inbound UDP responses from the same source IP:port within a timeout window (typically 30–300 seconds).
- Dropping inbound UDP that doesn't match a pseudo-session.

ICMP is handled similarly — outbound echo-request creates a session; inbound echo-reply is permitted.

### Zone-Based Security Model

Interfaces are assigned to zones. Policies are applied between zone pairs:

```
[Internal VLAN 10] ─┐
[Internal VLAN 20] ─┤ TRUST zone ──→ UNTRUST zone ←── [Internet WAN]
[Wi-Fi]            ─┘
                              ↕
                           DMZ zone ─── [Web Server]
                                    ─── [Mail Server]
```

Zone rules:
- **Intra-zone:** Traffic between interfaces in the same zone — typically permitted by default (though not universal across all platforms).
- **Inter-zone:** Traffic crossing zone boundaries — denied by default, permitted only by explicit policy.
- **Self zone:** Traffic destined to the firewall itself (SSH management, SNMP, routing protocols) — controlled separately.

Each zone policy specifies: source zone, destination zone, match criteria (application, IP, port, user identity on NGFW), and action (permit, deny, log, inspect).

### The DMZ

**DMZ (Demilitarised Zone):** A network segment between the internal trusted network and the external internet. Servers in the DMZ (web, mail, DNS) are accessible from the internet but cannot initiate connections to the internal trusted network.

Typical zone policies for a DMZ:

| Source zone | Dest zone | Action |
|---|---|---|
| Untrust (internet) | DMZ | Permit HTTPS to web server IP only |
| DMZ | Untrust | Permit outbound for software updates |
| Trust (internal) | DMZ | Permit management protocols (SSH) |
| DMZ | Trust | **Deny all** — compromised DMZ server cannot reach internal network |
| Trust | Untrust | Permit HTTP/HTTPS, DNS |
| Untrust | Trust | **Deny all** |

The key security principle: a compromised DMZ server cannot be used to pivot into the internal network.

### SYN Flood — Session Table Exhaustion

A **SYN flood attack** sends thousands of TCP SYN packets per second, each with a spoofed source IP. The firewall creates a session table entry for each — the server sends SYN-ACKs that are never answered, and the session table fills. Legitimate connections are rejected.

Mitigation:
- **SYN cookies:** The firewall responds to SYN with a SYN-ACK without creating a full session entry. Only when a valid ACK is received does the full session get created.
- **Rate limiting SYN:** Limit new SYN packets per source per second.
- **Half-open session timeout:** Expire incomplete sessions quickly.

### Next-Generation Firewall (NGFW)

Traditional stateful firewalls operate at Layer 3/4. **NGFW** adds:

- **Application identification:** Classify traffic by application (Netflix, Zoom, BitTorrent) regardless of port. Block or shape specific applications.
- **User identity:** Policy based on AD/LDAP user, not just IP address.
- **Intrusion Prevention (IPS):** Deep packet inspection for signatures of known attacks, exploits, and malware patterns.
- **TLS/SSL inspection:** Decrypt, inspect, re-encrypt TLS traffic — necessary because most modern traffic is HTTPS. Has privacy implications; requires certificate trust on clients.
- **URL filtering / DNS filtering:** Block categories of web content.

NGFW capabilities come at a significant performance cost — throughput for full DPI is typically 3–10× lower than stateful-only throughput. Size hardware accordingly.

---

## Vendor Implementations

=== "Cisco IOS-XE (Zone-Based Firewall)"

    ```
    ! Define zones
    zone security TRUST
    zone security UNTRUST
    zone security DMZ

    ! Class map — match traffic
    class-map type inspect match-any WEB-TRAFFIC
     match protocol https
     match protocol http

    ! Policy map — action
    policy-map type inspect TRUST-TO-UNTRUST
     class type inspect WEB-TRAFFIC
      inspect
     class class-default
      drop

    ! Zone pair — bind policy to zone pair
    zone-pair security TRUST-UNTRUST source TRUST destination UNTRUST
     service-policy type inspect TRUST-TO-UNTRUST

    ! Assign interfaces to zones
    interface GigabitEthernet0/1
     zone-member security TRUST
    interface GigabitEthernet0/0
     zone-member security UNTRUST
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_zbf/configuration/xe-17/sec-data-zbf-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_zbf/configuration/xe-17/sec-data-zbf-xe-17-book.html)

=== "Juniper SRX (Junos)"

    ```
    # Define zones and interfaces
    set security zones security-zone TRUST interfaces ge-0/0/1.0
    set security zones security-zone UNTRUST interfaces ge-0/0/0.0
    set security zones security-zone DMZ interfaces ge-0/0/2.0

    # Define address book entries
    set security zones security-zone DMZ address-book address WEB-SERVER 10.0.0.100/32

    # Security policy: Trust → Untrust
    set security policies from-zone TRUST to-zone UNTRUST policy ALLOW-WEB match source-address any
    set security policies from-zone TRUST to-zone UNTRUST policy ALLOW-WEB match destination-address any
    set security policies from-zone TRUST to-zone UNTRUST policy ALLOW-WEB match application junos-https
    set security policies from-zone TRUST to-zone UNTRUST policy ALLOW-WEB then permit

    # Default deny (already implicit on SRX — made explicit here)
    set security policies default-policy deny-all

    # Verification
    show security flow session
    show security policies
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-overview.html](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-overview.html)

---

## Common Pitfalls

1. **Not logging denied traffic.** A firewall that silently drops without logging gives no visibility into attack attempts, misconfigurations, or legitimate traffic being incorrectly blocked. Always log deny rules, especially for inter-zone and internet-facing policies.

2. **DMZ policy allowing DMZ → Trust.** The purpose of the DMZ is to isolate potentially compromised servers from the internal network. If a policy exists that permits DMZ servers to initiate connections to internal hosts, a compromised DMZ server can pivot internally. Default-deny DMZ → Trust; permit only explicit management traffic (e.g., monitoring server pull from internal NMS).

3. **TLS inspection certificate not trusted by clients.** TLS inspection requires the firewall to re-sign intercepted connections with its own CA certificate. If clients don't trust the firewall's CA, they receive certificate errors and the inspection breaks legitimate applications. Deploy the firewall's CA to all managed endpoints via GPO/MDM.

4. **Session table exhaustion from misconfiguration.** Long UDP timeouts (e.g., 600s) and high-volume UDP applications (media streaming, DNS) can consume session table memory. Tune UDP timeouts per application profile; separate DNS sessions from long-lived media sessions.

5. **Assuming firewall = ACL.** A stateful firewall that is not inspecting application layer is still blind to application-layer attacks. An NGFW with TLS inspection enabled is the only way to inspect modern encrypted traffic. Both are necessary — ACLs for speed at scale, stateful firewalls at zone boundaries.

---

## Practice Problems

**Q1.** A stateful firewall permits outbound TCP sessions from the trust zone to the internet. A packet arrives inbound on the internet interface: SYN flag set, destination 10.1.1.5:22 (SSH). What does the firewall do?

??? answer
    The firewall checks the session table — no matching session exists for an inbound connection to 10.1.1.5:22. The packet doesn't match any existing outbound session and there is no explicit policy permitting inbound connections to 10.1.1.5:22. The firewall drops it. The stateful firewall's default-deny catches unsolicited inbound traffic automatically — no explicit rule needed.

**Q2.** Why is a DMZ server with a policy permitting DMZ → Trust a significant security risk?

??? answer
    If a web server in the DMZ is compromised (e.g., via CVE exploiting a web application), the attacker gains a foothold inside the network perimeter. With a DMZ → Trust policy, that compromised server can initiate connections to internal databases, file servers, and workstations — a lateral movement path from the DMZ into the protected internal network. The DMZ's purpose is to limit blast radius: the compromise stays isolated in the DMZ.

**Q3.** What is the difference between stateful inspection and an ACL using the `established` keyword?

??? answer
    `established` (stateless) only checks if the ACK or RST bit is set in the TCP header. An attacker can send any packet with ACK set — it matches the rule regardless of whether a real session exists. A stateful firewall maintains the actual session table with session parameters (IP:port pairs, TCP sequence numbers, state) and validates each packet against the tracked session. An ACK-flagged packet for a session that doesn't exist in the table is dropped.

---

## Summary & Key Takeaways

- **Stateful inspection** tracks per-session state — automatically permits return traffic for established sessions; drops unsolicited inbound traffic.
- The **session table** records src/dst IP:port, protocol, TCP state, and timeout.
- **Zone-based policy** groups interfaces into security zones (Trust, Untrust, DMZ) and applies inter-zone policies — much more scalable than per-interface ACLs.
- The **DMZ** isolates servers accessible from the internet — default-deny DMZ → Trust is critical.
- **SYN floods** exhaust the session table; mitigate with SYN cookies and rate limiting.
- **NGFW** adds application identification, user-identity policy, IPS, and TLS inspection — necessary for Layer 7 visibility.
- ACLs (stateless) + stateful firewalls + NGFW are complementary layers; no single layer is sufficient alone.

---

## Where to Next

- **SEC-003 — VPN & IPSec:** Encrypted tunnels across untrusted networks.
- **SEC-006 — Network Segmentation & DMZ:** Advanced segmentation design.
- **RT-001 — Routing Fundamentals:** Firewalls sit at routing boundaries and need to route between zones.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| Cisco CCNA | Firewall concepts, ACL vs stateful |
| Cisco CCNP Security | Zone-based firewall configuration, NGFW |
| CompTIA Security+ | Stateful inspection, DMZ, firewall types |
| CompTIA Network+ | Firewall types, zone concepts |
| NIST SP 800-41 | Guidelines on Firewalls and Firewall Policy |

---

## References

- NIST SP 800-41 Rev.1 — Guidelines on Firewalls and Firewall Policy. [https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final](https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final)

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
| SEC-003 | VPN & IPSec | VPNs terminate on or pass through firewalls |
| SEC-006 | Network Segmentation & DMZ | Zone-based segmentation design |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SEC-001 | Access Control Lists | Stateless filtering — prerequisite and complement |
| IP-001 | IP Addressing Fundamentals | Session table records IP addresses |
| RT-001 | Routing Fundamentals | Firewalls operate at routing zone boundaries |
<!-- XREF-END -->
