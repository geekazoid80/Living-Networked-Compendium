---
id: SW-005
title: "Port Security & DAI (Dynamic ARP Inspection)"
description: "How to restrict which devices can connect to switch ports and how to prevent ARP spoofing attacks using DHCP Snooping and Dynamic ARP Inspection."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - SW-001
  - SW-002
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - switching
  - port-security
  - dai
  - dhcp-snooping
  - arp-inspection
  - layer2-security
created: 2026-04-19
updated: 2026-04-19
---

# SW-005 — Port Security & DAI (Dynamic ARP Inspection)

## The Problem

An employee plugs an unmanaged switch into their desk port. Now twenty devices share that one port — MAC table slots consumed, more broadcast traffic, potential policy bypass. Meanwhile, an attacker on another port crafts ARP replies claiming their MAC maps to the gateway IP, intercepting all traffic destined for the router. Both attacks work at Layer 2, below where firewalls and routers can see them.

### Step 1: Limit who can connect to a port

The access switch knows which physical port is designated for a single workstation. You configure that port to accept frames from at most one MAC address — if a second MAC appears, the port shuts down. You have just invented **port security** — limiting the number (and optionally the identity) of MAC addresses on an access port.

### Step 2: Prevent ARP spoofing

ARP is stateless: any device can send an unsolicited ARP reply claiming any MAC-to-IP mapping. The switch has no way to know if `192.168.1.1 → aa:bb:cc:dd:ee:ff` is legitimate. But the switch does know which IP addresses were legitimately assigned by the DHCP server — it watched those exchanges. You record those DHCP assignments in a **DHCP Snooping binding table**: port → MAC → IP → lease time. Then you validate every ARP reply against this table. A gratuitous ARP claiming an IP not in the binding table is dropped. This is **Dynamic ARP Inspection (DAI)**.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Limit MACs per port; shutdown on violation | Port Security |
| Recording legitimate DHCP assignments | DHCP Snooping |
| Validating ARP against DHCP bindings | Dynamic ARP Inspection (DAI) |
| Port allowed to receive DHCP server replies | Trusted port (DHCP Snooping) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain the threats that port security and DAI defend against.
2. Configure port security with static, dynamic, and sticky MAC learning.
3. Describe the three port security violation modes (protect, restrict, shutdown).
4. Explain how DHCP Snooping builds its binding table.
5. Describe how DAI uses the DHCP Snooping table to validate ARP.
6. Configure DHCP Snooping and DAI on at least two vendor platforms.

---

## Prerequisites

- SW-001 — Switching Fundamentals (MAC table, flooding)
- SW-002 — VLANs & 802.1Q (VLAN assignment for port-level policies)

---

## Core Content

### Port Security

**Port security** controls which MAC addresses are authorised to send frames on an access port, and what happens when an unauthorised MAC is detected.

#### MAC address modes

| Mode | Behaviour |
|---|---|
| **Static** | Manually configure authorised MACs in the running config |
| **Dynamic** | First MAC seen is automatically allowed; lost on reload unless saved |
| **Sticky** | First MAC(s) seen are automatically learned and written to the running config (survive reload when saved) |

Sticky MAC is the most common — the switch learns the legitimate device's MAC on first connection and remembers it through reboots without requiring manual configuration.

#### Violation modes

When an unauthorised MAC is detected:

| Mode | Action | Counter incremented? | Port stays up? |
|---|---|---|---|
| **Protect** | Drop offending frames silently | No | Yes |
| **Restrict** | Drop frames; log; increment violation counter | Yes | Yes |
| **Shutdown** | Err-disable the port; log; SNMP trap | Yes | No (err-disabled) |

**Shutdown** (default) is the most secure and the most disruptive. Protect is the least noisy but also least visible. Restrict is a useful middle ground for visibility without disruption.

#### Recovering from err-disabled

An err-disabled port does not recover automatically unless `errdisable recovery` is configured. Manual recovery: `shutdown` → `no shutdown` on the interface.

### DHCP Snooping

**DHCP Snooping** is a switch feature that monitors DHCP exchanges and builds a table of legitimate IP-to-MAC-to-port-to-VLAN bindings.

#### Trusted vs untrusted ports

- **Trusted ports:** Connected to legitimate DHCP servers or upstream switches. DHCP server replies (OFFER, ACK) are allowed through.
- **Untrusted ports:** Connected to end devices. Only DHCP client messages (DISCOVER, REQUEST) are allowed. A DHCP server reply on an untrusted port is dropped — this prevents rogue DHCP servers.

The binding table is populated from DHCP ACK messages seen on trusted ports: when the server assigns `192.168.10.50` to MAC `aa:bb:cc:dd:ee:01` on port `Gi0/5` in VLAN 10, the switch records this tuple.

#### What DHCP Snooping prevents

- **Rogue DHCP servers:** A device connected to an untrusted port cannot respond to DHCP DISCOVERs — its replies are dropped.
- **DHCP starvation:** An attacker flooding DHCP DISCOVERs with random MACs (exhausting the pool) can be rate-limited per port.

DHCP Snooping is the prerequisite for DAI — without a binding table, DAI has no data to validate against.

### Dynamic ARP Inspection (DAI)

**ARP spoofing** (also called ARP poisoning): an attacker sends a gratuitous ARP reply claiming that the gateway's IP (`192.168.1.1`) maps to the attacker's MAC. Hosts update their ARP cache and begin sending traffic intended for the gateway to the attacker — who can intercept, modify, and forward it (**man-in-the-middle attack**).

DAI prevents this by validating ARP packets against the DHCP Snooping binding table:

1. An ARP reply arrives on an untrusted port.
2. The switch checks: does the sender IP + sender MAC in the ARP packet match a binding table entry for this port?
3. If it matches → forward.
4. If it doesn't match → drop; log; optionally increment violation counter.

On trusted ports (uplinks, servers with static IPs), ARP validation is bypassed — or static ARP ACL entries cover static-IP devices.

#### ARP ACL for static IP hosts

Devices with statically assigned IPs (servers, routers) don't appear in the DHCP Snooping table. DAI would drop their ARP unless an explicit **ARP ACL** is configured mapping their IP to their MAC.

```
arp access-list SERVER-ARPS
 permit ip host 192.168.10.1 mac host aa:bb:cc:dd:ee:ff
```

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Port Security — sticky, max 2 MACs, shutdown on violation
    interface GigabitEthernet0/1
     switchport mode access
     switchport access vlan 10
     switchport port-security maximum 2
     switchport port-security violation shutdown
     switchport port-security mac-address sticky
     switchport port-security

    ! DHCP Snooping
    ip dhcp snooping
    ip dhcp snooping vlan 10,20
    ! Mark uplinks as trusted
    interface GigabitEthernet0/24
     ip dhcp snooping trust

    ! Dynamic ARP Inspection
    ip arp inspection vlan 10,20
    ! ARP ACL for static-IP server
    arp access-list STATIC-SERVERS
     permit ip host 192.168.10.1 mac host aa:bb:cc:dd:ee:ff
    ip arp inspection filter STATIC-SERVERS vlan 10

    ! Verification
    show port-security interface Gi0/1
    show ip dhcp snooping binding
    show ip arp inspection vlan 10
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/sec/b_173_sec_9300_cg/configuring_port_security.html](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-x/configuration_guide/sec/b_173_sec_9300_cg/configuring_port_security.html)

=== "Juniper EX (Junos)"

    ```
    # DHCP Snooping (called "DHCP trusted" in EX context)
    set vlans VLAN10 dhcp-trusted-server 192.168.10.253

    # MAC limiting (port security equivalent)
    set interfaces ge-0/0/1 unit 0 family ethernet-switching mac-limit 2
    set interfaces ge-0/0/1 unit 0 family ethernet-switching mac-limit action drop

    # Dynamic ARP Inspection
    set vlans VLAN10 arp-inspection

    # Trusted uplink
    set interfaces ge-0/0/23 unit 0 family ethernet-switching dhcp-trusted

    # Verification
    show dhcp snooping binding
    show arp inspection statistics
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/security-services/topics/topic-map/dai-dhcpv4-snooping.html](https://www.juniper.net/documentation/us/en/software/junos/security-services/topics/topic-map/dai-dhcpv4-snooping.html)

=== "Arista EOS"

    ```
    ! DHCP Snooping
    ip dhcp snooping
    ip dhcp snooping vlan 10,20

    ! Trusted uplink
    interface Ethernet24
       ip dhcp snooping trust

    ! Dynamic ARP Inspection
    ip arp inspection vlan 10,20

    ! MAC Security (port security)
    interface Ethernet1
       mac security maximum addresses 2
       mac security violation shutdown

    ! Verification
    show ip dhcp snooping binding
    show ip arp inspection vlan 10
    show mac security
    ```

    Full configuration reference: [https://www.arista.com/en/um-eos/eos-dhcp-snooping](https://www.arista.com/en/um-eos/eos-dhcp-snooping)

---

## Common Pitfalls

1. **Not marking uplinks as trusted for DHCP Snooping.** If the uplink to the DHCP server is not trusted, DHCP ACK replies from the server are dropped and clients cannot get addresses. Always mark server-facing and uplink ports as trusted.

2. **DAI dropping ARP from statically configured hosts.** Static-IP devices (routers, servers) have no DHCP Snooping binding entry. DAI will drop their ARP unless an ARP ACL is configured or the port is trusted.

3. **Port security with sticky MACs and moved devices.** If a device is moved to a different port, the old sticky MAC persists in the config and the new port will violation-shutdown when the device connects. Run `clear port-security sticky interface` before moving devices.

4. **DHCP Snooping and Option 82 (relay information).** Some DHCP relay configurations insert Option 82. Certain switches drop DHCP packets with Option 82 set on untrusted ports. Disable the check with `no ip dhcp snooping information option` if Option 82 is legitimate in your environment.

5. **Applying DAI without enabling DHCP Snooping first.** Without a binding table, DAI has no data to validate against and drops all ARP — including legitimate ARP from valid hosts. Enable DHCP Snooping first and let the table populate before enabling DAI.

---

## Practice Problems

**Q1.** A switch port has port security configured with max 1 MAC, violation shutdown, and sticky mode. An admin connects a new laptop to this port, but the old laptop's sticky MAC is still in the config. What happens?

??? answer
    The port immediately err-disables when the new laptop sends its first frame — the new MAC doesn't match the saved sticky MAC. The admin must clear the sticky MAC entry (`clear port-security sticky interface <if>`) and bring the port back up.

**Q2.** You enable DHCP Snooping on VLAN 10 but forget to mark the uplink as trusted. What happens to DHCP clients in VLAN 10?

??? answer
    They cannot obtain IP addresses. Their DISCOVER messages go through, but the DHCP server's OFFER and ACK replies arrive on the untrusted uplink port and are dropped by DHCP Snooping. Clients time out without an address.

**Q3.** An attacker sends a gratuitous ARP claiming IP 192.168.10.1 maps to their MAC. DAI is enabled on VLAN 10. The DHCP Snooping table shows 192.168.10.50 → attacker's MAC on port Gi0/5. Is the attacker's ARP forwarded?

??? answer
    No. DAI checks the ARP sender IP (192.168.10.1) and sender MAC against the binding table entry for port Gi0/5. The binding table has 192.168.10.50 for that MAC on that port — not 192.168.10.1. The mismatch causes DAI to drop the ARP.

**Q4.** What violation mode should you use if you want visibility into violations without disrupting traffic?

??? answer
    **Restrict** — drops offending frames, increments the violation counter, and generates a log message, but leaves the port up. Protect is silent (no logging, no counter). Shutdown is the most disruptive.

---

## Lab

**Objective:** Configure port security with sticky MACs; enable DHCP Snooping and DAI; simulate an ARP spoofing attack and verify DAI blocks it.

**Steps:**
1. Configure a switch with two access ports (VLAN 10), one trusted uplink.
2. Enable DHCP Snooping on VLAN 10; mark uplink as trusted.
3. Connect two hosts; obtain DHCP addresses. Verify the binding table with `show ip dhcp snooping binding`.
4. Enable DAI on VLAN 10.
5. On one host, send a gratuitous ARP claiming the gateway IP with a different MAC (using `arping -U` or Scapy). Verify DAI drops it with `show ip arp inspection statistics`.
6. Enable port security (sticky, max 1 MAC, shutdown violation) on an access port. Disconnect the authorised device; connect a different device and observe the err-disable.

---

## Summary & Key Takeaways

- **Port security** limits the number (and optionally identity) of MACs on an access port, protecting against unauthorised devices and MAC flooding.
- **Sticky MAC** learns the first MAC seen and saves it to config — most practical for access ports.
- Violation modes: **Protect** (silent drop), **Restrict** (drop + log), **Shutdown** (err-disable, default).
- **DHCP Snooping** monitors DHCP exchanges and builds a MAC-IP-port binding table; prevents rogue DHCP servers.
- Uplink ports must be **trusted** or DHCP replies from the server are dropped.
- **Dynamic ARP Inspection (DAI)** validates ARP sender IP/MAC against the DHCP Snooping binding table; prevents ARP spoofing / man-in-the-middle.
- Static-IP hosts need **ARP ACLs** to avoid DAI false-positive drops.
- Enable DHCP Snooping before DAI; populate the binding table first.

---

## Where to Next

- **SEC-001 — Access Control Lists:** Layer 3/4 filtering — the next security layer up from Layer 2.
- **SEC-002 — Firewall Concepts:** Stateful inspection beyond ACLs.
- **SV-002 — DHCP:** DHCP protocol detail; relay agents; Option 82.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| IEEE 802.1X | Port-based Network Access Control (NAC) — the enterprise-grade successor to port security |
| RFC 5227 | IPv4 Address Conflict Detection (ARP probing) |
| Cisco CCNA | Port security configuration, DHCP Snooping, DAI |
| Cisco CCNP Enterprise | Layer 2 security hardening, 802.1X integration |
| CompTIA Security+ | ARP spoofing, Layer 2 attacks, switch hardening |

---

## References

- RFC 5227 — IPv4 Address Conflict Detection. [https://www.rfc-editor.org/rfc/rfc5227](https://www.rfc-editor.org/rfc/rfc5227)

---

## Attribution & Licensing

- Module content: original draft, AI-assisted (Claude Sonnet 4.6), 2026-04-19.
- No third-party text reproduced.
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- XREF-START -->
## Cross-References

### Vendor Feature Mapping

| Feature | Cisco IOS-XE | Juniper EX (Junos) | Arista EOS |
|---|---|---|---|
| Port security enable | `switchport port-security` | `mac-limit` on interface | `mac security maximum addresses` |
| Sticky MAC | `mac-address sticky` | n/a (manual static only) | n/a |
| Violation mode | `violation shutdown\|restrict\|protect` | `action drop\|shutdown` | `violation shutdown` |
| DHCP Snooping enable | `ip dhcp snooping vlan <id>` | `dhcp-trusted-server` | `ip dhcp snooping vlan <id>` |
| Trusted port | `ip dhcp snooping trust` | `dhcp-trusted` | `ip dhcp snooping trust` |
| DAI enable | `ip arp inspection vlan <id>` | `arp-inspection` on VLAN | `ip arp inspection vlan <id>` |
| Show bindings | `show ip dhcp snooping binding` | `show dhcp snooping binding` | `show ip dhcp snooping binding` |

### Modules That Reference This Module

| Module ID | Title | Relationship |
|---|---|---|
| SEC-001 | Access Control Lists | L3/4 security builds on L2 security foundation |
| SV-002 | DHCP | DHCP Snooping depends on DHCP protocol understanding |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SW-001 | Switching Fundamentals | MAC table and flooding — what port security protects |
| SW-002 | VLANs & 802.1Q Trunking | VLANs scope DHCP Snooping and DAI domains |
<!-- XREF-END -->
