---
id: SEC-004
title: "AAA — Authentication, Authorisation & Accounting"
description: "How AAA frameworks (TACACS+ and RADIUS) centralise network device access control, command authorisation, and session accounting."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 40
prerequisites:
  - IP-001
  - SEC-001
  - SV-004
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - aaa
  - tacacs
  - radius
  - authentication
  - authorisation
  - accounting
  - security
created: 2026-04-19
updated: 2026-04-19
---

# SEC-004 — AAA — Authentication, Authorisation & Accounting

## The Problem

Fifty routers, managed by a team of ten network engineers and four contractors. Each device has local accounts (`admin`, `readonly`). When an engineer leaves, you change the password on 50 devices. Contractors have full admin access — you want to restrict them to read-only commands but currently can't do this per-device. You have no record of who made which configuration change and when.

### Step 1: Centralise identity

Instead of managing accounts on each device, all devices point to one server that holds all user accounts. The device asks the server: "Is this username/password valid?" The server answers yes or no. When an engineer leaves, you delete their account from one place. This is **Authentication** (A1) — centralised.

### Step 2: Define what each user can do

The server doesn't just say yes/no — it also tells the device what the user is authorised to do. A contractor might be authorised only for `show` commands. An engineer gets full admin. This per-user permission is applied without touching each device. This is **Authorisation** (A2).

### Step 3: Record everything

Every login attempt, every command executed, every session start and end is sent to a logging server. You now have a complete audit trail. This is **Accounting** (A3).

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Centralised login verification | Authentication |
| Per-user command permission | Authorisation |
| Session and command audit logging | Accounting |
| The three together | AAA |
| Cisco-originated protocol for device management | TACACS+ |
| UDP-based standard protocol, broad support | RADIUS |
| Device that queries the AAA server | NAS (Network Access Server) |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain the three components of AAA and why centralisation matters.
2. Describe TACACS+ and RADIUS — their architecture, transport, and key differences.
3. Configure AAA on a router using a TACACS+ or RADIUS server.
4. Configure fallback to local authentication when the AAA server is unreachable.
5. Explain privilege levels and command authorisation.
6. Describe RADIUS's role in 802.1X port-based access control.

---

## Prerequisites

- IP-001 — IP Addressing Fundamentals (server reachability)
- SEC-001 — ACLs (ACL for management plane protection)
- SV-004 — NTP (accurate timestamps in accounting records)

---

## Core Content

### AAA Architecture

```
Network Engineer ──SSH──→ [Router (NAS)] ──TACACS+/RADIUS──→ [AAA Server]
                                                                     │
                                                              [User Database]
                                                              [Command ACLs]
                                                              [Accounting DB]
```

The **NAS (Network Access Server)** is the network device being accessed (router, switch, firewall). It acts as a client to the AAA server.

The AAA server maintains:
- User accounts and passwords (or integrates with LDAP/AD)
- Authorisation profiles (privilege levels, command sets, VLAN assignment)
- Accounting records

Common AAA server software: Cisco ISE (Identity Services Engine), FreeRADIUS, ClearPass, Juniper Access Control.

### TACACS+ vs RADIUS

| Property | TACACS+ | RADIUS |
|---|---|---|
| Standard | Cisco-originated (RFC 8907 in 2020) | RFC 2865 (1997) |
| Transport | TCP port 49 | UDP port 1812 (auth/authz), 1813 (accounting) |
| Encryption | Encrypts entire payload | Encrypts only the password field |
| A-A-A separation | Separate A, A, A — each independently configured | Auth and authz combined; accounting separate |
| Command authorisation | Full command-level control (per-command authorisation) | Limited; not designed for command authorisation |
| Primary use case | Network device management (CLI access) | Network access control (user auth, 802.1X, VPN) |
| Multi-vendor support | Historically Cisco-heavy | Universal |

**Rule of thumb:** Use **TACACS+** for network device management (CLI access control, command authorisation). Use **RADIUS** for network access (user WiFi, 802.1X port access, VPN authentication, DHCP integration).

Both can be used simultaneously — TACACS+ for device management, RADIUS for user network access.

### Authentication Methods

TACACS+ and RADIUS support multiple authentication protocols:

| Method | Description |
|---|---|
| PAP | Password in plaintext (RADIUS: password encrypted in RADIUS packet) |
| CHAP | Challenge-Handshake — shared secret, one-way hash response |
| MS-CHAPv2 | Microsoft variant; used with Active Directory for Windows clients |
| EAP | Extensible Authentication Protocol — tunnels other methods (EAP-TLS, PEAP, EAP-TTLS) |

For network device management (SSH login): PAP over TLS (TACACS+ encrypts whole payload; RADIUS with EAP) is acceptable. For 802.1X: EAP-TLS (certificate-based) is the gold standard.

### Privilege Levels (Cisco)

Cisco IOS has 16 privilege levels (0–15). Level 15 = full admin (enable-equivalent); level 1 = user-exec (default, show commands only).

With TACACS+, the server assigns a privilege level per user on login, or defines per-command authorisation:

```
! AAA model on router
aaa new-model
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa authorization commands 15 default group tacacs+ local none
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+

! TACACS+ server
tacacs server ISE-1
 address ipv4 10.0.0.100
 key 7 MySharedSecret

! Fallback to local
username admin privilege 15 secret ChangeMe
```

`local` at the end of the method list = fallback to local accounts when the TACACS+ server is unreachable.

### 802.1X — Port-Based Network Access Control

RADIUS is used in 802.1X (IEEE standard) for network-level authentication:

1. A device plugs into a switch port.
2. The switch (as RADIUS NAS) challenges the device: "Identify yourself."
3. The device (802.1X supplicant) provides credentials (certificate or username/password).
4. The switch forwards the challenge to the RADIUS server.
5. RADIUS authenticates and returns the authorised VLAN, QoS policy, ACL.
6. The switch applies the policy and brings the port up.

Until authenticated, the port only passes 802.1X and DHCP — nothing else. This eliminates unauthorised devices from accessing the network regardless of port (unlike port security, which uses MACs — easier to spoof).

### Accounting Records

Accounting sends records for:
- **Login/logout:** User, source IP, session duration.
- **Command:** Every command entered in exec or configuration mode.
- **Network:** RADIUS accounting for session start/stop, bytes transferred.

Accounting records are invaluable for forensic investigation ("who ran `reload` on the core router at 2am?") and compliance (PCI-DSS, SOC2 require audit trails for network device access).

---

## Vendor Implementations

=== "Cisco IOS-XE (TACACS+)"

    ```
    ! Enable AAA model
    aaa new-model

    ! Authentication for SSH/console login
    aaa authentication login default group tacacs+ local

    ! Authorisation — exec mode and all privilege 15 commands
    aaa authorization exec default group tacacs+ local
    aaa authorization commands 15 default group tacacs+ local none

    ! Accounting — record all exec sessions and commands
    aaa accounting exec default start-stop group tacacs+
    aaa accounting commands 15 default start-stop group tacacs+

    ! Define TACACS+ server
    tacacs server ISE-PRIMARY
     address ipv4 10.0.0.100
     key 0 MySharedSecret    ! key 0 = plaintext; use type 7/8/9 in production

    ! Server group
    aaa group server tacacs+ TACACS-SERVERS
     server name ISE-PRIMARY

    ! Local fallback account
    username admin privilege 15 secret Class!fy2026

    ! Apply login to VTY lines
    line vty 0 15
     login authentication default
     authorization exec default

    ! Verification
    show aaa sessions
    show tacacs
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_aaa/configuration/xe-17/sec-usr-aaa-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_aaa/configuration/xe-17/sec-usr-aaa-xe-17-book.html)

=== "Juniper (Junos — RADIUS)"

    ```
    set system radius-server 10.0.0.100 secret "MySharedSecret"
    set system radius-server 10.0.0.100 port 1812

    set system authentication-order [ radius password ]

    # Accounting
    set system accounting destination radius server 10.0.0.100 secret "MySharedSecret"
    set system accounting events [ login interactive-commands ]

    # Local fallback
    set system login user admin class super-user authentication plain-text-password

    # Verification
    show system accounting statistics
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/user-access/topics/topic-map/radius-tacacs-aaa.html](https://www.juniper.net/documentation/us/en/software/junos/user-access/topics/topic-map/radius-tacacs-aaa.html)

=== "MikroTik RouterOS"

    ```
    # RADIUS for device management
    /radius
    add address=10.0.0.100 secret="MySharedSecret" service=login

    # Enable RADIUS authentication
    /user aaa
    set use-radius=yes

    # Local fallback
    /user add name=admin group=full password=Str0ngPa55!

    # Accounting
    /radius add address=10.0.0.100 secret="MySharedSecret" service=login accounting=yes

    # Verification
    /radius print
    /user active print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/RADIUS+Client](https://help.mikrotik.com/docs/display/ROS/RADIUS+Client)

---

## Common Pitfalls

1. **No local fallback account.** If the TACACS+/RADIUS server is unreachable (link failure, server restart), and there is no local fallback, no one can log in to the device. Always configure `local` at the end of the method list and maintain at least one local admin account.

2. **Shared secret mismatch.** The shared secret between the NAS (device) and AAA server must match exactly. A mismatch causes all authentication attempts to fail silently (no error message from the server — the RADIUS/TACACS+ packet is simply invalid and dropped). Verify the secret on both sides.

3. **TACACS+ server unreachable (firewall blocking TCP 49).** TACACS+ uses TCP 49. If an ACL or firewall blocks this port between the device and the AAA server, authentication fails. Add an explicit permit for TCP 49 from the device's management IP to the server.

4. **Accounting without NTP.** Accounting records are timestamped by the device. Without NTP (SV-004), timestamps are meaningless for forensics and compliance. Configure NTP before enabling AAA accounting.

5. **Command authorisation with no fallback.** If TACACS+ server is down and command authorisation is set to `group tacacs+ none`, no commands are authorised — the device is unmanageable. Set `group tacacs+ if-authenticated` (authorise based on authenticated level) or `local none` as fallback for exec authorisation.

---

## Practice Problems

**Q1.** What is the key difference between TACACS+ and RADIUS for network device management?

??? answer
    TACACS+ encrypts the entire payload (not just the password), uses TCP (reliable), and supports per-command authorisation — making it the standard choice for network device CLI access control. RADIUS only encrypts the password, uses UDP, and does not natively support per-command authorisation. RADIUS is preferred for network access (802.1X, VPN, WiFi) where its broader client support and standard EAP integration matter.

**Q2.** An engineer logs in successfully to a router using TACACS+. She runs `show ip route` and gets no output — the command seems to execute but returns nothing. However, after disconnecting and using local auth (admin), `show ip route` works correctly. What is the likely cause?

??? answer
    The TACACS+ server returned privilege level 1 for this user (user-exec), which doesn't have access to `show ip route` in some IOS versions, or the user is in exec mode with restricted view. Alternatively, the TACACS+ authorisation is stripping output for certain show commands via per-command ACL. Check the server's authorisation profile for this user and verify her assigned privilege level with `show privilege`.

**Q3.** Why is it critical to configure `aaa accounting commands 15 default start-stop group tacacs+` in a production environment?

??? answer
    This records every privilege-15 (admin) command entered by every user to the TACACS+ accounting server. The record includes: username, device, timestamp (from NTP), and the exact command. This is the audit trail required for compliance (PCI-DSS, SOC2, ISO 27001) and for forensic investigation of configuration changes ("who issued `no ip route 0.0.0.0/0` at 3am?"). Without command accounting, there is no post-incident traceability.

---

## Summary & Key Takeaways

- **AAA** = Authentication (who?), Authorisation (what are you allowed to do?), Accounting (log everything).
- Centralised AAA eliminates per-device account management — one change applies everywhere.
- **TACACS+** (TCP 49, full payload encryption): use for network device management (CLI access, command authorisation).
- **RADIUS** (UDP 1812/1813, only password encrypted): use for network access (802.1X, WiFi, VPN).
- Always configure a **local fallback account** — if the AAA server is unreachable, you need a way in.
- **Command accounting** creates the audit trail required for compliance and forensics — enable it.
- RADIUS + 802.1X enables port-based network access control — no device is allowed on the network until authenticated.
- NTP (SV-004) is a prerequisite for meaningful accounting timestamps.

---

## Where to Next

- **SEC-005 — Encryption Standards & PKI:** Certificate-based EAP-TLS for 802.1X.
- **SEC-006 — Network Segmentation & DMZ:** Separate management plane from data plane.
- **SV-004 — NTP:** Accurate timestamps for accounting records.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 8907 | TACACS+ Protocol (2020 standardisation) |
| RFC 2865 | RADIUS — Remote Authentication Dial-In User Service |
| RFC 2866 | RADIUS Accounting |
| IEEE 802.1X | Port-Based Network Access Control |
| Cisco CCNP Security | AAA configuration, TACACS+/RADIUS, 802.1X |
| CompTIA Security+ | AAA concepts, RADIUS, TACACS+ |

---

## References

- RFC 8907 — The TACACS+ Protocol. [https://www.rfc-editor.org/rfc/rfc8907](https://www.rfc-editor.org/rfc/rfc8907)
- RFC 2865 — Remote Authentication Dial In User Service (RADIUS). [https://www.rfc-editor.org/rfc/rfc2865](https://www.rfc-editor.org/rfc/rfc2865)
- RFC 2866 — RADIUS Accounting. [https://www.rfc-editor.org/rfc/rfc2866](https://www.rfc-editor.org/rfc/rfc2866)

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
| SEC-005 | Encryption Standards & PKI | EAP-TLS uses certificates for 802.1X |
| SEC-006 | Network Segmentation & DMZ | Management plane separation |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | AAA server reachability |
| SEC-001 | Access Control Lists | ACL permits management traffic to AAA server |
| SV-004 | NTP | Accurate timestamps for accounting records |
<!-- XREF-END -->
