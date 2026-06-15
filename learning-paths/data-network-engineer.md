---
title: "Learning Path: Data Network Engineer"
path_id: "DNE"
status: "active"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
---

# Learning Path: Data Network Engineer

This path takes you from network fundamentals through to professional-level enterprise and carrier data networking. It maps closely to the **Cisco CCNA → CCNP Enterprise** certification progression.

**Assumed baseline:** Singapore polytechnic or university diploma/degree in IS, CS, or EE.
**Target outcome:** Capable junior-to-mid network engineer in an enterprise, ISP, or carrier environment.

---

## Stage 1 — Foundation (CCNA Level, Part 1)

*Get the model right, the addressing right, and the physical layer right. Everything else builds on this.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 1 | [NW-001](../modules/fundamentals/networking/osi-model.md) | The OSI Model | done | 40 min |
| 2 | NW-002 | Network Topologies | pending | 30 min |
| 3 | NW-003 | Ethernet & Cabling | pending | 35 min |
| 4 | [IP-001](../modules/fundamentals/ip/ip-addressing.md) | IP Addressing Fundamentals | done | 45 min |
| 5 | [IP-002](../modules/fundamentals/ip/subnetting.md) | IP Subnetting & VLSM | done | 60 min |
| 6 | PS-000 | Professional Standards & Frameworks | pending |  |

**Stage 1 milestone:** You can describe the OSI model, calculate subnets, and identify what type of cable or connector is needed for a given link.

---

## Stage 2 — Switching (CCNA Level, Part 2)

*VLANs and switches are everywhere. You'll configure them before your first week is out.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 7 | SW-001 | Switching Fundamentals | pending | 40 min |
| 8 | SW-002 | VLANs & Trunking (802.1Q) | pending | 50 min |
| 9 | SW-003 | Spanning Tree Protocol (STP/RSTP) | pending | 50 min |
| 10 | SW-004 | EtherChannel & Link Aggregation | pending | 35 min |
| 11 | SW-005 | Port Security & DHCP Snooping | pending | 30 min |

**Stage 2 milestone:** You can build a switched network with VLANs, trunks, and loop prevention. You understand what STP is doing and why.

---

## Stage 3 — Routing (CCNA Level, Part 3)

*Routing is the core skill. No routing knowledge, no network engineering career.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 12 | RT-001 | Routing Fundamentals | pending | 45 min |
| 13 | RT-002 | Static Routing | pending | 40 min |
| 14 | RT-003 | RIP & Distance-Vector Concepts | pending | 30 min |
| 15 | RT-004 | OSPF Fundamentals | pending | 60 min |
| 16 | RT-007 | BGP Fundamentals | pending | 60 min |
| 17 | IP-003 | IPv6 Addressing | pending | 45 min |

**Stage 3 milestone:** You can configure and verify static routes and OSPF. You understand what BGP is and can describe its role in the internet.

---

## Stage 4 — Services & Security (CCNA Level, Part 4)

*The plumbing that makes networks liveable: DHCP, DNS, NAT, ACLs.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 18 | SV-001 | DNS | pending | 35 min |
| 19 | SV-002 | DHCP | pending | 40 min |
| 20 | SV-003 | NAT & PAT | pending | 45 min |
| 21 | SV-004 | NTP & Time Synchronisation | pending | 25 min |
| 22 | SV-005 | SNMP & Syslog | pending | 35 min |
| 23 | SEC-001 | Access Control Lists (ACLs) | pending | 55 min |
| 24 | SEC-002 | Firewall Concepts | pending | 45 min |

**Stage 4 milestone:** CCNA-level readiness. You can design, configure, and troubleshoot a small-to-medium enterprise network.

---

## Checkpoint: Cisco CCNA 200-301

At this point you have covered the core of the CCNA curriculum.

**Recommended before sitting the exam:**
- Practice labs: Cisco Packet Tracer (free) or GNS3
- Mock exams: Boson ExSim, or the official Cisco practice exam
- Jeremy's IT Lab (free, YouTube + Packet Tracer labs) — excellent CCNA-aligned resource

---

## Stage 5 — Professional Routing (CCNP Level)

*Deeper into the routing protocols that run real networks.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 25 | RT-005 | OSPF Advanced - Multi-Area, Redistribution & Filtering | pending | 75 min |
| 26 | RT-008 | BGP Advanced - Communities, Policy & Filtering | pending | 90 min |
| 27 | RT-009 | Route Redistribution & Policy | pending | 60 min |
| 28 | RT-011 | Multicast Routing | pending |  |
| 29 | CT-001 | MPLS Fundamentals | pending | 60 min |

---

## Stage 6 — Quality of Service

*When traffic matters, QoS matters. Voice and video without QoS is an unhappy user.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 30 | QOS-001 | QoS Fundamentals | pending | 45 min |
| 31 | QOS-002 | Traffic Classification & Marking (DSCP, CoS) | pending | 40 min |
| 32 | QOS-003 | Queuing Mechanisms | pending | 45 min |
| 33 | QOS-004 | Traffic Policing vs. Shaping | pending | 40 min |

---

## Stage 7 — Network Security (Professional)

*Security is not optional. Every network engineer owns some of it.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 34 | SEC-003 | VPN & IPSec | pending | 60 min |
| 35 | SEC-004 | AAA: TACACS+ & RADIUS | pending | 45 min |
| 36 | SEC-005 | Encryption Standards & PKI | pending | 50 min |
| 37 | SEC-006 | Network Segmentation & DMZ Design | pending | 50 min |

---

## Stage 8 — Automation & Programmability

*Modern network engineering includes code. This is no longer optional.*

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 38 | AUTO-001 | Python for Network Engineers | pending | 75 min |
| 39 | AUTO-002 | REST APIs & Network Automation | pending | 60 min |
| 40 | AUTO-003 | NETCONF, YANG & gRPC | pending | 60 min |
| 41 | AUTO-004 | Ansible for Network Automation | pending | 60 min |

---

## Certification Roadmap

```
Stage 1–4: Cisco CCNA 200-301
                ↓
        2–3 years hands-on
                ↓
Stage 5–8: Cisco CCNP Enterprise (ENCOR 350-401)
                ↓
     Architecture / Specialist roles
     (CCIE, cloud, security tracks)
```

---

## Recommended External Resources

| Resource | Cost | Best for |
|---|---|---|
| [Jeremy's IT Lab](https://jeremysitlab.com) | Free | CCNA self-study (videos + labs) |
| [NetworkLessons.com](https://networklessons.com) | Paid | Deep-dive explanations, great diagrams |
| [Cisco Networking Academy](https://netacad.com) | Free | CCNA Official Courseware |
| [Packet Tracer](https://www.netacad.com/resources/lab-downloads) | Free | Lab simulation, beginner-friendly |
| [GNS3](https://www.gns3.com) | Free | More realistic router/switch emulation |
| Odom — *CCNA 200-301 Official Cert Guide* | ~SGD 80 | The definitive exam prep book |
