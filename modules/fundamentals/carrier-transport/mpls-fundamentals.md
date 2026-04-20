---
title: "MPLS Fundamentals"
module_id: "CT-001"
domain: "fundamentals/carrier-transport"
difficulty: "advanced"
prerequisites: ["RT-001", "RT-004", "RT-007"]
estimated_time: 60
version: "1.0"
last_updated: "2026-04-19"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["mpls", "label", "lsp", "fec", "ldp", "rsvp-te", "ler", "lsr", "label-stack", "php", "vpn", "traffic-engineering"]
cert_alignment: "CCNP ENCOR 350-401 | JNCIS-SP JN0-362 | Nokia NRS II | Huawei HCIP-Datacom"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "Arista EOS"]
language: "en"
---
## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** why MPLS was developed and what IP forwarding problem it solves
2. **Describe** the MPLS label structure and how labels are encoded in a packet
3. **Explain** the roles of LER, LSR, and the operations: push, swap, and pop
4. **Describe** how LDP distributes label bindings and creates an LSP
5. **Identify** PHP (Penultimate Hop Popping) and explain why it is used
6. **Describe** the major MPLS applications: L3VPN, TE tunnels, and fast-reroute - at a conceptual level

---
## Prerequisites

- [Routing Fundamentals](../routing/routing-fundamentals.md) (`RT-001`) - routing table, forwarding table (FIB), LPM
- [OSPF Fundamentals](../routing/ospf-fundamentals.md) (`RT-004`) or [IS-IS Fundamentals](../routing/isis-fundamentals.md) (`RT-006`) - IGP provides the topology MPLS builds on
- [BGP Fundamentals](../routing/bgp-fundamentals.md) (`RT-007`) - MP-BGP is used for MPLS VPN signalling

---
## The Problem

A carrier router in 1995. The internet is growing fast. The routing table is large - tens of thousands of BGP prefixes. Every packet that arrives needs a longest-prefix match against the entire table. This lookup happens in software on the main CPU, at every single hop along the path. With millions of packets per second, this is the bottleneck.

A mechanism is needed that allows core routers to forward packets without performing a full IP routing-table lookup at every hop.

### Step 1: The IP lookup is the expensive part

Every IP packet carries a 20-byte header. At every router hop, the router reads the destination IP, runs a software longest-prefix match against a potentially massive routing table, finds the next-hop, rewrites the Layer 2 header, and transmits. At each subsequent hop, the same process repeats - the same full IP lookup against the same full table.

The core is doing expensive work it doesn't need to do. By the time a packet reaches hop 3, its fate is already clear - it will follow the same path to the same destination. Why repeat the full IP lookup?

### Step 2: Decide the path at the edge; carry a simple label in the core

What if the edge router - the first router the packet enters - does the full IP lookup **once**, decides the complete path through the network, and attaches a short **label** to the packet? A label is just a 20-bit number. Every core router, instead of reading the IP header and running an expensive lookup, reads only the label, swaps it for a new label, and forwards.

No more LPM at every hop. The core routers simply do:
```text
Incoming label 100 on interface eth0 → swap to label 200 → forward out eth1
```

This is MPLS: **Multi-Protocol Label Switching**. The intelligence moves to the edge; the core becomes a fast label-swapping fabric.

### Step 3: Labels are stacked

What if you need to express more than one level of forwarding information? A packet might carry:
- An outer label identifying the path through the transport network (the LSP)
- An inner label identifying the VPN or service the packet belongs to

Labels are pushed onto a **label stack** - a last-in-first-out structure. Core routers only process the top (outermost) label. When the outermost label is popped at the exit, the next label (or the original IP header) is revealed and processed.

This is how MPLS VPNs work: the outer label is the transport label (get the packet to the right PE router); the inner label is the VPN label (deliver the packet to the correct VRF at the far end).

### Step 4: Who assigns the labels?

Labels are local to each router - a label assigned by Router A has meaning only to Router A's downstream neighbour. Labels are distributed hop-by-hop so every router knows which label to expect for each destination (FEC - Forwarding Equivalence Class).

**LDP (Label Distribution Protocol)** automates this. When a router learns an IP prefix from the IGP, it assigns a label for it and advertises the binding (prefix ↔ label) to its LDP neighbours. Those neighbours install the binding in their LFIB (Label Forwarding Information Base).

### What You Just Built

MPLS - Multi-Protocol Label Switching. A forwarding mechanism where edge routers apply labels to packets, core routers swap labels without reading the IP header, and label stacks enable VPNs, traffic engineering tunnels, and other overlay services.

| Scenario element | Technical term |
|---|---|
| Packet group forwarded identically through the network | FEC (Forwarding Equivalence Class) |
| Short tag attached to the packet at the edge | MPLS Label (20-bit value) |
| The router that pushes the first label | LER - Label Edge Router (ingress PE) |
| A core router that only swaps labels | LSR - Label Switch Router (P router) |
| The path a labelled packet follows from entry to exit | LSP - Label Switched Path |
| The per-router table of label swap/pop/forward operations | LFIB - Label Forwarding Information Base |
| Protocol that distributes label bindings automatically | LDP - Label Distribution Protocol |

---
## Core Content

### The MPLS Label

An MPLS label is a **32-bit shim header** inserted between the Layer 2 header and the Layer 3 (IP) header. It is not a new protocol layer - it is literally a 32-bit word inserted in the existing packet.

```text
Packet structure with MPLS:
┌────────────────┬───────────────────────────────────┬──────────────┐
│  Layer 2 hdr   │  MPLS label stack (one per label) │ IP header... │
│  (Ethernet)    │  ← 32 bits per label entry →       │              │
└────────────────┴───────────────────────────────────┴──────────────┘

Single label entry (32 bits):
 ┌────────────────────────┬───┬─┬────────────┐
 │  Label value (20 bits) │Exp│S│ TTL (8 bits)│
 └────────────────────────┴───┴─┴────────────┘
   ↑ 0–1,048,575               ↑  ↑
   Forwarding label          CoS  Bottom of Stack
                             (3b)  S=1 means this
                                   is the last label
```

**Fields:**
- **Label value** (20 bits): 0–1,048,575. Labels 0–15 are reserved (see below).
- **Exp** (3 bits): Experimental/TC (Traffic Class) - used for QoS/CoS marking (equivalent to DSCP in intent)
- **S** (1 bit): Bottom of Stack. `1` = this is the last label; the next byte is the IP header (or inner protocol)
- **TTL** (8 bits): Time to live - decremented at each hop to prevent loops

**Reserved labels:**
| Value | Name | Meaning |
|---|---|---|
| 0 | IPv4 Explicit Null | Pop this label; forward as IPv4 (preserve QoS bits) |
| 1 | Router Alert | Signal to process locally |
| 2 | IPv6 Explicit Null | Pop this label; forward as IPv6 |
| 3 | Implicit Null / PHP | Assigned by egress - tells penultimate hop to pop label |

### MPLS Network Roles

MPLS uses a clear role separation between edge and core:

```text
         CE           PE                P              PE           CE
(Customer (Ingress  (Core router,    (Egress   (Customer
 router)  LER/LSR)   label-only)     LER/LSR)   router)
   [R]──→  [PE1] ──label──→ [P1] ──label──→ [PE2] ──→ [R]

PE = Provider Edge (Label Edge Router) — pushes/pops labels; connects to customers
P  = Provider (Label Switch Router) — swaps labels only; no customer connections
CE = Customer Edge — no MPLS; sees only IP
```

| Role | Full name | What it does |
|---|---|---|
| **LER** | Label Edge Router | Ingress: pushes labels onto packets (IP → MPLS). Egress: pops labels (MPLS → IP). Is a PE router. |
| **LSR** | Label Switch Router | Core: receives labelled packet, swaps the top label, forwards. Never sees IP header. Is a P router. |
| **CE** | Customer Edge | The customer's router. Connects to PE. Runs IP routing (often BGP or OSPF with PE). No MPLS awareness. |

### Label Operations

Three basic operations manipulate labels:

| Operation | Who does it | What happens |
|---|---|---|
| **Push** | Ingress LER | Adds a new label to the top of the stack |
| **Swap** | LSR (core) | Removes incoming label, adds outgoing label |
| **Pop** | Egress LER (or penultimate hop) | Removes the top label |

A packet's journey through an MPLS network:

```text
IP packet enters PE1:
  PE1 looks up destination IP in BGP/FIB
  PE1 pushes label stack: [outer=transport label][inner=VPN label]
  Packet leaves PE1 as MPLS

At P1 (core LSR):
  P1 reads outer label (e.g., 100)
  P1's LFIB: label 100 in → swap to label 200 → out eth1
  P1 does NOT read the IP header or inner label

At PE2-1 (penultimate hop, if PHP configured):
  Pops the outer label → exposes inner VPN label
  Packet leaves with only VPN label

At PE2 (egress LER):
  Reads inner VPN label → identifies the VRF
  Pops inner label → delivers IP packet to the CE
```

### LDP - Label Distribution Protocol

LDP (RFC 5036) automates the distribution of label bindings across the MPLS network. Without LDP, every label assignment would be manual.

**LDP process:**

1. LDP discovers neighbours on directly connected links using **UDP multicast hellos** (`224.0.0.2`, port 646)
2. LDP establishes a **TCP session** (port 646) with each neighbour
3. For every prefix in the IP routing table (learned from IGP), each router assigns a local label and advertises the binding: "For prefix 10.1.1.0/24, use label 305 when sending to me"
4. Each router installs received bindings in its **LFIB**
5. An **LSP** is established hop-by-hop: ingress assigns the first label; each intermediate hop maps the upstream label to a downstream label

**LDP loop prevention:**
LDP does not have an inherent loop-detection mechanism - it relies on the underlying IGP being loop-free. If the IGP has a loop, LDP will create a looping LSP. This is why a correctly converged IGP is an absolute prerequisite for MPLS.

**LDP FEC (Forwarding Equivalence Class):**
An FEC is the group of packets that will be forwarded identically - in basic LDP, an FEC corresponds to an IP prefix. All packets destined for `10.1.1.0/24` are in the same FEC and get the same label at each hop.

### PHP - Penultimate Hop Popping

When a labelled packet arrives at the egress PE, the PE must:
1. Read the top (transport) label to confirm it's for this PE
2. Pop the transport label
3. Look up the inner label (or IP header) for final delivery

This is two lookups at the final hop. PHP offloads the first lookup to the **penultimate router** (the second-to-last LSR before the egress PE).

**How PHP works:**
- The egress PE advertises **label 3 (Implicit Null)** to its upstream neighbour for its own prefixes
- The upstream (penultimate) router receives this: "if you're going to send traffic to PE2, send it to me with no label (pop before sending)"
- The penultimate router pops the transport label before forwarding
- The egress PE receives an IP packet (or a packet with only inner labels) - only one lookup needed

PHP is enabled by default in all major MPLS implementations. The result: the last-hop router is not burdened with both label processing and IP/VPN lookup.

??? supplementary "Explicit Null vs Implicit Null"
    - **Implicit Null (label 3):** The penultimate hop pops the label and sends an unlabelled (IP) packet or a packet with only inner labels. QoS markings in the MPLS label header (Exp/TC bits) are lost on the pop.
    - **Explicit Null (label 0 for IPv4, label 2 for IPv6):** The penultimate hop replaces the transport label with the explicit null label instead of popping it. The egress PE sees label 0/2 and pops it - but the Exp/TC bits from the label header are preserved into the IP DSCP field. Use Explicit Null when QoS markings in the MPLS header must be preserved to the egress PE.

### MPLS Applications

MPLS by itself is just a forwarding optimisation. Its real value is as a platform for services:

**1. MPLS L3VPN (RFC 4364)**

The most widely deployed MPLS application. Provides Layer 3 VPN service to enterprise customers:
- PE routers maintain per-customer **VRF (Virtual Routing and Forwarding)** tables - isolated routing tables, one per VPN
- CE-PE routing runs BGP, OSPF, or static - within the VRF
- Between PEs, **MP-BGP** (Multiprotocol BGP, RFC 4760) distributes VPN routes with a **Route Distinguisher (RD)** to make them globally unique and a **Route Target (RT)** to control which VRFs import/export which routes
- Packets carry a **two-label stack**: outer = transport LSP label (gets to the right PE), inner = VPN label (identifies the VRF)

```text
Label stack for L3VPN packet:
  [ Transport label (LDP/RSVP-TE) | VPN label (MP-BGP) | IP header ]
  ↑ popped by PHP at penultimate hop      ↑ identifies VRF at egress PE
```

**2. RSVP-TE - Traffic Engineering Tunnels**

Standard MPLS routing follows the IGP shortest path. RSVP-TE (Resource Reservation Protocol - Traffic Engineering, RFC 3209) allows operators to manually specify or signal explicit paths through the network - useful when:
- You want to avoid specific links for policy or bandwidth reasons
- You need guaranteed bandwidth reservation along a path
- You need pre-computed backup paths (Fast-Reroute)

RSVP-TE signals a **TE tunnel** with explicit path and bandwidth; LSRs along the path reserve bandwidth and allocate labels. The result is a signalled LSP with a path that may differ from the IGP shortest path.

**3. MPLS Fast-Reroute (FRR)**

MPLS FRR (RFC 4090) pre-computes backup LSPs before failures occur. When a link or node fails:
- The router detecting the failure immediately switches traffic to the pre-signalled backup LSP
- Switchover time: typically 50ms or less (vs seconds for IGP reconvergence)
- FRR protects individual links (link protection) or entire nodes (node protection)
- Once the IGP and LDP/RSVP reconverge, traffic moves to the new optimal path

FRR is the technology that allows carrier-grade MPLS networks to meet 50ms restoration SLAs.

??? supplementary "Segment Routing - The Evolution Beyond LDP/RSVP-TE"
    Traditional MPLS requires:
    - LDP sessions on every router (label distribution)
    - RSVP-TE sessions and state on every router along a TE path (per-LSP state)
    - Complex distributed state for large TE deployments

    **Segment Routing (SR)** replaces LDP and RSVP-TE with a simpler model:
    - The IGP itself (IS-IS or OSPF) distributes labels (Segment IDs - SIDs) via new TLVs
    - No separate LDP protocol needed
    - The ingress node encodes the entire path as a stack of SIDs - no per-LSP state in the core
    - SR-MPLS uses the same MPLS label stack; SRv6 uses IPv6 extension headers instead

    SR is the current standard for new carrier and data-centre deployments. LDP/RSVP-TE remain in legacy networks. Segment Routing is covered in CT-004 (SR-MPLS) and CT-005 (SRv6).

---
## Vendor Implementations

MPLS forwarding and LDP are standardised in RFC 3031 (MPLS architecture) and RFC 5036 (LDP). All compliant implementations interoperate for basic LSP establishment and L3VPN. Vendor differences appear in TE, FRR, and advanced service features.

!!! success "Standard - RFC 3031 (MPLS Architecture), RFC 5036 (LDP), RFC 4364 (MPLS L3VPN)"
    MPLS and LDP are fully standardised. Multi-vendor MPLS networks are common in carrier environments. Verify LDP transport address, hello intervals, and authentication match across vendors.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Enable MPLS globally on interfaces
    interface GigabitEthernet0/0
     mpls ip                        ! enable LDP on this interface
     ip address 10.0.12.1 255.255.255.252

    ! LDP Router ID (loopback)
    mpls ldp router-id Loopback0 force

    ! Enable CEF (required for MPLS — usually on by default)
    ip cef

    ! Verify
    show mpls ldp neighbor
    show mpls ldp bindings
    show mpls forwarding-table
    show mpls interfaces
    ```
    On IOS-XE, `mpls ip` enables LDP per-interface. The LDP Router ID should be the loopback - `force` ensures it uses the loopback even if it comes up after LDP starts. MPLS requires CEF to be enabled (default on most platforms).

    Full configuration reference: [Cisco MPLS Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mpls/configuration/xe-16/mpls-xe-16-book.html)

=== "Juniper Junos"
    ```junos
    # Enable MPLS on interfaces
    set protocols mpls interface ge-0/0/0.0

    # Enable LDP
    set protocols ldp interface ge-0/0/0.0

    # LDP transport address (loopback)
    set protocols ldp transport-address 1.1.1.1

    # Enable RSVP (for TE)
    set protocols rsvp interface ge-0/0/0.0

    # Verify
    show ldp neighbor
    show ldp database
    show mpls lsp
    show route table mpls.0
    ```
    In Junos, MPLS, LDP, and RSVP are separately enabled per-interface. `mpls.0` is the MPLS routing table (LFIB). LDP transport address should be set to the loopback for session stability. Junos auto-enables PHP (implicit null) unless `explicit-null` is configured.

    Full configuration reference: [Juniper MPLS Configuration Guide](https://www.juniper.net/documentation/us/en/software/junos/mpls/index.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # Enable MPLS and LDP on interfaces (classic CLI)
    configure router mpls
        interface "to-R2"
            no shutdown
        exit
        no shutdown
    exit

    configure router ldp
        interface-parameters
            interface "to-R2"
                no shutdown
            exit
        exit
        targeted-session
        no shutdown
    exit

    # Verify
    show router ldp neighbor
    show router ldp bindings
    show router mpls lsp
    show router fib 1
    ```
    SR-OS configures MPLS and LDP as separate router protocols. `targeted-session` is required for LDP sessions to non-directly-connected peers (used in L2VPN pseudowires). Interface names in SR-OS are strings (quoted).

    Full configuration reference: [Nokia SR-OS MPLS Guide](https://documentation.nokia.com/sr/)

=== "Arista EOS"
    ```arista-eos
    ! Enable MPLS LDP
    mpls ldp
       router-id interface Loopback0
       transport-address interface Loopback0

    interface Ethernet1
       mpls ldp interface

    ! Enable IP/MPLS forwarding
    ip cef
    mpls ip

    ! Verify
    show mpls ldp neighbor
    show mpls ldp bindings
    show mpls forwarding-table
    ```
    Arista EOS MPLS syntax is similar to Cisco IOS-XE. LDP is configured globally and enabled per-interface. Arista supports SR-MPLS as a newer alternative to LDP.

    Full configuration reference: [Arista EOS MPLS Configuration](https://www.arista.com/en/um-eos/eos-mpls-configuration)

---
## Common Pitfalls

### Pitfall 1: MPLS enabled but CEF/fast-forwarding not enabled

MPLS requires the hardware/software forwarding plane to be active. On Cisco IOS-XE, CEF (`ip cef`) must be enabled - it usually is by default, but disabling it (or having a platform that doesn't support it on certain interfaces) silently breaks MPLS. Confirm with `show mpls interfaces` - interfaces should show `Yes` under the LDP column.

### Pitfall 2: LDP session uses wrong source address

LDP sessions should use the loopback as the transport address. If LDP forms sessions using a physical interface IP, the LDP session drops when that interface flaps - even if there is an alternative path to the peer. Configure `mpls ldp router-id Loopback0 force` (Cisco) or `transport-address` (Junos/Nokia) to bind LDP sessions to the loopback.

### Pitfall 3: IGP not fully converged before MPLS

MPLS LSPs follow the IGP topology. If the IGP is not fully converged (a route is missing), LDP will not have a label binding for that destination and traffic will fall back to IP forwarding - or be dropped if `mpls ip` is configured to block IP fallback. Always confirm the IGP is stable and all routes are present before enabling MPLS.

### Pitfall 4: MTU issues - MPLS adds 4 bytes per label

Each MPLS label adds 4 bytes to the packet. A standard Ethernet MTU of 1500 bytes with a 2-label stack (L3VPN) means the actual IP payload is limited to 1492 bytes. If path MTU discovery is broken (ICMP blocked - a common firewall mistake), large packets are silently dropped in the MPLS network. Solution: increase the interface MTU on MPLS-facing links to at least `1500 + (number of labels × 4)` bytes, or enable jumbo frames.

### Pitfall 5: PHP removes QoS markings unexpectedly

If PHP is enabled (default) and the router relies on MPLS Exp/TC bits for QoS classification at the egress PE, those bits are lost when the penultimate hop pops the label. The egress PE only sees the IP packet. Configure Explicit Null on the egress PE if QoS markings in the MPLS header must be preserved to the final hop.

---
## Practice Problems

1. A packet enters the MPLS network at PE1. PE1's LFIB shows: for prefix `10.5.0.0/24`, push labels [500, 200] and forward out eth1. The core LSR P1's LFIB shows: for incoming label 500 on eth0, swap to label 600 and forward out eth1. What label stack does the packet carry at each point: after PE1, after P1?

2. What is PHP? Why is it used? What is the label value that signals PHP to the upstream router?

3. An LDP session between R1 and R2 is not forming. R1 can ping R2's loopback address. What are three things to check?

4. A carrier network uses MPLS L3VPN to provide VPN service to two customers. Customer A has sites in three cities; Customer B has sites in two cities. Why does the MPLS backbone need to maintain only one routing table for the entire backbone, while each PE maintains per-customer VRF tables?

5. Explain in one paragraph why MPLS FRR can achieve 50ms switchover times while waiting for IGP reconvergence would take seconds.

??? "Answers"
    **1.** After PE1: packet carries label stack [outer=500, inner=200] - PE1 pushed both labels. After P1: P1 sees label 500, swaps it to 600; inner label 200 is unchanged. Packet now carries [outer=600, inner=200].

    **2.** PHP (Penultimate Hop Popping) is the practice of popping the outermost transport label at the second-to-last router before the egress PE, rather than at the egress PE itself. This saves the egress PE from performing both a label lookup (to verify/pop the transport label) and the inner lookup (VPN label or IP forwarding). The penultimate hop does the first pop, so the egress PE only needs one lookup. The label value that triggers PHP is **label 3 (Implicit Null)** - the egress PE advertises this label to its upstream neighbour for its own prefixes, signalling "pop before you send to me."

    **3.** Three things to check: (1) LDP transport address reachability - can R1 establish a TCP connection to R2's LDP transport address (usually its loopback IP)? Ping the loopback, not just the connected interface. (2) LDP port 646 - is TCP port 646 permitted by any ACL or firewall between R1 and R2? (3) LDP Router ID mismatch or misconfiguration - verify `show mpls ldp neighbor` shows an attempt; if the session is in an unexpected state, check `show mpls ldp discovery` to confirm hellos are being sent and received on the expected interfaces.

    **4.** The MPLS backbone P routers only swap labels - they never look at IP addresses or routing tables. They need only the LFIB (label-to-label mapping). All IP routing decisions are made at the PE routers, which maintain per-customer VRFs. This is the MPLS design principle: push IP intelligence to the edge; make the core fast and simple. The backbone doesn't need to know how many customers exist or how many routes each customer has - it just swaps labels.

    **5.** IGP reconvergence requires: the failure to be detected (hello timer expiry - seconds), the LSA/LSP to be flooded (propagation delay), and SPF to run on all affected routers (computation time). Total: typically 2–10 seconds. MPLS FRR pre-computes the backup path and pre-installs it in the LFIB **before** any failure occurs. When a failure is detected (by the directly connected router - milliseconds via hardware signal), the router immediately switches the label to the pre-installed backup LSP. No flood, no SPF, no reconvergence needed. The switchover is just a table lookup change - achievable in under 50ms.

---
## Summary & Key Takeaways

- **MPLS** adds a 32-bit shim header (label) between Layer 2 and Layer 3; core routers forward based on label only - no IP lookup
- The MPLS label contains: **label value** (20 bits), **TC/Exp** (3 bits, QoS), **S bit** (bottom of stack), **TTL** (8 bits)
- Labels are **stacked** - multiple labels allow nested services (transport + VPN, transport + TE tunnel)
- **FEC** groups packets with identical forwarding treatment; in basic LDP, one FEC = one IP prefix
- **LER** (Label Edge Router) is the PE - pushes/pops labels at the network edge
- **LSR** (Label Switch Router) is the P router - swaps labels in the core; never reads IP
- **LDP** (RFC 5036) automatically distributes label bindings by piggybacking on IGP routes - no manual label configuration needed
- **PHP** (Penultimate Hop Popping) offloads the final label removal to the second-to-last hop, reducing egress PE processing; triggered by label 3 (Implicit Null)
- MPLS applications: **L3VPN** (per-customer VRF + MP-BGP + two-label stack), **TE tunnels** (RSVP-TE for explicit paths), **FRR** (50ms backup path switchover)
- **Segment Routing** (CT-004/CT-005) replaces LDP/RSVP-TE in new deployments - simpler, IGP-distributed SIDs, no per-LSP state in the core
- MPLS MTU: each label adds 4 bytes - adjust interface MTU on MPLS links to avoid silent drops

---
## Where to Next

- **Continue:** [MPLS VPNs - L3VPN](mpls-vpns-l3vpn.md) (`CT-002`) - the full L3VPN architecture with VRFs, RD/RT, and MP-BGP
- **Continue:** [Segment Routing - SR-MPLS](segment-routing-mpls.md) (`CT-004`) - the modern evolution; replaces LDP/RSVP-TE
- **Related:** [IS-IS Fundamentals](../routing/isis-fundamentals.md) (`RT-006`) - IS-IS is the most common IGP in MPLS networks; SR-MPLS uses IS-IS TLV extensions
- **Related:** [BGP Fundamentals](../routing/bgp-fundamentals.md) (`RT-007`) - MP-BGP is the signalling protocol for MPLS L3VPN and EVPN
- **Applied context:** [Learning Path: Carrier Engineer](../../../learning-paths/carrier-engineer.md) - MPLS is the foundation of all carrier transport modules

---
## Standards & Certifications

**Relevant standards:**
- [RFC 3031 - Multiprotocol Label Switching Architecture](https://www.rfc-editor.org/rfc/rfc3031)
- [RFC 3032 - MPLS Label Stack Encoding](https://www.rfc-editor.org/rfc/rfc3032)
- [RFC 5036 - LDP Specification](https://www.rfc-editor.org/rfc/rfc5036)
- [RFC 4364 - BGP/MPLS IP Virtual Private Networks (L3VPN)](https://www.rfc-editor.org/rfc/rfc4364)
- [RFC 3209 - RSVP-TE: Extensions to RSVP for LSP Tunnels](https://www.rfc-editor.org/rfc/rfc3209)
- [RFC 4090 - RSVP-TE Fast Reroute](https://www.rfc-editor.org/rfc/rfc4090)

**Where this topic appears in certification syllabi:**

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNP ENCOR 350-401 | Cisco | MPLS concepts; LDP; label operations |
| JNCIS-SP JN0-362 | Juniper | MPLS fundamentals; LDP; LSP |
| Nokia NRS II | Nokia | MPLS architecture; LDP; L3VPN introduction |
| Huawei HCIP-Datacom | Huawei | MPLS basics; label forwarding |

---
## References

- IETF - [RFC 3031: Multiprotocol Label Switching Architecture](https://www.rfc-editor.org/rfc/rfc3031)
- IETF - [RFC 3032: MPLS Label Stack Encoding](https://www.rfc-editor.org/rfc/rfc3032)
- IETF - [RFC 5036: LDP Specification](https://www.rfc-editor.org/rfc/rfc5036)
- Davie, B.; Rekhter, Y. - *MPLS: Technology and Applications*, Morgan Kaufmann, 2000
- Doyle, J.; Carroll, J. - *Routing TCP/IP, Volume II*, Cisco Press, 2001 - Ch. 14–15 (MPLS)
- Pepelnjak, I.; Guichard, J. - *MPLS and VPN Architectures*, Cisco Press, 2002

---
## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - content
**AI assistance:** Draft written by Claude Sonnet 4.6. RFC citations verified against IETF RFC index. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [CT-002](mpls-vpns-l3vpn.md) | MPLS VPNs (L3VPN / VRF) | L3VPN builds directly on MPLS forwarding concepts | 2026-04-19 |
| [CT-004](segment-routing-mpls.md) | Segment Routing (SR-MPLS) | SR-MPLS uses the same label stack; replaces LDP/RSVP-TE | 2026-04-19 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](../routing/routing-fundamentals.md) | Routing Fundamentals | RIB vs FIB; LPM (what MPLS replaces in the core) | 2026-04-19 |
| [RT-004](../routing/ospf-fundamentals.md) | OSPF Fundamentals | OSPF as the common IGP underpinning LDP | 2026-04-19 |
| [RT-006](../routing/isis-fundamentals.md) | IS-IS Fundamentals | IS-IS as IGP in carrier MPLS networks; SR-MPLS uses IS-IS TLVs | 2026-04-19 |
| [RT-007](../routing/bgp-fundamentals.md) | BGP Fundamentals | MP-BGP for L3VPN and EVPN signalling | 2026-04-19 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | Arista EOS |
|---|---|---|---|---|---|
| Enable LDP on interface | RFC 5036 | `mpls ip` on interface | `set protocols ldp interface X` | `configure router ldp interface` | `mpls ldp interface` |
| LDP transport address | RFC 5036 | `mpls ldp router-id Lo0 force` | `set protocols ldp transport-address X` | Set via loopback config | `transport-address interface Lo0` |
| View LDP neighbours | RFC 5036 | `show mpls ldp neighbor` | `show ldp neighbor` | `show router ldp neighbor` | `show mpls ldp neighbor` |
| View label bindings | RFC 5036 | `show mpls ldp bindings` | `show ldp database` | `show router ldp bindings` | `show mpls ldp bindings` |
| View LFIB (forwarding table) | RFC 3031 | `show mpls forwarding-table` | `show route table mpls.0` | `show router fib 1 mpls` | `show mpls forwarding-table` |

### Maintenance Notes

- When CT-002 (MPLS L3VPN) is written, add a back-reference here covering VRF and MP-BGP concepts
- When CT-004 (SR-MPLS) is written, add a comparison note: SR replaces LDP/RSVP-TE; MPLS label stack mechanics are identical
- When IS-IS Advanced or SR modules are written, cross-reference IS-IS TLV extensions for SR SIDs back to the TLV section in RT-006

<!-- XREF-END -->
