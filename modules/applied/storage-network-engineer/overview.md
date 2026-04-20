---
title: "Applied: Storage Network Engineer - Overview"
module_id: "SNE-000"
domain: "applied/storage-network-engineer"
difficulty: "intermediate"
prerequisites: ["NW-001", "IP-001", "IP-002", "SW-001", "SW-002", "DC-001"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, storage, san, nas, iscsi, fibre-channel, nvme-of, storage-networking]
---

## The Analogy

Think of storage networking like the filing system for a large office building. Every desk (server) can have its own filing cabinet under the desk (direct-attached storage) - simple, but not shared. Or you can have a central filing room (storage array) that all desks access over the internal mail system (the storage network).

The trick is that the filing room needs to serve hundreds of desks simultaneously, with documents arriving and leaving fast enough that no desk is ever waiting. The "filing room connection" - the storage network - must be extremely fast, extremely reliable, and handled differently from the regular office email system, because unlike an email that can wait a few milliseconds, a disk request that's slow makes the whole computer feel slow.

**Mapping:**
| Analogy | Technical Term |
|---|---|
| Desk with its own filing cabinet | Direct-Attached Storage (DAS) |
| Central filing room | Storage Array (SAN or NAS) |
| Internal mail system | Storage Network (FC SAN or iSCSI) |
| Document request | Block I/O or file I/O |
| Filing room address | LUN (Logical Unit Number) or NFS share |
| Mail system capacity/speed | Bandwidth, IOPS, latency |
| Dedicated fast courier service | Fibre Channel (FC) |
| Regular mail but prioritised | iSCSI over Ethernet |

---

## What Is a Storage Network Engineer?

A storage network engineer designs and operates the network infrastructure that connects servers to centralised storage systems - Storage Area Networks (SANs) and Network-Attached Storage (NAS).

Key responsibilities:
- Designing and configuring Fibre Channel SANs (zoning, WWN management, fabric topology)
- Deploying and troubleshooting iSCSI networks (Ethernet-based block storage)
- Managing NAS infrastructure (NFS, SMB/CIFS - file-level storage)
- Performance analysis: IOPS, latency, bandwidth - storage networks have very tight requirements
- Disaster recovery: replication between storage arrays over WAN/DCI links
- Evaluating and deploying NVMe over Fabrics (NVMe-oF) - the next generation

**Where you'll find these engineers:** Data centres, financial services (very storage-intensive), healthcare, media/broadcast (large media file workflows), cloud infrastructure teams, enterprise IT, and storage vendors (Pure Storage, NetApp, Dell EMC, HPE).

---

## Why This Is a Distinct Path

Storage networking has its own protocols, its own failure modes, and its own performance culture:

- **Fibre Channel (FC) is not Ethernet.** FC has its own frame format, its own addressing (WWNs), its own switch fabric, and its own management paradigm. An Ethernet engineer cannot simply transfer their skills - FC requires dedicated learning.
- **Loss is not acceptable.** In data networking, dropped packets are retransmitted and mostly invisible to users. In storage networking, a dropped I/O can corrupt data or cause application crashes. FC fabrics are designed to be lossless. iSCSI on Ethernet requires DCB (Data Centre Bridging) or very careful QoS to approach FC-class reliability.
- **IOPS and latency matter more than throughput.** Database storage is about how many operations per second and how fast each one completes - not raw megabytes per second. Understanding the difference between sequential and random I/O, and how to measure and optimise each, is central to this role.
- **Intersection with DC networking:** iSCSI, NVMe-oF, and FCoE all run over Ethernet. The storage network engineer must understand DC switching, VLAN design, DCB/PFC, and jumbo frames. This path deliberately builds on the DC networking foundations.

---

## Proposed Stage Overview

**Stage 1 - Foundation:**
NW-001 (OSI - storage protocols are multi-layer), IP-001, IP-002, SW-001, SW-002 (VLANs), DC-001 (Spine-leaf design - where storage lives)

**Stage 2 - Storage Concepts:**
Storage fundamentals (block vs file vs object), RAID levels (RAID 0/1/5/6/10 - not networking but critical context), LUN design and multipathing

**Stage 3 - Fibre Channel:**
FC protocol basics (FC frames, FLOGI, PLOGI), FC switch fabric (ISL, zoning, WWN addressing), FC topologies (point-to-point, arbitrated loop, fabric), N_Port, F_Port, E_Port, Cisco MDS and Brocade/Broadcom switches

**Stage 4 - Ethernet-Based Storage:**
iSCSI over Ethernet (RFC 7143), iSCSI initiator/target configuration, DCB / Priority-based Flow Control (PFC - IEEE 802.1Qbb), FCoE (Fibre Channel over Ethernet - RFC 2625, IEEE 802.3), NAS: NFS (RFC 7530) and SMB/CIFS

**Stage 5 - NVMe over Fabrics:**
NVMe-oF concepts (NVMe/FC, NVMe/RDMA, NVMe/TCP), RDMA fundamentals (RoCE, iWARP), why NVMe-oF matters for latency-sensitive workloads

**Stage 6 - Replication & DR:**
Synchronous vs asynchronous replication, RPO and RTO in storage context, WAN optimisation for storage replication, storage-aware DCI (link to DC-005)

---

## See Full Learning Path

[learning-paths/storage-network-engineer.md](../../../learning-paths/storage-network-engineer.md) *(pending)*

## Call for Contributors

Open a GitHub Issue with label `storage-network-path`. Engineers with Fibre Channel, iSCSI, or NVMe-oF experience especially welcome.
