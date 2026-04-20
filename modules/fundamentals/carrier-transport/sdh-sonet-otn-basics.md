---
module_id: CT-010
title: "SDH/SONET & OTN Basics"
description: "The architecture of synchronous digital hierarchy (SDH/SONET) and optical transport network (OTN) - the physical and optical transport layers beneath IP/MPLS carrier networks."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - CT-001
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - sdh
  - sonet
  - otn
  - transport
  - optical
  - synchronous
  - tdm
  - carrier
created: 2026-04-19
updated: 2026-04-19
---

# CT-010 - SDH/SONET & OTN Basics
## Learning Objectives

After completing this module you will be able to:

1. Describe the SONET/SDH hierarchy - signal rates, containers, and multiplexing.
2. Explain the SDH frame structure - sections, lines/multiplex sections, paths.
3. Describe DWDM - wavelengths, channel spacing, amplification.
4. Explain OTN (G.709) - OTU rates, ODU hierarchy, FEC, and overhead.
5. Describe how IP/MPLS traffic is mapped into OTN containers.
6. Explain protection mechanisms at the transport layer - MSP, SNCP, OTU protection.

---
## Prerequisites

- CT-001 - MPLS Fundamentals (IP transport context; what runs above the optical layer)

---
## The Problem

An IP/MPLS network forwards packets - but what actually carries those packets between cities? Between continents? Between PE routers that are 2000 km apart? The answer is not a long Ethernet cable. Between major nodes, IP traffic is carried on **optical transport infrastructure** - a separate technology layer with its own framing, multiplexing, protection, and OAM that operates below the IP layer.

Understanding this layer matters for carrier engineers because: transport capacity is provisioned separately from IP routing; faults at the optical transport layer cause IP path failures that appear to the IP layer as link drops; optical alarms feed into network management and must be correlated with IP events.

### Step 1: Synchronous framing - SDH/SONET

Before packet networks dominated, telephone networks carried voice using **TDM (Time-Division Multiplexing)** - each voice call was assigned a fixed time slot in a regular frame. **SONET** (North America) and **SDH** (international) standardised the optical framing for these TDM signals, providing: a standard frame structure, byte-synchronous multiplexing, and built-in OAM channels.

Even as IP traffic replaced voice, SDH/SONET remained the transport layer - IP packets were mapped into SDH containers (cells in a regular frame) and carried across optical rings.

### Step 2: Wavelength multiplexing - DWDM

A single optical fibre can carry multiple wavelengths (colours) of light simultaneously - each wavelength is a separate channel carrying independent data. **DWDM (Dense Wavelength-Division Multiplexing)** multiplexes dozens or hundreds of wavelengths onto one fibre, increasing capacity from a single channel to 80 or 400 channels on the same fibre. Each wavelength typically carries a 100G, 200G, or 400G signal.

### Step 3: Optical transport framing - OTN

**OTN (Optical Transport Network, ITU-T G.709)** is the modern transport standard designed for packet-optimised networks (not TDM). OTN wraps client signals (Ethernet, SONET, SDH, IP) in a standardised container with:
- Forward Error Correction (FEC) - correcting bit errors over long optical spans.
- Nested overhead for OAM at multiple layers.
- A hierarchical multiplexing structure for carrying multiple clients on one wavelength.

OTN is the current standard for carrier core transport. SDH/SONET is legacy but still present - millions of circuit-based leased lines still rely on it.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Fixed-frame TDM hierarchy (North America) | SONET (Synchronous Optical Network) |
| Fixed-frame TDM hierarchy (international) | SDH (Synchronous Digital Hierarchy) |
| SONET base rate (51.84 Mbps) | OC-1 / STS-1 |
| SDH base rate (155.52 Mbps) | STM-1 |
| Multiple wavelengths on one fibre | DWDM |
| Each wavelength | Optical channel (OCh) |
| Modern optical transport standard | OTN (G.709) |
| OTN basic data unit | OTU (Optical Transport Unit) |
| FEC applied at the OTN layer | Reed-Solomon or EFEC |

---
## Core Content

### SONET/SDH Hierarchy

SONET and SDH are equivalent technologies standardised in parallel (SONET in North America by Bellcore/ANSI; SDH internationally by ITU-T). Both use synchronous TDM framing.

**Signal rates:**

| SONET Level | SDH Level | Line Rate |
|---|---|---|
| OC-1 / STS-1 | - | 51.84 Mbps |
| OC-3 / STS-3 | STM-1 | 155.52 Mbps |
| OC-12 / STS-12 | STM-4 | 622.08 Mbps |
| OC-48 / STS-48 | STM-16 | 2.488 Gbps |
| OC-192 / STS-192 | STM-64 | 9.953 Gbps |
| OC-768 / STS-768 | STM-256 | 39.813 Gbps |

Higher rates are exact multiples of the base rate (OC-1 = 51.84 Mbps; OC-N = N × 51.84 Mbps).

**SDH frame structure:**

An STM-1 frame is 270 columns × 9 rows × 8 bits = 19,440 bits, transmitted every 125 µs (matching the 8 kHz voice sampling rate). The frame consists of:
- **Section Overhead (SOH):** First 3 columns × 9 rows per block. Includes framing bytes (A1/A2), section-level OAM (B1 BIP parity, E1 orderwire, F1 user channel), and multiplexer section overhead.
- **AU (Administrative Unit) pointer:** Locates the payload within the frame - allows flexible payload positioning (pointer justification handles SDH clock differences).
- **Virtual Container (VC) payload:** The SDH container carrying the client signal.

**Virtual containers** are the SDH payload containers. VC-4 (139.264 Mbps payload) is the primary container for STM-1; VC-12 (2.048 Mbps) carries E1 circuits; VC-3 (34.368 Mbps) carries DS3/E3.

**SDH layering:**
- **Regenerator section:** Between adjacent SDH regenerators; B1 parity monitoring.
- **Multiplex section:** Between SDH multiplexers; B2 parity, AIS/RDI signalling, Automatic Protection Switching (APS/MSP).
- **Path:** End-to-end VC path between path-terminating equipment; B3 parity, path-level OAM.

### DWDM - Dense Wavelength-Division Multiplexing

DWDM multiplexes multiple optical wavelengths on a single fibre pair. Each wavelength carries an independent data stream.

**Channel grid:** ITU-T G.694.1 defines the DWDM channel grid around 193.1 THz (1550 nm window). Standard spacings:
- **100 GHz spacing:** 40 channels on the C-band
- **50 GHz spacing:** 80 channels
- **25 GHz (flex-grid):** 96+ channels; supports various signal bandwidths

**Optical amplification:** Optical signals attenuate over distance. **EDFA (Erbium-Doped Fibre Amplifier)** amplifies all wavelengths simultaneously at ~80 km intervals without converting to electrical signals - purely optical amplification. This extended the practical distance of optical transmission to transoceanic scales.

**ROADM (Reconfigurable Optical Add/Drop Multiplexer):** Allows wavelengths to be added, dropped, or passed through at a network node without converting to electrical signals. Enables optical mesh networking - wavelength paths can be established and rerouted through software without physical rewiring.

**Coherent optical:** Modern DWDM uses coherent detection (with DSP) to achieve higher spectral efficiency. A single wavelength carries 100G, 200G, or 400G using advanced modulation (DP-QPSK, 16QAM, 64QAM). The modulation format is selected based on the link distance and noise budget.

### OTN - Optical Transport Network (G.709)

OTN (ITU-T G.709) is the modern optical transport standard, designed for packet networks. OTN provides:
- Standardised framing for any client signal (Ethernet, SONET, SDH, MPLS).
- FEC (Forward Error Correction) - corrects bit errors without retransmission, extending optical reach.
- Nested OAM overhead at multiple layers.
- Hierarchical multiplexing.

**OTN layer model:**

| Layer | Abbreviation | Function |
|---|---|---|
| Optical Channel | OCh | One wavelength end-to-end |
| Optical Multiplex Section | OMS | Between OADMs; all wavelengths |
| Optical Transmission Section | OTS | Between optical amplifiers/regenerators |
| Optical Transport Unit | OTU | Client mapping with FEC |
| Optical Data Unit | ODU | Client framing without FEC |
| Optical Payload Unit | OPU | Actual client payload |

**OTU rates (G.709):**

| OTU Level | Client rate | Line rate (with FEC) |
|---|---|---|
| OTU1 | OC-48 / STM-16 (2.5G) | 2.666 Gbps |
| OTU2 | OC-192 / STM-64 (10G) | 10.709 Gbps |
| OTU3 | OC-768 / STM-256 (40G) | 43.018 Gbps |
| OTU4 | 100GbE | 111.809 Gbps |

**FEC in OTN:** The OTN FEC (Reed-Solomon RS(255,239)) adds ~7% overhead to the line rate. Enhanced FEC (EFEC or OFEC in modern coherent systems) provides additional coding gain - effectively extending optical reach by reducing the signal-to-noise ratio required.

**ODU multiplexing:** ODUs can be multiplexed - lower-rate ODUs are packed into higher-rate ODUs. Example: four ODU2 (10G) signals multiplex into one ODU3 (40G). This enables sub-wavelength granularity - a 100G wavelength (OTU4) can carry multiple lower-rate client services.

### Mapping IP/MPLS into OTN

The path from an IP router to the optical layer:

```
IP router (100GbE port)
    → 100GbE signal enters transponder / muxponder
    → Mapped into OPU4 payload
    → Wrapped in ODU4 frame (OAM added)
    → Wrapped in OTU4 frame (FEC added)
    → Modulated onto a 100G or 200G optical wavelength
    → Multiplexed with other wavelengths on the DWDM mux
    → Transmitted on the fibre
```

**Transparent vs opaque transport:**
- **Transparent (passthrough):** The OTN network switches optical wavelengths without converting to electrical signals (all-optical switching via ROADMs). Lower latency; preserves exact client signal.
- **Opaque (regeneration):** The OTN network terminates the optical signal, processes the OTN frame (OAM, FEC), and re-generates the optical signal. Allows per-OTU monitoring and switching.

### Protection at the Transport Layer

**MSP (Multiplex Section Protection, 1+1 or 1:N):** SDH/SONET ring or linear protection. On failure, traffic switches from the working to the protection fibre/ring segment. Recovery ~50ms. Defined in ITU-T G.841 for rings (MSSPRING) and G.783 for linear.

**SNCP (Subnetwork Connection Protection):** Path-level protection - the source sends traffic on both working and protection paths simultaneously; the sink selects the better signal. True 1+1 path protection; seamless switching.

**OTU/ODU protection (G.873.1):** OTN equivalent of SDH linear protection - ODU-level 1+1 or 1:N protection at the OTN layer.

---
## Common Pitfalls

1. **Confusing SONET/SDH rates with Ethernet rates.** OC-48 ≈ 2.5 Gbps, but its actual rate (2.488 Gbps) differs slightly from Gigabit Ethernet (1 Gbps) or 10 GbE (10 Gbps). Mapping Ethernet into SONET requires justification/adaptation because the rates don't align exactly. OTN solves this via asynchronous mapping with frequency justification.

2. **OTN overhead not accounted for in capacity planning.** OTU4 carries 100GbE client traffic but the line rate is ~111.8 Gbps (FEC overhead). The 11.8 Gbps is used by FEC, not available for client data. When calculating wavelength capacity, use the client rate (100G), not the line rate.

3. **Alarm propagation direction confusion.** In SDH/OTN, AIS (Alarm Indication Signal) propagates downstream (away from the failure). RDI (Remote Defect Indication) propagates upstream (toward the failure source) - it tells the far-end equipment "you're sending me defective signal." Engineers often confuse which direction each alarm flows when correlating faults.

4. **Assuming IP and optical fault timescales align.** Transport protection switching (50ms) happens faster than IP routing convergence (seconds). An IP network management system may see a link flap that is actually a transport protection switch - the link recovered before IP even knew it was gone. Over-reacting to short-duration link events at the IP layer when transport protection is in place wastes resources.

5. **Mixing SONET and SDH terminology in multi-vendor environments.** North American carriers use SONET terminology (OC-N, STS-N, VT); international carriers use SDH (STM-N, VC). The rates and structure are equivalent but the naming is different. Always clarify which standard is being used in cross-vendor documentation.

---
## Practice Problems

**Q1.** A 10 GbE IP link runs over OTN OTU2. What is the approximate line rate on the optical wavelength, and why is it higher than 10 Gbps?

??? answer
    The OTU2 line rate is approximately **10.709 Gbps**. The 10 GbE client signal (10.3125 Gbps, including Ethernet 64b/66b encoding overhead) is mapped into an OPU2 payload, wrapped in ODU2 (adding OTN overhead bytes for OAM), then wrapped in OTU2 with Reed-Solomon FEC (RS(255,239)). The FEC adds approximately 7% overhead to correct optical transmission errors - extending the effective reach of the link without requiring retransmission. The FEC overhead is the difference between the 10G client rate and the ~10.7G line rate.

**Q2.** What is the difference between an EDFA and a ROADM, and what does each do for the optical network?

??? answer
    An **EDFA (Erbium-Doped Fibre Amplifier)** amplifies all optical wavelengths simultaneously in the optical domain - it boosts signal power to compensate for fibre attenuation over distance (~80 km between amplifiers). It does not add or drop specific wavelengths; it simply amplifies everything passing through it. A **ROADM (Reconfigurable Optical Add/Drop Multiplexer)** selectively adds (inserts) and drops (extracts) specific wavelengths at a network node, while passing others through. ROADMs are remotely configurable - wavelength routing can be changed via software without physical rewiring, enabling optical mesh networking and wavelength-path provisioning.

**Q3.** A carrier uses SDH MSP (ring protection) on their backbone. During a fibre cut, the IP layer detects a link down event for 200ms before the link recovers. Is this expected, and what does it indicate?

??? answer
    200ms is longer than expected for MSP protection (target <50ms) but may reflect several factors: (1) The 200ms may include both the MSP protection switch (~50ms) and subsequent IP hello timer expiry/recovery time - these are additive. (2) If MSP switching is on a slower path or experienced a double fault, it could take longer. (3) The link down event seen by the IP layer may be caused by the loss of optical signal during the fault - even if MSP recovers the path quickly, the IP physical layer may register the transient as a link down. Review SONET APS/MSP switching logs to confirm protection switching occurred within 50ms; if not, investigate the MSP configuration, APS byte signalling, or ring topology for issues.

---
## Summary & Key Takeaways

- **SONET/SDH:** Synchronous TDM optical transport - fixed 125µs frame, byte-synchronous multiplexing, built-in OAM. OC-N (SONET) = STM-N/4 (SDH). Legacy but still widespread.
- **DWDM:** Multiple wavelengths on one fibre - 40 to 400+ channels per fibre pair; EDFA amplifies; ROADMs switch wavelengths.
- **OTN (G.709):** Modern optical transport - wraps any client signal, adds FEC, nested OAM hierarchy, ODU multiplexing for sub-wavelength granularity.
- **FEC:** ~7% overhead on OTU rates; corrects bit errors optically, extending reach.
- Transport protection (MSP, SNCP, ODU protection) targets <50ms recovery - faster than IP routing convergence.
- AIS propagates downstream; RDI propagates upstream - understand alarm direction for fault localisation.
- IP/MPLS runs above the optical transport layer; transport faults appear as link drops to the IP layer.

---
## Where to Next

- **CT-011 - Optical Transport Network (OTN):** Deep dive into OTN multiplexing, ODU hierarchy, and modern coherent transport.
- **CT-012 - Traffic Engineering:** Coordination between IP/MPLS TE and optical transport layer.
- **CT-009 - Carrier Ethernet Services:** Carrier Ethernet riding on SDH/OTN transport.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| ITU-T G.707 | SDH Network Node Interface |
| ITU-T G.709 | Interfaces for the Optical Transport Network (OTN) |
| ITU-T G.694.1 | DWDM Frequency Grid |
| ITU-T G.841 | SDH Ring Protection |
| ANSI T1.105 | SONET Base Standard |
| Cisco CCIE Service Provider | Transport layer understanding |

---
## References

- ITU-T G.709 - Interfaces for the OTN. [https://www.itu.int/rec/T-REC-G.709](https://www.itu.int/rec/T-REC-G.709)
- ITU-T G.694.1 - DWDM Frequency Grid. [https://www.itu.int/rec/T-REC-G.694.1](https://www.itu.int/rec/T-REC-G.694.1)
- ITU-T G.707 - SDH Network Node Interface. [https://www.itu.int/rec/T-REC-G.707](https://www.itu.int/rec/T-REC-G.707)

---
## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| CT-011 | Optical Transport Network (OTN) | OTN deep dive; CT-010 provides the foundation |
| CT-012 | Traffic Engineering | TE coordination with optical transport |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-001 | MPLS Fundamentals | IP/MPLS layer that rides above optical transport |
<!-- XREF-END -->
