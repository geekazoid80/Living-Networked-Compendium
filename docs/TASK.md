# Task Tracker

Cross-session progress tracker for the Living Networked Compendium.

**How to use:**
- Update this file at the start and end of every Claude session
- One task per row. Move status as work progresses
- Add follow-ups discovered during work immediately — don't lose them
- `blocked` tasks need human input before proceeding

**Statuses:** `pending` | `in-progress` | `done` | `blocked`

---

## Current Session Focus

**Current area:** Architecture expansion — multi-vendor scope, new domains, private research folder

---

## Architecture & Tooling Tasks

| # | Task | Area | Status | Notes |
|---|---|---|---|---|
| 1 | Create directory structure | Architecture | done | |
| 2 | Write `docs/INSTRUCTION.md` | Architecture | done | Updated with multi-vendor guidelines, new prefix table, private workflow |
| 3 | Write `docs/TASK.md` (this file) | Architecture | done | |
| 4 | Write `docs/MODULE_TEMPLATE.md` | Architecture | done | |
| 5 | Update `README.md` | Architecture | done | Needs refresh for expanded scope |
| 6 | Create `private/` folder + `private/README.md` | Architecture | done | Gitignored; holds uploads, parsed, research, notes |
| 7 | Create `.gitignore` | Architecture | done | |
| 8 | Create build scripts | Tooling | done | build-web, build-pdf, build-pptx, generate-changelog |
| 9 | Create `tools/templates/` | Tooling | done | marp-theme.css |
| 10 | Create `mkdocs.yml` | Tooling | done | Needs nav update for new domains |
| 11 | Create `.github/workflows/build-deploy.yml` | CI/CD | done | |
| 12 | Create `learning-paths/` files | Architecture | done | data-network-engineer, rf-satellite-engineer, broadcast-engineer |
| 13 | Create applied path stubs | Architecture | done | DNE, RSE, BRD, RCE, VTE, RME, SNE, CE, DCE, _new-path-template |
| 14 | Add new fundamentals domains | Architecture | done | access-media, carrier-transport, datacentre, protocols, functions |
| 15 | Add CE and DCE applied stubs | Architecture | done | carrier-engineer/overview.md, datacentre-engineer/overview.md |
| 16 | Create learning-path files for all roles | Architecture | done | CE and DCE files added; all 9 paths now have learning-path files |
| 17 | Update `mkdocs.yml` nav for new paths and domains | Tooling | done | Added RF-Coax, Voice, RF Mobile, Storage, Carrier, DC paths; Professional Standards |
| 18 | Create professional-standards domain stub | Architecture | done | modules/fundamentals/professional-standards/overview.md; PS-000 |
| 19 | Create `preprocess-module.py` | Tooling | done | Three-bucket transformation for pdf/pptx output targets |
| 20 | Integrate preprocessor into `build-pdf.sh` and `build-pptx.sh` | Tooling | done | Both scripts now call preprocess-module.py before Pandoc/Marp |
| 21 | Retrofit seed modules (NW-001, IP-001, IP-002) to new template | Content | pending | Add analogy section, ??? supplementary blocks, XREF markers |
| 22 | Update `README.md` for expanded scope | Architecture | pending | Multi-vendor, new paths, three-bucket model |
| 23 | Resolve `services/` domain overlap with `protocols/` + `functions/` | Architecture | blocked | See follow-up D |

---

## Seed Modules (Session 1 — Done)

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| S1 | NW-001 | The OSI Model | done | Needs human review → set `human_reviewed: true` |
| S2 | IP-001 | IP Addressing Fundamentals | done | Needs human review |
| S3 | IP-002 | IP Subnetting & VLSM | done | Needs human review |

---

## Content Backlog — Fundamentals/Networking

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C01 | NW-002 | Network Topologies | pending | Star, mesh, bus, ring, hybrid |
| C02 | NW-003 | Ethernet Standards & Cabling | pending | Cat5e/6/6a/7, SFP, DAC, fibre types |

---

## Content Backlog — Fundamentals/Access Media (NEW)

Covers physical medium evolution: how we connect devices, from the beginning to now.

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C03 | AM-001 | Serial & Rollover Cables | pending | DB-9/25, RJ-45 console, management access history |
| C04 | AM-002 | Token Ring & FDDI | pending | Historical; why they lost to Ethernet |
| C05 | AM-003 | Ethernet Evolution | pending | 10BASE-T → 100M → 1G → 10G → 25/40/100/400G |
| C06 | AM-004 | DSL Technologies | pending | ADSL, ADSL2+, VDSL, VDSL2; copper limits |
| C07 | AM-005 | Coaxial Cable & Cable Broadband | pending | DOCSIS 1.x/2.0/3.0/3.1/4.0; HFC networks |
| C08 | AM-006 | Grey Optical (Uncoloured / Direct) | pending | Single-mode, multimode; SFP/QSFP types; reach/wavelength |
| C09 | AM-007 | Coloured Optical — CWDM & DWDM | pending | ITU grid, channel spacing, amplification (EDFA), ROADMs |
| C10 | AM-008 | RF over Optical (Analogue/Digital) | pending | HFC, RFoG, Remote PHY |
| C11 | AM-009 | Wi-Fi (802.11 Evolution) | pending | 802.11a/b/g/n/ac/ax/be; bands, channels, MU-MIMO, OFDMA |
| C12 | AM-010 | Mobile Networks (2G→5G) | pending | GSM, UMTS, LTE, 5G NR; backhaul, roaming, network slicing |
| C13 | AM-011 | VSAT & Satellite Broadband Access | pending | Link to RF modules; DVB-RCS/RCS2, ACM, throughput |

---

## Content Backlog — Fundamentals/IP

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C14 | IP-003 | IPv6 Addressing | pending | Format, types, EUI-64, NDP, DHCPv6 |
| C15 | IP-004 | IPv4 Exhaustion & Transition | pending | CGNAT, 6rd, DS-Lite, NAT64 |

---

## Content Backlog — Fundamentals/Routing

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C16 | RT-001 | Routing Fundamentals | pending | Routing table, longest-prefix match, AD |
| C17 | RT-002 | Static Routing | pending | Default route, floating static, next-hop vs exit-if |
| C18 | RT-003 | RIP & Distance-Vector Concepts | pending | Brief; mainly historical context |
| C19 | RT-004 | OSPF Fundamentals | pending | LSA types, DR/BDR, areas, cost; multi-vendor |
| C20 | RT-005 | OSPF Advanced | pending | Multi-area, redistribution, filtering, virtual links |
| C21 | RT-006 | IS-IS Fundamentals | pending | Used heavily in SP/DC; multi-vendor |
| C22 | RT-007 | BGP Fundamentals | pending | EBGP/IBGP, attributes, path selection; multi-vendor |
| C23 | RT-008 | BGP Advanced | pending | Communities, policies, route-maps, filtering |
| C24 | RT-009 | Route Redistribution & Policy | pending | |
| C25 | RT-010 | EIGRP | pending | Cisco proprietary (now RFC 7868); seeking-standardisation callout |
| C26 | RT-011 | Multicast Routing | pending | IGMP, PIM-SM, PIM-DM, SSM, RP |

---

## Content Backlog — Fundamentals/Switching

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C27 | SW-001 | Switching Fundamentals | pending | MAC learning, forwarding, flooding; multi-vendor |
| C28 | SW-002 | VLANs & 802.1Q Trunking | pending | Access/trunk ports, native VLAN |
| C29 | SW-003 | Spanning Tree Protocol (STP/RSTP/MSTP) | pending | 802.1D, 802.1w, 802.1s; per-vendor flavours |
| C30 | SW-004 | EtherChannel / LAG (LACP) | pending | 802.3ad LACP vs Cisco PAgP (proprietary) |
| C31 | SW-005 | Port Security & DAI | pending | MAC limiting, DHCP snooping, Dynamic ARP Inspection |
| C32 | SW-006 | Layer 3 Switching & SVIs | pending | |

---

## Content Backlog — Fundamentals/Carrier-Transport (NEW)

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C33 | CT-001 | MPLS Fundamentals | pending | Labels, FEC, LDP, RSVP-TE; standard + multi-vendor |
| C34 | CT-002 | MPLS VPNs (L3VPN / VRF) | pending | RFC 4364; PE-CE routing |
| C35 | CT-003 | MPLS L2VPN (VPLS, Pseudowire) | pending | RFC 4761, 4762 |
| C36 | CT-004 | Segment Routing (SR-MPLS) | pending | IETF standard; Cisco, Nokia, Juniper implementations |
| C37 | CT-005 | SRv6 | pending | SR over IPv6 data plane |
| C38 | CT-006 | EVPN Fundamentals | pending | RFC 7432; MAC/IP advertisement; multi-vendor |
| C39 | CT-007 | EVPN-VXLAN | pending | Overlay + underlay; DC and carrier use |
| C40 | CT-008 | Metro Ethernet Forum (MEF) Standards | pending | E-Line, E-LAN, E-Tree, E-Access; MEF 3.0 |
| C41 | CT-009 | Carrier Ethernet Services | pending | CE 2.0 attributes, CoS, bandwidth profiles |
| C42 | CT-010 | SDH/SONET & OTN Basics | pending | Legacy transport; still present in carrier core |
| C43 | CT-011 | Optical Transport Network (OTN) | pending | G.709; ODU multiplexing |
| C44 | CT-012 | Traffic Engineering (RSVP-TE & SR-TE) | pending | Tunnels, path computation, fast-reroute |

---

## Content Backlog — Fundamentals/Data Centre (NEW)

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C45 | DC-001 | Data Centre Network Design | pending | Spine-leaf vs 3-tier; oversubscription |
| C46 | DC-002 | VXLAN Fundamentals | pending | RFC 7348; VTEP, VNI, BUM traffic |
| C47 | DC-003 | BGP in the Data Centre | pending | BGP as DC underlay; RFC 7938 |
| C48 | DC-004 | EVPN in the Data Centre | pending | MAC mobility, ARP suppression, multihoming |
| C49 | DC-005 | Data Centre Interconnect (DCI) | pending | OTV, EVPN DCI, dark fibre |
| C50 | DC-006 | Storage Networking Basics | pending | iSCSI, FCoE, NVMe-oF; brief overview |

---

## Content Backlog — Fundamentals/Protocols (NEW)

Standard and widely-used protocols — one module per protocol.

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C51 | PROTO-001 | DNS — Domain Name System | pending | Hierarchy, resolution, record types (A, AAAA, MX, CNAME, PTR, NS, SOA) |
| C52 | PROTO-002 | ARP & GARP | pending | IPv4 ARP; Gratuitous ARP; proxy ARP; DAI mitigation |
| C53 | PROTO-003 | NTP & PTP | pending | NTP strata, NTPv4; PTP/IEEE 1588 for precision timing |
| C54 | PROTO-004 | Syslog | pending | RFC 5424; severity levels; centralised logging |
| C55 | PROTO-005 | SNMP | pending | v1/v2c/v3; MIB, OID, traps vs polling |
| C56 | PROTO-006 | NetFlow & IPFIX | pending | RFC 7011; flow records; collector/exporter; Cisco vs standard |
| C57 | PROTO-007 | Streaming Telemetry | pending | gRPC/gNMI; OpenConfig; vs SNMP/NetFlow |
| C58 | PROTO-008 | NETCONF & YANG | pending | RFC 6241; data models; vs CLI |
| C59 | PROTO-009 | RESTCONF | pending | RFC 8040; HTTP-based alternative to NETCONF |
| C60 | PROTO-010 | DHCP Deep Dive | pending | DORA, options, relay, DHCPv6 |
| C61 | PROTO-011 | BFD (Bidirectional Forwarding Detection) | pending | Sub-second failure detection; used with routing protocols |
| C62 | PROTO-012 | LLDP & CDP | pending | LLDP (standard 802.1AB) vs CDP (Cisco proprietary); neighbour discovery |

---

## Content Backlog — Fundamentals/Functions (NEW)

Network functions — conceptual and implementation, multi-vendor.

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C63 | FN-001 | Switching — How It Works | pending | CAM/TCAM; hardware forwarding; cut-through vs store-forward |
| C64 | FN-002 | Routing — How It Works | pending | Control plane vs data plane; RIB, FIB, CEF |
| C65 | FN-003 | NAT & PAT | pending | Static, dynamic, overload (PAT); CGNAT; RFC 3022 |
| C66 | FN-004 | Stateless ACLs | pending | Packet filtering; standard vs extended; match criteria |
| C67 | FN-005 | Stateful Firewall & ACLs | pending | Connection tracking; reflexive ACLs; zone-based FW |
| C68 | FN-006 | IDS & IPS | pending | Signature vs anomaly; inline vs passive; Snort/Suricata |
| C69 | FN-007 | Deep Packet Inspection (DPI) | pending | Layer 7 inspection; use cases; vendor tools |
| C70 | FN-008 | Application Layer Gateway (ALG) | pending | Why NAT breaks protocols (FTP, SIP, H.323); ALG fix |

---

## Content Backlog — Fundamentals/Services

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C71 | SV-001 | DNS | pending | Covered by PROTO-001; link or merge |
| C72 | SV-002 | DHCP | pending | Covered by PROTO-010; link or merge |
| C73 | SV-003 | NAT & PAT | pending | Covered by FN-003; link or merge |
| C74 | SV-004 | NTP | pending | Covered by PROTO-003; link or merge |
| C75 | SV-005 | SNMP & Syslog | pending | Covered by PROTO-004/005; link or merge |

> **Note:** There is overlap between `services/` and `protocols/` + `functions/`. Decision needed: keep `services/` as an alias/redirect layer, or merge the content. Flag for human decision.

---

## Content Backlog — Fundamentals/Security

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C76 | SEC-001 | ACLs | pending | Link to FN-004/005 for function; cover config multi-vendor |
| C77 | SEC-002 | Firewall Concepts | pending | |
| C78 | SEC-003 | VPN & IPSec | pending | IKEv1/v2, ESP/AH, tunnel vs transport |
| C79 | SEC-004 | AAA — TACACS+ & RADIUS | pending | TACACS+ (Cisco-originated; now standard); RADIUS RFC 2865 |
| C80 | SEC-005 | Encryption Standards & PKI | pending | AES, RSA, certificates, CA; brief |
| C81 | SEC-006 | Network Segmentation & DMZ | pending | |

---

## Content Backlog — Fundamentals/QoS

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C82 | QOS-001 | QoS Fundamentals | pending | Delay, jitter, loss, bandwidth |
| C83 | QOS-002 | Classification & Marking | pending | DSCP (RFC 2474), 802.1p CoS; multi-vendor |
| C84 | QOS-003 | Queuing Mechanisms | pending | FIFO, PQ, WFQ, CBWFQ, LLQ |
| C85 | QOS-004 | Traffic Policing & Shaping | pending | Token bucket; vendor implementations |
| C86 | QOS-005 | QoS in MPLS Networks | pending | EXP/TC bits; pipe vs uniform mode |

---

## Content Backlog — Fundamentals/Automation

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C87 | AUTO-001 | Python for Network Engineers | pending | Netmiko, Paramiko, NAPALM |
| C88 | AUTO-002 | REST APIs | pending | JSON/XML; HTTP methods; Postman |
| C89 | AUTO-003 | NETCONF & YANG | pending | Link to PROTO-008 |
| C90 | AUTO-004 | Ansible for Networks | pending | Playbooks, roles, vendor modules |
| C91 | AUTO-005 | Terraform for Networks | pending | Infrastructure as code |

---

## Content Backlog — Fundamentals/RF

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C92 | RF-001 | RF Fundamentals | pending | |
| C93 | RF-002 | Modulation Techniques | pending | |
| C94 | RF-003 | Antenna Theory | pending | |
| C95 | RF-004 | Link Budget Calculations | pending | |

---

## Content Backlog — Fundamentals/Professional Standards (NEW)

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| C93 | PS-001 | ITIL 4 for Network Engineers | needed | Service management; incident/change/problem processes |
| C94 | PS-002 | NIST SP 800-53 — Security Controls | needed | Control families; relevance to network config |
| C95 | PS-003 | BCP38 / BCP84 — Anti-Spoofing | needed | Ingress filtering; why it matters for DDoS |
| C96 | PS-004 | TIA-942 — Data Centre Tiers | needed | Tier I–IV; redundancy levels; common misconceptions |
| C97 | PS-005 | ISO/IEC 27001 for Engineers | needed | ISMS; risk treatment; network security controls |
| C98 | PS-006 | MEF 3.0 — LSO and Carrier Ethernet | needed | Service orchestration; MEF service attributes |
| C99 | PS-007 | IEEE 802 Standards Overview | needed | 802.1, 802.3, 802.11, 802.1Q, 802.1X landscape |
| C100 | PS-008 | RFC Track Explained | needed | Standards-track vs BCP vs Informational vs Experimental |

---

## Content Backlog — Applied: RF-Coax / Cable Engineer

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| RC1 | RCE-001 | DOCSIS 3.0 — Channel Bonding | needed | |
| RC2 | RCE-002 | DOCSIS 3.1 — OFDM and OFDMA | needed | |
| RC3 | RCE-003 | DOCSIS 4.0 — Full Duplex and Extended Spectrum | needed | |
| RC4 | RCE-004 | CMTS Architecture and Configuration | needed | |
| RC5 | RCE-005 | Subscriber Provisioning (DHCP, TFTP, config files) | needed | |
| RC6 | RCE-006 | QoS in DOCSIS (Service Flows, Classifiers) | needed | |
| RC7 | RCE-007 | Remote PHY Architecture (RPD, CCAP) | needed | |
| RC8 | RCE-008 | Fibre-Deep and Node + 0 Design | needed | |
| RC9 | RCE-009 | Signal Level Management and Upstream Noise | needed | |
| RC10 | RCE-010 | Node Utilisation and Splitting Decisions | needed | |

---

## Content Backlog — Applied: Voice / Telephony Engineer

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| VT1 | VTE-001 | SIP — Session Initiation Protocol (RFC 3261) | needed | |
| VT2 | VTE-002 | RTP/RTCP — Real-time Transport Protocol | needed | |
| VT3 | VTE-003 | Codecs — G.711, G.729, Opus, iLBC | needed | |
| VT4 | VTE-004 | DTMF Handling (RFC 2833 / RFC 4733) | needed | |
| VT5 | VTE-005 | H.323 Overview | needed | Legacy, still deployed |
| VT6 | VTE-006 | PSTN Architecture — Switching Hierarchy | needed | |
| VT7 | VTE-007 | ISDN — BRI and PRI | needed | |
| VT8 | VTE-008 | SS7 — Signalling System 7 Architecture | needed | |
| VT9 | VTE-009 | SIGTRAN — SS7 over IP (RFC 3057) | needed | |
| VT10 | VTE-010 | SIP PBX Design and Architecture | needed | |
| VT11 | VTE-011 | Session Border Controllers (SBCs) | needed | |
| VT12 | VTE-012 | NAT Traversal for VoIP (STUN, TURN, ICE) | needed | |
| VT13 | VTE-013 | SIP Trunking — Enterprise to Carrier | needed | |
| VT14 | VTE-014 | MOS, Jitter, and Call Quality Measurement | needed | |
| VT15 | VTE-015 | Wireshark for VoIP (SIP and RTP capture) | needed | |
| VT16 | VTE-016 | VoIP Security — Toll Fraud, SIP Brute Force | needed | |
| VT17 | VTE-017 | WebRTC Fundamentals | needed | |
| VT18 | VTE-018 | Microsoft Teams Direct Routing | needed | |
| VT19 | VTE-019 | Contact Centre Telephony Architecture | needed | |
| VT20 | VTE-020 | E911 and Emergency Call Routing | needed | |

---

## Content Backlog — Applied: RF Mobile / Cellular Engineer

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| RM1 | RME-001 | LTE RAN Architecture (eNB, S1/X2 interfaces) | needed | |
| RM2 | RME-002 | 5G NR Architecture (gNB, CU/DU split, F1 interface) | needed | |
| RM3 | RME-003 | Cell Planning — Coverage, Capacity, Interference | needed | |
| RM4 | RME-004 | Massive MIMO and Beamforming | needed | |
| RM5 | RME-005 | SON — Self-Organising Networks | needed | |
| RM6 | RME-006 | Microwave Point-to-Point Backhaul | needed | |
| RM7 | RME-007 | 4G EPC Architecture (MME, SGW, PGW, HSS, PCRF) | needed | |
| RM8 | RME-008 | GTP — GPRS Tunnelling Protocol | needed | |
| RM9 | RME-009 | 5G Core SBA Architecture (AMF, SMF, UPF, UDM, PCF) | needed | |
| RM10 | RME-010 | DIAMETER Protocol (4G charging, AAA) | needed | |
| RM11 | RME-011 | Roaming Architecture (GRX, IPX, SS7/DIAMETER) | needed | |
| RM12 | RME-012 | RF KPIs (RSRP, RSRQ, SINR, CQI, MCS) | needed | |
| RM13 | RME-013 | RAN Optimisation Techniques | needed | |
| RM14 | RME-014 | Drive Testing and Post-Processing | needed | |
| RM15 | RME-015 | Private 5G — Enterprise Campus Networks | needed | |
| RM16 | RME-016 | Open RAN (O-RAN Alliance) | needed | |
| RM17 | RME-017 | Network Slicing for Vertical Industries | needed | |
| RM18 | RME-018 | Multi-access Edge Computing (MEC) | needed | |

---

## Content Backlog — Applied: Storage Network Engineer

| # | Module ID | Title | Status | Notes |
|---|---|---|---|---|
| SN1 | SNE-001 | Block vs File vs Object Storage | needed | |
| SN2 | SNE-002 | RAID Levels and Storage Resiliency | needed | |
| SN3 | SNE-003 | LUN Design and Multipathing | needed | |
| SN4 | SNE-004 | Fibre Channel Protocol (FC frames, port types) | needed | |
| SN5 | SNE-005 | FC Fabric — FLOGI, PLOGI, FDISC, Zoning | needed | |
| SN6 | SNE-006 | FC Switch Topologies and ISL Design | needed | |
| SN7 | SNE-007 | FC Switch Platforms (Cisco MDS, Brocade/Broadcom) | needed | |
| SN8 | SNE-008 | iSCSI — IP-based Block Storage (RFC 7143) | needed | |
| SN9 | SNE-009 | DCB / Priority Flow Control (IEEE 802.1Qbb) | needed | |
| SN10 | SNE-010 | FCoE — Fibre Channel over Ethernet | needed | |
| SN11 | SNE-011 | NAS — NFS (RFC 7530) and SMB/CIFS | needed | |
| SN12 | SNE-012 | NVMe-oF Concepts and Architectures | needed | |
| SN13 | SNE-013 | RDMA — RoCE and iWARP | needed | |
| SN14 | SNE-014 | NVMe/TCP (RFC 8041) | needed | |
| SN15 | SNE-015 | Synchronous vs Asynchronous Replication | needed | |
| SN16 | SNE-016 | RPO, RTO, and Storage SLAs | needed | |
| SN17 | SNE-017 | WAN Optimisation for Storage Traffic | needed | |

---

## Applied Paths — Status

| # | Path | Status | Notes |
|---|---|---|---|
| A1 | Carrier/SP Network Engineer (`CE`) | done | Overview + learning-path file created |
| A2 | Data Centre Network Engineer (`DCE`) | done | Overview + learning-path file created |
| A3 | RF-Coax / Cable Engineer (`RCE`) | done | Overview + learning-path file created; module content needed |
| A4 | Voice / Telephony Engineer (`VTE`) | done | Overview + learning-path file created; module content needed |
| A5 | RF Mobile / Cellular Engineer (`RME`) | done | Overview + learning-path file created; module content needed |
| A6 | Storage Network Engineer (`SNE`) | done | Overview + learning-path file created; module content needed |

---

## Decisions & Context Log

| Date | Decision | Reason |
|---|---|---|
| 2026-04-15 | Use `AI_GUARDRAILS.md` (plural) as canonical filename | GitHub Actions workflows do literal filesystem check |
| 2026-04-15 | MkDocs Material theme for web output | Best-in-class for technical docs |
| 2026-04-15 | Pandoc for PDF, Marp for PPTX | Pandoc most powerful; Marp minimal friction |
| 2026-04-15 | Handout version format `vNNN-YYYY-MM-DD` | Running number + date |
| 2026-04-15 | Module ID prefix scheme | Stable cross-references that survive file renames |
| 2026-04-15 | Singapore poly/university IS/CS/EE as baseline | Target audience |
| 2026-04-15 | Multi-vendor scope: Cisco, Juniper, Nokia, Arista, Huawei, ZTE, MikroTik | Fair representation; carrier/DC environments use all of these |
| 2026-04-15 | Standard / Proprietary-seeking-standard / Proprietary-specific distinction | Readers must know what they can rely on in mixed environments |
| 2026-04-15 | Carrier-transport domain added (CT) | MPLS, SR, EVPN, MEF — essential for telco/SP roles |
| 2026-04-15 | Data centre domain added (DC) | Spine-leaf, VXLAN, EVPN-DC — distinct enough to warrant own domain |
| 2026-04-15 | Access-media domain added (AM) | Physical layer evolution from serial to 400G to wireless |
| 2026-04-15 | Protocols domain added (PROTO) | One module per standard protocol for atomic reference |
| 2026-04-15 | Functions domain added (FN) | Switching, routing, NAT, ACL, IDS/IPS, DPI, ALG as distinct concepts |
| 2026-04-15 | `private/` folder created and gitignored | Local research, uploads, parsed docs — never public |
| 2026-04-15 | Three-bucket content model adopted | Critical (all outputs), Supplementary (collapsed/notes/speaker), XREF (markdown-only) |
| 2026-04-15 | Analogy-first mandatory structure | Every module opens with layman analogy + mapping table before any technical content |
| 2026-04-15 | `preprocess-module.py` handles output-specific transformation | Strips/transforms buckets for pdf and pptx targets; web passes through unchanged |
| 2026-04-15 | Certs as benchmarks only — not curriculum anchors | Curriculum follows standards and skills, not exam objectives |
| 2026-04-15 | Target audience is global, not Singapore-specific | Singapore IS/CS/EE reference is illustrative of typical reader background only |
| 2026-04-15 | Professional Standards domain added (PS) | ITIL, NIST, BCP38, TIA-942, ISO 27001, MEF, IEEE — what engineers are audited against |
| 2026-04-15 | Multilingual support via file naming convention | `module.md` = EN default; `module.zh-CN.md`, `module.ms.md`, `module.ta.md` for translations |

---

## Follow-ups Requiring Human Input

| # | Question / Decision Needed | Raised |
|---|---|---|
| A | What is the target custom domain for GitHub Pages? (update CNAME and mkdocs.yml) | 2026-04-15 |
| B | Should handout PDFs be committed to the repo or only published as GitHub Release artifacts? | 2026-04-15 |
| C | Who is the initial maintainer handle to put in module frontmatter? | 2026-04-15 |
| D | Should `services/` domain be kept as a distinct folder or merged into `protocols/` + `functions/`? | 2026-04-15 |
| E | Are there existing training materials or lesson plans to upload to `private/uploads/` as source material? | 2026-04-15 |
| F | Should ZTE vendor CLI examples be included (limited English documentation available)? | 2026-04-15 |
| G | Priority order for content backlog — which domains/modules to tackle first? | 2026-04-15 |
