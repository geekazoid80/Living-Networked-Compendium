---
module_id: SEC-001
title: "Access Control Lists (ACLs)"
description: "How ACLs filter packets at Layer 3/4 based on IP addresses, protocols, and ports - the foundational traffic control mechanism on routers and switches."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - IP-001
  - IP-002
  - RT-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - acl
  - security
  - packet-filtering
  - layer3
  - layer4
created: 2026-04-19
updated: 2026-04-19
---

# SEC-001 - Access Control Lists (ACLs)
## Learning Objectives

After completing this module you will be able to:

1. Explain what an ACL is and how the implicit deny-any at the end works.
2. Distinguish standard ACLs from extended ACLs.
3. Describe the rule-processing order and why it matters.
4. Apply an ACL to a router interface correctly (inbound vs outbound).
5. Write ACL rules for common filtering scenarios.
6. Configure named extended ACLs on at least two vendor platforms.

---
## Prerequisites

- IP-001 - IP Addressing Fundamentals (subnet notation)
- IP-002 - IP Subnetting (wildcard masks)
- RT-001 - Routing Fundamentals (router interface context)

---
## The Problem

Two departments - HR and Engineering - share a network. HR handles salary data; Engineering handles source code. You don't want Engineering staff able to reach the HR file server, and you don't want HR users reaching the Engineering build servers. Both groups need internet access. A router connects all three segments.

### Step 1: The router sees every packet

Every packet between segments passes through the router. The router can inspect the packet's source IP, destination IP, protocol, and port - and decide whether to forward it or drop it.

### Step 2: A list of rules

You write a list of match conditions and actions - a **policy**. "If source is from Engineering subnet and destination is HR server → deny. Everything else → permit." The router checks each packet against the list in order, top to bottom. The first matching rule applies. You have invented an **Access Control List (ACL)**.

### Step 3: Where to apply it

An ACL is a definition - it does nothing until applied to a router interface, in a direction. Applied **inbound**: the router checks the ACL before routing. Applied **outbound**: the router checks the ACL after routing, before sending the packet out. The direction and interface determine which traffic the ACL sees.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Ordered list of match + action rules | ACL |
| Forward the packet | Permit |
| Drop the packet | Deny |
| Matching source IP only | Standard ACL |
| Matching src IP, dst IP, protocol, port | Extended ACL |
| ACL applied to an interface | ACL binding (in/out) |
| Last rule in every ACL | Implicit deny any |

---
## Core Content

### ACL Processing - The Core Logic

An ACL is processed **top-to-bottom, first match wins**. As soon as a packet matches a rule, that rule's action (permit or deny) is applied and processing stops. No further rules are checked.

If no rule matches, the **implicit deny any** at the end of every ACL drops the packet. This implicit rule is invisible - it's always there. Forgetting it is a common cause of accidentally blocking all traffic.

**Consequence:** Rule order matters. A broad permit placed before a narrow deny means the deny is never reached. Always place specific rules before general ones.

### Standard ACLs

Match on **source IP address only**. Numbered 1–99 and 1300–1999 on Cisco IOS; also supported as named ACLs.

Use cases: filtering based on source host or network (e.g., permit a specific management subnet to access a device via SSH; deny all others).

Limitation: no destination or protocol matching - less precise. Apply close to the destination to avoid accidentally blocking legitimate traffic going elsewhere.

### Extended ACLs

Match on:
- Source IP (with wildcard mask)
- Destination IP (with wildcard mask)
- Protocol (TCP, UDP, ICMP, IP, OSPF, etc.)
- Source port (for TCP/UDP)
- Destination port (for TCP/UDP)
- TCP flags (established - match return traffic)
- DSCP / IP Precedence (optional)

Extended ACLs (numbered 100–199 and 2000–2699 on Cisco; named on all platforms) provide precise filtering. Apply close to the source to prevent unwanted traffic from traversing the network before being dropped.

### Wildcard Masks

ACLs use **wildcard masks** (inverse subnet masks) to specify address ranges:

- `0.0.0.0` - match exactly this host (`host` keyword = `x.x.x.x 0.0.0.0`)
- `0.0.0.255` - match entire /24 subnet
- `0.0.255.255` - match entire /16 subnet
- `255.255.255.255` - match any address (`any` keyword)

Wildcard mask bit: **0 = must match**, **1 = don't care**.

### Inbound vs Outbound ACL

| Direction | When checked | What it affects |
|---|---|---|
| **Inbound** | Before routing decision | Traffic arriving on the interface, before the router decides where to forward it |
| **Outbound** | After routing decision | Traffic leaving the interface, after the router has determined the egress interface |

Best practice guideline:
- **Extended ACLs:** Apply **inbound** on the interface closest to the source - stops unwanted traffic before it traverses the network.
- **Standard ACLs:** Apply **outbound** on the interface closest to the destination - since they only match source IP, applying them too early may block traffic going to other destinations.

Only one ACL per interface per direction (inbound or outbound) per protocol (IPv4 or IPv6) can be applied.

### The TCP Established Keyword

For TCP-based filtering, the `established` keyword matches packets that are part of an existing TCP session (ACK or RST bit set). This allows:

```
permit tcp any 192.168.1.0 0.0.0.255 established
```

"Allow return traffic for established TCP sessions from any source to the 192.168.1.0/24 network." This is a stateless approximation of stateful inspection - it's not a replacement for a stateful firewall (see SEC-002) because an attacker can set the ACK bit on unsolicited packets, but it significantly narrows attack surface.

### IPv6 ACLs

IPv6 ACLs work on the same principles but:
- Match on IPv6 source/destination prefixes.
- Must also permit ICMPv6 Neighbor Discovery (ND) traffic or IPv6 will break. Add explicit permits for ICMPv6 type 133–137 (RS/RA/NS/NA/Redirect).
- Cisco: `ipv6 access-list NAME` → `permit icmp any any nd-na`, `permit icmp any any nd-ns`.

---
## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Named extended ACL — permit Engineering to internet, deny HR server
    ip access-list extended ENG-OUT
     deny   ip 10.1.1.0 0.0.0.255 10.2.2.10 0.0.0.0   ! Engineering → HR server: deny
     permit ip 10.1.1.0 0.0.0.255 any                  ! Engineering → internet: permit
     deny   ip any any log                               ! Log and deny everything else

    ! Apply inbound on Engineering segment interface
    interface GigabitEthernet0/1
     ip access-group ENG-OUT in

    ! Verify
    show ip access-lists ENG-OUT
    show ip interface GigabitEthernet0/1 | include access list
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_acl/configuration/xe-17/sec-data-acl-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_acl/configuration/xe-17/sec-data-acl-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # Firewall filter (equivalent to ACL)
    set firewall family inet filter ENG-OUT term DENY-HR from source-address 10.1.1.0/24
    set firewall family inet filter ENG-OUT term DENY-HR from destination-address 10.2.2.10/32
    set firewall family inet filter ENG-OUT term DENY-HR then discard

    set firewall family inet filter ENG-OUT term PERMIT-ENG from source-address 10.1.1.0/24
    set firewall family inet filter ENG-OUT term PERMIT-ENG then accept

    set firewall family inet filter ENG-OUT term DENY-ALL then reject

    # Apply to interface
    set interfaces ge-0/0/1 unit 0 family inet filter input ENG-OUT

    # Verification
    show firewall filter ENG-OUT
    show interfaces ge-0/0/1 detail | match filter
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/routing-policy/topics/topic-map/firewall-filter-overview.html](https://www.juniper.net/documentation/us/en/software/junos/routing-policy/topics/topic-map/firewall-filter-overview.html)

=== "Arista EOS"

    ```
    ! Named extended ACL
    ip access-list ENG-OUT
       deny ip 10.1.1.0/24 10.2.2.10/32
       permit ip 10.1.1.0/24 any
       deny ip any any

    ! Apply to interface
    interface Ethernet1
       ip access-group ENG-OUT in

    ! Verification
    show ip access-lists ENG-OUT
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-acls](https://www.arista.com/en/um-eos/eos-acls)

=== "MikroTik RouterOS"

    ```
    # ACL via firewall filter rules
    /ip firewall filter
    add chain=forward src-address=10.1.1.0/24 dst-address=10.2.2.10 action=drop comment="Engineering → HR server: deny"
    add chain=forward src-address=10.1.1.0/24 action=accept comment="Engineering → internet: permit"
    add chain=forward action=drop comment="Deny all other"

    # Verification
    /ip firewall filter print stats
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/Filter](https://help.mikrotik.com/docs/display/ROS/Filter)

---
## Common Pitfalls

1. **Forgetting the implicit deny-any.** Every ACL ends with an invisible `deny any any`. If you apply an ACL to an interface and don't explicitly permit the traffic you want, it is silently dropped. A new ACL with only deny rules blocks everything - including routing protocol hellos, management SSH, and NTP. Always add explicit permits for what you want before applying.

2. **Wrong direction or wrong interface.** An ACL on the wrong interface or in the wrong direction (in vs out) either does nothing or blocks the wrong traffic. Verify with `show ip interface` and confirm which ACL is applied in which direction.

3. **Standard ACL applied on the wrong interface.** Standard ACLs only match source IP. If applied on the wrong interface, they may block a source from reaching all destinations - not just the intended target. Extended ACLs are almost always preferable for precision.

4. **ACL blocking routing protocol traffic.** An ACL applied to a routed interface that denies `any any` will also block OSPF hellos (IP protocol 89), BGP (TCP 179), LDP, and other protocol traffic - causing adjacencies to drop. Add explicit permits for routing protocol traffic.

5. **ACL blocking ICMPv6 ND in IPv6.** An IPv6 ACL with a deny-all at the end blocks Neighbor Discovery (ICMPv6 types 133–137) - IPv6 hosts can no longer resolve addresses on the link. Always add explicit `permit icmp any any nd-na` and `permit icmp any any nd-ns` before the deny-all.

---
## Practice Problems

**Q1.** An ACL has these rules in order: (1) `deny ip 10.1.1.5 any`, (2) `permit ip 10.1.1.0 0.0.0.255 any`. A packet from 10.1.1.5 arrives. What happens?

??? answer
    Rule 1 matches - source is 10.1.1.5 exactly - so the packet is denied. Rule 2 is never checked (first match wins). Even though rule 2 would permit the /24 subnet (which includes 10.1.1.5), the more specific deny comes first.

**Q2.** You apply an empty ACL (no rules) to an interface. What happens to all traffic on that interface?

??? answer
    All traffic is dropped. An empty ACL has only the implicit `deny any any` rule. Every packet matches the implicit deny and is dropped. Apply at least one explicit `permit` rule before any deny to avoid a complete traffic blackout.

**Q3.** Should you apply an extended ACL inbound or outbound, and on which interface?

??? answer
    Inbound, on the interface closest to the source. This stops unwanted traffic as early as possible - before it consumes router resources for routing lookups and before it traverses internal links.

**Q4.** What does `permit tcp any 10.0.0.0 0.0.0.255 established` match, and what does it allow?

??? answer
    It matches TCP packets arriving from any source destined for 10.0.0.x, where the TCP header has the ACK or RST flag set. It allows return traffic for TCP sessions that were initiated from inside (10.0.0.x) toward the outside. New inbound TCP connections (SYN only, no ACK) don't match and fall through to subsequent rules.

---
## Summary & Key Takeaways

- An ACL is an ordered list of match conditions and actions (permit/deny) processed **top-to-bottom, first match wins**.
- Every ACL ends with an **implicit deny any** - if no rule matches, the packet is dropped.
- **Standard ACLs** match source IP only; apply close to the destination.
- **Extended ACLs** match src IP, dst IP, protocol, and port; apply close to the source.
- **Wildcard masks**: 0 = must match, 1 = don't care.
- Applied **inbound** = checked before routing; **outbound** = checked after routing.
- ACLs are stateless - they don't track TCP connection state. Use a stateful firewall (SEC-002) for session-aware filtering.
- Always permit routing protocol traffic, management access, and ICMPv6 ND before a deny-all.

---
## Where to Next

- **SEC-002 - Firewall Concepts:** Stateful inspection - the upgrade from stateless ACL filtering.
- **RT-005 - OSPF Advanced:** Route filtering using distribute-lists (ACL-based) and prefix-lists.
- **SV-003 - NAT & PAT:** ACLs work alongside NAT to define what traffic is translated.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2460 | IPv6 Specification (ICMPv6 Neighbor Discovery context) |
| Cisco CCNA | Standard and extended ACLs, wildcard masks, application direction |
| Cisco CCNP Enterprise | Named ACLs, VACLs, time-based ACLs, object-groups |
| CompTIA Network+ | ACL concepts, permit/deny, implicit deny |
| CompTIA Security+ | Packet filtering as a security control |

---
## References

*(No single RFC defines ACLs as a technology - they are a platform implementation concept. Wildcard mask usage is rooted in IP addressing standards.)*

---
## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Vendor Feature Mapping

| Feature | Cisco IOS-XE | Juniper (Junos) | Arista EOS | MikroTik RouterOS |
|---|---|---|---|---|
| Named extended ACL | `ip access-list extended <name>` | `firewall family inet filter <name>` | `ip access-list <name>` | `/ip firewall filter` |
| Permit rule | `permit ip <src> <wild> <dst> <wild>` | `then accept` | `permit ip <src/pfx> <dst/pfx>` | `action=accept` |
| Deny rule | `deny ip <src> <wild> <dst> <wild>` | `then discard` | `deny ip <src/pfx> <dst/pfx>` | `action=drop` |
| Apply inbound | `ip access-group <name> in` | `family inet filter input <name>` | `ip access-group <name> in` | `chain=forward` (position-based) |
| Show ACL stats | `show ip access-lists <name>` | `show firewall filter <name>` | `show ip access-lists <name>` | `/ip firewall filter print stats` |

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| SEC-002 | Firewall Concepts | ACLs are the stateless predecessor to stateful firewall rules |
| RT-005 | OSPF Advanced | Route filtering with distribute-lists |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | Source/destination IP matching |
| IP-002 | IP Subnetting | Wildcard masks |
| RT-001 | Routing Fundamentals | Router interface context for ACL application |
<!-- XREF-END -->
