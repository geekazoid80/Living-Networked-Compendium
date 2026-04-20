---
title: "Ethernet Standards & Cabling"
module_id: "NW-003"
domain: "fundamentals/networking"
difficulty: "novice"
prerequisites: ["NW-001", "NW-002"]
estimated_time: 35
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [ethernet, cabling, copper, fibre, sfp, cat5e, cat6, transceiver, physical-layer]
vendors: []
language: en
cert_alignment: "CCNA 200-301 — 1.3; CompTIA Network+ — 1.3; JNCIA-Junos — Networking Fundamentals"
---

## The Problem

You have two computers you want to connect. You run a copper wire between them. It works — at one metre.

Now stretch that wire across a building. The signal weakens, picks up noise from power cables nearby, and by the time it reaches the other end, bits are corrupted. You need to rebuild the wire.

### Step 1: Twist the wires to cancel interference

Electrical signals in a wire radiate noise, and nearby cables radiate noise back. The fix: twist pairs of wires around each other. The twist causes the noise to cancel itself out — what hits one wire hits the other equally, and the difference signal carries your data cleanly.

This is **Unshielded Twisted Pair (UTP)** — the foundation of copper Ethernet cabling.

### Step 2: More twists, tighter twists, better shielding for longer or faster links

As you push more data faster and over longer distances, the twisted pairs need tighter wists, better insulation between pairs, and sometimes metallic shielding around the bundle. Each generation of the standard sets tighter tolerances.

That's why there are **cable categories** — Cat5e, Cat6, Cat6A, Cat7. Each is a tighter specification of the same basic concept, tested to carry more bandwidth with less crosstalk over the specified distance.

### Step 3: Copper has limits — distance and speed

Copper attenuates the signal. Past roughly 100 metres for standard Ethernet, the signal is too weak. You either need a repeater (switch), or a different medium.

And copper can only carry so much frequency. At 10 Gbps and beyond over long distances, you need something that doesn't have the same physics limitations.

### Step 4: Light in a glass tube

Glass fibre carries light instead of electricity. Light doesn't attenuate the way electrical signals do, doesn't pick up electromagnetic interference, and can carry vastly more bandwidth over vastly longer distances.

The trade-off: fibre requires a transceiver — a device that converts electrical signals from the network interface to light and back. And the glass itself is fragile compared to copper.

Different use cases call for different fibre: **multimode** for short runs (inside a building), **single-mode** for long runs (between buildings, across cities).

### Step 5: Standardise the transceiver so equipment is interchangeable

Rather than build the optical transceiver permanently into every piece of equipment, the industry settled on swappable form factors — pluggable modules that clip into a standard port. Different modules for different speeds, distances, and wavelengths, all fitting the same slot.

That's the **SFP/QSFP family** of transceivers — pluggable optics that let you mix and match media without replacing the switch or router.

### What You Just Built

Ethernet physical media is the answer to a series of engineering constraints: cancel interference (twisted pair), extend distance (fibre), scale bandwidth (tighter standards), and enable interchangeability (pluggable transceivers). Each generation solves the bottleneck of the previous one.

| Constraint | Solution | Technical term |
|---|---|---|
| Wire interference | Twist wire pairs together | UTP (Unshielded Twisted Pair) |
| Faster speeds / longer copper runs | Tighter twists, shielding, stricter tolerances | Cable categories (Cat5e → Cat6A) |
| Distance limit of copper | Use glass fibre and light | Fibre optic cabling |
| Different distances / wavelengths | Choose the right fibre type | Multimode vs. single-mode |
| Swappable optics without replacing equipment | Standard pluggable transceiver module | SFP / QSFP |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Identify** the common copper cabling categories (Cat5e, Cat6, Cat6A) and their specifications
2. **Distinguish** between multimode and single-mode fibre and when each is used
3. **Select** the appropriate cable or transceiver for a given link distance, speed, and environment
4. **Recognise** common connector and transceiver types (RJ-45, LC, SC, SFP, QSFP)
5. **Explain** why direct attach cable (DAC) and active optical cable (AOC) exist as alternatives

---

## Prerequisites

- [The OSI Model](osi-model.md) (`NW-001`) — specifically, understanding that cabling operates at Layer 1 (Physical)
- [Network Topologies](network-topologies.md) (`NW-002`) — understanding the physical layouts that cabling must support

---

## Core Content

### Copper: Unshielded Twisted Pair (UTP)

UTP is the dominant copper medium for short-range Ethernet. Eight wires, twisted into four pairs, terminated with an RJ-45 connector.

The "category" defines the cable's performance specification — how much bandwidth it can carry with acceptable crosstalk (interference between adjacent pairs):

| Category | Max speed (typical) | Max distance | Notes |
|---|---|---|---|
| Cat5e | 1 Gbps | 100 m | Minimum for new installations; widely deployed |
| Cat6 | 1 Gbps / 10 Gbps (to 55 m) | 100 m / 55 m | Better crosstalk rejection; common in new builds |
| Cat6A | 10 Gbps | 100 m | Augmented Cat6; required for 10G to full 100 m |
| Cat7 | 10 Gbps | 100 m | Shielded; GG45/TERA connectors; niche use |
| Cat8 | 25/40 Gbps | 30 m | Data centre patch cabling; very short runs |

!!! success "Standard — TIA/EIA-568"
    Copper cabling performance specifications (categories, distances, connector pinouts) are defined by TIA/EIA-568 (Telecommunications Industry Association) and ISO/IEC 11801. All compliant cables of the same category must meet the same performance floor.

??? supplementary "Straight-through vs. Crossover cables"
    Ethernet cables come in two pinout configurations:

    - **Straight-through:** Pin 1 connects to Pin 1 at both ends. Used to connect unlike devices (PC to switch, switch to router).
    - **Crossover:** Transmit pins on one end connect to receive pins on the other. Used to connect like devices (PC to PC, switch to switch) without an intermediate device.

    Modern equipment with **Auto-MDI/MDIX** (almost everything made after 2002) detects the connection type and adjusts automatically — you can use either cable. But in legacy or industrial environments, you may still encounter crossover requirements.

---

### Copper: Shielded Variants

Environments with high electromagnetic interference (factory floors, data centres with dense cable runs) may require shielded cable:

| Type | Shield coverage | Use case |
|---|---|---|
| UTP | None | Standard office/campus |
| F/UTP (FTP) | Overall foil wrap | Moderate interference environments |
| S/UTP (ScTP) | Braided screen around bundle | Higher-interference environments |
| SF/UTP | Foil + braid | Severe interference |
| S/FTP | Braid around bundle + foil per pair | Maximum shielding; data centre, industrial |

Shielded cable requires proper grounding at both ends. An improperly grounded shield can act as an antenna and make interference worse.

---

### Fibre Optic Cabling

Fibre carries light through a glass or plastic core. No electrical signal means no electromagnetic interference, no crosstalk, and much longer distances.

#### Multimode Fibre (MMF)

Multiple paths (modes) of light travel through a relatively thick core (50 µm or 62.5 µm). Multiple modes cause dispersion — the light pulses spread as they travel, limiting distance.

**Use case:** Short-range, high-speed links — within a data centre, between floors of a building, campus backbone up to ~500 m.

Common multimode grades:

| Grade | Core | Max distance (10G) | Max distance (100G) |
|---|---|---|---|
| OM3 | 50 µm | 300 m | 100 m |
| OM4 | 50 µm | 400 m | 150 m |
| OM5 | 50 µm | 400 m (SWDM) | 150 m | 

#### Single-Mode Fibre (SMF)

A very thin core (8–10 µm) allows only one path of light. No modal dispersion — light travels in a straight line. Much longer distances.

**Use case:** Long-range links — campus to campus, building interconnects, metropolitan and wide-area links, undersea cables. Distances from 10 km to thousands of km depending on amplification.

Common single-mode grades:

| Type | Standard | Typical use |
|---|---|---|
| OS1 | ITU-T G.652 | Indoor, tighter bend radius |
| OS2 | ITU-T G.652D/G.657 | Outdoor, long-haul, low-water-peak |

#### Connectors

| Connector | Form factor | Common use |
|---|---|---|
| LC (Lucent Connector) | Small form factor, duplex | SFP modules, patch panels |
| SC (Subscriber Connector) | Larger, push-pull | Older equipment, some patch panels |
| MPO/MTP | Multi-fibre (8, 12, 24 fibres) | High-density data centre trunk cabling |
| ST (Straight Tip) | Bayonet-style | Legacy enterprise, some industrial |

LC is the dominant connector for modern SFP-based links. MPO is used for high-density parallel optic links (QSFP to breakout panels).

---

### Transceivers: SFP, QSFP, and the Pluggable Ecosystem

Rather than integrating the optical transceiver permanently into equipment, modern switches and routers use **pluggable transceiver modules** — a standard mechanical form factor with an electrical interface on the equipment side and an optical (or copper) interface on the link side.

| Form factor | Typical speeds | Notes |
|---|---|---|
| SFP (Small Form-factor Pluggable) | 100 Mbps – 1 Gbps | 1G links; ubiquitous in enterprise and carrier |
| SFP+ | 10 Gbps | 10G links; same physical size as SFP |
| SFP28 | 25 Gbps | 25G; common in data centre server links |
| QSFP+ | 4×10G = 40 Gbps | 40G links; used in spine/aggregation |
| QSFP28 | 4×25G = 100 Gbps | 100G links; dominant in modern DC spine |
| QSFP-DD | 8×25G / 8×50G = 200/400 Gbps | 400G; emerging in hyperscale data centres |

!!! info "Proprietary — Seeking Standardisation"
    Transceiver form factors (SFP, QSFP) originated as multi-vendor agreements (SFF Committee) and are widely implemented. The electrical interface specifications (SFF-8472, SFF-8636) are published. However, some vendors implement **DOM** (Digital Optical Monitoring) and **vendor lock** differently — some equipment will only accept transceivers with that vendor's coded EEPROM. Check compatibility before purchasing third-party optics.

#### Direct Attach Cable (DAC)

A short passive copper cable with SFP/QSFP connectors factory-terminated at both ends. No optical transceiver — the cable is the connection.

- Range: 1–7 m (passive); up to ~15 m (active DAC)
- Speed: matches the connector (10G SFP+, 25G SFP28, 100G QSFP28)
- Use case: top-of-rack to spine switch connections in data centres

Lower cost than optical SFP + fibre. No laser, no glass. The dominant connection for sub-5 m links.

#### Active Optical Cable (AOC)

A factory-terminated cable where the transceiver is integrated into the cable connector and uses optical fibre for the run. Lighter and more flexible than DAC at longer lengths (3–100 m).

- Use case: longer rack-to-rack or inter-row connections where DAC is too stiff or heavy
- No field-replaceable transceiver — the cable and transceiver are one unit

---

### Ethernet Speed Standards

Ethernet has evolved from 10 Mbps coaxial in 1980 to 400 Gbps and beyond. The key milestones:

| Standard | Speed | Media | Year |
|---|---|---|---|
| 10BASE-T | 10 Mbps | Cat3 copper | 1990 |
| 100BASE-TX (Fast Ethernet) | 100 Mbps | Cat5 copper | 1995 |
| 1000BASE-T (Gigabit Ethernet) | 1 Gbps | Cat5e/6 copper | 1999 |
| 1000BASE-SX/LX | 1 Gbps | MMF / SMF | 1998 |
| 10GBASE-T | 10 Gbps | Cat6A copper | 2006 |
| 10GBASE-SR/LR | 10 Gbps | MMF / SMF | 2002 |
| 25GBASE-SR | 25 Gbps | MMF | 2016 |
| 40GBASE-SR4 | 40 Gbps | MMF (×4) | 2010 |
| 100GBASE-SR4/LR4 | 100 Gbps | MMF / SMF | 2010 |
| 400GBASE-SR8/DR4 | 400 Gbps | MMF / SMF | 2018 |

!!! success "Standard — IEEE 802.3"
    All Ethernet physical layer specifications are defined in IEEE 802.3. The naming convention is: `[speed]BASE-[medium code]`. `T` = twisted pair, `S` = short-wavelength (MMF), `L` = long-wavelength (SMF), `R` = large block coding, numbers = parallel fibre count.

??? supplementary "Why does copper top out at 100 m?"
    Copper Ethernet uses echo cancellation and advanced signal processing to deal with crosstalk and attenuation. But the physics still limits how much signal remains after 100 m of copper at high frequencies. 

    Higher-speed standards (10GBASE-T, 40GBASE-T) require progressively tighter cabling specifications (Cat6A, Cat8) to work at all, and often run at reduced distances.

    Fibre doesn't have this problem — light attenuation in fibre is much lower, and there's no crosstalk between fibre strands. For anything over 100 m, or anything 25 Gbps and above at any distance beyond a rack, fibre is the standard choice.

---

## Common Pitfalls

### Pitfall 1: Using Cat6 cable and expecting 10G to full 100 m

Cat6 supports 10 Gbps only to 55 m (under the standard). From 55–100 m, Cat6 is only certified for 1 Gbps. If you need 10 Gbps to the full 100 m standard Ethernet distance, you need Cat6A. Vendors sometimes sell "10G-capable Cat6" — read the fine print.

### Pitfall 2: Mixing multimode and single-mode fibre or transceivers

A multimode transceiver plugged into single-mode fibre (or vice versa) will technically connect — you won't get a link error immediately — but the link will have high bit error rates or simply fail at any distance. The wavelengths and core sizes are designed as a system. SMF uses 1310 nm or 1550 nm; MMF typically uses 850 nm. They are not interchangeable.

### Pitfall 3: Forgetting bend radius

Fibre is glass. Bend it too sharply and you crack the core or cause light to escape, causing signal loss. Every fibre cable has a minimum bend radius specification. Violations won't always be obvious immediately — the link may work at lower quality until the fibre eventually fails. Use proper cable management.

### Pitfall 4: Vendor transceiver lock-in

Some vendors (notably Cisco on certain platforms) will reject third-party transceivers by default. You may need to enable a compatibility override (`service unsupported-transceiver` on Cisco IOS). Verify compatibility before purchasing, especially in production environments.

---

## Practice Problems

1. You need to run a 10 Gbps link between two switches 80 metres apart inside a building. What cable category do you specify for copper? What fibre option is available?

2. A data centre row switch needs to connect to the top-of-rack switches 3 metres away at 100 Gbps. What is the most cost-effective physical medium?

3. You have a 300-metre fibre run between two campus buildings at 10 Gbps. Should you use multimode or single-mode? Why?

4. A technician tells you they installed Cat6 cabling rated for 10G. You measure the run at 70 metres. Is this compliant for 10G? What should have been installed?

??? supplementary "Answers"
    **1.** Copper: **Cat6A** (required for 10G at 80 m — Cat6 only supports 10G to 55 m). Fibre option: 10GBASE-SR (short reach, multimode, good for 80 m with OM3/OM4).

    **2.** **Direct Attach Cable (DAC)** — 100G QSFP28 DAC. No optics required at 3 m; lowest cost, lowest power, no glass.

    **3.** **Single-mode fibre.** 300 m exceeds the maximum for 10GBASE-SR on OM3 (300 m max, but at margin) or OM4 (400 m max). For reliable headroom, SMF with 10GBASE-LR (up to 10 km) is the correct choice.

    **4.** No — not compliant. Cat6 supports 10G only to 55 m under the standard. At 70 m, Cat6 is only certified for 1G. **Cat6A** should have been installed for 10G at that distance.

---

## Lab

### Lab: Cable Identification and Transceiver Inventory

**Tools needed:** Your own work environment (or a lab with real equipment)
**Estimated time:** 15 minutes

**Objective:** Identify the physical cabling and transceivers in use in a real network.

**Steps:**

1. Find a patch panel or switch in your lab or workplace. Look at the cable labels — what category is the copper cabling? Is it Cat5e, Cat6, Cat6A?

2. Look at the SFP/QSFP slots in a switch or router. Are any transceivers installed? Read the label on the transceiver — it will tell you the speed (1G/10G/25G/100G), the reach (SR/LR/ZR), and the manufacturer.

3. If you have a switch with a CLI, run the vendor's transceiver show command:

=== "Cisco IOS-XE"
    ```cisco-ios
    show interfaces transceiver
    ```
    Full configuration reference: [Cisco Transceiver Modules](https://www.cisco.com/c/en/us/products/interfaces-modules/transceiver-modules/index.html)

=== "Juniper Junos"
    ```junos
    show chassis pic fpc-slot 0 pic-slot 0
    show interfaces diagnostics optics ge-0/0/0
    ```
    Full configuration reference: [Juniper Transceivers](https://www.juniper.net/documentation/us/en/software/junos/interfaces-ethernet/topics/topic-map/transceivers.html)

=== "Arista EOS"
    ```arista-eos
    show interfaces transceiver
    ```
    Full configuration reference: [Arista Transceiver Guide](https://www.arista.com/en/support/product-documentation)

4. Note the DOM (Digital Optical Monitoring) values: Tx power, Rx power, temperature. A healthy link typically shows Rx power between −3 dBm and −20 dBm depending on the optic type. Very low Rx power (below −30 dBm) suggests a dirty connector or fibre fault.

**Stretch:** If you have a fibre tester or VFL (Visual Fault Locator), trace a fibre run and look for bends or connectors with high insertion loss.

---

## Summary & Key Takeaways

- **UTP copper** categories (Cat5e/6/6A) define maximum bandwidth and distance — Cat6A is required for 10G at full 100 m
- Copper Ethernet maxes out at ~100 m — beyond that, use a switch as a repeater or switch to fibre
- **Multimode fibre** (OM3/OM4/OM5): short-range, 850 nm, inside buildings and data centres
- **Single-mode fibre** (OS2): long-range, 1310/1550 nm, campus and WAN links
- **SFP/QSFP** are pluggable transceivers — the electrical side faces the switch; the optical side faces the fibre
- **DAC** (Direct Attach Cable): passive copper, sub-7 m, lowest cost for intra-rack and cross-row links
- Ethernet speed standards (IEEE 802.3) follow the naming: `[speed]BASE-[medium]`
- Verify transceiver compatibility with your equipment vendor before purchasing third-party optics

---

## Where to Next

- **Apply to switching:** [Switching Fundamentals](../switching/switching-fundamentals.md) (`SW-001`) — the device at the end of the cable
- **Physical media deep dive:** [Grey Optical — Uncoloured / Direct Fibre](../access-media/grey-optical.md) (`AM-006`) — deeper coverage of single-mode and wavelength planning
- **Coloured optics:** [CWDM & DWDM](../access-media/coloured-optical.md) (`AM-007`) — multiplexing multiple wavelengths on one fibre

---

## Standards & Certifications

**Relevant standards:**
- IEEE 802.3 — Ethernet (all physical layer specifications)
- TIA/EIA-568 — Commercial Building Telecommunications Cabling Standard
- ISO/IEC 11801 — Generic Cabling for Customer Premises
- ITU-T G.652 — Characteristics of single-mode optical fibre cable

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant section |
|---|---|---|
| CCNA 200-301 | Cisco | 1.3 — Physical interface and cabling |
| CompTIA Network+ | CompTIA | 1.3 — Cables and connectors |
| JNCIA-Junos JN0-103 | Juniper | Networking fundamentals |

---

## References

- IEEE 802.3-2022 — Ethernet Standard (all BASE-T, BASE-X physical specifications)
- TIA/EIA-568.2-D — Balanced Twisted-Pair Telecommunications Cabling
- ITU-T G.652 — Characteristics of a single-mode optical fibre and cable
- Odom, Wendell — *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2020 — Chapter 2
- Stallings, William — *Data and Computer Communications*, 10th ed., Pearson, 2013 — Chapter 4

---

## Attribution & Licensing

**Author:** @geekazoid80
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Claude used for initial draft structure and prose. Technical specifications verified against IEEE 802.3-2022, TIA-568, and Odom's CCNA Official Cert Guide.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| SW-001 | Switching Fundamentals | Prerequisite — switches terminate copper and fibre at Layer 1 | 2026-04-17 |
| AM-006 | Grey Optical | This module introduces single-mode fibre; AM-006 covers it in depth | 2026-04-17 |
| AM-007 | Coloured Optical (CWDM/DWDM) | This module introduces SFP form factors; AM-007 covers DWDM optics | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| NW-001 | The OSI Model | Prerequisite — cabling operates at Layer 1 | 2026-04-17 |
| NW-002 | Network Topologies | Prerequisite — topology determines cable layout | 2026-04-17 |
| SW-001 | Switching Fundamentals | "Where to Next" forward reference | 2026-04-17 |
| AM-006 | Grey Optical | "Where to Next" forward reference | 2026-04-17 |
| AM-007 | Coloured Optical | "Where to Next" forward reference | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Notes |
|---|---|---|
| Ethernet physical layer | IEEE 802.3 | All vendors must comply for interoperability |
| Copper cabling categories | TIA/EIA-568 / ISO 11801 | Cat5e, Cat6, Cat6A specifications |
| SMF characteristics | ITU-T G.652 | OS1/OS2 fibre |
| SFP electrical interface | SFF-8472, SFF-8636 | Multi-vendor standard; EEPROM vendor lock varies |

### Maintenance Notes

- When AM-006 (Grey Optical) is written, add a back-reference pointing here for the physical layer introduction.
- When SW-001 (Switching Fundamentals) is written, add a back-reference pointing here for physical interface context.
- SFP vendor compatibility notes may need updating as new platform releases change compatibility matrices.
<!-- XREF-END -->
