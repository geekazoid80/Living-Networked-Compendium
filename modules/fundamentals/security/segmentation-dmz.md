---
module_id: SEC-006
title: "Network Segmentation & DMZ"
description: "How to design multi-zone network architectures - DMZ, management plane, micro-segmentation - to contain breaches and enforce least privilege."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - SEC-001
  - SEC-002
  - SW-002
  - RT-001
learning_path_tags:
  - DNE
difficulty: advanced
tags:
  - segmentation
  - dmz
  - microsegmentation
  - security-zones
  - management-plane
  - zero-trust
created: 2026-04-19
updated: 2026-04-19
---

# SEC-006 - Network Segmentation & DMZ
## Learning Objectives

After completing this module you will be able to:

1. Describe common security zone models and the purpose of each zone.
2. Explain DMZ architecture and why DMZ servers cannot initiate connections to the trust zone.
3. Describe the management plane and why it should be separated.
4. Explain micro-segmentation with VLANs, ACLs, and private VLANs.
5. Describe Zero Trust networking concepts.
6. Design a segmented architecture for a typical enterprise.

---
## Prerequisites

- SEC-001 - ACLs (inter-zone traffic filtering)
- SEC-002 - Firewall Concepts (zone-based policy model)
- SW-002 - VLANs & 802.1Q (VLANs as segmentation mechanism)
- RT-001 - Routing Fundamentals (routing at zone boundaries)

---
## The Problem

A flat network - all devices in the same broadcast domain, no zone boundaries - is a single security perimeter. One compromised workstation can reach every server, every router's management interface, every other workstation. The blast radius of any breach is the entire network.

### Step 1: Define security zones

Group devices by trust level and access requirements. The internet is untrusted. Internal users are partially trusted. Servers exposed to the internet are in a semi-trusted middle ground. Management interfaces are fully trusted but accessible only to administrators. Each zone has different traffic rules.

### Step 2: Apply policies at zone boundaries

Only a firewall (or router with ACLs) interconnects zones. All inter-zone traffic must cross this chokepoint - where policy is enforced. A compromised device in the DMZ cannot reach internal users because the firewall policy forbids DMZ → Trust traffic.

### Step 3: Segment within zones

Even within the "trust" zone, HR servers should not be reachable from Engineering workstations, and no workstation should reach the management interface of any network device. **Micro-segmentation** enforces least privilege within a zone - each segment can only reach what it needs.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Grouping devices by trust level | Security zone |
| Zone between trust and untrust | DMZ (Demilitarised Zone) |
| Restricting access within a zone | Micro-segmentation |
| Separate path for device management | Out-of-band management / management plane |
| Policy: deny all except explicitly permitted | Least privilege / default-deny |
| Model assuming no implicit trust | Zero Trust |

---
## Core Content

### Security Zones

A **security zone** groups interfaces and devices that share the same trust level and access policies. Policies are defined between zones rather than per-interface.

Common zones:

| Zone | Contents | Trust | Policies |
|---|---|---|---|
| **Untrust** | Internet, extranet | Zero | Default-deny inbound |
| **DMZ** | Public-facing servers (web, mail, DNS) | Semi | Permit from untrust on specific ports only |
| **Trust** | Internal users, workstations | High | Permit most outbound; restrict server access |
| **Servers** | Internal databases, file servers | High | Only specific trust subnets can reach specific server ports |
| **Voice** | IP phones, VoIP infrastructure | High | Only VoIP protocols permitted |
| **Management** | Router/switch management, NMS, jump hosts | Highest | Only admins from specific IPs via SSH |
| **Guest** | Visitor WiFi | Zero | Internet-only; no internal access |

### DMZ Architecture

The DMZ sits between the internet (Untrust) and the internal network (Trust). Servers in the DMZ can receive connections from the internet but cannot initiate connections to the Trust zone.

```
                          Firewall
                     ┌──────────────┐
Internet ─── Untrust─┤              ├─ Trust (internal users)
                     │              │
                     └──────┬───────┘
                            │
                          DMZ zone
                     ┌──────────────┐
                     │ Web server   │
                     │ Mail gateway │
                     │ Public DNS   │
                     └──────────────┘
```

**Why DMZ → Trust must be default-deny:**
A web server running a vulnerable application can be compromised. The attacker then has a foothold in the DMZ. If DMZ → Trust is permitted (even for one protocol), the attacker can pivot to internal servers, databases, and workstations. A strict default-deny DMZ → Trust policy limits the blast radius to the DMZ.

**Permitted DMZ → Trust flows (exceptions to default-deny):**
- DMZ servers querying internal LDAP for user authentication (strict source/destination/port).
- DMZ servers sending logs to internal syslog server.
- Monitoring server polling DMZ servers via SNMP.

All exceptions should be narrowly scoped: specific source IP, specific destination IP, specific port, specific direction.

### Dual-Firewall DMZ

Higher-security deployments use two separate firewalls from different vendors:

```
Internet ─── [FW1: Untrust → DMZ] ─── DMZ ─── [FW2: DMZ → Trust] ─── Trust
```

If FW1 is compromised, FW2 (different vendor, different codebase) still blocks DMZ → Trust traffic. A single vulnerability in the firewall vendor's code doesn't break both layers.

### Management Plane Separation

Network device management (SSH, SNMP, Syslog) should be isolated from the data plane - the same interfaces carrying user traffic.

**In-band management:** Management access over production interfaces. Simpler. Risk: a data-plane compromise can reach management interfaces; management traffic competes with user traffic; compromised routing means management access may be disrupted at the same time as the network problem you're trying to fix.

**Out-of-band (OoB) management:** A dedicated management network - separate physical ports (management Ethernet on routers), or a separate VLAN that is never routed to the data plane. Access via a jump host or bastion host in the management zone.

```
[Production network] ─── Data VLAN ─── [Router data port]
                                              │
[Management network] ─── Mgmt VLAN ─── [Router mgmt port] ─── [NMS / Bastion]
```

OoB management means you can still access network devices even if the data-plane routing is broken - critical for incident response.

**Management plane VRF (Virtual Routing and Forwarding):** Alternatively, configure a separate VRF for management traffic on the same physical interface. Management traffic is isolated in its own routing table, not shared with user routing. Less strict than true OoB but better than no isolation.

### Micro-Segmentation

Micro-segmentation enforces least privilege within zones. Even inside the Trust zone, not every device should reach every other device.

**VLAN-based segmentation:** Each department or function in a separate VLAN. Inter-VLAN routing controlled by the L3 switch or firewall. ACLs on SVIs restrict which VLANs can communicate.

**Private VLANs (PVLANs):** Ports in a PVLAN are isolated from each other at Layer 2 - they can only communicate via the promiscuous port (typically a firewall or gateway). All traffic between hosts in the PVLAN is forced through the gateway for inspection. Used in hosting environments where tenants share a VLAN but must not reach each other.

**Host-based firewall:** When VLANs are not fine-grained enough, host-based firewalls (Windows Defender Firewall, `iptables`/`nftables`) enforce policy at the individual host level. Essential for server environments where multiple server roles share a VLAN.

### Zero Trust Networking

Traditional security model: trust everything inside the perimeter. Zero Trust challenges this:

> Never trust, always verify. Authenticate every request regardless of source location.

Zero Trust principles:
- **Verify explicitly:** Every access request is authenticated and authorised - network location (inside vs outside) grants no implicit trust.
- **Least privilege:** Users and devices get only the access they need, when they need it.
- **Assume breach:** Design assuming the perimeter has been breached; contain lateral movement.

Practical implementations:
- **Identity-aware proxy:** Authenticate before accessing internal applications (no VPN needed; application is behind the proxy).
- **Micro-segmentation with policy enforcement per flow:** Each application workload communicates only on explicitly permitted flows.
- **Continuous verification:** Re-authenticate at intervals; revoke access when posture changes.

Zero Trust is a framework, not a single product. It represents the evolution of perimeter security to identity and context-based access.

---
## Common Pitfalls

1. **DMZ → Trust policy with overly broad rules.** "Permit any from DMZ to Trust" or "permit any from DMZ to database server" is not sufficient segmentation. Specify exact source/destination IP:port pairs. Update the rules whenever the DMZ application changes.

2. **Management interfaces on production VLANs.** Router and switch management interfaces (Cisco: `interface Vlan1` or `interface management`) sitting on the same VLAN as user traffic expose management to data-plane attacks. Place management interfaces on a dedicated management VLAN/VRF.

3. **No jump host.** Direct SSH from engineering workstations to network devices means the workstation is in the management plane. Any workstation compromise = direct access to network devices. A bastion/jump host forces all management access through a single hardened, audited, and monitored system.

4. **Forgetting OoB management power and console access.** OoB network access is useless if the device loses power or has a software crash. Real OoB management includes: console server, out-of-band power switch (PDU), and physical access procedures. OoB network management only handles software-level failures.

5. **Guest WiFi on the Trust VLAN.** Guest access on the same VLAN as internal users allows guests to attack internal systems. Guest WiFi must be in a separate VLAN, internet-only, with no route to internal subnets. Use captive portal and rate limiting as additional controls.

---
## Practice Problems

**Q1.** A web server in the DMZ serves an internal HR application. Internal users authenticate against Active Directory (AD). Which traffic flows are needed between DMZ and Trust, and how should they be scoped?

??? answer
    1. LDAP/LDAPS from the web server (specific DMZ IP) to the AD domain controllers (specific Trust IPs), TCP 389/636 only.
    2. Kerberos from web server to AD, TCP/UDP 88 to specific DC IPs.
    No other DMZ → Trust traffic needed. Permit only these exact flows; deny everything else. Source IP must be the specific web server, not the entire DMZ subnet.

**Q2.** Why is a dual-firewall DMZ (two firewalls from different vendors) more secure than a single firewall?

??? answer
    A single firewall from one vendor may have a zero-day vulnerability exploitable by attackers to bypass the firewall entirely. A dual-firewall design uses two different vendors' products - a vulnerability in vendor A's firewall doesn't apply to vendor B's firewall. An attacker who exploits FW1 still cannot pass FW2 without exploiting a different vulnerability. The cost is higher complexity and operational overhead, but the security benefit is significant for high-value environments.

**Q3.** What is the management plane and why should it be separated from the data plane?

??? answer
    The management plane is the set of protocols and interfaces used to manage network devices (SSH, SNMP, Syslog, NETCONF). The data plane is the set of interfaces and protocols carrying user traffic. Separation ensures: (1) Management access remains available even if the data plane is congested or broken. (2) Data-plane compromises (user traffic interception, routing attacks) don't automatically reach management interfaces. (3) Management traffic is isolated from potential eavesdropping in the data plane.

---
## Summary & Key Takeaways

- **Security zones** group devices by trust level; policies are applied between zones.
- **DMZ** is semi-trusted - servers accessible from the internet, but default-deny DMZ → Trust protects internal network from compromised DMZ servers.
- **Dual-firewall DMZ** (different vendors) provides defence-in-depth against vendor-specific vulnerabilities.
- **Management plane separation** (out-of-band management, VRF, bastion host) keeps device management accessible even during data-plane failures or attacks.
- **Micro-segmentation** (VLANs, PVLANs, ACLs, host firewalls) enforces least privilege within zones.
- **Zero Trust:** "Never trust, always verify" - every access request authenticated and authorised regardless of source location.
- Guest WiFi must be on a separate, internet-only VLAN - never on the Trust VLAN.
- Design for breach containment: assume attackers will get past the perimeter; limit lateral movement.

---
## Where to Next

- **AUTO-001 - Python for Network Engineers:** Automating security policy deployment.
- **CT-006 - EVPN Fundamentals:** Micro-segmentation in data centre using EVPN.
- **DC-001 - Data Centre Network Design:** Spine-leaf and micro-segmentation in DC environments.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| NIST SP 800-41 | Guidelines on Firewalls and Firewall Policy |
| NIST SP 800-207 | Zero Trust Architecture |
| CIS Controls v8 | Control 12: Network Infrastructure Management |
| Cisco CCNP Security | DMZ design, zone-based firewall, segmentation |
| CompTIA Security+ | Network segmentation, DMZ, zero trust |
| CompTIA Network+ | Segmentation concepts, DMZ |

---
## References

- NIST SP 800-207 - Zero Trust Architecture. [https://csrc.nist.gov/publications/detail/sp/800-207/final](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- NIST SP 800-41 Rev.1 - Guidelines on Firewalls and Firewall Policy. [https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final](https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final)

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
| AUTO-001 | Python for Network Engineers | Automating security policy and segmentation |
| DC-001 | Data Centre Network Design | DC micro-segmentation design |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SEC-001 | Access Control Lists | Inter-zone traffic filtering |
| SEC-002 | Firewall Concepts | Zone-based policy model |
| SW-002 | VLANs & 802.1Q Trunking | VLANs as the Layer 2 segmentation mechanism |
| RT-001 | Routing Fundamentals | Routing at zone boundaries |
<!-- XREF-END -->
