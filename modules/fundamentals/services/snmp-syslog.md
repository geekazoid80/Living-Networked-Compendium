---
module_id: SV-005
title: "SNMP & Syslog - Network Monitoring Fundamentals"
description: "How SNMP enables structured device monitoring and management, and how Syslog collects event messages across network infrastructure."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - IP-001
  - RT-001
  - SV-004
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - snmp
  - syslog
  - monitoring
  - network-management
  - services
created: 2026-04-19
updated: 2026-04-19
---

# SV-005 - SNMP & Syslog - Network Monitoring Fundamentals
## Learning Objectives

After completing this module you will be able to:

1. Describe the SNMP architecture: manager, agent, MIB, OID.
2. Distinguish SNMP v1, v2c, and v3 - especially v3's security improvements.
3. Explain the difference between SNMP GET, SET, TRAP, and INFORM.
4. Describe Syslog severity levels and how to configure a central syslog server.
5. Configure SNMP v2c and v3 on router platforms.
6. Configure Syslog forwarding on router platforms.

---
## Prerequisites

- IP-001 - IP Addressing Fundamentals
- RT-001 - Routing Fundamentals (reachability to management servers)
- SV-004 - NTP (Syslog timestamps require synchronised clocks)

---
## The Problem

Fifty routers, a hundred switches, three firewalls. You need to know: which interfaces are down, what the CPU utilisation is across all devices, whether any routing adjacency dropped, when the last configuration change happened, and who logged in at 2:00 AM. Logging into each device individually to check is not viable at scale.

### Step 1: A standard data model for network devices

Every router has interfaces, routing tables, CPU stats, memory counters. If each vendor stored these differently, you'd need 50 different tools to query them. A **MIB (Management Information Base)** defines a standard tree of named variables - each with a unique numeric identifier (OID). A router, switch, or firewall exposes data through this tree; a management system queries any device using the same protocol.

### Step 2: A polling protocol

A central management station sends a **GET** request to a device asking for the value of a specific OID. The device returns the current value. Polling every device for every counter on a schedule gives you time-series monitoring - graphs, thresholds, capacity trends.

### Step 3: Devices sending alerts without being asked

Polling only tells you what's happening at polling intervals. A link that goes down for 30 seconds between polls is invisible. Devices need to send unsolicited alerts - **traps** - when important events occur (interface down, CPU threshold exceeded, authentication failure). The management station receives these in real time.

You have invented **SNMP - Simple Network Management Protocol**.

### Step 4: Unstructured event logging

Not all events fit into structured SNMP variables. Log messages - free-text records of what happened - need a separate channel. Every device sends time-stamped human-readable messages to a central log collector. This is **Syslog** - a simple protocol for shipping text log messages over the network.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Standard variable tree for device data | MIB / OID |
| Polling protocol | SNMP GET |
| Device-initiated alert | SNMP Trap / Inform |
| Structured device data repository | SNMP MIB |
| Text log message protocol | Syslog |
| Severity rating on log messages | Syslog facility/severity |

---
## Core Content

### SNMP Architecture

**Manager:** The monitoring platform (Zabbix, LibreNMS, Cacti, Nagios, Grafana+Prometheus with SNMP exporter). Polls agents and receives traps.

**Agent:** Software running on the network device. Exposes device data via the MIB tree; responds to GETs; sends traps.

**MIB (Management Information Base):** A hierarchical database of object definitions. Each object has:
- An **OID (Object Identifier):** A dotted numeric path, e.g., `1.3.6.1.2.1.2.2.1.7` - the `ifOperStatus` (interface operational status).
- A type (integer, string, counter, gauge, timetick).
- Read-only or read-write access.

Common MIBs:
- **MIB-II (RFC 1213):** Interfaces, IP, TCP, UDP, ICMP statistics. Universally supported.
- **IF-MIB (RFC 2863):** Enhanced interface counters (64-bit).
- Vendor-specific MIBs: Cisco CISCO-PROCESS-MIB (CPU/memory), Juniper JUNIPER-MIBS.

### SNMP Operations

| Operation | Direction | Purpose |
|---|---|---|
| **GET** | Manager → Agent | Retrieve the value of one or more OIDs |
| **GETNEXT** | Manager → Agent | Walk the MIB tree - retrieve the next OID after a given one |
| **GETBULK** (v2c+) | Manager → Agent | Retrieve a block of MIB rows efficiently |
| **SET** | Manager → Agent | Write a value to a writable OID (e.g., disable an interface) |
| **TRAP** | Agent → Manager | Unsolicited notification; UDP, no acknowledgement |
| **INFORM** (v2c+) | Agent → Manager | Unsolicited notification with acknowledgement; manager confirms receipt |

SNMP uses **UDP port 161** (agent receives GET/SET) and **UDP port 162** (manager receives traps/informs).

### SNMP Versions

| Version | Authentication | Encryption | Notes |
|---|---|---|---|
| **v1** | Community string (plaintext) | None | Obsolete; avoid |
| **v2c** | Community string (plaintext) | None | Adds GETBULK, Informs, 64-bit counters. Still widely deployed but credentials in plaintext |
| **v3** | Username + authentication (MD5/SHA) | Optional (DES/AES) | Current standard. Use always for new deployments |

**Community strings** in v1/v2c are essentially passwords sent in plaintext. A default community string of `public` (read-only) or `private` (read-write) is widely known and exploited. Always change community strings; use ACLs to restrict which management IPs can query.

SNMP v3 security levels:

| Level | Authentication | Encryption |
|---|---|---|
| noAuthNoPriv | No | No |
| authNoPriv | Yes (SHA/MD5) | No |
| authPriv | Yes (SHA/MD5) | Yes (AES/DES) |

Always use **authPriv** with SHA authentication and AES encryption in production.

### Syslog

**Syslog (RFC 5424)** is a simple protocol for transmitting log messages from devices to a centralised log server. Devices send log messages over **UDP port 514** (default) or TCP 514/6514 (for reliability and TLS encryption).

#### Syslog Message Format

```
<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
```

The `<PRI>` value encodes **facility** and **severity**:

```
PRI = (Facility × 8) + Severity
```

#### Facilities (source of the message)

| Code | Facility |
|---|---|
| 0 | Kernel |
| 3 | System daemon |
| 16–23 | Local use (local0–local7) - commonly used for network devices |

Network devices typically use `local6` or `local7` by default.

#### Severity Levels

| Level | Keyword | Meaning |
|---|---|---|
| 0 | Emergency | System unusable |
| 1 | Alert | Immediate action required |
| 2 | Critical | Critical condition |
| 3 | Error | Error conditions |
| 4 | Warning | Warning conditions |
| 5 | Notice | Normal but significant event |
| 6 | Informational | Informational messages |
| 7 | Debug | Debug-level messages |

**Lower number = higher severity.** Logging verbosity is controlled by setting the minimum severity - "logging level 6" means log everything from severity 0 through 6 (debug excluded).

**Common production setting:** Level 5 (Notice) or Level 6 (Informational) - captures significant events without the noise of debug messages.

#### Syslog Transport

- **UDP 514:** Stateless, no guarantee of delivery. Fine for high-volume logging; some messages may be lost under load.
- **TCP 514:** Reliable; connection-based; better for security audit logging.
- **TCP 6514 with TLS:** Encrypted; recommended for security-sensitive environments (RFC 5425).

??? supplementary "Syslog vs SNMP for Monitoring"
    Syslog and SNMP serve different purposes. Syslog is **event-driven** - a message is sent when something happens (interface down, user login, BGP adjacency drop). It's free-text and human-readable but hard to aggregate programmatically. SNMP is **polling-based** - a manager requests current values on a schedule, producing time-series data (interface utilisation, CPU load, error counters). Both are needed: SNMP for metrics and trending, Syslog for events and auditing. Modern observability platforms often ingest both plus streaming telemetry (PROTO-007).

---
## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! SNMP v2c (simple, but plaintext community string)
    snmp-server community MyReadCommunity RO 10
    access-list 10 permit 10.0.0.0 0.0.0.255   ! restrict to management subnet

    ! SNMP v3 (recommended)
    snmp-server group MONITOR v3 priv
    snmp-server user admin MONITOR v3 auth sha AuthPass123 priv aes 128 PrivPass456

    ! SNMP trap destination
    snmp-server host 10.0.0.5 version 3 priv admin
    snmp-server enable traps

    ! Syslog
    logging host 10.0.0.6
    logging trap informational
    logging source-interface Loopback0
    service timestamps log datetime msec localtime

    ! Verification
    show snmp community
    show snmp user
    show logging
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/snmp/configuration/xe-17/snmp-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/snmp/configuration/xe-17/snmp-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # SNMP v3
    set snmp v3 usm local-engine user admin authentication-sha authentication-password "AuthPass123"
    set snmp v3 usm local-engine user admin privacy-aes128 privacy-password "PrivPass456"
    set snmp v3 vacm security-to-group security-model usm security-name admin group MONITOR-GROUP
    set snmp v3 vacm access group MONITOR-GROUP default-context-prefix security-model usm security-level privacy read-view all

    # SNMP trap target
    set snmp v3 target-address TRAP-SERVER address 10.0.0.5
    set snmp v3 target-parameters TRAP-PARAMS usm security-name admin security-level privacy

    # Syslog
    set system syslog host 10.0.0.6 any notice
    set system syslog host 10.0.0.6 source-address 10.0.1.1

    # Verification
    show snmp statistics
    show log messages | last 50
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/network-mgmt/topics/topic-map/snmp-v3-configuration.html](https://www.juniper.net/documentation/us/en/software/junos/network-mgmt/topics/topic-map/snmp-v3-configuration.html)

=== "MikroTik RouterOS"

    ```
    # SNMP v2c
    /snmp community set [ find name=public ] read-access=yes write-access=no
    /snmp set enabled=yes contact="admin@example.com" location="Server Room"

    # SNMP trap
    /snmp trap set enabled=yes community=public

    # Syslog to remote server
    /system logging action set remote name=remote target=remote remote=10.0.0.6 remote-port=514
    /system logging add action=remote topics=info,warning,error,critical

    # Verification
    /snmp print
    /system logging print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/SNMP](https://help.mikrotik.com/docs/display/ROS/SNMP)

---
## Common Pitfalls

1. **Default SNMP community strings (`public`/`private`).** These are universally known. An SNMP v2c `private` community with write access gives an attacker full read-write access to device MIBs - including configuration. Always change community strings and restrict with ACLs. Better: use SNMPv3 authPriv.

2. **SNMP v3 user/group misconfiguration.** SNMPv3 requires user, group, and view to be configured consistently. A common error is creating the user without assigning the group, or assigning the group to a view that doesn't cover the OID being queried. Test with `snmpwalk -v3 ...` before deploying monitoring.

3. **Syslog timestamps incorrect due to missing NTP.** A log message that says `00:01:23` (device uptime since boot) is useless for incident response. Always configure NTP before enabling Syslog; use `service timestamps log datetime msec localtime` (Cisco) to embed absolute timestamps.

4. **Syslog over UDP with no acknowledgement.** During high-load events (crash, rapid link flapping), the device may generate thousands of log messages per second - UDP syslog will drop messages under load. For audit trails and compliance, use TCP syslog with buffering.

5. **Management traffic not on a separate management plane.** If SNMP and Syslog traffic travels in-band on production interfaces, it competes with user traffic and may be captured. Use a dedicated management VRF / out-of-band management network where possible.

---
## Practice Problems

**Q1.** What is the difference between an SNMP Trap and an SNMP Inform?

??? answer
    Both are unsolicited notifications from an agent to the manager. A Trap uses UDP with no acknowledgement - the agent sends it and doesn't know if it was received. An Inform requires the manager to send an acknowledgement; if no ACK is received, the agent retransmits. Informs are more reliable but add overhead; use Traps for high-volume events, Informs for critical alerts.

**Q2.** A network engineer configures `snmp-server community public RO` with no ACL. What is the security risk?

??? answer
    Anyone on any network who can reach the device on UDP 161 can query all read-only MIBs - including routing tables, interface details, ARP caches, system description, and version information. This provides reconnaissance data to attackers. Mitigate by restricting to an ACL limiting queries to the management station's IP, and by migrating to SNMPv3 authPriv.

**Q3.** A Syslog severity level is set to `warning` (level 4) on a device. Which messages are forwarded to the syslog server?

??? answer
    Messages at severity 0 (Emergency), 1 (Alert), 2 (Critical), 3 (Error), and 4 (Warning) - all messages at severity level 4 and below (more severe). Messages at severity 5 (Notice), 6 (Informational), and 7 (Debug) are not forwarded.

---
## Summary & Key Takeaways

- **SNMP** enables structured device monitoring: GET (poll), SET (configure), Trap/Inform (alerts).
- The **MIB** defines the tree of OID-addressed variables that agents expose.
- SNMP v1/v2c use plaintext community strings - insecure; **SNMPv3 authPriv** (SHA + AES) is the production standard.
- SNMP uses **UDP 161** (queries) and **UDP 162** (traps/informs).
- **Syslog** ships free-text log messages to a central server over UDP/TCP port 514.
- Syslog severity: 0 (Emergency) to 7 (Debug). Lower number = more severe. Production: level 5 or 6.
- Accurate Syslog timestamps require **NTP** (SV-004).
- Change default community strings; use ACLs; prefer SNMPv3; use TCP Syslog for audit trails.

---
## Where to Next

- **SEC-001 - Access Control Lists:** Restrict management access; control which IPs can reach SNMP/Syslog ports.
- **AUTO-001 - Python for Network Engineers:** Programmatic SNMP polling and log parsing.
- **PROTO-007 - Streaming Telemetry:** Modern alternative to SNMP polling for high-frequency metrics.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 3411–3418 | SNMP Architecture (SNMPv3 framework) |
| RFC 2578–2580 | SMI (Structure of Management Information) for SNMP MIBs |
| RFC 5424 | Syslog Protocol |
| RFC 5425 | Syslog over TLS |
| Cisco CCNA | SNMP configuration, Syslog configuration |
| Cisco CCNP Enterprise | SNMPv3 hardening, monitoring design |
| CompTIA Network+ | SNMP/Syslog concepts |

---
## References

- RFC 3411 - SNMP Architecture. [https://www.rfc-editor.org/rfc/rfc3411](https://www.rfc-editor.org/rfc/rfc3411)
- RFC 5424 - The Syslog Protocol. [https://www.rfc-editor.org/rfc/rfc5424](https://www.rfc-editor.org/rfc/rfc5424)
- RFC 5425 - Transport Layer Security (TLS) Transport Mapping for Syslog. [https://www.rfc-editor.org/rfc/rfc5425](https://www.rfc-editor.org/rfc/rfc5425)

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
| SEC-001 | Access Control Lists | ACLs restrict access to SNMP/Syslog management ports |
| AUTO-001 | Python for Network Engineers | Programmatic SNMP querying and log parsing |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | SNMP/Syslog use UDP/IP |
| RT-001 | Routing Fundamentals | Reachability to management stations |
| SV-004 | NTP | Accurate timestamps for Syslog |
<!-- XREF-END -->
