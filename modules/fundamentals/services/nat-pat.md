---
id: SV-003
title: "NAT & PAT — Network Address Translation"
description: "How NAT and PAT translate private IP addresses to public IPs, enabling many devices to share a single internet-routable address."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - IP-001
  - IP-002
  - RT-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - nat
  - pat
  - network-address-translation
  - ipv4
  - services
created: 2026-04-19
updated: 2026-04-19
---

# SV-003 — NAT & PAT — Network Address Translation

## The Problem

An organisation has 500 devices, all needing internet access. ISPs sell public IPv4 addresses in small blocks — you get 8 usable addresses. You cannot give every device a routable public IP. The internet cannot route to private addresses (10.x, 172.16–31.x, 192.168.x) — routers on the internet drop those packets.

### Step 1: A translator at the edge

You assign private addresses to internal devices (192.168.0.1–192.168.0.254) and put one public IP on the router's external interface. When a device sends a packet to the internet, the router rewrites the source IP — replacing the private address with the public one — before forwarding it. Replies come back to the public IP; the router rewrites the destination IP to the original private address and delivers it internally. This is **NAT — Network Address Translation**.

### Step 2: But how does the router know which reply belongs to which device?

If 100 internal devices all send packets and the router replaces all source IPs with the same public IP, the replies all arrive at the same public IP with no way to distinguish which internal host they belong to.

The router also translates the **source port number** — each internal session gets a unique port mapping. Reply packets carry the destination port number; the router looks it up and knows which internal host and port to forward to. This is **PAT — Port Address Translation** (also called **NAPT** or **NAT overload**). One public IP supports thousands of simultaneous sessions by differentiating them by port.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Replacing source IP at the edge | Source NAT (SNAT) / NAT |
| Replacing source IP + port for many sessions | PAT / NAT overload / NAPT |
| Replacing destination IP (for inbound) | Destination NAT (DNAT) |
| Table mapping internal ↔ external sessions | NAT translation table |
| Internal address space | Inside local |
| Public address used externally | Inside global |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why NAT is necessary in IPv4 networks with private addressing.
2. Distinguish static NAT, dynamic NAT, and PAT (NAT overload).
3. Describe the NAT translation table and how sessions are tracked.
4. Configure source NAT/PAT on a router using standard commands.
5. Configure static DNAT for inbound server access.
6. Identify protocols that NAT breaks and explain why.

---

## Prerequisites

- IP-001 — IP Addressing Fundamentals (private vs public address space, RFC 1918)
- IP-002 — Subnetting (understanding address pools)
- RT-001 — Routing Fundamentals (routing context for NAT deployment)

---

## Core Content

### NAT Address Terminology (Cisco)

Cisco defines four NAT address types:

| Term | Meaning |
|---|---|
| **Inside local** | Private IP of the internal host (e.g., 192.168.1.10) |
| **Inside global** | Public IP representing the internal host externally (e.g., 203.0.113.5) |
| **Outside local** | IP of the external destination as seen by internal hosts (usually same as outside global) |
| **Outside global** | Actual IP of the external destination server (e.g., 93.184.216.34) |

For most deployments, outside local = outside global. The inside local/global distinction is what matters.

### Static NAT

**One-to-one mapping:** A specific internal IP is always translated to a specific public IP.

Use case: an internal server (192.168.1.100) that must be reachable from the internet with a consistent public IP (203.0.113.10).

Static NAT is bidirectional — the mapping works for both outbound traffic (inside → outside) and inbound traffic (outside → inside).

### Dynamic NAT

A pool of public IPs is assigned dynamically to internal addresses on demand. If 10 internal hosts try to reach the internet simultaneously and only 5 public IPs are in the pool, the 11th through Nth hosts wait or are denied.

Use case: a block of public IPs that must be shared across a moderate number of internal hosts when port-based sharing (PAT) is insufficient (rare in modern deployments; PAT is almost always preferred).

### PAT — Port Address Translation (NAT Overload)

PAT multiplexes many internal sessions through one public IP using unique source port numbers.

When a host (192.168.1.10:51234) initiates a connection to a web server:
1. Router translates: src IP 192.168.1.10:51234 → 203.0.113.5:1025 (unique allocated port).
2. The translation table entry: `203.0.113.5:1025 ↔ 192.168.1.10:51234`.
3. Web server replies to 203.0.113.5:1025.
4. Router looks up the translation table: finds 192.168.1.10:51234, rewrites destination, forwards internally.

PAT supports up to ~65,535 simultaneous sessions per public IP per protocol (TCP, UDP, ICMP use different ranges). In practice, thousands to tens of thousands of sessions per IP is routine.

### Destination NAT (DNAT / Port Forwarding)

DNAT rewrites the **destination** address (and optionally port) of incoming packets. Used to expose internal servers to the internet:

- Public IP 203.0.113.5, port 443 → internal 192.168.1.100:443 (HTTPS server)
- Public IP 203.0.113.5, port 8080 → internal 192.168.1.200:80 (different internal server)

The router matches the inbound destination IP:port, rewrites to the internal target, and tracks the session for return traffic.

### Protocols NAT Breaks

NAT works transparently for most TCP/UDP protocols but breaks protocols that embed IP addresses in the application payload:

| Protocol | Problem |
|---|---|
| FTP (active mode) | Embeds client IP in PORT command; server tries to connect to private IP |
| SIP / H.323 | Embed IP/port in session description; NAT breaks signalling and media |
| IPSec AH | AH covers source IP in integrity check; NAT changes source IP → AH fails |
| IPSec ESP (in transport mode) | Session IDs embedded in ESP; some NAT implementations can't track |

**ALG (Application Layer Gateway):** NAT devices include ALGs to handle common protocols. The NAT device inspects the payload, rewrites embedded IPs, and creates additional translation entries (pinhole opening) for secondary connections. ALGs add complexity and are often the source of VoIP NAT problems. See FN-008.

**NAT-T (NAT Traversal):** IPSec uses UDP encapsulation (port 4500) to traverse NAT. The NAT device can track UDP sessions; the IPSec payload is inside UDP and is not inspected.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Define inside and outside NAT interfaces
    interface GigabitEthernet0/0
     ip address 203.0.113.5 255.255.255.252
     ip nat outside

    interface GigabitEthernet0/1
     ip address 192.168.1.1 255.255.255.0
     ip nat inside

    ! PAT (NAT overload) — all inside hosts share the outside interface IP
    access-list 1 permit 192.168.1.0 0.0.0.255
    ip nat inside source list 1 interface GigabitEthernet0/0 overload

    ! Static DNAT for inbound server access
    ip nat inside source static tcp 192.168.1.100 443 203.0.113.5 443

    ! Verification
    show ip nat translations
    show ip nat statistics
    debug ip nat
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_nat/configuration/xe-17/nat-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_nat/configuration/xe-17/nat-xe-17-book.html)

=== "Juniper (Junos — SRX)"

    ```
    # Source NAT pool (PAT equivalent — interface-based)
    set security nat source rule-set INTERNET-SNAT from zone trust
    set security nat source rule-set INTERNET-SNAT to zone untrust
    set security nat source rule-set INTERNET-SNAT rule SNAT-ALL match source-address 192.168.1.0/24
    set security nat source rule-set INTERNET-SNAT rule SNAT-ALL then source-nat interface

    # Static destination NAT
    set security nat destination pool HTTPS-SERVER address 192.168.1.100/32 port 443
    set security nat destination rule-set INBOUND from zone untrust
    set security nat destination rule-set INBOUND rule DNAT-HTTPS match destination-address 203.0.113.5/32
    set security nat destination rule-set INBOUND rule DNAT-HTTPS match destination-port 443
    set security nat destination rule-set INBOUND rule DNAT-HTTPS then destination-nat pool HTTPS-SERVER

    # Verification
    show security nat source summary
    show security nat destination summary
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/nat-overview.html](https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/nat-overview.html)

=== "MikroTik RouterOS"

    ```
    # Source NAT / Masquerade (PAT with dynamic public IP)
    /ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade

    # Source NAT with fixed public IP
    /ip firewall nat add chain=srcnat src-address=192.168.1.0/24 \
        out-interface=ether1 action=src-nat to-addresses=203.0.113.5

    # Destination NAT (port forwarding)
    /ip firewall nat add chain=dstnat protocol=tcp dst-port=443 \
        in-interface=ether1 action=dst-nat to-addresses=192.168.1.100 to-ports=443

    # Verification
    /ip firewall connection print
    /ip firewall nat print stats
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/NAT](https://help.mikrotik.com/docs/display/ROS/NAT)

---

## Common Pitfalls

1. **No `ip nat inside` / `ip nat outside` on interfaces (Cisco).** NAT will not translate without both interface designations. The most common missed step. Verify with `show ip nat translations` — no entries means NAT isn't seeing traffic.

2. **ACL too restrictive for the NAT inside source list.** If the ACL permits only specific subnets, hosts outside those subnets don't get translated and can't reach the internet. Verify the ACL matches all intended inside address space.

3. **Stale NAT translation entries blocking new sessions.** The translation table has timeout values. In some cases stale entries consume port space. Flush with `clear ip nat translation *` (carefully — clears all active sessions).

4. **DNAT without a corresponding security policy.** On stateful firewall platforms (SRX, ASA, FortiGate), a DNAT entry alone doesn't allow traffic through — a corresponding security policy permitting the inbound zone-to-zone traffic is also required.

5. **Protocols with embedded IPs failing through NAT.** If FTP, SIP, or H.323 sessions fail through NAT, verify ALG is enabled for that protocol. On some platforms ALGs are enabled by default; on others they must be explicitly enabled.

---

## Practice Problems

**Q1.** A host (192.168.1.50:55000) connects to a server (93.184.216.34:80) through a PAT router with public IP 203.0.113.5. The server replies to 203.0.113.5:1100. What does the router do with this reply?

??? answer
    The router looks up 203.0.113.5:1100 in the NAT translation table, finds the mapping to 192.168.1.50:55000, rewrites the destination IP to 192.168.1.50 and destination port to 55000, and forwards the packet internally.

**Q2.** Why does IPSec AH fail through NAT but IPSec ESP (in tunnel mode) can work?

??? answer
    AH (Authentication Header) computes an integrity check over the IP header including the source IP. NAT changes the source IP — the integrity check fails at the destination. ESP (Encapsulating Security Payload) in tunnel mode encapsulates the original packet inside a new IP header; NAT changes the outer source IP but the ESP payload (with its integrity check) only covers the inner packet. NAT-T wraps ESP in UDP to allow UDP session tracking by the NAT device.

**Q3.** What is the difference between static NAT and PAT?

??? answer
    Static NAT is a one-to-one, bidirectional mapping between one inside IP and one outside IP — primarily used for inbound access to internal servers. PAT (NAT overload) maps many inside IPs to one outside IP by differentiating sessions by port number — used for outbound internet access from many devices through a single public IP.

---

## Summary & Key Takeaways

- **NAT** translates IP addresses between inside (private) and outside (public) address spaces.
- **PAT** (NAT overload) extends this by also translating port numbers — many devices share one public IP.
- The **NAT translation table** maps inside local IP:port ↔ inside global IP:port and tracks session state.
- **Static NAT** provides a persistent one-to-one mapping — needed for inbound access to internal servers.
- **DNAT / port forwarding** rewrites destination IP:port for inbound connections.
- NAT breaks protocols that embed IP addresses in payloads (FTP, SIP, H.323); ALGs compensate.
- NAT is an IPv4 workaround for address exhaustion; IPv6's large address space is designed to eliminate the need for NAT.

---

## Where to Next

- **SV-004 — NTP:** Time synchronisation — critical for logging, security, and protocol convergence.
- **SEC-001 — ACLs:** Packet filtering; works alongside NAT for security policy.
- **IP-003 — IPv6 Addressing:** IPv6 removes the driver for NAT with its large address space.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 1918 | Address Allocation for Private Internets |
| RFC 2663 | IP Network Address Translator (NAT) Terminology and Considerations |
| RFC 3022 | Traditional IP Network Address Translator (Traditional NAT) |
| RFC 4787 | NAT Behavioral Requirements for Unicast UDP |
| Cisco CCNA | NAT/PAT configuration and verification |
| CompTIA Network+ | NAT concepts, public vs private addressing |

---

## References

- RFC 1918 — Address Allocation for Private Internets. [https://www.rfc-editor.org/rfc/rfc1918](https://www.rfc-editor.org/rfc/rfc1918)
- RFC 3022 — Traditional IP Network Address Translator. [https://www.rfc-editor.org/rfc/rfc3022](https://www.rfc-editor.org/rfc/rfc3022)

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
| SEC-001 | Access Control Lists | ACLs and NAT are complementary at the network edge |
| IP-003 | IPv6 Addressing | IPv6 is designed to eliminate the need for NAT |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | Private address space (RFC 1918) |
| IP-002 | IP Subnetting | Understanding inside address pools |
| RT-001 | Routing Fundamentals | NAT operates at routing boundaries |
| SV-002 | DHCP | DHCP assigns the private IPs that NAT translates |
<!-- XREF-END -->
