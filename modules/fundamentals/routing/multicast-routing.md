---
title: "Multicast Routing"
module_id: "RT-011"
domain: "fundamentals/routing"
difficulty: "advanced"
prerequisites: ["RT-001", "IP-001"]
estimated_time: 60
version: "0.1"
last_updated: "2026-05-18"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [multicast, pim, igmp, mld, rendezvous-point, source-tree, shared-tree]
cert_alignment: ""
vendors: []
language: en
---

## Planned Module

This module is a planned stub. It is referenced as a forward-link from [Network Topologies](../networking/network-topologies.md) but the substantive content has not yet been written.

Until it lands, [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) covers the unicast routing primitives this module extends to one-to-many distribution.

## Scope (planned)

Once written, the reader will be able to:

1. **Distinguish** IGMP (IPv4) and MLD (IPv6) host-side membership signalling from the network-side PIM protocol family.
2. **Compare** PIM-SM (shared tree via RP), PIM-SSM (source-specific, no RP), PIM-DM (dense-mode flood-and-prune), and PIM-Bidir (bidirectional shared tree) by deployment fit.
3. **Configure** a Rendezvous Point (RP) using static, Auto-RP, BSR, or anycast-RP methods and reason about the trade-offs.
4. **Diagnose** common multicast failure modes (RPF check failure, missing IGMP querier, asymmetric routing breaking PIM, MSDP between domains).
5. **Apply** multicast appropriately versus unicast or application-layer fan-out, recognising the operational cost of network-layer multicast.

## How to contribute

This module needs an author. To claim it, open an issue or PR referencing module ID `RT-011`. The structure must follow [`MODULE_TEMPLATE.md`](../../../MODULE_TEMPLATE.md).

## References (placeholder)

Substantive content and standards references will be added by the author. Likely sources include RFC 4601 (PIM-SM), RFC 7761 (PIM-SM revised), RFC 3569 (PIM-SSM rationale), RFC 5015 (PIM-Bidir), RFC 3376 (IGMPv3), RFC 3810 (MLDv2), and vendor multicast deployment guides.
