---
id: NW-REF-001
title: "Network Operating System Platform Reference"
description: "Factual reference for major network operating systems - what hardware they run on, where they are deployed, and links to official documentation portals."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: reference
estimated_time: 10
prerequisites: []
learning_path_tags:
  - DNE
  - CE
  - DCE
difficulty: beginner
tags:
  - platforms
  - nos
  - ios-xe
  - ios-xr
  - junos
  - sr-os
  - eos
  - vrp
  - routeros
  - reference
created: 2026-04-19
updated: 2026-04-19
---

# NW-REF-001 - Network Operating System Platform Reference

This page provides factual information about the major network operating systems referenced throughout this compendium. Use it to understand what each OS is, what it runs on, and where to find official documentation.

This is a reference page - not a tutorial. For configuration examples, see the relevant module's Vendor Implementations section.

---

## Cisco IOS-XE

**What it is:** The current mainline Cisco IOS for enterprise and service provider platforms. A modular operating system with a separation between the IOS process (control plane) and the underlying Linux-based infrastructure.

**Runs on:** Cisco Catalyst (enterprise switching), Cisco ISR and ASR 1000 series (enterprise/SP routing), Cisco CSR 1000v (virtual/cloud), Cisco ASR 9000 (partial - see IOS-XR).

**Common in:** Enterprise campus networks, enterprise WAN, small and mid-scale service provider edge.

**Official documentation:** [https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe/tsd-products-support-series-home.html](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe/tsd-products-support-series-home.html)

**Configuration reference index:** [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/master/](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/master/)

---

## Cisco IOS-XR

**What it is:** A separate, distributed operating system designed for carrier-grade scalability and high availability. Distinct codebase from IOS-XE. Supports in-service software upgrade (ISSU) and distributed processing across multiple line card CPUs.

**Runs on:** Cisco ASR 9000 (service provider edge and core), Cisco NCS 540/560/5500/5700 (carrier routing), Cisco XRv 9000 (virtual/lab).

**Common in:** Service provider backbone, large-scale PE/P routers, mobile backhaul, subsea cable landing stations.

**Official documentation:** [https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xr-software/tsd-products-support-series-home.html](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xr-software/tsd-products-support-series-home.html)

**Configuration guide library:** [https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/](https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5500/)

---

## Cisco NX-OS

**What it is:** Cisco's operating system for data centre switching. Designed for high-density leaf-spine topologies, VXLAN/EVPN overlays, and data centre interconnect.

**Runs on:** Cisco Nexus 9000 (spine/leaf), Nexus 7000 (core), Nexus 5000/2000 (access/FEX), Nexus Dashboard Fabric Controller (management), Cisco N9Kv (virtual).

**Common in:** Enterprise and cloud data centre networks, EVPN-VXLAN fabrics, storage networking.

**Official documentation:** [https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/tsd-products-support-series-home.html](https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/tsd-products-support-series-home.html)

---

## Juniper Junos

**What it is:** Juniper's unified network operating system. A single codebase runs across routing, switching, security, and SD-WAN platforms. Uses a modular architecture (Routing Engine + Packet Forwarding Engine separation). Configuration is hierarchical; `commit` applies changes atomically.

**Runs on:** Juniper MX series (service provider routing), EX series (enterprise switching), QFX series (data centre), SRX series (security/firewall), PTX series (carrier core/transport), vMX/vSRX/vQFX (virtual).

**Common in:** Service provider backbone and edge, enterprise WAN, data centre fabric, SP security gateways.

**Official documentation:** [https://www.juniper.net/documentation/](https://www.juniper.net/documentation/)

**Junos configuration reference:** [https://www.juniper.net/documentation/us/en/software/junos/](https://www.juniper.net/documentation/us/en/software/junos/)

---

## Nokia SR-OS (Service Router Operating System)

**What it is:** Nokia's operating system for service provider and carrier core routing. Formerly TiMetra/Alcatel-Lucent. Designed for multi-service edge, carrier Ethernet, MPLS, and segment routing. Configuration uses a hierarchical `configure` structure with `commit` semantics.

**Runs on:** Nokia 7750 SR (service provider edge, PE router), 7450 ESS (multi-service edge), 7210 SAS (access), 7950 XRS (core), vSR (virtual).

**Common in:** Tier-1 and Tier-2 carrier networks, MPLS VPN services, mobile core transport, subsea and long-haul SP networks.

**Official documentation:** [https://documentation.nokia.com/](https://documentation.nokia.com/)

**SR-OS release documentation:** [https://documentation.nokia.com/sr/](https://documentation.nokia.com/sr/)

---

## Arista EOS (Extensible Operating System)

**What it is:** Arista's Linux-based network operating system. Fully programmable - runs standard Linux tools and supports eAPI (JSON-RPC), NETCONF/RESTCONF, OpenConfig, and gNMI natively. All state stored in a central in-memory database (Sysdb); all daemons are restartable without traffic disruption.

**Runs on:** Arista 7000 series (data centre leaf/spine/core), 7300 series (core), CloudEOS (virtual/cloud), cEOS (containerised lab).

**Common in:** Data centre leaf-spine fabrics (EVPN-VXLAN), cloud provider networks, financial services, enterprises prioritising automation and programmability.

**Official documentation:** [https://www.arista.com/en/support/product-documentation](https://www.arista.com/en/support/product-documentation)

**EOS configuration manual:** [https://www.arista.com/en/um-eos/eos-table-of-contents](https://www.arista.com/en/um-eos/eos-table-of-contents)

---

## Huawei VRP (Versatile Routing Platform)

**What it is:** Huawei's network operating system for routing and switching. Broadly deployed in Asia-Pacific and European carrier markets. VRP is a modular platform supporting routing, MPLS, carrier Ethernet, and data centre features. CLI style is similar to Cisco IOS with some differences (e.g., `display` instead of `show`, `undo` to negate commands).

**Runs on:** Huawei NE series (carrier routing - NE40E, NE9000), CE series (data centre switching), AR series (enterprise routing), S series (enterprise switching).

**Common in:** Tier-1 and Tier-2 carriers (especially in APAC, Middle East, Africa, Europe), enterprise networks in those regions.

**Official documentation:** [https://support.huawei.com/enterprise/en/](https://support.huawei.com/enterprise/en/)

**Product documentation portal:** [https://support.huawei.com/enterprise/en/doc/](https://support.huawei.com/enterprise/en/doc/)

---

## MikroTik RouterOS

**What it is:** MikroTik's proprietary operating system for RouterBOARD hardware. A full-featured routing and switching OS supporting BGP, OSPF, MPLS, VPN, firewall, QoS, and more. Managed via Winbox (GUI), WebFig, SSH CLI (`/ip route print` style hierarchical commands), or API. RouterOS v7 introduced major improvements including EVPN, OpenFlow, and enhanced BGP.

**Runs on:** MikroTik RouterBOARD (x86, ARM, MIPS hardware), CHR (Cloud Hosted Router - virtualised, runs on KVM/VMware/Hyper-V/cloud).

**Common in:** ISPs (particularly in developing markets), wireless ISPs (WISPs), enterprise networks (SMB and mid-market), homelab and network engineering labs worldwide.

**Official documentation:** [https://help.mikrotik.com/docs/](https://help.mikrotik.com/docs/)

**RouterOS command reference:** [https://help.mikrotik.com/docs/display/ROS/RouterOS](https://help.mikrotik.com/docs/display/ROS/RouterOS)

---

## Finding the Right Documentation

When working with any platform, the most reliable documentation source is always the **official vendor portal** linked above. For specific features:

1. Navigate to the platform's documentation portal.
2. Select the correct OS version (commands and features vary significantly across releases).
3. Use the feature-specific configuration guide (e.g., "MPLS Configuration Guide", "BGP Configuration Guide").

Each module in this compendium links directly to the relevant vendor documentation page for the specific feature being taught - use those links rather than searching from the portal root.

---

## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
