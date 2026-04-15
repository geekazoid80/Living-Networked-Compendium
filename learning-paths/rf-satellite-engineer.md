---
title: "Learning Path: RF & Satellite Network Engineer"
path_id: "RSE"
status: "active"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
---

# Learning Path: RF & Satellite Network Engineer

This path covers the knowledge a working satellite or RF network engineer needs — from the physics of radio signals through to satellite link design, payload architecture, and integration with IP networks.

**Assumed baseline:** Singapore polytechnic or university diploma/degree in EE, Electronics, or Telecommunications. Some mathematics comfort required (logarithms, decibels).

**Target outcome:** Capable junior RF/satellite engineer able to understand link budgets, participate in satellite network operations, and troubleshoot RF and IP-over-satellite issues.

**Note:** There is no single standard certification for satellite engineering. Engineers in this space typically hold a mix of networking certifications (CCNA level) and vendor-specific or manufacturer-issued credentials. This path gives you the technical foundation regardless of which vendor's system you operate.

---

## Stage 1 — Networking Foundation

*RF and satellite engineers still need solid IP networking. Start here if you haven't already.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 1 | [NW-001](../modules/fundamentals/networking/osi-model.md) | The OSI Model | 40 min |
| 2 | [IP-001](../modules/fundamentals/ip/ip-addressing.md) | IP Addressing Fundamentals | 45 min |
| 3 | [IP-002](../modules/fundamentals/ip/subnetting.md) | IP Subnetting & VLSM | 60 min |
| 4 | RT-001 | Routing Fundamentals | 45 min |

**Stage 1 milestone:** You can build and troubleshoot a basic IP network. You understand how data moves from application to wire.

---

## Stage 2 — RF Fundamentals

*The physics doesn't care if you're a network engineer or an RF engineer. You need both.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 5 | RF-001 | RF Fundamentals (frequency, wavelength, power, dB) | 55 min |
| 6 | RF-002 | Modulation Techniques (AM, FM, PSK, QAM, OFDM) | 60 min |
| 7 | RF-003 | Antenna Theory (gain, directivity, polarisation, patterns) | 55 min |
| 8 | RF-004 | RF Propagation & Path Loss | 50 min |

**Stage 2 milestone:** You understand the decibel system, can describe common modulation schemes, and know what antenna gain and beamwidth mean.

---

## Stage 3 — Satellite Systems

*Orbital mechanics, link budgets, and how a satellite actually works.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 9 | RF-005 | Satellite Orbits (GEO, MEO, LEO — trade-offs and characteristics) | 50 min |
| 10 | RF-006 | Satellite Payload Architecture | 55 min |
| 11 | RF-007 | Frequency Bands (C, Ku, Ka, Q/V — characteristics and use cases) | 45 min |
| 12 | RF-008 | Link Budget Calculations | 75 min |
| 13 | RF-009 | Rain Fade & Atmospheric Attenuation | 45 min |
| 14 | RF-010 | Uplink & Downlink Design | 60 min |

**Stage 3 milestone:** You can read and sanity-check a link budget. You understand why Ka-band rains off and why GEO has latency.

---

## Stage 4 — Coding & Standards

*How satellite systems actually encode and transmit data.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 15 | RF-011 | Digital Modulation for Satellite (DVB-S2, DVB-S2X) | 60 min |
| 16 | RF-012 | Forward Error Correction (FEC) & Coding Gain | 50 min |
| 17 | RF-013 | Spectral Efficiency & MODCOD | 45 min |
| 18 | RF-014 | Multiple Access Schemes (TDMA, FDMA, CDMA, MF-TDMA) | 55 min |

---

## Stage 5 — IP over Satellite

*Where RF meets IP — and why it's not just the same as running IP on fibre.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 19 | RF-015 | Latency in Satellite Networks — causes and mitigations | 50 min |
| 20 | RF-016 | TCP Performance over Satellite (PEP, ACM) | 55 min |
| 21 | RF-017 | QoS in Satellite Networks | 50 min |
| 22 | RF-018 | Satellite Network Architectures (hub-and-spoke, mesh, hybrid) | 55 min |

---

## Stage 6 — Operations & Design

*Putting it all together: designing, operating, and troubleshooting.*

| Order | Module ID | Title | Est. Time |
|---|---|---|---|
| 23 | RF-019 | Satellite Network Operations — monitoring, alarms, escalation | 50 min |
| 24 | RF-020 | Frequency Planning & Interference Management | 60 min |
| 25 | RF-021 | Capacity Planning for Satellite Networks | 55 min |
| 26 | RF-022 | Troubleshooting RF & Satellite Links — systematic approach | 60 min |

---

## Recommended External Resources

| Resource | Cost | Best for |
|---|---|---|
| [ITU Radio Regulations](https://www.itu.int/en/ITU-R/Pages/default.aspx) | Free | Authoritative frequency allocation reference |
| [ETSI DVB Standards](https://www.dvb.org/standards) | Free | DVB-S2, DVB-S2X specifications |
| Pratt, Bostian, Allnutt — *Satellite Communications*, 2nd ed. | ~SGD 120 | The standard reference textbook |
| Roddy — *Satellite Communications*, 4th ed., McGraw-Hill | ~SGD 100 | Thorough introduction to satellite systems |
| [Satcom Direct Training](https://www.satcomdirect.com) | Varies | Vendor-specific operational training |
| [SSPI (Society of Satellite Professionals International)](https://www.sspi.org) | Membership | Industry professional development, networking |
