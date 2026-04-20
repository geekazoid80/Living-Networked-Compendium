---
id: SV-002
title: "DHCP — Dynamic Host Configuration Protocol"
description: "How DHCP automatically assigns IP addresses and network configuration to hosts using the DORA exchange."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 35
prerequisites:
  - IP-001
  - SV-001
learning_path_tags:
  - DNE
difficulty: beginner
tags:
  - dhcp
  - services
  - ip-addressing
  - layer7
created: 2026-04-19
updated: 2026-04-19
---

# SV-002 — DHCP — Dynamic Host Configuration Protocol

## The Problem

A new laptop joins the office network. It has no IP address. You need to assign one — and also tell it the subnet mask, the default gateway, the DNS server, and the NTP server. If you do this manually for every device, you need an IP address inventory, a process, and someone to do it. When the gateway changes, you update hundreds of devices.

### Step 1: Let the device ask

The laptop broadcasts a message: "I have no address. Does anyone have one for me?" A server hears this and replies with a proposed address, a lease duration, and all the configuration parameters the laptop needs. The laptop accepts. Done in milliseconds, no administrator required.

### Step 2: Leases, not permanent assignments

The server gives addresses as **leases** — time-limited assignments. When a device leaves the network and doesn't renew, the lease expires and the address returns to the pool. The pool serves a dynamic population without running out of addresses.

### Step 3: What if the server is on a different subnet?

Broadcasts don't cross routers. A DHCP server on one subnet can't hear a broadcast from a laptop on another subnet. A **relay agent** on the router listens for broadcasts, wraps them in a unicast packet with the client's subnet information, and forwards them to the DHCP server. The server uses the relay information to pick the right address pool and reply.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Device asking for an address | DHCP client |
| Server assigning addresses | DHCP server |
| Time-limited address assignment | DHCP lease |
| Router forwarding DHCP across subnets | DHCP relay agent |
| The four-message exchange | DORA (Discover, Offer, Request, Acknowledge) |

---

## Learning Objectives

After completing this module you will be able to:

1. Describe the DORA exchange and what each message does.
2. Explain what a DHCP lease is and how renewal works.
3. Describe the role of a DHCP relay agent.
4. List the common DHCP options and their purpose.
5. Configure a basic DHCP server and relay on router platforms.
6. Troubleshoot common DHCP failures using debug and show commands.

---

## Prerequisites

- IP-001 — IP Addressing Fundamentals
- SV-001 — DNS (DHCP provides DNS server address as an option)

---

## Core Content

### The DORA Exchange

DHCP uses **UDP** — DISCOVER and REQUEST are broadcasts (dst 255.255.255.255, src 0.0.0.0); OFFER and ACK are unicast to the client's MAC (or broadcast if the client requests it).

```
Client                              DHCP Server
  |                                      |
  |--- DISCOVER (broadcast) ---------->  |  "I need an address"
  |                                      |
  |<-- OFFER (unicast/broadcast) ------- |  "Here's 192.168.1.50, lease 24h"
  |                                      |
  |--- REQUEST (broadcast) ----------->  |  "I'd like that address"
  |                                      |
  |<-- ACK (unicast/broadcast) --------- |  "It's yours for 24 hours"
  |                                      |
```

- **DISCOVER:** Client has no IP. Sends broadcast on UDP port 68 (src) to port 67 (dst). Contains client MAC address.
- **OFFER:** Server reserves the address and offers it. Contains: offered IP, subnet mask, lease time, server IP, options.
- **REQUEST:** Client broadcasts acceptance (broadcast so other DHCP servers know the offer was not accepted). Contains the server identifier of the chosen server.
- **ACK:** Server confirms the lease. Client now configures its interface.

If the address is already in use (server's conflict detection fails), the client sends **DECLINE** and the process restarts. When a client leaves gracefully, it sends **RELEASE**.

### Lease Renewal

A lease does not expire without warning:

- At **50% of lease time (T1):** Client sends a unicast RENEW to the original DHCP server. If the server responds with ACK, the lease is extended.
- At **87.5% of lease time (T2):** If renewal failed, client broadcasts a REBIND to any DHCP server. First server to respond wins.
- At **100% (expiry):** If still no ACK, the client releases the address and restarts DORA.

### DHCP Options

DHCP delivers configuration via **options** — numbered fields in the DHCP packet. Common options:

| Option | Name | Description |
|---|---|---|
| 1 | Subnet Mask | Client's subnet mask |
| 3 | Router | Default gateway IP(s) |
| 6 | DNS Servers | Up to 8 DNS server IPs |
| 12 | Hostname | Client's hostname |
| 15 | Domain Name | DNS search domain |
| 42 | NTP Servers | Time server IPs |
| 51 | Lease Time | Duration in seconds |
| 52 | Option Overload | Options in sname/file fields |
| 53 | DHCP Message Type | Identifies DISCOVER/OFFER/REQUEST/ACK etc |
| 54 | Server Identifier | DHCP server's IP |
| 61 | Client Identifier | Usually MAC address |
| 82 | Relay Agent Information | Added by relay agents (see below) |
| 121 | Classless Static Routes | Routes pushed to client (RFC 3442) |

### DHCP Relay Agent (Option 82)

Routers configured as relay agents listen for DHCP broadcasts on their interfaces and forward them as unicast to a configured DHCP server. The relay agent adds **Option 82** to the forwarded packet:

- **Circuit ID:** Identifies the interface/VLAN the client connected to.
- **Remote ID:** Usually the relay agent's MAC or hostname.

The DHCP server uses Option 82 to:
- Select the correct address pool (the client is in VLAN 10 → assign from the 192.168.10.0/24 pool).
- Implement per-port or per-VLAN policies.

The relay agent forwards the server's reply back to the client on the originating interface.

### DHCP Conflict Detection

Before offering an address, the server may **ping** it to verify it's unused (RFC 2131 recommends this). Conflict detection adds latency but prevents duplicate IP assignments when stale leases or static assignments overlap the pool.

Some platforms use **ARP** instead of ICMP for conflict detection. Clients also perform conflict detection after receiving an ACK using **ARP probing** (RFC 5227).

### DHCPv6

DHCPv6 (RFC 3315/RFC 8415) provides IPv6 address assignment to complement SLAAC. The exchange uses **Solicit / Advertise / Request / Reply** (SARR) — analogous to DORA. DHCPv6 uses link-local multicast (FF02::1:2) on UDP port 547 (server) / 546 (client).

DHCPv6 can operate in:
- **Stateful mode:** Server assigns addresses and records state (full DHCPv6).
- **Stateless mode (SLAAC + DHCPv6):** SLAAC provides the address; DHCPv6 provides only configuration options (DNS, NTP) without tracking address state.

See IP-003 for SLAAC/DHCPv6 interplay.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! DHCP Server
    ip dhcp excluded-address 192.168.10.1 192.168.10.10
    ip dhcp pool VLAN10
     network 192.168.10.0 255.255.255.0
     default-router 192.168.10.1
     dns-server 8.8.8.8 8.8.4.4
     domain-name example.com
     lease 1                      ! 1 day

    ! DHCP Relay on router interface
    interface GigabitEthernet0/1
     ip helper-address 10.0.0.1   ! DHCP server IP

    ! Verification
    show ip dhcp binding
    show ip dhcp pool
    debug ip dhcp server events
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_dhcp/configuration/xe-17/dhcp-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_dhcp/configuration/xe-17/dhcp-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # DHCP local server
    set system services dhcp-local-server interface ge-0/0/1.0

    set access address-assignment pool VLAN10 family inet network 192.168.10.0/24
    set access address-assignment pool VLAN10 family inet range CLIENT-RANGE low 192.168.10.11
    set access address-assignment pool VLAN10 family inet range CLIENT-RANGE high 192.168.10.254
    set access address-assignment pool VLAN10 family inet dhcp-attributes router 192.168.10.1
    set access address-assignment pool VLAN10 family inet dhcp-attributes name-server [8.8.8.8 8.8.4.4]
    set access address-assignment pool VLAN10 family inet dhcp-attributes maximum-lease-time 86400

    # DHCP relay
    set forwarding-options helpers bootp server 10.0.0.1

    # Verification
    show dhcp server binding
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/dhcp/topics/topic-map/dhcp-overview.html](https://www.juniper.net/documentation/us/en/software/junos/dhcp/topics/topic-map/dhcp-overview.html)

=== "MikroTik RouterOS"

    ```
    # DHCP Server (quick setup)
    /ip dhcp-server setup
    # Interactive — select interface, address pool, gateway, DNS, lease time

    # Manual setup
    /ip pool add name=VLAN10-POOL ranges=192.168.10.11-192.168.10.254
    /ip dhcp-server add name=VLAN10 interface=vlan10 address-pool=VLAN10-POOL lease-time=1d
    /ip dhcp-server network add address=192.168.10.0/24 gateway=192.168.10.1 dns-server=8.8.8.8,8.8.4.4

    # DHCP Relay
    /ip dhcp-relay add name=RELAY interface=vlan10 dhcp-server=10.0.0.1 local-address=192.168.10.1

    # Verification
    /ip dhcp-server lease print
    /ip dhcp-server print stats
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/DHCP](https://help.mikrotik.com/docs/display/ROS/DHCP)

---

## Common Pitfalls

1. **Forgetting to exclude static-IP addresses from the DHCP pool.** If a router gateway (192.168.10.1) is within the pool range and not excluded, DHCP may offer it to a client — causing a duplicate IP. Always exclude all static addresses before the pool starts.

2. **Relay agent not configured or pointed at wrong DHCP server.** Clients in a different subnet never receive a response. Verify with `debug ip dhcp server events` on the server and check that the relay interface has `ip helper-address` pointing to the correct server.

3. **DHCP Snooping dropping relayed packets with Option 82.** When DHCP Snooping is enabled, packets arriving on untrusted ports with Option 82 already set may be dropped. Disable the Option 82 validation check if relay agents legitimately insert it: `no ip dhcp snooping information option` (Cisco).

4. **Pool exhaustion.** A pool sized for the subnet (e.g., /24 = 254 addresses, lease 24h) may exhaust if many short-lived devices (phones, IoT) join without releasing. Shorten lease times for high-churn pools, or size the pool generously.

5. **Rogue DHCP servers.** Any device can run a DHCP server. A rogue server responding faster than the legitimate server can assign wrong gateways (routing all traffic through the attacker). Mitigate with DHCP Snooping (SW-005).

---

## Practice Problems

**Q1.** A DHCP client sends a DISCOVER. Two servers respond with OFFERs. What does the client do?

??? answer
    The client selects one offer (typically the first one received) and sends a broadcast REQUEST including the server identifier (Option 54) of the chosen server. The other server sees the REQUEST, recognises its offer was not selected, and releases the reserved address back to its pool.

**Q2.** A client has a 24-hour lease. When does it first attempt to renew?

??? answer
    At T1 = 50% of lease time = 12 hours. It sends a unicast RENEW to the original DHCP server. If no response by T2 (87.5% = 21 hours), it broadcasts a REBIND to any available server.

**Q3.** A client on VLAN 20 (192.168.20.0/24) receives DHCP from a server on VLAN 1 (10.0.0.1). How does this work?

??? answer
    The router has a DHCP relay agent (ip helper-address 10.0.0.1) on the VLAN 20 interface. It intercepts the client's broadcast DISCOVER and forwards it as a unicast to the DHCP server. The relay adds Option 82 with the VLAN 20 circuit ID. The server uses this to select the 192.168.20.0/24 pool and replies. The relay forwards the reply back to the client.

**Q4.** Why does a client send a broadcast REQUEST after receiving an OFFER, rather than a unicast directly to the server?

??? answer
    Because other DHCP servers in the broadcast domain may have also sent OFFERs and are holding reserved addresses waiting for the client to accept. A broadcast REQUEST allows all servers to see which one was selected, so the others can release their holds. A unicast would leave those reserved addresses locked unnecessarily.

---

## Summary & Key Takeaways

- DHCP automatically assigns IP addresses and configuration via the **DORA** (Discover, Offer, Request, Acknowledge) exchange.
- Addresses are **leased** for a configured duration — clients renew at 50% (T1) and 87.5% (T2) of lease time.
- DHCP options deliver subnet mask, default gateway, DNS servers, NTP, domain name, and more.
- **Relay agents** forward DHCP broadcasts across subnet boundaries — required in any routed environment.
- Option 82 carries relay agent information — used by servers to select the correct pool.
- **DHCP Snooping** (SW-005) prevents rogue DHCP servers and builds binding tables for DAI.
- DHCPv6 provides the same service for IPv6, complementing SLAAC.

---

## Where to Next

- **SV-003 — NAT & PAT:** DHCP assigns private IPs; NAT translates them to reach the internet.
- **SW-005 — Port Security & DAI:** DHCP Snooping and Dynamic ARP Inspection.
- **PROTO-010 — DHCP Deep Dive:** Full DHCP option set, LDAP integration, failover.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2131 | DHCP for IPv4 |
| RFC 2132 | DHCP Options and BOOTP Vendor Extensions |
| RFC 3442 | Classless Static Route Option (Option 121) |
| RFC 8415 | DHCPv6 (replaces RFC 3315) |
| Cisco CCNA | DHCP server, relay, troubleshooting |
| CompTIA Network+ | DHCP concepts, DORA exchange |

---

## References

- RFC 2131 — Dynamic Host Configuration Protocol. [https://www.rfc-editor.org/rfc/rfc2131](https://www.rfc-editor.org/rfc/rfc2131)
- RFC 2132 — DHCP Options and BOOTP Vendor Extensions. [https://www.rfc-editor.org/rfc/rfc2132](https://www.rfc-editor.org/rfc/rfc2132)
- RFC 8415 — Dynamic Host Configuration Protocol for IPv6. [https://www.rfc-editor.org/rfc/rfc8415](https://www.rfc-editor.org/rfc/rfc8415)

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
| SW-005 | Port Security & DAI | DHCP Snooping uses DHCP binding table |
| SV-003 | NAT & PAT | DHCP assigns private IPs that NAT translates |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | DHCP assigns IP addresses from configured pools |
| SV-001 | DNS | DHCP delivers DNS server address as Option 6 |
| SW-005 | Port Security & DAI | DHCP Snooping depends on this module |
<!-- XREF-END -->
