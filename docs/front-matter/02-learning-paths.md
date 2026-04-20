# Learning Paths

A learning path is a curated sequence of modules designed to build skills progressively toward a specific engineering role. You can follow a path from start to finish as a structured curriculum, or use it as a checklist to identify gaps in your existing knowledge.

## Available Paths

| Path ID | Title | Starting point |
|---|---|---|
| DNE | Data Network Engineer | No prerequisites |
| CE | Carrier Engineer | Stage 1-3 of DNE, then carrier-transport modules |
| DCE | Data Centre Engineer | Stage 1-3 of DNE, then data centre modules |

Full path details are in the `learning-paths/` directory. A summary of the two main paths follows.

---

## Data Network Engineer (DNE)

Takes you from network fundamentals through to professional-level enterprise and carrier data networking. Maps closely to the Cisco CCNA to CCNP Enterprise certification progression.

**Assumed background:** Basic familiarity with computers and the concept that networks connect them. No prior networking knowledge required.

**Target outcome:** Junior-to-mid network engineer capable of designing, configuring, and troubleshooting enterprise and ISP networks.

| Stage | Focus | Key module IDs |
|---|---|---|
| 1 - Foundation | OSI model, IP addressing, physical layer | NW-001, NW-002, NW-003, IP-001, IP-002 |
| 2 - Switching | VLANs, STP, EtherChannel | SW-001 through SW-005 |
| 3 - Routing | Static routes, OSPF, BGP, IPv6 | RT-001 through RT-003, RT-004, RT-007, IP-003 |
| 4 - Services and security | DNS, DHCP, NAT, ACLs, firewalls | SV-001 through SV-005, SEC-001, SEC-002 |
| 5 - Professional routing | OSPF advanced, BGP advanced, MPLS | RT-005, RT-006, RT-007, RT-008 |
| 6 - Quality of service | QoS classification, queuing, policing | QOS-001 through QOS-004 |
| 7 - Security (professional) | VPN, IPsec, AAA, PKI, segmentation | SEC-003 through SEC-006 |
| 8 - Automation | Python, REST APIs, NETCONF, Ansible | AUTO-001 through AUTO-004 |

**Recommended starting point:** Begin at NW-001 (The OSI Model) regardless of experience level. The module is short and establishes the vocabulary used throughout the rest of the compendium.

---

## Carrier Engineer (CE)

Builds on the DNE foundation and covers the transport technologies that underpin large-scale service provider and carrier networks: MPLS, segment routing, EVPN, OTN, and MEF standards.

**Assumed background:** Stages 1-3 of the DNE path, or equivalent practical experience with IP routing and BGP.

**Target outcome:** Engineer capable of designing and operating carrier transport networks, understanding service definitions, and working with multi-vendor carrier equipment.

| Stage | Focus | Key module IDs |
|---|---|---|
| CE-1 | MPLS fundamentals and applications | CT-001, CT-002, CT-003 |
| CE-2 | Traffic engineering and segment routing | CT-004, CT-005 |
| CE-3 | EVPN and VXLAN | CT-006, CT-007 |
| CE-4 | Optical transport | CT-010, CT-011 |
| CE-5 | MEF standards and carrier Ethernet services | CT-008, CT-009 |

---

## Module Tags

Each module's frontmatter contains a `learning_path_tags` list showing which paths include that module. When reading the compendium as a reference rather than following a path, this tells you which role contexts a given topic is most relevant to.

Example: a module tagged `[DNE, CE]` is covered in both the data network engineer and carrier engineer paths. A module tagged `[CE]` only appears in the carrier track and assumes familiarity with the DNE foundation modules.
