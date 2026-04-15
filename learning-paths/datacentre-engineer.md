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

## Stage 1 — Foundation

| Order | Module ID | Title | Status |
|---|---|---|---|
| 1 | NW-001 | The OSI Model | done |
| 2 | IP-001 | IP Addressing Fundamentals | done |
| 3 | IP-002 | IP Subnetting & VLSM | done |
| 4 | SW-001 | Switching Fundamentals | pending |
| 5 | SW-002 | VLANs & 802.1Q Trunking | pending |
| 6 | RT-007 | BGP Fundamentals | pending |

## Stage 2 — Data Centre Design

| Order | Module ID | Title | Status |
|---|---|---|---|
| 7 | DC-001 | Data Centre Network Design — Spine-Leaf Topology | pending |
| 8 | FN-001 | How Switching Works Internally (MAC tables, CAM, TCAM) | needed |
| 9 | FN-002 | How Routing Works Internally (FIB, CEF, ASIC forwarding) | needed |

## Stage 3 — VXLAN Overlay

| Order | Module ID | Title | Status |
|---|---|---|---|
| 10 | DC-002 | VXLAN Fundamentals (RFC 7348) | needed |
| 11 | CT-006 | EVPN Fundamentals (RFC 7432) | needed |
| 12 | DC-004 | EVPN-VXLAN in the Data Centre | needed |

## Stage 4 — BGP Underlay

| Order | Module ID | Title | Status |
|---|---|---|---|
| 13 | DC-003 | BGP in the Data Centre (RFC 7938) | pending |
| 14 | RT-008 | BGP Advanced — Route Reflection, Communities, Policy | needed |

## Stage 5 — DCI & Storage Networking

| Order | Module ID | Title | Status |
|---|---|---|---|
| 15 | DC-005 | Data Centre Interconnect (DCI) | needed |
| 16 | DC-006 | Storage Networking Basics for DC Engineers | needed |

## Stage 6 — Automation & Operations

| Order | Module ID | Title | Status |
|---|---|---|---|
| 17 | AUTO-001 | Python for Network Engineers | pending |
| 18 | AUTO-002 | REST APIs and Network Automation | pending |
| 19 | AUTO-004 | Ansible for Network Automation | pending |
| 20 | AUTO-005 | Terraform for Network Infrastructure | needed |

---

## Benchmark Certifications

| Cert | Body | Relevance |
|---|---|---|
| Arista ACE-L3 | Arista | EOS, VXLAN, EVPN on Arista |
| Cisco CCNP Data Center | Cisco | NX-OS, ACI, VXLAN |
| Juniper JNCIP-DC | Juniper | QFX, EVPN-VXLAN, Apstra |
| VMware VCP-NV (NSX) | VMware | Overlay networking for virtualised DC |
| HashiCorp Terraform Associate | HashiCorp | Infrastructure-as-code for DC automation |
