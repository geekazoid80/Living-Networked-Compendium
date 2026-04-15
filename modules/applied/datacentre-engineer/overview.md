---
title: "Applied: Data Centre Network Engineer — Overview"
module_id: "DCE-000"
domain: "applied/datacentre-engineer"
difficulty: "advanced"
prerequisites: ["NW-001", "IP-001", "IP-002", "RT-007", "SW-001", "SW-002"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, datacentre, spine-leaf, vxlan, evpn, bgp, fabric]
---

## What Is a Data Centre Network Engineer?

A data centre (DC) network engineer designs and operates the network infrastructure inside data centres — the switching fabric, server connectivity, storage networking, and the links that connect DCs to each other and to the outside world.

Key responsibilities include:
- Designing spine-leaf fabric topologies
- Deploying VXLAN overlays for workload mobility and multi-tenancy
- Operating BGP-based underlay routing (often following RFC 7938)
- Managing EVPN control planes for MAC/IP distribution
- Designing Data Centre Interconnect (DCI) solutions
- Supporting DevOps and cloud teams with programmable network infrastructure

Vendors you'll encounter most: **Arista (EOS)**, **Cisco (Nexus/NX-OS, ACI)**, **Juniper (QFX, Apstra)**, **Nokia (DC fabric)**, **Huawei (CloudEngine)**.

Data centre networking has moved fast in the last decade. The traditional 3-tier (access/distribution/core) architecture has been largely replaced by **spine-leaf**, and VLANs stretched over STP have been replaced by **VXLAN + EVPN**. Understanding the old way helps explain why the new way exists.

## Why This Is a Distinct Path

DC networking differs from enterprise in:
- **Scale and speed:** Zero-touch provisioning, API-driven configuration, continuous deployment
- **Technology stack:** BGP as the underlay IGP (not OSPF); VXLAN + EVPN as the overlay; no STP in the fabric
- **Automation-first:** Change management in DCs increasingly happens through code (Ansible, Terraform, Arista CloudVision, Cisco NSO)
- **Workload-awareness:** The network must move with virtual machines, containers, and Kubernetes pods

This path assumes solid foundation in IP networking and switching, then builds the DC-specific knowledge on top.

## The Full Learning Path

See [learning-paths/datacentre-engineer.md](../../../learning-paths/datacentre-engineer.md) for the complete ordered module sequence.

*(This learning path file is pending — see TASK.md item A2.)*

## Proposed Stage Overview

**Stage 1 — Foundation:**
NW-001, IP-001, IP-002, SW-001, SW-002 (VLANs), RT-007 (BGP fundamentals)

**Stage 2 — DC Design:**
DC-001 (Spine-Leaf Design), FN-001 (Switching internals), FN-002 (Routing internals)

**Stage 3 — Overlay:**
DC-002 (VXLAN Fundamentals), CT-006 (EVPN), DC-004 (EVPN in DC)

**Stage 4 — DC BGP:**
DC-003 (BGP in DC / RFC 7938), RT-008 (BGP Advanced)

**Stage 5 — DCI & Storage:**
DC-005 (Data Centre Interconnect), DC-006 (Storage Networking Basics)

**Stage 6 — Automation:**
AUTO-001 (Python), AUTO-002 (REST APIs), AUTO-004 (Ansible), AUTO-005 (Terraform)

## Call for Contributors

Arista EOS and Cisco NX-OS coverage is particularly needed here. If you work with DC fabrics, especially in production, we'd love your real-world input on design patterns, operational pitfalls, and troubleshooting approaches.

Open a GitHub Issue with the label `datacentre-path` to discuss.
