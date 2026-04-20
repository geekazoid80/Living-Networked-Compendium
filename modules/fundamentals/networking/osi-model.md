---
title: "The OSI Model"
module_id: "NW-001"
domain: "fundamentals/networking"
difficulty: "novice"
prerequisites: []
estimated_time: 40
version: "1.1"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [osi, model, layers, encapsulation, networking-fundamentals]
vendors: []
language: en
cert_alignment: "CCNA 200-301 — 1.1; CompTIA Network+ — 1.1; JNCIA-Junos — Networking Fundamentals"
---

## The Problem

Two people are standing next to each other. They want to communicate. One opens their mouth and speaks. The other hears it. Done — it works perfectly.

Now let's make this harder, one problem at a time.

### Step 1: They're in different rooms

They can no longer hear each other through the wall. They need something to carry the signal — a string between two tin cans, a wire, a radio transmitter. Whatever they choose, it just moves the raw signal from one side to the other. It doesn't know who is speaking or what they're saying.

They've just invented the concept of a **medium** — something that carries the signal. In networking: the **Physical layer (Layer 1)**.

### Step 2: There are now five people in the room

One person speaks — and everyone hears it. How does anyone know which message is meant for them? They agree: every message starts with the recipient's name. "Alice: can you hear me?" Now Alice knows it's for her, and the others ignore it.

They've just invented **addressing at the local level** — identifying who on this shared medium should pay attention. In networking: **MAC addressing**, the **Data Link layer (Layer 2)**.

### Step 3: They're in different buildings

Alice is in one building. Bob is in another, three blocks away. There's no direct wire between them. They need someone in the middle — a relay — who can pass the message along. But the relay needs to know *which building* to forward it to, not just which person.

They've invented **logical addressing across multiple locations** — a way to identify not just who, but *where on the network* they are. In networking: **IP addresses**, the **Network layer (Layer 3)**.

### Step 4: The message must arrive reliably

Some messages get lost in transit. Important messages — contracts, instructions — need confirmation: "I got it." If no confirmation arrives, resend. For quick, casual messages — "are you there?" — the overhead isn't worth it.

They've invented **reliable vs. best-effort delivery**, and the concept of a connection before sending. In networking: **TCP** (reliable) and **UDP** (best-effort), the **Transport layer (Layer 4)**.

### Step 5: Alice speaks French, Bob speaks English

They can transmit and route the message reliably — but Bob can't read it. They need to agree on a common format, or use a translator. They also might want to compress the message to save time, or encrypt it so only Bob can read it.

They've invented **data formatting, encryption, and encoding agreements**. In networking: the **Presentation layer (Layer 6)**.

### Step 6: They're having a long conversation with multiple topics

One wire, two people, many messages going back and forth over time. How do they track which reply belongs to which question? How do they resume if the connection drops mid-conversation?

They've invented **session management** — tracking the state of an ongoing exchange. In networking: the **Session layer (Layer 5)**.

### Step 7: The actual content of the message

All of the above is infrastructure. Alice still needs to actually say something — ask a question, request a file, send an email. The content itself, and the interface that lets her compose and send it.

In networking: the **Application layer (Layer 7)** — HTTP, DNS, SMTP, SSH.

### What You Just Built

Working through those seven constraints, you constructed the OSI model from scratch. Each layer exists because a real problem required it.

| Scenario element | Technical term |
|---|---|
| The wire, string, or radio signal | Physical layer — Layer 1 |
| "Start every message with the recipient's name" | MAC addressing — Data Link layer — Layer 2 |
| Building + room logical addressing | IP addressing — Network layer — Layer 3 |
| Guaranteed delivery with confirmation | TCP — Transport layer — Layer 4 |
| Tracking a multi-part conversation | Session layer — Layer 5 |
| Agreeing on a common language / encoding / encryption | Presentation layer — Layer 6 |
| The message itself, and the app that sends it | Application layer — Layer 7 |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Name and describe** all seven layers of the OSI model and what each one does
2. **Identify** which networking devices and protocols operate at which layer
3. **Explain** encapsulation and decapsulation — how data gets wrapped and unwrapped as it moves through the model
4. **Use** the OSI model as a troubleshooting framework to isolate where a network problem is occurring

---

## Prerequisites

No prerequisites. This is the starting point.

If you're completely new to networking, that's fine — this module assumes nothing beyond the fact that computers can talk to each other over a network, and you want to understand how.

---

## Why This Matters

Every networking conversation eventually comes back to the OSI model. When an engineer says "that's a Layer 2 problem" or "this is a Layer 7 issue," they're speaking shorthand that assumes everyone in the room knows the model. Without it, you're locked out of the language.

More practically: the OSI model is your troubleshooting compass. When something breaks — and things always break — you need a systematic way to figure out where the problem is. Is the cable dead? Is the IP address wrong? Is the application misconfigured? Each of those is a different layer, and working through them in order stops you from chasing the wrong problem.

You'll reference this model for the rest of your career. Get it right once, and it saves you time every day.

---

## Core Content

### What Is the OSI Model?

The Open Systems Interconnection (OSI) model is a conceptual framework that describes how data moves from an application on one computer to an application on another — across any network, using any combination of hardware and software.

It was developed by the International Organisation for Standardisation (ISO) in the 1980s. It's not a protocol — it doesn't do anything by itself. It's a model: a way of thinking about and describing what each piece of networking software and hardware is responsible for.

The model has **seven layers**. Think of them as a stack:

```
┌─────────────────────────────┐
│  Layer 7 — Application      │  What the user sees
├─────────────────────────────┤
│  Layer 6 — Presentation     │  Format and encrypt
├─────────────────────────────┤
│  Layer 5 — Session          │  Manage conversations
├─────────────────────────────┤
│  Layer 4 — Transport        │  End-to-end delivery
├─────────────────────────────┤
│  Layer 3 — Network          │  Logical addressing and routing
├─────────────────────────────┤
│  Layer 2 — Data Link        │  Physical addressing and access
├─────────────────────────────┤
│  Layer 1 — Physical         │  Bits on a wire (or radio wave)
└─────────────────────────────┘
```

Data flows **down** the stack on the sending side and **up** the stack on the receiving side.

A popular mnemonic for remembering the layers top-to-bottom: **All People Seem To Need Data Processing** (Application, Presentation, Session, Transport, Network, Data Link, Physical). Bottom-to-top: **Please Do Not Throw Sausage Pizza Away**.

Pick whichever sticks. You'll use these labels constantly.

---

### Layer 1 — Physical

**What it does:** Transmit raw bits — 0s and 1s — between devices.

The Physical layer is concerned with the medium and the signal. It has no concept of addresses or error correction. It just moves electricity, light, or radio waves.

**What lives here:**
- Ethernet cables (Cat5e, Cat6, Cat6a, fibre)
- Wi-Fi radio signals
- Repeaters and hubs (dumb signal amplifiers/splitters)
- Network Interface Cards (NICs) — the part that converts digital data to a physical signal

**Data unit:** Bit

**Analogy:** Layer 1 is the road. It doesn't know who is driving or where they're going — it just exists for traffic to move on.

---

### Layer 2 — Data Link

**What it does:** Reliable transfer of data between two directly connected devices, and access control to the shared physical medium.

Layer 2 introduces **addressing** for the first time. Each network interface has a unique Media Access Control (MAC) address — a 48-bit identifier burned into the hardware (e.g. `00:1A:2B:3C:4D:5E`). Layer 2 uses MAC addresses to identify source and destination on a local network.

Layer 2 also handles:
- **Error detection** (CRC checks) — it can detect corrupted frames, but discards them rather than fixing them (that's Layer 4's job)
- **Media access control** — deciding who gets to transmit on the shared wire (Ethernet uses CSMA/CD; Wi-Fi uses CSMA/CA)

The data unit at Layer 2 is called a **frame**.

Layer 2 is split into two sub-layers:
- **MAC (Media Access Control)** — hardware addressing and media access
- **LLC (Logical Link Control)** — identifies which Layer 3 protocol is being carried

**What lives here:**
- Ethernet switches
- Wi-Fi Access Points (the radio part)
- Bridges
- MAC addresses

**Data unit:** Frame

**Analogy:** Layer 2 is the street address on your suburb. It's how packets find the right house on the local block — but it doesn't know about the next suburb over.

---

### Layer 3 — Network

**What it does:** Logical addressing and routing — moving packets from source to destination across multiple networks.

Where Layer 2 moves data between directly connected devices, Layer 3 moves data between devices that may be many hops apart — across different networks, countries, or continents.

Layer 3 uses **IP addresses** (Internet Protocol) instead of MAC addresses. IP addresses are logical — they can be assigned and changed by configuration. They indicate not just *which device*, but *which network* the device is on.

Routers operate at Layer 3. They examine the destination IP address in each packet and make a forwarding decision — "send this packet out that interface toward that next hop."

**Data unit:** Packet

**What lives here:**
- Routers
- Layer 3 switches (switches with routing capability)
- IP addresses (IPv4 and IPv6)
- Routing protocols: OSPF, BGP, EIGRP, RIP

**Analogy:** Layer 3 is the postal service. It knows how to route your letter from Singapore to Tokyo — across multiple sorting offices (routers), each making a local decision about where to send it next.

---

### Layer 4 — Transport

**What it does:** End-to-end communication between applications, including reliability, flow control, and multiplexing.

Layer 3 delivers packets to the right machine. Layer 4 delivers data to the right **application** on that machine, and manages the conversation.

Two main protocols live here:

| | TCP | UDP |
|---|---|---|
| Full name | Transmission Control Protocol | User Datagram Protocol |
| Connection | Connection-oriented (handshake first) | Connectionless (fire and forget) |
| Reliability | Guaranteed delivery, retransmits lost data | No guarantee — lost packets stay lost |
| Order | Data arrives in order | Data may arrive out of order |
| Overhead | Higher (acknowledgements, sequence numbers) | Lower (minimal header) |
| Use when | Accuracy matters (web, email, file transfer) | Speed matters (video, voice, DNS, gaming) |

Layer 4 also uses **port numbers** to multiplex multiple applications on the same machine. Web traffic goes to port 80 (HTTP) or 443 (HTTPS); SSH goes to port 22; DNS goes to port 53. This is how your computer handles 20 browser tabs, a Zoom call, and a Spotify stream simultaneously — each gets its own port.

**Data unit:** Segment (TCP) or Datagram (UDP)

---

### Layer 5 — Session

**What it does:** Establish, manage, and terminate sessions (conversations) between applications.

**Data unit:** Data

??? supplementary "Layer 5 in Practice"
    Think of a session as a formal conversation — it has a beginning, a middle, and an end. Layer 5 handles the setup and teardown of that conversation, and can checkpoint long transfers so they can resume if interrupted.

    In practice, Layer 5 functionality is often embedded in application protocols or operating systems rather than existing as a distinct component you'll configure. You'll encounter it most clearly in:
    - **RPC (Remote Procedure Call)** — used heavily in enterprise file systems and Active Directory
    - **SMB (Server Message Block)** — Windows file sharing; manages session state across a share connection
    - **NetBIOS** — legacy name resolution and session management (largely replaced by DNS)

    The reason Layer 5 seems "invisible" is that modern application protocols (HTTP, TLS) bundle session management into themselves, collapsing what the OSI model treats as separate concerns.

---

### Layer 6 — Presentation

**What it does:** Data formatting, encryption, and compression — translating data between application format and network format.

**Data unit:** Data

??? supplementary "Layer 6 in Practice"
    Layer 6 ensures that data sent by one application can be read by another, even if they use different internal representations. It handles:
    - **Character encoding** (ASCII, UTF-8, Unicode) — agreed-upon ways to represent text as bytes
    - **Encryption and decryption** — SSL/TLS is often cited as a Layer 6 protocol, though it spans Layers 4–7 in practice
    - **Compression** — reducing data size before transmission (e.g., gzip on HTTP responses)

    Like Layer 5, in practice you rarely configure Layer 6 explicitly — it's usually part of the application or protocol stack. When someone says "TLS is a Layer 6 protocol," they mean it handles presentation concerns (encryption, formatting) — not that it fits neatly into one box.

---

### Layer 7 — Application

**What it does:** Provide networking services directly to user-facing applications.

Layer 7 is the interface between your software and the network. It doesn't mean "the application itself" — it means the networking interface that the application uses.

**What lives here:**
- HTTP and HTTPS (web browsing)
- DNS (domain name resolution)
- SMTP, IMAP, POP3 (email)
- FTP, SFTP (file transfer)
- SNMP (network management)
- Telnet, SSH (remote access)

**Data unit:** Data

---

### Encapsulation and Decapsulation

This is the mechanism that makes the whole model work.

When you send data, each layer **adds its own header** (and sometimes a trailer) to the data passed down from the layer above. This is called **encapsulation**.

```
Application data:        [  APPLICATION DATA  ]
Layer 4 adds header:     [ L4 HDR ][  APPLICATION DATA  ]
Layer 3 adds header:     [ L3 HDR ][ L4 HDR ][  APPLICATION DATA  ]
Layer 2 adds header+trailer: [ L2 HDR ][ L3 HDR ][ L4 HDR ][  DATA  ][ L2 FCS ]
Layer 1 transmits:       101001010101010...  (bits on the wire)
```

Each header contains the information that layer needs to do its job: MAC addresses (Layer 2), IP addresses (Layer 3), port numbers (Layer 4).

On the receiving end, each layer **strips its header** as data moves up the stack (**decapsulation**), until the original application data is handed to the receiving application.

This layering means each layer is independent — Layer 3 doesn't care what's inside the data it's routing; Layer 2 doesn't care what IP address is inside the frame. This is what makes the internet's modularity possible.

---

### The OSI Model as a Troubleshooting Tool

When something isn't working, start at Layer 1 and work up:

| Layer | Question to ask | Tool to use |
|---|---|---|
| 1 — Physical | Is the cable plugged in? Are the LEDs on? | Your eyes; `show interfaces` (check for input errors) |
| 2 — Data Link | Is the MAC address resolving? Is there a duplicate MAC? | `show mac address-table`; `arp -a` |
| 3 — Network | Is the IP address correct? Is there a route? | `ping`; `show ip route`; `traceroute` |
| 4 — Transport | Is the port open? Is the firewall blocking it? | `telnet host port`; `netstat`; firewall logs |
| 5–6 | Is encryption/format causing issues? | Application logs |
| 7 — Application | Is the service running? Is the config correct? | Application logs; `nslookup`; `curl` |

Working bottom-up means you don't spend an hour debugging a routing problem only to find the cable was loose.

---

## Common Pitfalls

### Pitfall 1: Confusing Layer 2 and Layer 3 addressing

MAC addresses are Layer 2. IP addresses are Layer 3. A device can have the same IP address but different MAC addresses depending on which interface you look at. On a local network, Layer 2 (MAC) is used to actually deliver the frame. Layer 3 (IP) is used to route it to the right network. Both are always present — just at different layers.

### Pitfall 2: Thinking OSI maps exactly to real protocols

Real protocols don't always fit neatly into one layer. TCP/IP (the protocol suite that actually runs the internet) compresses the OSI model into four layers. SSL/TLS touches Layers 4, 5, and 6. The OSI model is a conceptual guide, not a strict implementation spec.

### Pitfall 3: Forgetting the data unit names

Vendors, exam questions, and colleagues all use them: **bit** (L1), **frame** (L2), **packet** (L3), **segment** (L4). Getting these wrong in a technical conversation causes confusion. Memorise them.

---

## Practice Problems

1. A user reports they cannot access a website. You verify they have a valid IP address and can ping the default gateway, but cannot reach any external addresses. Which OSI layer is most likely the problem? Explain your reasoning.

2. An Ethernet switch operates at which OSI layer? What information does it use to make forwarding decisions?

3. You run `traceroute` to a server and see the path: your PC → router A → router B → server. At which OSI layer does `traceroute` operate, and what information does it rely on?

4. Describe in one sentence what happens at Layer 2 when a frame arrives at a switch destined for a MAC address not in the switch's MAC address table.

??? supplementary "Answers"
    **1.** Layer 3 (Network). The user can reach the local gateway (Layer 2 and Layer 3 local are fine), but cannot route beyond it. This suggests a missing or incorrect route — either on the local router or upstream. It could also be Layer 1/2 on the uplink from the gateway, but the most targeted guess is Layer 3 routing.

    **2.** Layer 2. A switch uses **MAC addresses** to make forwarding decisions. It looks up the destination MAC in its MAC address table and forwards the frame out the corresponding port. If the MAC is unknown, it floods the frame out all ports except the one it arrived on.

    **3.** Layer 3. `traceroute` uses IP packets (ICMP or UDP depending on OS) with incrementing TTL values. Each router that receives a packet with TTL=1 decrements it to 0 and returns an ICMP "Time Exceeded" message, revealing that router's Layer 3 (IP) address.

    **4.** The switch **floods** the frame out all ports except the ingress port. This is called "unknown unicast flooding." The switch simultaneously records the source MAC → ingress port mapping in its table.

---

## Lab

### Lab: Exploring the OSI Model with Wireshark

**Tools needed:** Wireshark (free, wireshark.org) installed on your PC
**Estimated time:** 20 minutes

**Objective:** Capture live traffic and identify OSI layer headers in real packets.

**Steps:**

1. Open Wireshark. Select your active network interface (e.g., Wi-Fi or Ethernet) and start a capture.

2. Open a web browser and visit any website (e.g., `example.com`).

3. Stop the capture after 30 seconds.

4. In Wireshark, find a packet with "DNS" in the protocol column. Click on it.

5. In the packet detail pane (middle panel), expand each layer:
    - **Frame** — Physical/Data Link layer information (arrival time, interface, length)
    - **Ethernet II** — Layer 2: source and destination MAC addresses
    - **Internet Protocol** — Layer 3: source and destination IP addresses
    - **User Datagram Protocol** — Layer 4: source and destination ports
    - **Domain Name System** — Layer 7: the actual DNS query

6. Note the MAC addresses vs. IP addresses. The MAC addresses are local — they show your machine and your gateway. The IP addresses show the actual source and destination across the internet.

7. Find an HTTP or HTTPS packet. Expand the layers and compare the structure.

**Stretch goal:** Filter the capture to show only traffic to port 443 (`tcp.port == 443`). Observe that you can see the TCP handshake (SYN, SYN-ACK, ACK) at Layer 4 before any data is exchanged.

---

## Summary & Key Takeaways

- The OSI model has **7 layers**: Physical, Data Link, Network, Transport, Session, Presentation, Application
- Each layer has a specific responsibility and passes data to the layer above or below it
- Data units by layer: **bit** (L1), **frame** (L2), **packet** (L3), **segment/datagram** (L4)
- **Encapsulation**: each layer adds a header (and sometimes trailer) as data moves down the stack
- **Decapsulation**: each layer strips its header as data moves up the stack on the receiving side
- Devices map to layers: hubs → L1, switches → L2, routers → L3
- The model is a troubleshooting framework — work bottom-up from Physical to Application

---

## Where to Next

- **Continue the sequence:** [Network Topologies](network-topologies.md) (`NW-002`) — star, mesh, bus, ring, and hybrid topologies
- **Go deeper on addressing:** [IP Addressing Fundamentals](../ip/ip-addressing.md) (`IP-001`) — how Layer 3 addressing actually works
- **Go deeper on Layer 2:** [Switching Fundamentals](../switching/switching-fundamentals.md) (`SW-001`) — how switches learn and forward frames

---

## Standards & Certifications

**Relevant standards:**
- ISO/IEC 7498-1:1994 — Information Technology — Open Systems Interconnection — Basic Reference Model
- IETF RFC 1122 — Requirements for Internet Hosts — Communication Layers

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant section |
|---|---|---|
| CCNA 200-301 | Cisco | 1.1 — Network fundamentals |
| CompTIA Network+ | CompTIA | 1.1 — OSI model |
| JNCIA-Junos JN0-103 | Juniper | Networking fundamentals |
| HCIA-Routing & Switching | Huawei | Network fundamentals |

---

## References

- ISO/IEC 7498-1:1994 — Information Technology — Open Systems Interconnection — Basic Reference Model
- Forouzan, Behrouz A. — *Data Communications and Networking*, 5th ed., McGraw-Hill, 2013 — Chapter 2
- Cisco — OSI Model Reference: cisco.com/c/en/us/support/docs/ibm-technologies/logical-link-control/25862-way.html
- IETF — RFC 1122: Requirements for Internet Hosts — Communication Layers

---

## Attribution & Licensing

**Author:** @geekazoid80
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Claude used for initial draft structure and prose. All technical claims verified against Cisco documentation and Forouzan's textbook.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| NW-002 | Network Topologies | Prerequisite — OSI model used to classify where topology decisions operate | 2026-04-17 |
| IP-001 | IP Addressing Fundamentals | Prerequisite — Layer 3 (Network) context | 2026-04-17 |
| SW-001 | Switching Fundamentals | Prerequisite — Layer 2 (Data Link) context | 2026-04-17 |
| RT-001 | Routing Fundamentals | Prerequisite — Layer 3 (Network) context | 2026-04-17 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| NW-002 | Network Topologies | "Where to Next" forward reference | 2026-04-17 |
| IP-001 | IP Addressing Fundamentals | "Where to Next" forward reference | 2026-04-17 |
| SW-001 | Switching Fundamentals | "Where to Next" forward reference | 2026-04-17 |

### Vendor Mapping

| Concept | Standard |
|---|---|
| OSI Reference Model | ISO/IEC 7498-1 |
| TCP/IP (practical 4-layer collapse) | IETF RFC 1122 |

### Maintenance Notes

- When any layer's protocol coverage is updated in a downstream module, verify the layer description here remains consistent.
<!-- XREF-END -->
