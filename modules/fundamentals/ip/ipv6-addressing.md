---
title: "IPv6 Addressing"
module_id: "IP-003"
domain: "fundamentals/ip"
difficulty: "intermediate"
prerequisites: ["IP-001", "IP-002", "NW-001"]
estimated_time: 50
version: "1.0"
last_updated: "2026-04-17"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["ipv6", "addressing", "slaac", "ndp", "icmpv6", "dual-stack", "global-unicast", "link-local", "eui-64", "prefix"]
cert_alignment: "CCNA 200-301 - 1.8 | JNCIA-Junos JN0-103 | Nokia NRS I"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "Arista EOS", "Huawei VRP", "MikroTik RouterOS"]
language: "en"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** why IPv6 was necessary and what IPv4 limitation it solves
2. **Read and write** IPv6 addresses in both full and compressed notation, and expand a compressed address back to full form
3. **Describe** the structure of an IPv6 address - prefix, subnet ID, and interface ID - and apply /64 subnetting
4. **Identify** the major IPv6 address types (global unicast, link-local, loopback, ULA, multicast, anycast) by their prefix
5. **Explain** how NDP replaces ARP and how SLAAC enables stateless autoconfiguration
6. **Compare** dual-stack, tunnelling, and translation as IPv4/IPv6 coexistence strategies

---
## Prerequisites

- [IP Addressing Fundamentals](ip-addressing.md) (`IP-001`) - binary and hex notation, network vs host portions, subnet masks
- [IP Subnetting & VLSM](subnetting.md) (`IP-002`) - prefix length, CIDR notation, address carving
- [The OSI Model](../networking/osi-model.md) (`NW-001`) - Layer 3 context; what "network layer addressing" means

---
## The Problem

Two network architects in 1993 are designing an addressing plan. Their company has 500 devices - servers, workstations, printers. IPv4 works perfectly. Each device gets a 32-bit address. Everything connects. Life is good.

### Step 1: The address pool runs dry

The internet grows. Every phone, laptop, camera, smart meter, and industrial sensor wants an address. At 32 bits, IPv4 can express 4,294,967,296 unique values - just over four billion. That sounds enormous until you account for 8 billion people, each owning multiple devices, and billions of infrastructure nodes. The Regional Internet Registries began handing out their last address blocks in the 2010s.

The fix is obvious: make the address longer. But how long? The engineers designing the next version ask: what if every grain of sand on earth could have its own address, with room to spare? They settle on **128 bits**. That yields 2¹²⁸ - approximately **340 undecillion** addresses (3.4 × 10³⁸). The address shortage problem is solved for the foreseeable future. This decision is the foundation of IPv6.

### Step 2: 128 bits is unreadable

A 128-bit number in decimal notation runs to 39 digits. Nobody wants to type that. The designers agree on a compact notation: break the 128 bits into **8 groups of 16 bits**, write each group as **4 hexadecimal digits**, and separate groups with **colons**.

```text
2001:0db8:0000:0042:0000:8a2e:0370:7334
```

Eight groups. Four hex digits each. 32 hex characters plus 7 colons. This is the IPv6 address format.

### Step 3: Zeros everywhere

Most IPv6 addresses have long runs of zeros - especially in early deployment, where addresses are carefully allocated from structured prefixes. Writing every zero is tedious and error-prone. Two compression rules clean this up:

1. **Drop leading zeros** within any group: `0db8` → `db8`, `0042` → `42`, `0000` → `0`
2. **Collapse one consecutive run** of all-zero groups with `::` - used at most once per address

So `2001:0db8:0000:0000:0000:0000:0000:0001` compresses to `2001:db8::1`. A loopback address that is 127 zero bits followed by a one becomes simply `::1`.

### Step 4: ARP shouts at everyone

With IPv4, when a device needs a MAC address to match an IP, it broadcasts "**Who has 192.168.1.5?**" - a frame delivered to every device on the segment. Every device wakes up, reads the question, most discard it. We saw in NW-002 that broadcast storms are a real cost. Can IPv6 resolve addresses without shouting at everyone?

Yes. IPv6 uses **ICMPv6 Neighbor Discovery Protocol (NDP)**. Instead of a broadcast, a device sends a Neighbor Solicitation to a specific **solicited-node multicast address** - a special multicast group derived from the last 24 bits of the target's IPv6 address. Only the device (or devices) sharing that address suffix receive the message. Everyone else ignores it. ARP is gone; NDP replaces it with multicast precision.

### Step 5: Someone has to hand out addresses

With IPv4, a DHCP server tracks which address goes to which device, assigns leases, and renews them. It works - but it requires infrastructure to deploy and maintain. As networks grow to millions of addresses, can devices configure themselves without a server?

In IPv6, they can. A router periodically sends **Router Advertisement (RA)** messages announcing the local network prefix - for example, `2001:db8:1::/64`. A device that receives this takes the /64 prefix from the router and appends its own **64-bit interface identifier**, generated from its MAC address using a process called **EUI-64**. The result is a globally unique, self-configured IPv6 address - no server required. This is **SLAAC: Stateless Address Autoconfiguration**.

### What You Just Built

IPv6 - a 128-bit addressing scheme with hexadecimal colon notation, compression rules, multicast-based neighbour discovery, and stateless autoconfiguration.

| Scenario element | Technical term |
|---|---|
| 128-bit address space | IPv6 (Internet Protocol version 6) |
| 8 groups of 4 hex digits, separated by colons | Colon-hexadecimal notation |
| Drop leading zeros; collapse zero runs to `::` | IPv6 address compression |
| Targeted multicast instead of broadcast for address resolution | ICMPv6 / Neighbor Discovery Protocol (NDP) |
| Prefix from router + MAC-derived suffix | SLAAC (Stateless Address Autoconfiguration) |
| Derived interface identifier from MAC address | EUI-64 |

---
## Core Content

### Address Format and Notation

An IPv6 address is **128 bits**, written as **8 groups of 16 bits**, each expressed in **4 hexadecimal digits**, separated by colons.

```text
Full form:   2001:0db8:0000:0001:0000:0000:0000:0001
             ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑
           G1   G2   G3   G4   G5   G6   G7   G8
           (each group = 16 bits = 4 hex digits)
```

**Compression rules** - both may be applied together:

| Rule | Before | After |
|---|---|---|
| Drop leading zeros within a group | `0db8` | `db8` |
| Replace one consecutive run of all-zero groups with `::` | `0000:0000:0000` | `::` |

The `::` shorthand can appear **only once** per address. If two separate zero runs exist, collapse only the longer one (break ties by choosing the leftmost).

```text
Full:    2001:0db8:0000:0001:0000:0000:0000:0001
Step 1:  2001:db8:0:1:0:0:0:1        (drop leading zeros)
Step 2:  2001:db8:0:1::1             (collapse longest zero run — 3 groups)
```

**Expanding a compressed address** - reverse the process:

1. Find `::`. Count the groups present. The `::` represents (8 − groups present) × all-zero 16-bit groups.
2. Insert the missing `0000` groups where `::` appears.
3. Add leading zeros to any short group.

```text
Compressed:  2001:db8::1
Groups shown: 2001, db8, 1  →  3 groups
::  represents: 8 - 3 = 5 zero groups
Full:        2001:0db8:0000:0000:0000:0000:0000:0001
```

### Address Structure

Every IPv6 address has a three-part structure when /64 is the standard subnet boundary:

```text
| ←——————— Network Prefix ————————→ | ←— Subnet ID —→ | ←——— Interface ID ———→ |
  (global routing prefix)              (site subnetting)   (host identifier)
  typically /32–/48                    16 bits             64 bits
  assigned by ISP or RIR               you allocate        device generates

Example — /48 to org, /64 to subnet:
  2001:0db8:1234:0001:0000:0000:0000:0001/64
  ↑ Global prefix  ↑ Subnet  ↑ Interface ID
  2001:db8:1234    :0001     :0000:0000:0000:0001
```

**Standard allocation depths:**

| Allocation | Typical prefix | How many subnets downstream |
|---|---|---|
| RIR to ISP | /32 | - |
| ISP to organisation | /32–/48 | - |
| Organisation to site | /48 | 2¹⁶ = 65,536 /64 subnets |
| Site to end subnet | /64 | 2⁶⁴ host addresses per subnet |
| Single host/loopback | /128 | One address |

The **interface ID is always 64 bits** in standard SLAAC addressing. This is why /64 is the standard subnet prefix length - it splits the address space exactly in half: 64 bits for routing, 64 bits for the host.

??? supplementary "EUI-64: Deriving the Interface ID from a MAC Address"
    SLAAC needs a unique 64-bit interface ID. The standard method (RFC 4291) derives it from the device's 48-bit MAC address using EUI-64:

    1. Split the MAC at the midpoint: `AA:BB:CC` | `DD:EE:FF`
    2. Insert `FF:FE` in the middle: `AA:BB:CC:FF:FE:DD:EE:FF`
    3. Flip bit 7 (the Universal/Local bit) of the first byte - this inverts the "globally unique" sense from MAC to EUI-64 convention

    Example:
    ```text
    MAC:          00:50:56:C0:00:01
    Split:        00:50:56 | C0:00:01
    Insert FF:FE: 00:50:56:FF:FE:C0:00:01
    Flip bit 7:   02:50:56:FF:FE:C0:00:01   (0x00 → 0x02)
    Interface ID: 0250:56FF:FEC0:0001
    ```

    This means a device's SLAAC address reveals its MAC address - a privacy concern. RFC 4941 (Privacy Extensions) generates a random, time-limited interface ID for outbound connections instead. Most modern operating systems (Windows, macOS, Linux) enable privacy extensions by default. You may see multiple addresses per interface: one stable (EUI-64) and one or more temporary (privacy extensions).

### IPv6 Address Types

IPv6 has **no broadcast**. Specific address types serve specific roles, and multicast replaces all broadcast use cases.

| Type | Prefix | Scope | Purpose |
|---|---|---|---|
| **Global unicast** | `2000::/3` | Global internet | Routable addresses - equivalent of public IPv4 |
| **Link-local** | `fe80::/10` | Single link only | Auto-configured on every interface; used for NDP and routing protocols |
| **Loopback** | `::1/128` | Host only | Equivalent to `127.0.0.1`; always present |
| **Unique Local (ULA)** | `fc00::/7` (typically `fd00::/8`) | Organisation | Equivalent to RFC 1918 private space; not globally routable |
| **Multicast** | `ff00::/8` | Scope-dependent | One-to-many; replaces broadcast |
| **Anycast** | From unicast space | Routing | Same address on multiple nodes; packet goes to nearest |
| **Unspecified** | `::/128` | - | Equivalent to `0.0.0.0`; source before assignment |

**Key rule:** Every IPv6-enabled interface has **at least two addresses**:
1. A **link-local** address (`fe80::...`) - auto-configured, never forwarded beyond the link
2. A **global unicast** or **ULA** address - used for inter-network communication

```text
Link-local prefix:  FE80::/10
                    1111 1110 10xx xxxx  (remaining 54 bits = 0; last 64 = interface ID)

Multicast prefix:   FF00::/8
                    1111 1111  (first 8 bits)
                    ↑ followed by 4 flag bits, 4 scope bits, then 112-bit group ID
```

??? supplementary "Multicast Scopes in IPv6"
    The third byte of a multicast address encodes the **scope** - how far the multicast travels:

    | Scope value | Name | What it means |
    |---|---|---|
    | `1` | Interface-local | Loopback only |
    | `2` | Link-local | Single link (`ff02::`) |
    | `5` | Site-local | Organisation (deprecated) |
    | `8` | Organisation-local | Within an organisation |
    | `e` | Global | Internet-wide |

    Well-known link-local multicast addresses (`ff02::`):

    | Address | Purpose |
    |---|---|
    | `ff02::1` | All nodes on the link |
    | `ff02::2` | All routers on the link |
    | `ff02::5` | All OSPF routers |
    | `ff02::6` | OSPF designated routers |
    | `ff02::9` | All RIP routers |
    | `ff02::1:2` | All DHCPv6 relay agents and servers |
    | `ff02::1:ff00:0/104` | Solicited-node multicast (NDP) |

### ICMPv6 and Neighbor Discovery Protocol (NDP)

NDP (RFC 4861) replaces both ARP and several ICMP router-discovery functions from IPv4. It uses five ICMPv6 message types.

| NDP Message | ICMPv6 Type | Replaces | Purpose |
|---|---|---|---|
| Router Solicitation (RS) | 133 | - | Host asks: "Is there a router here?" |
| Router Advertisement (RA) | 134 | - | Router announces prefix, gateway, flags |
| Neighbor Solicitation (NS) | 135 | ARP Request | "Who has this IPv6 address?" (sent to solicited-node multicast) |
| Neighbor Advertisement (NA) | 136 | ARP Reply | "I have that address; here is my MAC" |
| Redirect | 137 | ICMP Redirect | Router tells host of a better next-hop |

**How address resolution works - replacing ARP:**

```text
Host A wants to reach Host B (2001:db8::1:100):

1. Derive solicited-node multicast:
   ff02::1:ff + last 24 bits of target  →  ff02::1:ff01:0100
2. Host A sends Neighbor Solicitation to ff02::1:ff01:0100
   Only Host B (and any others sharing that 24-bit suffix) receive it
3. Host B replies with Neighbor Advertisement to Host A's address
   NA includes Host B's MAC address
4. Host A stores the mapping in its Neighbor Cache (equivalent of the ARP table)
```

**How SLAAC works - step by step:**

```text
1. Interface comes up
   → Auto-generates link-local: fe80:: + EUI-64 interface ID
   → Performs DAD (Duplicate Address Detection) on the link-local

2. Sends Router Solicitation to ff02::2 (all routers):
   "Any routers on this link?"

3. Router replies with Router Advertisement containing:
   - Network prefix (e.g. 2001:db8:1::/64)
   - M flag: 0 = use SLAAC for address, 1 = use DHCPv6
   - O flag: 1 = use DHCPv6 for other options (DNS, domain)
   - Default router lifetime and preferences

4. Host appends its EUI-64 interface ID to the prefix:
   2001:db8:1:: + 0250:56ff:fec0:0001 = 2001:db8:1:0:250:56ff:fec0:1

5. Performs DAD on the new global unicast address
   → If no Neighbor Advertisement received: address is unique, assigned
   → If NA received: collision, generate new address (RFC 4941 random)
```

??? supplementary "Duplicate Address Detection (DAD)"
    Before using any new IPv6 address (including link-local), a node confirms the address is not already in use. It sends a Neighbor Solicitation with:
    - Source: `::/128` (unspecified - the node doesn't yet own the address)
    - Destination: the solicited-node multicast of the tentative address

    If no Neighbor Advertisement returns within a timeout (default: 1 second, up to RetransTimer), the address is considered unique and assigned.

    DAD applies to all new addresses: link-local, SLAAC-generated global unicast, statically configured, and DHCPv6-assigned. If you see an address stuck in "tentative" state, another device on the link already owns it.

### Address Assignment Methods

| Method | Server required? | Address source | Control |
|---|---|---|---|
| **Static** | No | Manual configuration | Full manual control; predictable |
| **SLAAC** | No (RA from router) | Prefix from RA + EUI-64 | Device generates its own; no tracking |
| **DHCPv6 Stateless** | Yes (options only) | SLAAC address + DHCPv6 for DNS/domain | Middle ground |
| **DHCPv6 Stateful** | Yes | DHCPv6-assigned address | Full server-side tracking; like IPv4 DHCP |

The RA's **M bit** (Managed) and **O bit** (Other) control host behaviour:

| M bit | O bit | Host behaviour |
|---|---|---|
| 0 | 0 | SLAAC only - no DHCPv6 |
| 0 | 1 | SLAAC for address; DHCPv6 for other options (DNS) |
| 1 | 0 | DHCPv6 stateful for address; no other options |
| 1 | 1 | DHCPv6 stateful for address and options |

### IPv4 and IPv6 Coexistence

The internet does not switch overnight. Three transition strategies exist:

**1. Dual-stack** - run both IPv4 and IPv6 simultaneously on every device and link

- Each interface has both an IPv4 and IPv6 address
- Applications prefer IPv6 where available (RFC 6724 address selection - "Happy Eyeballs")
- Both protocol stacks must be managed, secured, and monitored
- The current standard approach for enterprise and ISP networks

**2. Tunnelling** - carry IPv6 packets inside IPv4 (or vice versa)

- Used to cross IPv4-only segments
- Common mechanisms: 6in4 (static, explicit endpoints), 6rd (ISP-deployed), ISATAP (intranet)
- Adds header overhead; complicates troubleshooting (packets within packets)
- Used where upgrading the underlying network is not yet practical

**3. Translation** - convert between IPv4 and IPv6 at the boundary

- **NAT64**: maps IPv6 client requests to an IPv4 address for IPv4-only servers
- **DNS64**: synthesises AAAA records for A-only names so IPv6-only clients can reach IPv4-only servers
- Breaks end-to-end transparency; problematic for applications that embed IP addresses in payloads

??? supplementary "Address Selection - Why IPv6 is Preferred on Dual-Stack Hosts"
    When a dual-stack host has both an IPv4 and IPv6 address for a destination, RFC 6724 defines the default address selection algorithm. The general preference: IPv6 global unicast is ranked above IPv4-mapped addresses. In practice, when both A and AAAA DNS records exist, the OS typically connects over IPv6 first.

    This is why working IPv6 connectivity is critical before advertising AAAA records. A broken IPv6 path causes connection failures even when IPv4 would work - the client tries IPv6 first and waits for a timeout. RFC 8305 (Happy Eyeballs v2) mitigates this by racing IPv4 and IPv6 connections with a 250 ms stagger, but not all clients implement it fully.

---
## Vendor Implementations

The IPv6 address structure and NDP behaviour are standardised in RFC 8200 and RFC 4861. All compliant implementations share the same address notation, NDP message types, and SLAAC behaviour. Differences below are syntactic.

!!! success "Standard - RFC 8200 (IPv6), RFC 4861 (NDP), RFC 4862 (SLAAC)"
    Any RFC-compliant implementation produces interoperable neighbour discovery, SLAAC, and address resolution. Vendor configuration differences are syntactic only.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Enable IPv6 routing globally (required before any interface forwards IPv6 or sends RAs)
    ipv6 unicast-routing

    ! Configure a global unicast address on an interface
    interface GigabitEthernet0/0
     ipv6 address 2001:db8:1::1/64
     ipv6 enable
     no shutdown

    ! Verify
    show ipv6 interface brief
    show ipv6 neighbors
    ```
    Link-local addresses are auto-generated when `ipv6 enable` is applied; no explicit configuration needed. Without `ipv6 unicast-routing`, the router will not forward IPv6 packets or send Router Advertisements.

    Full configuration reference: [Cisco IOS IPv6 Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipv6_basic/configuration/xe-16/ip6b-xe-16-book.html)

=== "Juniper Junos"
    ```junos
    # Configure IPv6 on an interface
    set interfaces ge-0/0/0 unit 0 family inet6 address 2001:db8:1::1/64

    # Verify
    show ipv6 neighbors
    show interfaces ge-0/0/0 detail
    ```
    Junos activates IPv6 forwarding automatically when an `inet6` family is configured on an interface. No global `ipv6 unicast-routing` equivalent is required.

    Full configuration reference: [Juniper IPv6 User Guide](https://www.juniper.net/documentation/us/en/software/junos/interfaces-fundamentals/topics/concept/ipv6-overview.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # Configure IPv6 on a router interface (classic CLI)
    configure router interface "to-core" ipv6 address 2001:db8:1::1/64
    configure router interface "to-core" no shutdown

    # Verify
    show router neighbor
    show router interface "to-core" detail
    ```
    SR-OS requires explicit IPv6 configuration under each router or VPRN interface. IPv6 forwarding is enabled per-instance, not globally.

    Full configuration reference: [Nokia SR-OS Layer 3 Services Guide](https://documentation.nokia.com/sr/)

=== "Arista EOS"
    ```arista-eos
    ! Configure IPv6 on an interface
    interface Ethernet1
     ipv6 address 2001:db8:1::1/64
     no shutdown

    ! Verify
    show ipv6 neighbors
    show ipv6 interface Ethernet1
    ```
    Arista EOS enables IPv6 forwarding automatically when an IPv6 address is configured. Syntax is similar to Cisco IOS-XE.

    Full configuration reference: [Arista EOS IPv6 Configuration](https://www.arista.com/en/um-eos/eos-ipv6-address-configuration)

=== "Huawei VRP"
    ```huawei-vrp
    # Enable IPv6 globally
    ipv6

    # Configure IPv6 on an interface
    interface GigabitEthernet0/0/0
     ipv6 enable
     ipv6 address 2001:DB8:1::1 64
     undo shutdown

    # Verify
    display ipv6 neighbors
    display ipv6 interface brief
    ```
    Huawei VRP uses a **space** between address and prefix length (not a slash). The global `ipv6` command enables IPv6 forwarding.

    Full configuration reference: [Huawei VRP IPv6 Configuration](https://support.huawei.com/enterprise/en/doc/EDOC1100278578)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # Add an IPv6 address to an interface
    /ipv6 address add address=2001:db8:1::1/64 interface=ether1

    # Enable Router Advertisements for SLAAC
    /ipv6 nd add interface=ether1 advertise-dns=yes

    # Verify
    /ipv6 neighbor print
    /ipv6 address print
    ```
    RouterOS uses a flat command hierarchy under `/ipv6`. SLAAC is enabled by configuring neighbour discovery advertisements under `/ipv6 nd`. Link-local addresses are auto-generated when any global address is assigned.

    Full configuration reference: [MikroTik IPv6 Address Management](https://help.mikrotik.com/docs/display/ROS/IPv6+Addresses)

---
## Common Pitfalls

### Pitfall 1: Forgetting `ipv6 unicast-routing` on Cisco

On Cisco IOS-XE, an interface can have an IPv6 address but the router will not forward IPv6 packets or send Router Advertisements unless `ipv6 unicast-routing` is enabled globally. Symptom: hosts on the segment configure link-local addresses but never receive a global prefix via SLAAC; neighbours resolve but remote destinations are unreachable.

### Pitfall 2: Blocking ICMPv6 in the firewall

IPv6 relies on ICMPv6 for NDP and SLAAC. Firewalls that block all ICMP - carried over from IPv4 hardening habits - break IPv6 neighbour discovery entirely. Hosts cannot resolve MAC addresses, cannot perform DAD, and never receive Router Advertisements. At minimum, permit ICMPv6 types 133–137 (RS, RA, NS, NA, Redirect) inbound and outbound on all IPv6-enabled interfaces.

### Pitfall 3: Using `::` more than once

The `::` shorthand can appear only once per address. `2001:db8::1::2` is invalid - the parser cannot determine how many zero groups each `::` represents. Symptom: configuration is rejected or silently misinterpreted. When two separate zero runs exist, collapse only the longer one.

### Pitfall 4: Treating link-local addresses as routable

`fe80::` addresses are valid only on the link where they were configured. They cannot be forwarded by a router. Routing protocols (OSPFv3, BGP) use link-local addresses as the neighbour address - that is correct behaviour. But the **forwarding next-hop** for remote routes must be a global unicast address. Confusion here causes routes that form correctly but traffic that fails to forward.

### Pitfall 5: Treating ULA as globally routable

Unique Local Addresses (`fc00::/7`, typically `fd00::/8`) are the IPv6 equivalent of RFC 1918 private space. ISPs do not advertise them. If you configure ULA addresses expecting external reachability, traffic will be dropped at the internet boundary with no error visible to the source.

---
## Practice Problems

1. Write the full 128-bit form of the compressed address `2001:db8::cafe:1`. How many zero groups does `::` represent?

2. A router interface has MAC address `00:1A:2B:3C:4D:5E` and receives a Router Advertisement for the prefix `2001:db8:a1b2::/64`. What SLAAC address will the interface configure? Show the EUI-64 derivation step by step.

3. A network engineer is troubleshooting a host that has a link-local address (`fe80::1`) but no global unicast address, even though SLAAC should have completed. List three things to check, in order of most likely cause.

4. Your organisation has received the prefix `2001:db8:acad::/48` from your ISP. You need to allocate subnets for 12 sites, with each site needing up to 200 /64 host subnets. What prefix length do you assign per site? How many /64 subnets can each site support?

5. A dual-stack server has both A and AAAA DNS records. Users in a branch office report intermittent connection failures to this server. IPv4 connectivity to the server is confirmed working. What is the most likely cause, and what is the first diagnostic step?

??? "Answers"
    **1.** Groups in `2001:db8::cafe:1`: `2001`, `db8`, `cafe`, `1` = 4 groups present. `::` = 8 − 4 = **4 zero groups**.
    Full form: `2001:0db8:0000:0000:0000:0000:cafe:0001`

    **2.** MAC: `00:1A:2B:3C:4D:5E`
    - Split: `00:1A:2B` | `3C:4D:5E`
    - Insert FF:FE: `00:1A:2B:FF:FE:3C:4D:5E`
    - Flip bit 7 of first byte: `0x00` = `00000000` → flip bit 6 (U/L) → `00000010` = `0x02`
    - Interface ID: `021A:2BFF:FE3C:4D5E`
    - SLAAC address: `2001:db8:a1b2::21a:2bff:fe3c:4d5e`

    **3.** In order of most likely cause:
    1. **No router is sending RAs** - verify `ipv6 unicast-routing` is enabled; confirm RAs are being sent with `show ipv6 interface` or `debug ipv6 nd`
    2. **ICMPv6 blocked** - RA messages (type 134) are ICMPv6; a firewall or ACL may be dropping them before they reach the host
    3. **DAD failure** - the host attempted SLAAC but detected a duplicate; check the interface for "tentative" or "duplicate" state

    **4.** Allocate /56 per site (8 bits beyond the /48 gives 2⁸ = 256 ≥ 12 sites). Each /56 contains 2⁸ = **256 /64 subnets**, which exceeds the 200-subnet requirement per site.

    **5.** Most likely cause: the **IPv6 path to the server is broken** (routing gap, firewall, or misconfiguration), causing IPv6 connection attempts to time out. The intermittency occurs because the OS tries IPv6 first; Happy Eyeballs (RFC 8305) should race IPv4 and IPv6, but clients with poor implementations wait for the full IPv6 timeout before falling back.
    First diagnostic step: ping the server's IPv6 address directly from a branch client. If this fails while IPv4 ping succeeds, trace the IPv6 path to find the break.

---
## Lab

### Lab: Configure and Verify IPv6 Addressing with SLAAC

**Tools:** GNS3 (with Cisco IOS or Arista cEOS images) or Cisco Packet Tracer
**Estimated time:** 25 minutes
**Objective:** Configure global unicast IPv6 addresses on a router, observe SLAAC autoconfiguration on a host, and verify NDP neighbour resolution.

**Topology:**
```text
  [PC-A]                     [R1]                     [PC-B]
  GigE0/0                GigE0/0  GigE0/1             GigE0/0
  SLAAC                  ::1/64    ::1/64              SLAAC
  2001:db8:1::/64  ←————————————————————→  2001:db8:2::/64
```

**Steps:**

1. Enable IPv6 routing on R1 and configure both interfaces:

    ```cisco-ios
    ipv6 unicast-routing

    interface GigabitEthernet0/0
     ipv6 address 2001:db8:1::1/64
     ipv6 enable
     no shutdown

    interface GigabitEthernet0/1
     ipv6 address 2001:db8:2::1/64
     ipv6 enable
     no shutdown
    ```

2. Verify R1 has both link-local and global unicast addresses on each interface:

    ```text
    R1# show ipv6 interface brief
    GigabitEthernet0/0     [up/up]
      FE80::...            link-local
      2001:DB8:1::1        global unicast
    GigabitEthernet0/1     [up/up]
      FE80::...            link-local
      2001:DB8:2::1        global unicast
    ```

3. On PC-A (simulated as a second router acting as host), configure the interface for SLAAC:

    ```cisco-ios
    interface GigabitEthernet0/0
     ipv6 address autoconfig
     no shutdown
    ```

4. Verify PC-A received a global unicast address from SLAAC:

    ```text
    PC-A# show ipv6 interface GigabitEthernet0/0
    IPv6 is enabled, link-local address is FE80::...
    Global unicast address(es):
      2001:DB8:1::xxxx:xxxx:xxxx:xxxx, subnet is 2001:DB8:1::/64 [EUI/CAL/PRE]
    ```

5. Check the NDP neighbour table on R1 and ping from PC-A to R1:

    ```text
    R1# show ipv6 neighbors
    IPv6 Address              Age Link-layer Addr State  Interface
    FE80::...                   0 aabb.cc00.0100  REACH  Gi0/0
    2001:DB8:1::xxxx:...        0 aabb.cc00.0100  REACH  Gi0/0

    PC-A# ping ipv6 2001:db8:1::1
    !!!!!
    ```

??? supplementary "Lab extension: Capture NDP packets in Wireshark"
    Enable a Wireshark capture on the PC-A - R1 link before bringing the interface up. Look for:
    - **Router Solicitation** (ICMPv6 type 133) from PC-A to `ff02::2`
    - **Router Advertisement** (ICMPv6 type 134) from R1 to `ff02::1`
    - **Neighbor Solicitation for DAD** (type 135, source = `::`)
    - **Neighbor Advertisement** (type 136) - absent if no collision

    Seeing these four exchanges in sequence gives an intuitive picture of how SLAAC and NDP work that no diagram fully replaces.

---
## Summary & Key Takeaways

- IPv6 uses **128-bit addresses** - 3.4 × 10³⁸ possible values - to solve IPv4 exhaustion
- Addresses are written as **8 groups of 4 hex digits** separated by colons; leading zeros can be dropped; one consecutive run of all-zero groups collapses to `::`
- To expand `::`: count groups shown, subtract from 8, and that many zero groups replace the `::`
- The standard host subnet is **/64** - 64 bits for the routing prefix, 64 bits for the interface ID
- IPv6 has **no broadcast** - multicast addresses serve every role that broadcast served in IPv4
- Every IPv6-enabled interface auto-configures a **link-local address** (`fe80::/10`) at startup
- **NDP** (RFC 4861) replaces ARP: Neighbor Solicitations go to a **solicited-node multicast** group, not to all hosts
- **SLAAC** lets a device build its own global unicast address from the router's RA prefix + its own EUI-64 interface ID - no DHCP server required
- **DAD** (Duplicate Address Detection) confirms uniqueness before any address is used
- The RA's M and O flags control whether hosts use SLAAC, DHCPv6, or both
- Transition strategies: **dual-stack** (both protocols simultaneously), **tunnelling** (IPv6 in IPv4), **translation** (NAT64/DNS64)
- **Never block ICMPv6** - it carries NDP, DAD, and SLAAC; blocking it silently breaks IPv6

---
## Where to Next

- **Continue:** [Routing Fundamentals](../routing/routing-fundamentals.md) (`RT-001`) - how packets cross network boundaries; IPv6 forwarding builds directly on this module
- **Related:** [IP Subnetting & VLSM](subnetting.md) (`IP-002`) - the prefix-length and address-carving principles extend directly to IPv6 allocation
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) - this module is Stage 3, position 16 in the DNE path

---
## Standards & Certifications

**Relevant standards:**
- [RFC 8200 - Internet Protocol, Version 6 (IPv6) Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4291 - IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- [RFC 4861 - Neighbor Discovery for IP version 6 (NDP)](https://www.rfc-editor.org/rfc/rfc4861)
- [RFC 4862 - IPv6 Stateless Address Autoconfiguration (SLAAC)](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 4193 - Unique Local IPv6 Unicast Addresses (ULA)](https://www.rfc-editor.org/rfc/rfc4193)
- [RFC 4941 - Privacy Extensions for Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4941)
- [RFC 6724 - Default Address Selection for IPv6](https://www.rfc-editor.org/rfc/rfc6724)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 1.8 - Configure and verify IPv6 addressing and prefix |
| JNCIA-Junos JN0-103 | Juniper | IPv6 basics; neighbour discovery |
| Nokia NRS I | Nokia | IPv6 addressing and configuration |
| Huawei HCIA-Datacom | Huawei | IPv6 addressing, NDP, and SLAAC |

---
## References

- IETF - [RFC 8200: Internet Protocol, Version 6 (IPv6) Specification](https://www.rfc-editor.org/rfc/rfc8200)
- IETF - [RFC 4291: IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- IETF - [RFC 4861: Neighbor Discovery for IP version 6](https://www.rfc-editor.org/rfc/rfc4861)
- IETF - [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- Odom, W. - *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2019 - Ch. 24–27 (IPv6 addressing and configuration)
- Doyle, J.; Carroll, J. - *Routing TCP/IP, Volume I*, 2nd ed., Cisco Press, 2005 - Ch. 8 (IPv6)

---
## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Draft written by Claude Sonnet 4.6. All RFC citations verified against IETF RFC index. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](../routing/routing-fundamentals.md) | Routing Fundamentals | IPv6 forwarding and next-hop resolution | 2026-04-17 |
| [RT-004](../routing/ospf-fundamentals.md) | OSPF Fundamentals | OSPFv3 uses IPv6 addressing | 2026-04-17 |
| [RT-007](../routing/bgp-fundamentals.md) | BGP Fundamentals | MP-BGP address family inet6 | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [NW-001](../networking/osi-model.md) | The OSI Model | Layer 3 framing; network layer addressing | 2026-04-17 |
| [NW-002](../networking/network-topologies.md) | Network Topologies | Broadcast domain concept; multicast vs broadcast | 2026-04-17 |
| [IP-001](ip-addressing.md) | IP Addressing Fundamentals | Binary/hex notation; network vs host portion | 2026-04-17 |
| [IP-002](subnetting.md) | IP Subnetting & VLSM | Prefix length and address carving | 2026-04-17 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | Arista EOS | Huawei VRP | MikroTik RouterOS |
|---|---|---|---|---|---|---|---|
| Enable IPv6 forwarding | RFC 8200 | `ipv6 unicast-routing` | Automatic (inet6 family) | Per-instance | Automatic | `ipv6` global cmd | Automatic |
| Configure interface address | RFC 8200 | `ipv6 address X/Y` | `family inet6 address X/Y` | `ipv6 address X/Y` | `ipv6 address X/Y` | `ipv6 address X Y` | `/ipv6 address add` |
| View NDP neighbour table | RFC 4861 | `show ipv6 neighbors` | `show ipv6 neighbors` | `show router neighbor` | `show ipv6 neighbors` | `display ipv6 neighbors` | `/ipv6 neighbor print` |
| Configure SLAAC (host) | RFC 4862 | `ipv6 address autoconfig` | `family inet6 address X/Y eui-64` | Automatic | `ipv6 address autoconfig` | Automatic | `/ipv6 nd add` |

### Maintenance Notes

- When NW-002 is updated, verify the multicast vs broadcast distinction referenced in Step 4 of The Problem remains consistent
- When RT-001 is written, add a back-reference there to this module for IPv6 forwarding context
- When RT-004 (OSPF Fundamentals) is written, verify OSPFv3 address family details align with this module and add a back-reference

<!-- XREF-END -->
