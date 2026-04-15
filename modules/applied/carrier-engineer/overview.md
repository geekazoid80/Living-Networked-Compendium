---
title: "Applied: Carrier / Service Provider Network Engineer — Overview"
module_id: "CE-000"
domain: "applied/carrier-engineer"
difficulty: "advanced"
prerequisites: ["NW-001", "IP-001", "IP-002", "RT-004", "RT-007", "SW-001"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, carrier, service-provider, telco, mpls, sr, evpn, bgp]
---

## What Is a Carrier / Service Provider Network Engineer?

A carrier or service provider (SP) network engineer designs, builds, and operates the networks that connect cities, countries, and continents — the infrastructure that other networks ride on top of. This includes:

- ISP and telco backbone networks
- MPLS VPN services (L2 and L3) sold to enterprise customers
- Metro Ethernet and carrier Ethernet services
- International and submarine cable connectivity
- Network infrastructure for mobile operators (backhaul, core)
- Wholesale transit and peering

The role is distinct from enterprise networking in its **scale** (hundreds or thousands of nodes), its **technology stack** (MPLS, SR, IS-IS, EVPN dominate over OSPF and VLANs), and its **service mindset** (the network is the product, and SLAs are contractual commitments).

Vendors you'll encounter most in this space: **Cisco (IOS-XR, ASR/NCS/CRS)**, **Juniper (MX, PTX)**, **Nokia (7750 SR, 7210 SAS)**, **Huawei (NE series)**, and to a lesser extent **ZTE** in some markets.

## Why This Is a Distinct Path

Enterprise engineers who step into carrier roles often find that the technology is familiar in name but radically different in scale and philosophy:

- IS-IS is the routing protocol of choice, not OSPF
- BGP carries far more than just internet routes — it carries VPN, EVPN, and policy information
- MPLS label stacks are everywhere
- Traffic engineering is routine, not exceptional
- Operations processes (OSS, BSS, ticketing) are formal and contractual

This path assumes you have completed at minimum the first three stages of the **Data Network Engineer** path (networking fundamentals, switching, routing foundations). It then builds the carrier-specific knowledge on top.

## The Full Learning Path

See [learning-paths/carrier-engineer.md](../../../learning-paths/carrier-engineer.md) for the complete ordered module sequence.

*(This learning path file is pending — see TASK.md item A1.)*

## Proposed Stage Overview

**Stage 1 — Foundation (from DNE path):** NW-001, IP-001, IP-002, RT-004 (OSPF), RT-007 (BGP), SW-001

**Stage 2 — Carrier Routing:**
IS-IS (CT-domain), BGP Advanced (RT-008), Route Policy and Filtering

**Stage 3 — MPLS:**
MPLS Fundamentals (CT-001), MPLS L3VPN (CT-002), MPLS L2VPN (CT-003)

**Stage 4 — Segment Routing:**
SR-MPLS (CT-004), SRv6 (CT-005), Traffic Engineering (CT-012)

**Stage 5 — EVPN & Carrier Ethernet:**
EVPN (CT-006), MEF Standards (CT-008), Carrier Ethernet Services (CT-009)

**Stage 6 — Operations & Automation:**
QoS in MPLS (QOS-005), Telemetry (PROTO-007), NETCONF (PROTO-008), Automation toolchain

## Call for Contributors

If you work in a carrier or SP environment, especially with Nokia SR-OS, Juniper MX/PTX, or Huawei NE series, your vendor-specific knowledge is valuable here. Most existing resources focus heavily on Cisco IOS-XR. We want fair multi-vendor coverage.

Open a GitHub Issue with the label `carrier-path` to discuss.
