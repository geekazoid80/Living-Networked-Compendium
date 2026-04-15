---
title: "Learning Path: Broadcast Network Engineer"
path_id: "BRD"
status: "seeking-contributors"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
---

# Learning Path: Broadcast Network Engineer

> **This learning path is a framework awaiting content.** The structure below defines the curriculum — but the individual modules have not yet been written.
>
> If you work in broadcast, media, or OTT network engineering and want to contribute, this is where you can make a real difference. See [CONTRIBUTING.md](../CONTRIBUTING.md) to get started.

---

## About This Path

Broadcast network engineering sits at the intersection of traditional IP networking and media-specific protocols, standards, and production workflows. A broadcast network engineer needs to understand:

- How video is compressed and transported (MPEG-2, H.264, H.265)
- Streaming protocols (RTMP, HLS, DASH, MPEG-TS, SRT)
- The timing and synchronisation requirements unique to broadcast (jitter, lip-sync, PTP/IEEE 1588)
- Multicast distribution at scale (IGMP, PIM, SSM)
- Content Delivery Networks (CDN) and edge caching
- Production network design (including SMPTE ST 2110, the IP production standard)

**Assumed baseline:** IP networking fundamentals (Stages 1–4 of the Data Network Engineer path), plus exposure to video/audio concepts.

---

## Proposed Curriculum Framework

### Stage 1 — Networking Foundation

*Same as the Data Network Engineer path, Stages 1–4. Complete those first.*

Required prerequisites: NW-001, IP-001, IP-002, RT-001, SW-001, SW-002

---

### Stage 2 — Video & Compression Fundamentals

| Order | Module ID | Title | Status |
|---|---|---|---|
| 5 | BRD-001 | Video Fundamentals (resolution, frame rate, colour spaces) | Needed |
| 6 | BRD-002 | Video Compression (MPEG-2, H.264, H.265/HEVC, AV1) | Needed |
| 7 | BRD-003 | Audio in Broadcast Networks | Needed |

---

### Stage 3 — Streaming & Transport

| Order | Module ID | Title | Status |
|---|---|---|---|
| 8 | BRD-004 | MPEG-TS: The Workhorse of Broadcast | Needed |
| 9 | BRD-005 | Streaming Protocols (RTMP, HLS, DASH, SRT, RIST) | Needed |
| 10 | BRD-006 | Multicast Fundamentals (IGMP, PIM, SSM) | Needed |
| 11 | BRD-007 | Jitter, Latency & Lip-Sync Management | Needed |

---

### Stage 4 — Timing & Synchronisation

| Order | Module ID | Title | Status |
|---|---|---|---|
| 12 | BRD-008 | Clock & Sync in Broadcast (PTP/IEEE 1588, SMPTE ST 2059) | Needed |
| 13 | BRD-009 | NTP vs PTP — When Each Applies | Needed |

---

### Stage 5 — IP Production Standards

| Order | Module ID | Title | Status |
|---|---|---|---|
| 14 | BRD-010 | SMPTE ST 2110 — IP in the Production Studio | Needed |
| 15 | BRD-011 | SDI vs IP Production Networks | Needed |
| 16 | BRD-012 | Redundancy & Failover in Production Networks | Needed |

---

### Stage 6 — Content Delivery

| Order | Module ID | Title | Status |
|---|---|---|---|
| 17 | BRD-013 | CDN Architecture & Edge Caching | Needed |
| 18 | BRD-014 | OTT Platform Design | Needed |
| 19 | BRD-015 | Live Event Networking | Needed |

---

## How to Contribute to This Path

If you have experience in broadcast or media networking, your knowledge is exactly what this path needs.

**What we need:**
- Subject matter experts to write or review individual modules
- Engineers with hands-on experience in production environments (especially SMPTE ST 2110, HLS/DASH, CDN operations)
- Reviewers to validate technical accuracy

**How to start:**
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) and [CONTRIBUTION_SPEC.md](../CONTRIBUTION_SPEC.md)
2. Pick a module from the table above that you know well
3. Use [docs/MODULE_TEMPLATE.md](../docs/MODULE_TEMPLATE.md) to structure your contribution
4. Open a pull request — describe your experience in the PR description

**Questions?** Open a GitHub Issue with the label `broadcast-path` and we'll get back to you.

---

## Recommended External Resources

| Resource | Cost | Best for |
|---|---|---|
| [SMPTE Standards](https://www.smpte.org/standards) | Free (many) | ST 2110, ST 2059, and other production standards |
| [DVB Standards](https://www.dvb.org/standards) | Free | DVB-T, DVB-S2, HbbTV |
| [ABR Streaming Academy (Streaming Media)](https://www.streamingmedia.com) | Free | OTT, ABR streaming, CDN |
| [Haivision Blog](https://www.haivision.com/blog/) | Free | SRT protocol, live encoding |
| [SRT Alliance](https://www.srtalliance.org) | Free | SRT open source protocol documentation |
| Poynton — *Digital Video and HDTV*, 2nd ed., Morgan Kaufmann | ~SGD 100 | Deep reference on video fundamentals |
