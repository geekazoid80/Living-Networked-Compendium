---
title: "Data Centre Network Design"
module_id: "DC-001"
domain: "fundamentals/datacentre"
difficulty: "advanced"
prerequisites: ["NW-002", "SW-001", "RT-007"]
estimated_time: 75
version: "0.1.0"
last_updated: "2026-05-18"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [datacentre, spine-leaf, clos, fabric, east-west, oversubscription, ecmp]
cert_alignment: ""
vendors: []
language: en
---

# DC-001 - Data Centre Network Design
## Planned Module

This module is a planned stub. It is referenced as a forward-link from [Network Topologies](../networking/network-topologies.md) but the substantive content has not yet been written.

Until it lands, [Network Topologies](../networking/network-topologies.md) (`NW-002`) introduces the spine-leaf pattern as a structured partial mesh; this module would unpack the operational design choices that follow.

## Scope (planned)

Once written, the reader will be able to:

1. **Distinguish** three-tier (core / aggregation / access) from leaf-spine (Clos) designs and explain why east-west traffic patterns drove the shift.
2. **Compute** oversubscription ratios for a given spine count, leaf uplink count, and server downlink count; reason about when each ratio is acceptable.
3. **Apply** ECMP routing (BGP unnumbered or OSPF) across spines so leaf-to-leaf paths are equal-cost two-hop, and identify the symptoms when ECMP breaks (polarisation, flow stickiness, asymmetric path MTU).
4. **Compare** layer-2 fabrics (VXLAN-EVPN, see [EVPN-VXLAN](../carrier-transport/evpn-vxlan.md)) versus pure layer-3 leaf-spine for tenant isolation and mobility requirements.
5. **Plan** rack-row cable layout (top-of-rack versus end-of-row), power and cooling implications, and the failure-domain boundaries each choice implies.

## How to contribute

This module needs an author. To claim it, open an issue or PR referencing module ID `DC-001`. The structure must follow [`MODULE_TEMPLATE.md`](../../../MODULE_TEMPLATE.md).

## References (placeholder)

Substantive content and standards references will be added by the author. Likely sources include Charles Clos (1953) on multi-stage switching networks, RFC 7938 (BGP for DC fabrics), vendor DC reference architectures (Cisco VPC + ACI, Arista EVPN, Juniper QFX), and the Open Compute Project network specifications.
