---
title: "Learning Path: Data Centre Network Engineer"
path_id: "DCE"
status: "seeking-contributors"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
---

# Learning Path: Data Centre Network Engineer

> **This learning path framework is awaiting contributors.** Open a GitHub Issue with label `datacentre-path`.

See [modules/applied/datacentre-engineer/overview.md](../modules/applied/datacentre-engineer/overview.md) for role context and why spine-leaf / VXLAN+EVPN is a distinct engineering discipline.

---

## Stage 1: Foundation

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 1 | NW-001 | The OSI Model | done |  |
| 2 | IP-001 | IP Addressing Fundamentals | done |  |
| 3 | IP-002 | IP Subnetting & VLSM | done |  |
| 4 | SW-001 | Switching Fundamentals | pending |  |
| 5 | SW-002 | VLANs & 802.1Q Trunking | pending |  |
| 6 | RT-007 | BGP Fundamentals | pending |  |
| 7 | PS-000 | Professional Standards & Frameworks | pending |  |

## Stage 2: Data Centre Design

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 8 | DC-001 | Data Centre Network Design | pending |  |
| 9 | FN-001 | How Switching Works Internally (MAC tables, CAM, TCAM) | needed |  |
| 10 | FN-002 | How Routing Works Internally (FIB, CEF, ASIC forwarding) | needed |  |

## Stage 3: VXLAN Overlay

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 11 | DC-002 | VXLAN Fundamentals (RFC 7348) | needed |  |
| 12 | CT-006 | EVPN Fundamentals | pending |  |
| 13 | DC-004 | EVPN-VXLAN | pending |  |
| 14 | DC-007 | DC Overlay & L2-Fabric Alternatives | needed |  |

## Stage 4: BGP Underlay

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 15 | DC-003 | BGP in the Data Centre (RFC 7938) | pending |  |
| 16 | RT-008 | BGP Advanced - Communities, Policy & Filtering | needed |  |

## Stage 5: DCI & Storage Networking

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 17 | DC-005 | Data Centre Interconnect (DCI) | needed |  |
| 18 | DC-006 | Storage Networking Basics for DC Engineers | needed |  |

## Stage 6: Automation & Operations

| Order | Module ID | Title | Status | Est. Time |
|---|---|---|---|---|
| 19 | AUTO-001 | Python for Network Engineers | pending |  |
| 20 | AUTO-002 | REST APIs & Network Automation | pending |  |
| 21 | AUTO-004 | Ansible for Network Automation | pending |  |
| 22 | AUTO-005 | Terraform for Network Infrastructure | needed |  |

---

## Benchmark Certifications

| Cert | Body | Relevance |
|---|---|---|
| Arista ACE-L3 | Arista | EOS, VXLAN, EVPN on Arista |
| Cisco CCNP Data Center | Cisco | NX-OS, ACI, VXLAN |
| Juniper JNCIP-DC | Juniper | QFX, EVPN-VXLAN, Apstra |
| VMware VCP-NV (NSX) | VMware | Overlay networking for virtualised DC |
| HashiCorp Terraform Associate | HashiCorp | Infrastructure-as-code for DC automation |
