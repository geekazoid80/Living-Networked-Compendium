---
title: "Coloured Optics - CWDM & DWDM"
module_id: "AM-007"
domain: "fundamentals/access-media"
difficulty: "intermediate"
prerequisites: ["NW-003", "AM-006"]
estimated_time: 35
version: "0.1"
last_updated: "2026-05-18"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [optical, cwdm, dwdm, wavelength, multiplexing, mux, demux, itu-grid]
cert_alignment: ""
vendors: []
language: en
---

## Planned Module

This module is a planned stub. It is referenced as a forward-link from [Ethernet Standards & Cabling](../networking/ethernet-cabling.md) (`NW-003`) but the substantive content has not yet been written.

Until it lands, see [Grey Optical](grey-optical.md) (`AM-006`) for the single-wavelength baseline this module builds on, and the parent ethernet-cabling module for transceiver-form-factor context.

## Scope (planned)

Once written, the reader will be able to:

1. **Explain** how CWDM (Coarse Wavelength Division Multiplexing, 20 nm spacing, ITU-T G.694.2) and DWDM (Dense, 0.4 to 0.8 nm spacing, ITU-T G.694.1) carry multiple independent links over one fibre pair.
2. **Compare** CWDM versus DWDM trade-offs: channel count, optical amplification (EDFA / Raman) compatibility, transceiver cost, and operational complexity.
3. **Plan** a wavelength assignment for a small CWDM ring and compute the per-span optical budget.
4. **Diagnose** common multi-wavelength failure modes (mux insertion loss, cross-talk, EDFA tilt) using OTDR and OSA evidence.

## How to contribute

This module needs an author. To claim it, open an issue or PR referencing module ID `AM-007`. The structure must follow [`MODULE_TEMPLATE.md`](../../../MODULE_TEMPLATE.md).

## References (placeholder)

Substantive content and standards references will be added by the author. Likely sources include ITU-T G.694.1 (DWDM grid), ITU-T G.694.2 (CWDM grid), ITU-T G.692, MEF carrier-ethernet specifications, and vendor SFP+ / QSFP DWDM tunable-optic documentation.
