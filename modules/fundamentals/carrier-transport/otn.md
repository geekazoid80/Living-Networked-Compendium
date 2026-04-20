---
module_id: CT-011
title: "Optical Transport Network (OTN) - Deep Dive"
description: "OTN multiplexing hierarchy, ODU flexgrid, GCC channels, tandem connection monitoring, coherent optical modulation, and FlexE for high-capacity carrier transport."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 50
prerequisites:
  - CT-010
learning_path_tags:
  - CE
difficulty: advanced
tags:
  - otn
  - odu
  - otu
  - tcm
  - flexe
  - coherent
  - optical
  - carrier
  - g709
created: 2026-04-19
updated: 2026-04-19
---

# CT-011 - Optical Transport Network (OTN) - Deep Dive
## Learning Objectives

After completing this module you will be able to:

1. Describe the OTN frame structure - rows, columns, overhead bytes and their functions.
2. Explain ODU multiplexing - tributary slots, tributary port mapping, HO/LO ODU hierarchy.
3. Describe TCM - six independent monitoring layers, their endpoints, and use in multi-operator services.
4. Explain GFP (Generic Framing Procedure) for mapping Ethernet into OTN.
5. Describe FlexE - channel bonding for sub-rate and super-rate Ethernet services.
6. Explain coherent optical modulation - DP-QPSK and 16QAM trade-offs.

---
## Prerequisites

- CT-010 - SDH/SONET & OTN Basics (OTN overview, frame rates, FEC, DWDM)

---
## The Problem

CT-010 introduced OTN as a framing standard with FEC, overhead, and multiplexing. An engineer who provisions, monitors, and troubleshoots OTN-based transport services needs to go deeper: how exactly does ODU multiplexing work, where in the frame do OAM bytes live, how does tandem connection monitoring enable per-segment SLA enforcement, and what does FlexE enable for 100G+ client services?

This module builds OTN operational understanding from the frame structure up.

### Step 1: The OTN frame is a matrix of overhead and payload

An OTN frame (OTU, ODU, OPU layer) is a fixed-size matrix: 4 rows × 4080 columns × 8 bits, repeated at a rate determined by the signal rate. The first 7 columns of each row contain overhead; the remaining 3824 bytes carry the payload (OPU). The overhead is divided by layer - some bytes belong to the OTU layer (FEC, regenerator section), some to the ODU layer (path OAM, TCM), some to the OPU layer (payload type identifier, justification).

### Step 2: Nest lower-rate ODUs inside higher-rate ODUs

A 100G OTU4 wavelength can carry one 100GbE client, or it can carry four 25G ODU4-flex tributaries, or any combination of lower-rate ODUs that fit in the OPU4 tributary slot structure. This hierarchical multiplexing - packing ODU1s into an ODU2, ODU2s into an ODU3, ODU3s into an ODU4 - gives operators sub-wavelength granularity. A 100G wavelength serves multiple customers at 10G, 25G, or 40G each.

### Step 3: Monitor at multiple points along the path

An OTN service may traverse multiple operators and multiple amplifier spans. The OTN overhead includes **TCM (Tandem Connection Monitoring)** fields - six independent monitoring layers built into the ODU overhead. Each network segment (access, transit, core) can be monitored independently with its own performance counters and defect detection, without disrupting other segments. This enables per-operator SLA measurement on a multi-carrier service.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| OTN frame row × column overhead area | Section Monitoring (SM) / Path Monitoring (PM) overhead |
| Lower-rate signal packed into higher-rate container | ODU multiplexing / tributary slot |
| Independent OAM per network segment | TCM (Tandem Connection Monitoring) |
| Byte in OPU header identifying client type | Payload Structure Identifier (PSI / PT byte) |
| OTN framing for Ethernet at variable rates | ODUflex / GFP (Generic Framing Procedure) |
| Ethernet bonding over multiple OTN tributaries | FlexE (Flexible Ethernet) |
| DSP-based multi-level amplitude/phase modulation | Coherent optical (DP-QPSK, 16QAM, 64QAM) |

---
## Core Content

### OTN Frame Structure

An OTN frame is 4 rows × 4080 columns. The frame period depends on the signal rate:

| Signal | Frame period |
|---|---|
| OTU1 (2.666 Gbps) | ~48 µs |
| OTU2 (10.709 Gbps) | ~12 µs |
| OTU4 (111.809 Gbps) | ~1.2 µs |

**Column assignment:**

| Columns | Content |
|---|---|
| 1–7 | Overhead (OTU SM / ODU PM / TCM / OPU overhead) |
| 8–3824 | OPU payload (client data) |
| 3825–4080 | FEC (Reed-Solomon; 256 bytes per row) |

**Row 1 columns 1–7 - OTU/ODU/OPU overhead:**

| Row | Col 1–2 | Col 3–4 | Col 5–7 |
|---|---|---|---|
| 1 | FAS (Frame Alignment Signal: 0xF6F6F6282828) | OTU: SM (Section Monitoring) | OTU: GCC0 |
| 2 | OTU: RES | ODU: TCM ACT, TCM1–3 | ODU: GCC1 |
| 3 | ODU: TCM4–6 | ODU: PM + EXP | ODU: GCC2 |
| 4 | ODU: APS/PCC, RES | OPU: PSI [row 1] / NJO/PJO [rows 2–4] | OPU: RES |

**Key overhead bytes:**

- **FAS:** Frame Alignment Signal - 6-byte pattern (OA1/OA2 x3) identifying the start of each frame.
- **SM (Section Monitoring):** BIP-8 (B1 equivalent), Trail Trace Identifier (TTI - 64-byte string identifying source and destination of the OTU), SSF/SD/BEI/BIAE/BDI status bits.
- **PM (Path Monitoring):** Same structure as SM but for the ODU path end-to-end.
- **TCM1–6:** Six independent monitoring layers in the ODU overhead - each has its own BIP-8, TTI, and status bits.
- **GCC0/1/2 (General Communication Channel):** 2-byte overhead channels for management plane communication - used for DCN (Data Communications Network) between NMS and network elements.
- **PSI (Payload Structure Identifier):** 256-byte cyclic structure in OPU Row 1 Col 4, defining the payload type (PT byte in position 0) and tributary slot allocation map for multiplexed ODUs.
- **APS/PCC:** Automatic Protection Switching / Protection Communication Channel - used for OTN linear and ring protection signalling.

### ODU Multiplexing - HO and LO ODU

OTN multiplexing uses **tributary slots** - fixed portions of a higher-order (HO) ODU's OPU payload allocated to lower-order (LO) ODU signals.

**Tributary slot sizes by OTU level:**

| HO ODU | Tributary slot rate | Number of slots |
|---|---|---|
| ODU2 (10G) | ~1.25G (≈ 16 × ODU0) | 8 slots for ODU1, or 16 for ODU0 |
| ODU3 (40G) | ~1.25G (≈ 32) | 32 slots (can carry ODU1, ODU2, ODU0) |
| ODU4 (100G) | ~1.25G (≈ 80) | 80 slots (can carry ODU0/1/2/2e/3/flex) |

**Tributary port:** Each LO ODU occupies a set of tributary slots in the HO ODU. The tributary port number identifies which LO ODU the tributary slots belong to. The PSI overhead byte sequence maps tributary port → tributary slot allocation.

**Mixed multiplexing example:** An ODU4 carrying:
- 2 × ODU3 (each using 32 tributary slots = 64 total)
- 2 × ODU2 (each using 8 tributary slots = 16 total)
= 80 tributary slots filled exactly.

### TCM - Tandem Connection Monitoring

The ODU overhead includes **six independent TCM layers** (TCM1–6). Each TCM layer can be terminated at a different point in the network - independently monitoring a segment without affecting the end-to-end PM layer.

Use case - multi-carrier service:
- PM (Path Monitoring): end-to-end, carrier A to carrier C.
- TCM1: access segment (carrier A access node to carrier A gateway).
- TCM2: carrier A backbone segment.
- TCM3: inter-carrier handoff segment (carrier A gateway to carrier B gateway).
- TCM4: carrier B backbone segment.
- TCM5: carrier C segment.
- TCM6: spare / not used.

Each TCM layer independently measures BIP-8 bit errors, tracks trail trace ID, and reports BEI (Backward Error Indication) and BDI (Backward Defect Indication) - allowing each operator to prove their segment meets SLA without access to other operators' network management.

### GFP - Generic Framing Procedure (G.7041)

GFP maps variable-length client frames (Ethernet, Fibre Channel) into a synchronous OTN stream. Two modes:

**GFP-F (Frame-mapped):** Each client PDU is encapsulated in a GFP frame with a header (length, checksum) and mapped into the OPU payload. Idle frames fill gaps when no client data is present. Used for Ethernet over OTN.

**GFP-T (Transparent):** Maps 8B/10B-encoded signals (Fibre Channel, ESCON) block-by-block, preserving 8B/10B characters including idle characters. Used for storage protocol transport.

### ODUflex - Variable-Rate ODU

Standard ODU rates (ODU0=1.25G, ODU1=2.5G, ODU2=10G, ODU2e=10.3G, ODU3=40G, ODU4=100G) don't cover all Ethernet rates (25GbE, 50GbE, 200GbE, 400GbE). **ODUflex** (G.709 amendment) defines a flexible ODU rate matching any client rate. The number of 1.25G tributary slots is calculated to match the client bit rate. ODUflex uses GFP-F or CBR (constant bit rate) mapping.

### FlexE - Flexible Ethernet (OIF Implementation Agreement)

FlexE allows Ethernet MAC rates to be decoupled from Ethernet PHY rates. It bonds multiple 100G Ethernet PHYs into a single FlexE group, then sub-divides capacity in 5G increments.

Applications:
- **Bonding (super-rate):** Two 100G PHYs → one 200G FlexE service.
- **Sub-rate:** One 100G PHY → multiple sub-rate clients (e.g., 5G + 25G + 70G).
- **Channel isolation:** Each FlexE channel is isolated - one channel's traffic cannot consume another channel's slots (unlike standard Ethernet QoS).

FlexE is widely used for 5G fronthaul/midhaul transport (eCPRI over FlexE) and for creating deterministic bandwidth pipes between IP routers and transport equipment without running QoS on the optical layer.

### Coherent Optical - Modulation Formats

Modern DWDM systems use coherent detection with DSP-based digital signal processing. The modem selects the modulation format based on the link's optical signal-to-noise ratio (OSNR) budget:

| Modulation | Bits per symbol | Typical capacity | Typical reach |
|---|---|---|---|
| DP-BPSK | 2 | 100G | >3000 km (transoceanic) |
| DP-QPSK | 4 | 100G or 200G | 2000–5000 km |
| DP-16QAM | 8 | 200G or 400G | 500–2000 km |
| DP-64QAM | 12 | 400G or 600G | 100–500 km |

Higher modulation density = more bits per wavelength but requires higher OSNR (less reach, shorter span). Adaptive modulation (soft-decision FEC + variable constellation) allows the modem to select the optimal modulation for each link in real time.

---
## Common Pitfalls

1. **Not understanding FAS - treating random payload bits as frame alignment.** The FAS is a specific 6-byte pattern (0xF6F6F6282828) in rows 1–4, columns 1. Scrambling the payload (OTN mandates a polynomial scrambler) ensures random payload bits never mimic the FAS. Disabling the scrambler or using a non-standard scrambler polynomial causes false frame alignment - the receiver locks to the wrong position.

2. **TCM activation/deactivation protocol.** TCM layers must be activated before use and deactivated when not in use - an unmonitored TCM layer in pass-through mode is transparent (passes overhead without terminating). Activating a TCM layer at only one end means the far-end does not contribute BEI/BDI - one-sided monitoring. Always activate TCM at both endpoints of the monitored segment.

3. **GCC0 vs GCC1/2 scope.** GCC0 is in the OTU overhead - it is terminated at every OTN regenerator (every point where the OTU is terminated and re-generated). GCC1/2 are in the ODU overhead - they pass through OTU regenerators and are only terminated at ODU path endpoints. Use GCC0 for span-level management; GCC1/2 for end-to-end management plane transport.

4. **FlexE group misconfiguration.** A FlexE group requires all member PHYs to run at the same rate and be on the same physical device (or with precise phase alignment if distributed). A FlexE group with mismatched PHY speeds or timing fails to establish - FlexE channels are not created. Verify FlexE calendar (slot-to-channel mapping) is identical on both ends of the link.

5. **Modulation format mismatch.** If the transponder at one end selects DP-16QAM and the far-end expects DP-QPSK, the coherent receiver cannot demodulate the signal. Most modern transceivers auto-negotiate, but manual configuration overrides must match exactly. Always verify both ends report the same modulation format after link establishment.

---
## Practice Problems

**Q1.** An OTN network must carry six independent 10G client signals over a single 100G wavelength. How is this achieved, and what OTN structure is used?

??? answer
    The 100G wavelength is an OTU4, carrying one ODU4. The ODU4's OPU4 has 80 tributary slots (each ~1.25G). Six 10G client signals are each mapped into an ODU2 (which occupies 8 tributary slots each). Six ODU2s × 8 slots = 48 tributary slots out of 80 available - 32 slots remain unused (or available for additional services). Each client is first mapped via GFP-F into an OPU2, then wrapped in an ODU2 frame, and its tributary slots assigned in the OPU4 payload area of the ODU4. The PSI byte structure in OPU4 documents the tributary port and slot allocation for the multiplexer and demultiplexer at each end.

**Q2.** A multi-carrier service crosses three operators. How are TCM layers used to enable each operator to independently measure their segment's performance?

??? answer
    Three TCM layers are assigned - one per operator segment (e.g., TCM1 = Operator A, TCM2 = Operator B, TCM3 = Operator C). At each operator's ingress gateway, they activate their assigned TCM layer - the OAM bytes for that TCM layer are inserted into the ODU overhead. At their egress gateway, they terminate (read) that TCM layer, extracting BIP-8 error counts, BEI, BDI, and TTI. These measurements give the operator per-segment error rates for SLA reporting, independently of what other operators are measuring. The end-to-end PM (Path Monitoring) layer is separately terminated at the service endpoints (the two customer handoff points) and is not terminated by intermediate operators. This architecture allows each party to prove their segment meets contractual performance objectives.

**Q3.** What is the difference between DP-QPSK and DP-16QAM, and when would you choose each?

??? answer
    **DP-QPSK** (Dual-Polarisation Quadrature Phase Shift Keying) encodes 4 bits per symbol (2 bits per polarisation × 2 phases). It is spectrally efficient enough for 100G per wavelength with excellent noise tolerance - suitable for long-haul and ultra-long-haul spans (2000–5000+ km), transoceanic cables, and links with high amplification noise. **DP-16QAM** encodes 8 bits per symbol using 16 amplitude/phase states. It doubles spectral efficiency (200G or 400G per wavelength on the same channel width) but requires significantly higher OSNR - it is used on metro and regional links (500–2000 km) where signal quality is higher. Choose DP-QPSK when maximising reach is the priority; choose DP-16QAM when maximising capacity on shorter links where OSNR budget allows.

---
## Summary & Key Takeaways

- OTN frame: 4 rows × 4080 columns; columns 1–7 overhead, 8–3824 OPU payload, 3825–4080 FEC.
- **FAS** identifies frame boundaries; **SM/PM** provide section and path monitoring; **TCM1–6** provide six independent segment monitoring layers.
- **ODU multiplexing:** LO ODUs packed into HO ODUs via tributary slots (1.25G each); OTU4 has 80 slots.
- **TCM:** Multi-carrier per-segment SLA monitoring - up to 6 independent monitored segments per OTN path.
- **GFP-F:** Maps Ethernet frames into OTN OPU payload with variable length framing.
- **ODUflex:** Variable-rate ODU for non-standard Ethernet rates (25G, 50G, 400G).
- **FlexE:** Bonds multiple 100G PHYs; enables sub-rate channels with deterministic isolation.
- **Coherent modulation:** DP-QPSK for long-haul; DP-16QAM/64QAM for metro/regional - select based on OSNR budget.
- GCC0 is OTU-level (terminated at every regenerator); GCC1/2 are ODU-level (end-to-end).

---
## Where to Next

- **CT-012 - Traffic Engineering:** Coordination between OTN transport and IP/MPLS TE.
- **CT-010 - SDH/SONET & OTN Basics:** Foundational concepts for this module.
- **CT-009 - Carrier Ethernet Services:** Ethernet services riding on OTN transport.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| ITU-T G.709 | OTN frame structure, OTU/ODU/OPU hierarchy |
| ITU-T G.7041 | GFP (Generic Framing Procedure) |
| ITU-T G.7042 | Link Capacity Adjustment Scheme (LCAS) |
| OIF FlexE 2.1 | Flexible Ethernet implementation agreement |
| ITU-T G.694.1 | DWDM channel plan |
| Cisco CCIE Service Provider | OTN transport understanding |

---
## References

- ITU-T G.709 - OTN Interfaces. [https://www.itu.int/rec/T-REC-G.709](https://www.itu.int/rec/T-REC-G.709)
- ITU-T G.7041 - GFP. [https://www.itu.int/rec/T-REC-G.7041](https://www.itu.int/rec/T-REC-G.7041)
- OIF FlexE Implementation Agreement. [https://www.oiforum.com/technical-work/hot-topics/flexe/](https://www.oiforum.com/technical-work/hot-topics/flexe/)

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
| CT-012 | Traffic Engineering | TE-OTN coordination for end-to-end path optimisation |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| CT-010 | SDH/SONET & OTN Basics | OTN foundations: rates, FEC, DWDM |
<!-- XREF-END -->
