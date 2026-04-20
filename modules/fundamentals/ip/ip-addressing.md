---
title: "IP Addressing Fundamentals"
module_id: "IP-001"
domain: "fundamentals/ip"
difficulty: "novice"
prerequisites: ["NW-001"]
estimated_time: 45
version: "1.1"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [ip, addressing, ipv4, cidr, binary, classes, public, private]
vendors: []
language: en
cert_alignment: "CCNA 200-301 - 1.6; CompTIA Network+ - 1.4; JNCIA-Junos - Networking Fundamentals"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** what an IP address is and why we need it
2. **Convert** between dotted-decimal and binary notation
3. **Identify** whether an IP address is public or private, and in which class it falls
4. **Describe** the role of the subnet mask and how it separates the network and host portions of an address
5. **Recognise** special-purpose addresses (broadcast, loopback, APIPA)

---
## Prerequisites

- [The OSI Model](../networking/osi-model.md) (`NW-001`) - specifically, understanding that IP addressing lives at Layer 3 (Network layer)

You should also be comfortable with binary arithmetic - converting between binary and decimal. If you're rusty, spend 15 minutes on this first: [Binary Number System (Khan Academy)](https://www.khanacademy.org/computing/computers-and-internet/xcae6f4a7ff015e7d:digital-information/xcae6f4a7ff015e7d:binary-numbers/v/binary-numbers).

---
## The Problem

You've just moved into a new building. It's a big one - hundreds of rooms. You want to send a letter to someone in Room 47. You write "Room 47" on the envelope and hand it to the courier.

The courier looks at the envelope and asks: "Which building?" You forgot - Room 47 exists in every building on the street. The courier has no idea where to go.

### Step 1: You need a building identifier

You add the building number: "Building 3, Room 47." Now the courier can find the right building first, then locate the room. Two pieces of information working together: *where is the building*, and *which room inside it*.

This is the core idea behind an IP address. It has two parts: one that identifies the **network** (the building), and one that identifies the **host** (the room). Both are encoded in a single number.

### Step 2: But how do you know where the building ends and the room begins?

"Building 3, Room 47" only works if everyone agrees on how many digits belong to the building number and how many to the room number. If the courier reads it as "Building 33, Room 47" you've got a problem.

You need a rule - a boundary - that says: "the first N digits identify the building; the rest identify the room." That rule is the **subnet mask**. It doesn't add new information - it just tells you how to read the address you already have.

### Step 3: The building numbers are running out

There are only so many buildings you can number with the digits you've chosen. If your numbering scheme supports 4 billion addresses and the world needs more, you hit a wall.

One solution: let many buildings share the same external-facing number, using a translator at the door who swaps internal room numbers for external ones. That's **NAT** - Network Address Translation. The building has a public address on the street, and private numbering inside.

### What You Just Built

An IPv4 address is a 32-bit number divided into two parts by the subnet mask - a **network portion** and a **host portion**. The mask tells you the boundary. Private address ranges let millions of internal networks reuse the same number space without conflict.

| Scenario element | Technical term |
|---|---|
| Building number | Network portion of the IP address |
| Room number | Host portion of the IP address |
| The rule for where building ends and room begins | Subnet mask |
| The full "Building 3, Room 47" label | IP address in dotted-decimal notation |
| Buildings that reuse internal numbers | Private address ranges (RFC 1918) |
| The translator at the door | NAT - Network Address Translation |
| "Deliver to every room in this building" | Broadcast address |

---
## Why This Matters

Every single device that communicates on an IP network - your phone, your laptop, a router in Tokyo, a server in Frankfurt - has an IP address. It's the fundamental identity of a device at Layer 3.

Get this wrong and nothing works. Misconfigure an IP address and you can't reach anything. Don't understand the structure and you can't subnet, can't design networks, can't troubleshoot. IP addressing is the foundation that everything else in networking is built on.

The good news: once you understand binary, the rest follows logically. There's no magic - just a consistent set of rules applied over and over.

---
## Core Content

### What Is an IP Address?

An Internet Protocol (IP) address is a numerical label assigned to each device on a network that uses IP for communication. Think of it as your device's postal address on the network - it tells other devices where to send data.

This module covers **IPv4** - version 4 of the Internet Protocol, which has been in use since the 1980s and is still the dominant version in use today. IPv6 is covered in a separate module (`IP-003`).

### IPv4 Address Format

An IPv4 address is a **32-bit number**. That means it's just a long string of 32 binary digits (bits), each either 0 or 1.

```
Binary:   11000000 10101000 00000001 00000001
Decimal:  192      .168     .1       .1
```

Because a 32-bit binary number is hard to read and write, we split it into four groups of 8 bits (called **octets**) and convert each octet to its decimal equivalent. The four decimals are separated by dots - this is **dotted-decimal notation**.

Each octet can range from 0 to 255 (because 8 bits can represent values from 0000 0000 to 1111 1111).

So an IPv4 address looks like: `192.168.1.1`

#### Binary-to-Decimal Conversion

Each bit position in an octet has a value (a power of 2):

| Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 | Bit 0 |
|---|---|---|---|---|---|---|---|
| 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

To convert binary to decimal: add up the values of each bit position where the bit is 1.

**Example:** `11000000`
- Bit 7 (128): 1 → 128
- Bit 6 (64): 1 → 64
- Bits 5–0: all 0
- **Total: 128 + 64 = 192** ✓

**Example:** `10101000`
- 128 + 0 + 32 + 0 + 8 + 0 + 0 + 0 = **168** ✓

Practice this until it's automatic. You need it for subnetting.

---

### The Subnet Mask

An IP address on its own doesn't tell you which part identifies the **network** and which part identifies the **host** (the specific device) on that network. That's what the **subnet mask** is for.

A subnet mask is also a 32-bit number, always written with all the 1-bits on the left and all the 0-bits on the right:

```
Subnet mask:  11111111 11111111 11111111 00000000
Decimal:      255      .255     .255     .0
```

The rule:
- Bits where the subnet mask is **1** → those bits in the IP address identify the **network**
- Bits where the subnet mask is **0** → those bits identify the **host**

**Example:** IP address `192.168.1.100` with subnet mask `255.255.255.0`

```
IP address:   192.168.1.100   → 11000000.10101000.00000001.01100100
Subnet mask:  255.255.255.0   → 11111111.11111111.11111111.00000000
                                 |←── network portion ──→| |←host→|
```

- **Network:** `192.168.1` (first 24 bits)
- **Host:** `.100` (last 8 bits)
- All devices on this network share the `192.168.1.x` network address

#### CIDR Notation

Writing out `255.255.255.0` every time is verbose. A shorthand called **CIDR (Classless Inter-Domain Routing)** notation counts the number of 1-bits in the subnet mask and appends it after a slash:

`255.255.255.0` → `/24` (24 ones in the mask)

So instead of writing `192.168.1.100 255.255.255.0`, you write `192.168.1.100/24`.

Common masks and their CIDR equivalents:

| Subnet Mask | CIDR | Network Bits | Host Bits | Usable Hosts |
|---|---|---|---|---|
| 255.0.0.0 | /8 | 8 | 24 | 16,777,214 |
| 255.255.0.0 | /16 | 16 | 16 | 65,534 |
| 255.255.255.0 | /24 | 24 | 8 | 254 |
| 255.255.255.128 | /25 | 25 | 7 | 126 |
| 255.255.255.192 | /26 | 26 | 6 | 62 |
| 255.255.255.224 | /27 | 27 | 5 | 30 |
| 255.255.255.240 | /28 | 28 | 4 | 14 |
| 255.255.255.248 | /29 | 29 | 3 | 6 |
| 255.255.255.252 | /30 | 30 | 2 | 2 |

**Usable hosts** = 2^(host bits) − 2. You subtract 2 because the first address (all host bits = 0) is the **network address** and the last (all host bits = 1) is the **broadcast address** - neither can be assigned to a host.

---

### IPv4 Address Classes

Before CIDR was introduced, IPv4 addresses were divided into fixed **classes** based on the first octet. You'll still see class names used in conversation (especially "Class A", "Class B", "Class C"), so you need to know what they mean.

| Class | First Octet Range | Default Mask | Networks | Hosts per Network | Original Use |
|---|---|---|---|---|---|
| A | 1–126 | /8 (255.0.0.0) | 128 | 16,777,214 | Very large organisations |
| B | 128–191 | /16 (255.255.0.0) | 16,384 | 65,534 | Large organisations |
| C | 192–223 | /24 (255.255.255.0) | 2,097,152 | 254 | Small networks |
| D | 224–239 | N/A | Multicast | Multicast | Multicast groups |
| E | 240–255 | N/A | Reserved | Reserved | Experimental |

!!! note "127.x.x.x is missing from Class A"
    The range 127.0.0.0–127.255.255.255 is reserved for **loopback** (see Special Addresses below). That's why Class A starts at 1, not 0, and the highest usable first octet is 126.

Classful addressing is largely obsolete - modern networks use CIDR and variable-length subnet masks (covered in the subnetting module). But classful concepts remain useful for quick mental math and reading older documentation.

---

### Public vs. Private Addresses

IPv4 has a problem: with 32 bits, it can only address about 4.3 billion unique devices - and we've exceeded that. The internet runs out of unique public IP addresses years ago.

The solution (one of them, alongside IPv6) is **private address space** combined with **Network Address Translation (NAT)**.

**Private IP ranges** are reserved for internal use. They are not routed on the public internet - every network in the world can use them internally without conflict:

| Range | CIDR | Class | Typical use |
|---|---|---|---|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | A | Large enterprise networks |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | B | Medium networks |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | C | Home and small office |

Your home router uses a private address internally (e.g., `192.168.1.1`) and a single **public IP address** on its WAN (internet-facing) interface. NAT translates between the two, allowing many private devices to share one public address.

**Public addresses** are globally unique, assigned by Regional Internet Registries (RIRs) like APNIC (Asia-Pacific). Devices with public addresses are reachable directly from the internet (subject to firewall rules).

---

### Special-Purpose Addresses

Several IPv4 address ranges have specific meanings and cannot be used for regular hosts:

| Address / Range | Purpose |
|---|---|
| `0.0.0.0` | "This network" - used as a source in some protocols (e.g., DHCP discover) |
| `127.0.0.0/8` | **Loopback** - traffic sent here stays on the local machine; `127.0.0.1` is the standard loopback |
| `169.254.0.0/16` | **APIPA** (Automatic Private IP Addressing) - assigned automatically when no DHCP server is found |
| `255.255.255.255` | **Limited broadcast** - sent to all hosts on the local subnet |
| `x.x.x.255` (with /24) | **Directed broadcast** - sent to all hosts on a specific subnet (e.g., `192.168.1.255`) |
| `x.x.x.0` (with /24) | **Network address** - represents the subnet itself, not assignable to a host |
| `224.0.0.0/4` | **Multicast** - packets sent to a group of receivers |

!!! tip "APIPA is a diagnostic clue"
    If a device shows an IP address starting with `169.254.x.x`, it couldn't reach a DHCP server. This tells you immediately that there's a network or DHCP configuration problem - not an application issue.

---
## Common Pitfalls

### Pitfall 1: Confusing the network address with a host address

The address with all host bits set to 0 is the **network address** - it represents the subnet, not a device. You cannot assign `192.168.1.0` (with /24) to a host. Similarly, `192.168.1.255` is the broadcast address. New engineers regularly assign these by accident, causing confusing failures.

### Pitfall 2: Getting the subnet mask wrong direction

A subnet mask is always a continuous block of 1s followed by a continuous block of 0s. `255.255.255.0` is valid. `255.0.255.0` is not - you'll never see a valid subnet mask with 1s after 0s. If you ever calculate a mask and it has non-contiguous bits, you've made an arithmetic error.

### Pitfall 3: Treating private addresses as globally routable

Private addresses (`10.x.x.x`, `172.16–31.x.x`, `192.168.x.x`) are not routed on the internet. A router receiving a packet destined for `192.168.1.100` from the public internet will drop it. This is by design - but it catches people out when they misconfigure NAT or use private addresses where public ones are needed.

### Pitfall 4: Confusing dotted-decimal and CIDR masks

`/24` and `255.255.255.0` are the same thing. `192.168.1.0/24` and `192.168.1.0 255.255.255.0` describe the same network. Some tools want one format, some the other. Know how to convert between them quickly.

---
## Practice Problems

1. Convert the binary number `10110100` to decimal. Show your working.

2. Write the subnet mask `255.255.240.0` in CIDR notation.

3. Is the address `172.20.5.1` a private or public address? Which private range does it fall in?

4. A host has the IP address `192.168.10.50/26`. What is the network address? What is the broadcast address? How many usable host addresses are in this subnet?

5. Your colleague says their device got a `169.254.12.45` address. What does this tell you, and what would you check first?

??? supplementary "Answers"
    **1.** `10110100`
    - 128 (1) + 64 (0) + 32 (1) + 16 (1) + 8 (0) + 4 (1) + 2 (0) + 1 (0)
    - = 128 + 32 + 16 + 4 = **180**

    **2.** Count the 1-bits: `11111111.11111111.11110000.00000000`
    - 8 + 8 + 4 = **20 ones → /20**

    **3.** Private. The `172.16.0.0/12` range covers `172.16.0.0` through `172.31.255.255`. The address `172.20.5.1` falls within this range.

    **4.** `/26` means 26 network bits, 6 host bits. Subnet mask: `255.255.255.192`.
    - `.50` in the last octet - the /26 boundary in the last octet is at 64. 50 < 64, so the subnet is `192.168.10.0/26`.
    - **Network address:** `192.168.10.0`
    - **Broadcast address:** `192.168.10.63` (first subnet ends at .63)
    - **Usable hosts:** 2^6 − 2 = 64 − 2 = **62**

    **5.** The device has an APIPA address, meaning it couldn't reach a DHCP server. Check: (a) Is the device's network cable connected / Wi-Fi associated? (b) Is the DHCP server running and reachable? (c) Is there a DHCP scope configured for this subnet? Start at Layer 1 and work up.

---
## Lab

### Lab: IP Address Exploration on Your Local Machine

**Tools needed:** Your own computer (Windows, macOS, or Linux)
**Estimated time:** 15 minutes

**Objective:** Identify the IP addressing configuration of your local machine and understand what each component means.

**Steps:**

**Windows:**
```
ipconfig /all
```

**macOS / Linux:**
```bash
ip addr show
# or on older systems:
ifconfig
```

1. Find your active network interface (Wi-Fi or Ethernet).

2. Note down:
    - IPv4 address
    - Subnet mask
    - Default gateway
    - DNS server(s)

3. Convert your subnet mask to CIDR notation. How many host bits does your subnet have?

4. Calculate the network address and broadcast address for your subnet.

5. Is your IP address in a private range? Which one?

6. Test the loopback interface:
    ```bash
    ping 127.0.0.1
    ```
    This should always succeed - the packet never leaves your machine.

7. From the command line, check if your machine can reach the default gateway:
    ```bash
    ping <your-default-gateway-ip>
    ```

**Stretch goal:** Run `arp -a` (Windows/macOS) or `ip neigh` (Linux) to see the ARP table - the mapping between IP addresses (Layer 3) and MAC addresses (Layer 2) for devices on your local subnet.

---
## Summary & Key Takeaways

- An IPv4 address is a **32-bit number** written in dotted-decimal notation (four octets, 0–255 each)
- The **subnet mask** separates the network portion from the host portion of an IP address
- **CIDR notation** (`/24`) is shorthand for the subnet mask - it counts the number of 1-bits
- IPv4 is divided into **classes** (A, B, C, D, E) based on the first octet - classful thinking is still useful for quick reference
- **Private address ranges** (`10.x.x.x`, `172.16–31.x.x`, `192.168.x.x`) are for internal use and not routed on the internet
- **Special addresses** include loopback (`127.0.0.1`), broadcast, network address, and APIPA (`169.254.x.x`)
- Usable host count per subnet = 2^(host bits) − 2

---
## Where to Next

- **Continue the sequence:** [IP Subnetting & VLSM](subnetting.md) (`IP-002`) - how to divide a network into smaller subnets
- **Related topic:** [Routing Fundamentals](../routing/routing-fundamentals.md) (`RT-001`) - how IP addresses are used to move packets across networks
- **Services that use IP:** [DHCP](../services/dhcp.md) (`SV-002`) - how devices get their IP addresses automatically

---
## Standards & Certifications

**Relevant standards:**
- IETF RFC 791 - Internet Protocol (original IPv4 specification)
- IETF RFC 1918 - Address Allocation for Private Internets
- IETF RFC 4632 - Classless Inter-Domain Routing (CIDR)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant section |
|---|---|---|
| CCNA 200-301 | Cisco | 1.6 - IPv4 addressing |
| CompTIA Network+ | CompTIA | 1.4 - IP addressing |
| JNCIA-Junos JN0-103 | Juniper | Networking fundamentals |
| HCIA-Routing & Switching | Huawei | Network fundamentals |

---
## References

- IETF - RFC 791: Internet Protocol - the original IPv4 specification
- IETF - RFC 1918: Address Allocation for Private Internets
- IETF - RFC 4632: Classless Inter-domain Routing (CIDR)
- Odom, Wendell - *CCNA 200-301 Official Cert Guide, Volume 1*, Cisco Press, 2020 - Chapter 11–12
- Forouzan, Behrouz A. - *Data Communications and Networking*, 5th ed., McGraw-Hill, 2013 - Chapter 5

---
## Attribution & Licensing

**Author:** @geekazoid80
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Claude used for initial draft structure and prose. All technical claims verified against RFC 791, RFC 1918, and Odom's CCNA Official Cert Guide.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| IP-002 | IP Subnetting & VLSM | Prerequisite - network/host portion and subnet mask concepts | 2026-04-17 |
| RT-001 | Routing Fundamentals | Prerequisite - IP addressing is the foundation of routing decisions | 2026-04-17 |
| SV-002 | DHCP | Prerequisite - DHCP assigns addresses from the address space defined here | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| NW-001 | The OSI Model | Prerequisite - IP lives at Layer 3 (Network layer) | 2026-04-17 |
| IP-002 | IP Subnetting & VLSM | "Where to Next" forward reference | 2026-04-17 |
| RT-001 | Routing Fundamentals | "Where to Next" forward reference | 2026-04-17 |

### Vendor Mapping

| Concept | Standard |
|---|---|
| IPv4 address format | RFC 791 |
| Private address ranges | RFC 1918 |
| CIDR notation | RFC 4632 |

### Maintenance Notes

- When IP-003 (IPv6) is added, update this module's "Where to Next" to include a forward reference to IPv6 addressing.
- NAT & PAT (FN-003 / SV-003) references the private address space defined here - update both XREF sections when that module is written.
<!-- XREF-END -->
