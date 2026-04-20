---
title: "BGP Fundamentals"
module_id: "RT-007"
domain: "fundamentals/routing"
difficulty: "advanced"
prerequisites: ["RT-001", "RT-004", "IP-001", "IP-002"]
estimated_time: 60
version: "1.0"
last_updated: "2026-04-19"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: ["bgp", "ebgp", "ibgp", "as-path", "local-pref", "med", "path-vector", "autonomous-system", "route-reflector", "bgp-attributes", "internet-routing"]
cert_alignment: "CCNA 200-301 — 3.5 (awareness) | CCNP ENCOR 350-401 | JNCIS-SP JN0-362 | Nokia NRS II"
vendors: ["Cisco IOS-XE", "Juniper Junos", "Nokia SR-OS", "Arista EOS", "Huawei VRP", "MikroTik RouterOS"]
language: "en"
---

## The Problem

Two separate companies — ISP-A in Asia and ISP-B in Europe. Each runs its own internal network, its own IGP (OSPF or IS-IS), and its own addressing. Their customers want to reach each other. The two ISPs need to exchange routing information.

Can they just use OSPF?

### Step 1: Internal routing doesn't cross trust boundaries

OSPF floods its entire topology to every router in the domain. If ISP-A ran OSPF with ISP-B, ISP-A would see the complete internal topology of ISP-B's network — every router, every link, every address. ISP-B would see ISP-A's. Neither is willing to share this.

More fundamentally: routing policy. ISP-A wants to control which of ISP-B's customers it carries traffic for, how much, and via which paths. ISP-B wants the same control. An IGP has no mechanism for policy — it just finds the shortest path and uses it.

What's needed is a protocol where each party **explicitly decides** what routes to accept, what to advertise, and what policy to apply. The peering relationship itself must be intentional — not auto-discovered.

### Step 2: An explicit session between trusted peers

BGP establishes a **TCP session** between two routers that are explicitly configured to peer with each other (TCP port 179). Nothing happens automatically — you must configure the neighbour's address and the relationship before any routes are exchanged.

The session is between **Autonomous Systems (AS)** — each organisation's independently managed network is identified by an AS number. ISP-A is AS 65001. ISP-B is AS 65002. The BGP session between them is **eBGP (external BGP)** — a session crossing AS boundaries.

### Step 3: Path-vector — carry the full route history

BGP is not distance-vector (doesn't share hop counts) and not link-state (doesn't share topology). BGP is **path-vector**: every route advertisement carries the full list of AS numbers the route has traversed.

When ISP-A advertises its customer prefix `203.0.113.0/24` to ISP-B, the advertisement says:
```text
Network: 203.0.113.0/24
AS_PATH: 65001    (originated in AS 65001)
```

ISP-B re-advertises this to ISP-C with:
```text
Network: 203.0.113.0/24
AS_PATH: 65002 65001    (entered via 65002, originated in 65001)
```

If ISP-C tries to advertise this back to ISP-A: ISP-A sees its own AS number (65001) in the AS_PATH and **rejects the route** — loop detected. This is BGP's loop prevention mechanism: the AS_PATH attribute.

### Step 4: Not all paths are equal — attributes control policy

ISP-B has two paths to `203.0.113.0/24`: one via ISP-A (shorter), one via ISP-C (longer AS_PATH). ISP-B prefers the shorter path — but ISP-B has a business reason to prefer the path via ISP-C (cheaper transit).

BGP provides attributes that let operators express policy:
- **AS_PATH** — the list of ASes; shorter is generally preferred
- **LOCAL_PREF** — a local preference value; higher is better; used internally to prefer one exit point
- **MED (Multi-Exit Discriminator)** — a hint to the adjacent AS about preferred entry point; lower is better
- **COMMUNITIES** — arbitrary tags that carry policy information across AS boundaries

An operator can set LOCAL_PREF=200 on the ISP-C path, overriding the default preference for shorter AS_PATH. BGP does what the operator decides — not what the shortest path is.

### Step 5: Distributing BGP inside one AS

ISP-A has 20 routers. Only 2 of them peer with external ASes (the border routers). But packets arriving at any of the 20 routers might need to reach external destinations. The internal routers need to know BGP routes.

BGP also runs inside one AS — called **iBGP (internal BGP)**. The border routers distribute externally learned routes to all internal routers via iBGP sessions. iBGP does not add AS numbers to the AS_PATH (same AS — no loop risk), but it has a critical rule: **iBGP-learned routes cannot be re-advertised to other iBGP peers** — preventing internal loops.

This means all iBGP speakers in an AS must be fully connected to each other — a **full mesh** of iBGP sessions. With 20 routers, that's 190 sessions. At 100 routers: 4,950 sessions. This doesn't scale.

The solution: **Route Reflectors (RR)**. A Route Reflector re-advertises iBGP-learned routes to other iBGP peers, breaking the full-mesh requirement. Client routers peer only with the RR; the RR distributes routes to all clients. Loop prevention is handled by the RR via the ORIGINATOR_ID and CLUSTER_LIST attributes.

### What You Just Built

BGP — Border Gateway Protocol. A path-vector protocol that establishes explicit TCP peer relationships, carries full AS-path history to prevent loops, uses rich attributes to implement inter-domain routing policy, and scales inside an AS using route reflectors.

| Scenario element | Technical term |
|---|---|
| Independently managed network with its own routing | Autonomous System (AS) |
| BGP session between two different ASes | eBGP (external BGP) |
| BGP session within one AS | iBGP (internal BGP) |
| Full list of AS numbers a route has traversed | AS_PATH attribute |
| Loop detection: own AS in path → reject | AS_PATH loop prevention |
| Local preference for selecting outbound path | LOCAL_PREF attribute |
| Hint to neighbours about preferred inbound path | MED attribute |
| Policy tags carried in BGP advertisements | COMMUNITIES attribute |
| iBGP router that re-advertises routes to other iBGP peers | Route Reflector |

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Explain** what BGP is, why it exists, and how it differs from IGPs (OSPF, IS-IS)
2. **Distinguish** between eBGP and iBGP sessions and explain when each is used
3. **Describe** how AS_PATH works as both a routing attribute and a loop-prevention mechanism
4. **List** the key BGP attributes (AS_PATH, NEXT_HOP, LOCAL_PREF, MED, COMMUNITIES) and explain what each controls
5. **Explain** the BGP best-path selection algorithm at a high level and apply it to a simple scenario
6. **Describe** the iBGP full-mesh requirement and how Route Reflectors address the scaling problem

---

## Prerequisites

- [Routing Fundamentals](routing-fundamentals.md) (`RT-001`) — routing table, AD, metric concepts
- [OSPF Fundamentals](ospf-fundamentals.md) (`RT-004`) — IGP context; contrast with BGP's role
- [IP Addressing Fundamentals](../ip/ip-addressing.md) (`IP-001`) — CIDR notation; prefix aggregation
- [IP Subnetting & VLSM](../ip/subnetting.md) (`IP-002`) — prefix lengths; understanding BGP table entries

---

## Core Content

### Autonomous Systems and AS Numbers

An **Autonomous System (AS)** is a collection of IP networks and routers under a single technical administration, with a consistent routing policy visible to the internet.

AS numbers are 32-bit values (since RFC 6793), written as plain integers (`65001`) or in dotted notation (`0.65001`).

| Range | Purpose |
|---|---|
| 1 – 64511 | Public ASNs — assigned by Regional Internet Registries (ARIN, RIPE, APNIC, etc.) |
| 64512 – 65534 | Private ASNs — for internal use (like RFC 1918 addresses); not advertised on internet |
| 65535 | Reserved |
| 65536 – 4199999999 | 32-bit public ASNs |
| 4200000000 – 4294967294 | 32-bit private ASNs |

Every BGP speaker has an AS number. In eBGP, you always know which AS your peer belongs to. In iBGP, both ends are in the same AS.

### BGP vs IGP — Fundamental Differences

| Property | IGP (OSPF / IS-IS) | BGP |
|---|---|---|
| Scope | Within one AS | Between ASes (and within large ASes) |
| Goal | Find the shortest path | Apply routing policy; exchange reachability |
| Discovery | Automatic (hellos) | Manual — explicitly configured neighbours |
| Transport | IP (OSPF) or L2 (IS-IS) | TCP port 179 |
| Metric | Cost / hop count | Policy attributes (no single metric) |
| Convergence | Seconds | Minutes (large internet tables) |
| Table size | Hundreds to thousands of routes | ~1 million+ prefixes (full internet BGP table) |
| Use case | Fast convergence inside one org | Policy-driven inter-org routing |

BGP is not a replacement for an IGP — every AS still runs an IGP internally. BGP sits on top, exchanging external reachability between ASes.

### BGP Session States

BGP sessions progress through a state machine before routes are exchanged:

| State | What it means |
|---|---|
| **Idle** | BGP is not trying to connect |
| **Connect** | TCP connection attempt in progress |
| **Active** | TCP connection failed; retrying |
| **OpenSent** | TCP connected; OPEN message sent; waiting for peer's OPEN |
| **OpenConfirm** | OPEN received; waiting for KEEPALIVE |
| **Established** | Session up; UPDATE messages (routes) can now be exchanged |

A session stuck in **Active** state means the TCP connection is failing — check IP reachability, ACLs, and whether the far-end is configured.

**BGP message types:**
- **OPEN** — establishes session; negotiates AS number, BGP version, hold timer, Router ID
- **UPDATE** — advertises or withdraws routes; carries path attributes
- **KEEPALIVE** — keeps session alive when no UPDATE to send (default interval: 60s; hold time: 180s)
- **NOTIFICATION** — reports an error; closes the session

### AS_PATH and Loop Prevention

The AS_PATH attribute is a sequence of AS numbers representing the path a route has taken from its origin to the current router.

```text
Origin AS 65001 originates 203.0.113.0/24:
  Advertised to 65002 with AS_PATH: 65001

AS 65002 re-advertises to 65003:
  Prepends own AS: AS_PATH: 65002 65001

AS 65003 re-advertises to 65001 (original AS):
  65001 sees 65001 in AS_PATH → REJECTS — loop detected
```

**AS_PATH manipulation:**
- **AS_PATH prepending** — artificially lengthening the AS_PATH by repeating your own ASN, making a path appear less attractive:
  ```text
  Normal:    AS_PATH: 65001
  Prepended: AS_PATH: 65001 65001 65001
  ```
  Used to make one path less preferred by other ASes — influences inbound traffic from peers.

### BGP Path Attributes

BGP carries rich attributes with every route. These attributes encode policy and preference — they are what distinguish BGP from simple distance-based protocols.

**Mandatory attributes (in every UPDATE):**

| Attribute | Code | Description |
|---|---|---|
| ORIGIN | 1 | How the route entered BGP: `i` (IGP), `e` (EGP, obsolete), `?` (incomplete/redistributed) |
| AS_PATH | 2 | Ordered list of ASes the route traversed |
| NEXT_HOP | 3 | IP address of the next-hop router for this route |

**Well-known discretionary attributes:**

| Attribute | Code | Scope | Description |
|---|---|---|---|
| LOCAL_PREF | 5 | Within one AS | Preference for outbound path; **higher = preferred**; not carried to eBGP peers |
| ATOMIC_AGGREGATE | 6 | Domain | Indicates a more-specific route was suppressed |

**Optional transitive attributes (carried across AS boundaries):**

| Attribute | Code | Description |
|---|---|---|
| COMMUNITY | 8 | Policy tags — 32-bit values; used to signal routing policy between ASes |
| AS4_PATH | 17 | AS_PATH in 4-byte AS format |

**Optional non-transitive attributes (not carried to other ASes):**

| Attribute | Code | Scope | Description |
|---|---|---|---|
| MED | 4 | Between two ASes | Multi-Exit Discriminator — **lower = preferred**; hint to neighbour AS about preferred entry |
| ORIGINATOR_ID | 9 | Within AS | Set by Route Reflector — prevents loops in RR clusters |
| CLUSTER_LIST | 10 | Within AS | RR cluster path — prevents RR loops |

**NEXT_HOP behaviour — a critical detail:**
- In **eBGP**: NEXT_HOP is set to the advertising router's IP (the directly connected eBGP peer address)
- In **iBGP**: NEXT_HOP is **not changed** — iBGP passes the eBGP NEXT_HOP through unchanged
- This means internal routers must be able to reach the eBGP next-hop address, usually via the IGP
- If the iBGP next-hop is unreachable in the IGP, the BGP route exists but is not installed in the routing table

This is the common `next-hop-self` configuration on iBGP sessions from border routers:
```cisco-ios
neighbor 10.0.0.2 next-hop-self
```
This rewrites NEXT_HOP to the border router's own address before advertising to iBGP peers — ensuring internal routers have a reachable next-hop.

### BGP Best-Path Selection

When BGP has multiple paths to the same prefix from different peers, it selects the **best path** using a sequential decision process. The first criterion to produce a winner ends the comparison.

**Cisco IOS BGP best-path algorithm (simplified — memorise the order):**

| Step | Attribute | Prefer |
|---|---|---|
| 1 | Weight (Cisco-only) | Higher |
| 2 | LOCAL_PREF | Higher |
| 3 | Locally originated (network/aggregate) | Prefer locally originated |
| 4 | AS_PATH length | Shorter |
| 5 | ORIGIN code | IGP > EGP > incomplete |
| 6 | MED | Lower |
| 7 | eBGP over iBGP | Prefer eBGP |
| 8 | IGP metric to NEXT_HOP | Lower |
| 9 | Oldest eBGP path (stability) | Older |
| 10 | Router ID of advertising peer | Lower |
| 11 | Cluster list length | Shorter |
| 12 | Peer IP address | Lower |

In practice: **LOCAL_PREF controls outbound exit selection** (which path this AS uses to leave). **MED influences inbound path selection** (which path the neighbouring AS uses to enter). AS_PATH length is the primary inter-AS tiebreaker.

??? supplementary "BGP Communities in Detail"
    BGP Communities (RFC 1997) are 32-bit values attached to routes, formatted as `AS:value` (e.g., `65001:100`). They are used to pass policy signals between networks.

    Well-known communities:
    - `INTERNET` (0x00000000) — advertise to all BGP peers
    - `NO_EXPORT` (0xFFFFFF01) — do not advertise outside the AS
    - `NO_ADVERTISE` (0xFFFFFF02) — do not advertise to any BGP peer
    - `LOCAL_AS` (0xFFFFFF03) — do not send outside the sub-AS (confederation)

    Large communities (RFC 8092) extend this to 96-bit values (`AS:administrator:value`) for richer policy signalling in large networks.

    Example use: a customer tags their route with `65001:100` meaning "deprioritise this route." ISP-A has a route-map that reads this community and sets LOCAL_PREF=50 on the route. Policy is conveyed in the BGP attribute — no out-of-band configuration needed.

### iBGP, Full Mesh, and Route Reflectors

**The iBGP full-mesh requirement:**
The rule "do not re-advertise iBGP-learned routes to other iBGP peers" prevents internal routing loops. But it means every router in the AS must have a direct iBGP session to every other router — a full mesh.

```text
N routers → N×(N-1)/2 sessions
5 routers  → 10 sessions
20 routers → 190 sessions
100 routers → 4,950 sessions
```

**Route Reflectors (RFC 4456):**
A Route Reflector (RR) relaxes the no-readvertise rule: it may re-advertise iBGP-learned routes to its **clients** (other iBGP speakers configured to peer only with the RR).

```text
Without RR (full mesh — 6 sessions for 4 routers):
  R1 ←→ R2, R1 ←→ R3, R1 ←→ R4
  R2 ←→ R3, R2 ←→ R4, R3 ←→ R4

With RR (RR-A is the reflector — 3 sessions):
  R1, R2, R3 all peer only with RR-A
  RR-A reflects routes from R1 to R2 and R3; from R2 to R1 and R3; etc.
```

**RR loop prevention:**
- **ORIGINATOR_ID** — the RR sets this to the Route ID of the originating client. If a reflected route arrives back at the originating router, it recognises its own ORIGINATOR_ID and ignores the route.
- **CLUSTER_LIST** — a list of RR cluster IDs. If an RR receives a route with its own Cluster ID in the CLUSTER_LIST, it discards it.

Best practice: deploy **two RRs** per cluster for redundancy. Clients peer with both RRs; both RRs peer with each other (non-client iBGP session). Single RR failure doesn't break BGP.

### eBGP Configuration Basics

eBGP peers are directly connected in most deployments (though multi-hop eBGP is supported). The key parameters:
- Neighbour IP address
- Remote AS number
- Local AS number (defined globally)
- Prefixes to advertise (via `network` statements or redistribution)

```text
eBGP session: AS 65001 (R1: 10.0.0.1) ↔ AS 65002 (R2: 10.0.0.2)
              directly connected on 10.0.0.0/30
```

---

## Vendor Implementations

BGP is standardised in RFC 4271 (BGP-4). All compliant implementations form sessions with any other. The path attributes and best-path algorithm are standardised, though Cisco adds a local "Weight" attribute (not in the RFC) as step 1 in its decision process.

!!! success "Standard — RFC 4271 (BGP-4)"
    BGP-4 is universally implemented. Multi-vendor eBGP sessions are routine at every internet exchange point on earth. Verify AS numbers, neighbour addresses, and hold timers match across vendors.

!!! warning "Proprietary — Cisco Weight"
    Cisco IOS/IOS-XE/IOS-XR adds a **Weight** attribute (local to the router, not carried in UPDATE messages). Weight overrides all other BGP selection criteria on Cisco routers (step 1, higher = preferred). It is not in RFC 4271 and does not exist on Juniper, Nokia, Arista, or Huawei. Weight-based policy configured on a Cisco router has no effect on path selection at any other vendor.

=== "Cisco IOS-XE"
    ```cisco-ios
    ! Basic eBGP configuration
    router bgp 65001
     bgp router-id 1.1.1.1
     neighbor 10.0.0.2 remote-as 65002        ! eBGP peer
     neighbor 10.0.0.2 description ISP-B

     ! Advertise a prefix
     address-family ipv4
      neighbor 10.0.0.2 activate
      network 203.0.113.0 mask 255.255.255.0  ! must exist in routing table

    ! iBGP peer with next-hop-self
    router bgp 65001
     neighbor 10.1.1.2 remote-as 65001        ! iBGP (same AS)
     neighbor 10.1.1.2 update-source Loopback0
     neighbor 10.1.1.2 next-hop-self

    ! Verify
    show bgp summary
    show bgp ipv4 unicast
    show bgp ipv4 unicast 203.0.113.0/24
    ```
    `update-source Loopback0` sets the source IP of iBGP sessions to the loopback — ensures the session survives individual interface failures. Always use loopbacks for iBGP.

    Full configuration reference: [Cisco BGP Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bgp/configuration/xe-16/irg-xe-16-book.html)

=== "Juniper Junos"
    ```junos
    # eBGP peer
    set protocols bgp group EBGP type external
    set protocols bgp group EBGP peer-as 65002
    set protocols bgp group EBGP neighbor 10.0.0.2

    # iBGP peer (route reflector client example)
    set protocols bgp group IBGP type internal
    set protocols bgp group IBGP local-address 1.1.1.1
    set protocols bgp group IBGP cluster 1.1.1.1           ! RR cluster ID
    set protocols bgp group IBGP neighbor 10.1.1.2

    # Advertise a prefix
    set policy-options policy-statement ADVERTISE term 1 from route-filter 203.0.113.0/24 exact
    set policy-options policy-statement ADVERTISE term 1 then accept
    set protocols bgp group EBGP export ADVERTISE

    # Verify
    show bgp summary
    show bgp neighbor 10.0.0.2
    show route protocol bgp
    ```
    Junos uses groups to organise BGP peers — all peers in a group share the same type (internal/external) and policy. Policy is applied as an export/import policy to the group, not per-neighbour. `cluster` configures this router as a Route Reflector for that group.

    Full configuration reference: [Juniper BGP Configuration Guide](https://www.juniper.net/documentation/us/en/software/junos/bgp/index.html)

=== "Nokia SR-OS"
    ```nokia-sros
    # eBGP peer (classic CLI)
    configure router bgp
        group "EBGP"
            type external
            peer-as 65002
            neighbor 10.0.0.2
                no shutdown
            exit
        exit
        no shutdown
    exit

    # iBGP with route reflector
    configure router bgp
        group "IBGP"
            type internal
            local-address 1.1.1.1
            cluster 1.1.1.1
            neighbor 10.1.1.2
                no shutdown
            exit
        exit
    exit

    # Verify
    show router bgp summary
    show router bgp neighbor 10.0.0.2
    show router bgp routes
    ```
    SR-OS group-based BGP model similar to Junos. Route Reflector is configured with `cluster <id>` under the group. `no shutdown` is required at both the group and neighbour level, and under `bgp` globally.

    Full configuration reference: [Nokia SR-OS BGP Guide](https://documentation.nokia.com/sr/)

=== "Arista EOS"
    ```arista-eos
    ! eBGP peer
    router bgp 65001
       router-id 1.1.1.1
       neighbor 10.0.0.2 remote-as 65002
       neighbor 10.0.0.2 description ISP-B

       ! iBGP with route reflector
       neighbor 10.1.1.2 remote-as 65001
       neighbor 10.1.1.2 update-source Loopback0
       neighbor 10.1.1.2 route-reflector-client

       address-family ipv4
          neighbor 10.0.0.2 activate
          neighbor 10.1.1.2 activate
          network 203.0.113.0/24

    ! Verify
    show bgp summary
    show bgp ipv4 unicast
    ```
    Arista EOS BGP syntax is close to Cisco IOS-XE. `route-reflector-client` is configured per-neighbour on the RR, marking that neighbour as a client.

    Full configuration reference: [Arista EOS BGP Configuration](https://www.arista.com/en/um-eos/eos-bgp)

=== "Huawei VRP"
    ```huawei-vrp
    # eBGP peer
    bgp 65001
     router-id 1.1.1.1
     peer 10.0.0.2 as-number 65002
     peer 10.0.0.2 description ISP-B

     address-family ipv4 unicast
      peer 10.0.0.2 enable
      network 203.0.113.0 255.255.255.0

    # iBGP with route reflector
    bgp 65001
     peer 10.1.1.2 as-number 65001
     peer 10.1.1.2 connect-interface LoopBack0
     address-family ipv4 unicast
      peer 10.1.1.2 enable
      peer 10.1.1.2 reflect-client

    # Verify
    display bgp peer
    display bgp routing-table
    display bgp routing-table 203.0.113.0
    ```
    Huawei VRP uses `peer` (not `neighbor`) for BGP configuration. `reflect-client` marks the peer as an RR client. `connect-interface` sets the source interface for iBGP sessions (equivalent to `update-source`).

    Full configuration reference: [Huawei VRP BGP Configuration](https://support.huawei.com/enterprise/en/doc/EDOC1100278578)

=== "MikroTik RouterOS"
    ```mikrotik-ros
    # eBGP peer
    /routing bgp connection add name=ISP-B remote.as=65002 remote.address=10.0.0.2 \
        local.role=ebgp

    # iBGP peer
    /routing bgp connection add name=RR remote.as=65001 remote.address=10.1.1.2 \
        local.role=ibgp local.address=1.1.1.1

    # Advertise a prefix via an output filter
    /routing filter rule add chain=bgp-out rule="if (dst==203.0.113.0/24) {accept}"

    # Verify
    /routing bgp session print
    /ip route print where bgp
    ```
    RouterOS v7 uses a connection-based BGP model with `local.role` (ebgp/ibgp/rr-client). Policy is applied via routing filter chains. This is a significant redesign from RouterOS v6's `/routing bgp peer` syntax.

    Full configuration reference: [MikroTik BGP Reference](https://help.mikrotik.com/docs/display/ROS/BGP)

---

## Common Pitfalls

### Pitfall 1: Session stuck in Active state

BGP Active state means TCP connections are failing. Check: is the neighbour IP reachable (ping)? Is TCP port 179 permitted by any firewall or ACL? Is the `remote-as` number correct on both sides? Are both routers using the correct source address (especially for iBGP using loopbacks — verify `update-source` is set)?

### Pitfall 2: Routes in BGP table but not in routing table

A BGP route exists in `show bgp` but is absent from `show ip route`. Most common cause: the NEXT_HOP is unreachable. The IGP must have a route to the BGP next-hop address. On iBGP, if `next-hop-self` is not configured on the border router, internal routers receive the eBGP NEXT_HOP (an address only the border router can reach). Fix: configure `next-hop-self` on iBGP sessions from border routers.

### Pitfall 3: Advertising a prefix that isn't in the routing table

Cisco BGP `network` statements only advertise a prefix if an **exact match** exists in the routing table. If you configure `network 203.0.113.0 mask 255.255.255.0` but the routing table only has `203.0.113.0/25` and `203.0.113.128/25`, the /24 is not advertised. Create a static summary route to Null0 to ensure the aggregate prefix exists, then advertise it.

### Pitfall 4: AS_PATH loop prevention blocking a valid path

In some designs (BGP confederations, private ASNs stripped before advertisement), the AS_PATH may legitimately contain your own AS number. The default loop-prevention check will reject these routes. Fix: `allowas-in` permits receiving routes with your own AS in the path (use with care — only when you understand why the loop check is triggering).

### Pitfall 5: iBGP full mesh incomplete

If any iBGP session is missing in a full-mesh design (or any client is not peering with the Route Reflector), routes don't propagate to that router. Symptom: some internal routers can reach external destinations; others cannot. Audit iBGP session topology with `show bgp summary` on every router — every expected session should show `Established`.

---

## Practice Problems

1. Router R1 (AS 65001) has three BGP paths to `198.51.100.0/24`:
   - Path A: LOCAL_PREF=200, AS_PATH: 65002 65010
   - Path B: LOCAL_PREF=100, AS_PATH: 65003
   - Path C: LOCAL_PREF=200, AS_PATH: 65004
   Which path does R1 select as best? Explain step by step.

2. An iBGP border router learns the prefix `203.0.113.0/24` from its eBGP peer at `10.0.0.2`. The border router advertises this to all iBGP peers but does NOT configure `next-hop-self`. Internal routers can see the prefix in `show bgp` but cannot reach it. Why?

3. An AS has 8 iBGP speakers. How many sessions are needed for a full mesh? How many sessions does each router need in a Route Reflector design with 1 RR and 7 clients?

4. What is the purpose of AS_PATH prepending? Give a scenario where an operator would use it.

5. Two BGP paths to the same prefix: Path A has LOCAL_PREF=100, AS_PATH: 65002 65003 (2 ASes). Path B has LOCAL_PREF=100, AS_PATH: 65004 (1 AS). Which does BGP prefer after LOCAL_PREF is compared? Can an operator make Path A preferred? If so, how?

??? "Answers"
    **1.** Step 1 — LOCAL_PREF: Path A and Path C both have LP=200; Path B has LP=100 → Path B is eliminated. Step 2 — AS_PATH length: Path A has 2 ASes (65002 65010); Path C has 1 AS (65004) → **Path C wins** (shorter AS_PATH). Answer: Path C is best.

    **2.** The eBGP NEXT_HOP (`10.0.0.2`) is the border router's external peer address — it is reachable from the border router but not from internal routers (not in the IGP). Internal routers receive the route with NEXT_HOP=10.0.0.2; when they try to resolve this for forwarding, the IGP has no route to 10.0.0.2 → BGP route is not installed in their routing table. Fix: configure `next-hop-self` on the border router's iBGP sessions so internal routers see the border router's loopback as the NEXT_HOP (which is in the IGP).

    **3.** Full mesh: 8×7/2 = **28 sessions** total. With 1 RR and 7 clients: each client peers only with the RR → **7 sessions** total. Each client has 1 session; the RR has 7 sessions.

    **4.** AS_PATH prepending makes a BGP path appear longer (less attractive) by repeating your own AS number. Use case: you have two upstream providers. You want most traffic to use Provider A (lower cost) but keep Provider B as backup. You prepend your AS twice on advertisements to Provider B: `AS_PATH: 65001 65001 65001`. Provider B's other customers see a 3-hop path via you; Provider A's customers see a 1-hop path. Traffic flows primarily via Provider A.

    **5.** After LOCAL_PREF tie (both 100), step 4 is AS_PATH length: Path B (1 AS) is shorter → **Path B wins**. To make Path A preferred: raise LOCAL_PREF on Path A above 100 (e.g., LP=200) — LOCAL_PREF is evaluated before AS_PATH length and overrides it. Alternatively, use AS_PATH prepending on Path B to artificially lengthen it to 2+ ASes.

---

## Summary & Key Takeaways

- **BGP (Border Gateway Protocol)** is the routing protocol of the internet — it exchanges reachability between Autonomous Systems
- Each organisation managing its own network is an **Autonomous System (AS)**, identified by an AS number
- **eBGP** (external BGP) runs between different ASes; **iBGP** (internal BGP) distributes routes within one AS
- BGP establishes **TCP sessions (port 179)** to explicitly configured peers — nothing is auto-discovered
- BGP is **path-vector**: every route advertisement carries the full AS_PATH — the ordered list of ASes traversed
- **Loop prevention**: if a router sees its own AS in the AS_PATH, it rejects the route
- Key attributes: **LOCAL_PREF** (outbound exit selection — higher wins), **MED** (inbound hint — lower wins), **AS_PATH** (loop prevention and path length), **COMMUNITIES** (policy tags)
- BGP best-path selection is sequential: LOCAL_PREF → AS_PATH length → ORIGIN → MED → eBGP>iBGP → IGP metric → Router ID
- **iBGP full mesh** is required when no Route Reflectors are used: N routers need N×(N-1)/2 sessions
- **Route Reflectors** (RFC 4456) break the full-mesh requirement; clients peer only with the RR; the RR reflects routes between clients using ORIGINATOR_ID and CLUSTER_LIST for loop prevention
- BGP NEXT_HOP is not changed on iBGP sessions — internal routers must reach the eBGP next-hop via the IGP; use `next-hop-self` on border routers to fix this

---

## Where to Next

- **Continue:** [MPLS Fundamentals](../carrier-transport/mpls-fundamentals.md) (`CT-001`) — MPLS builds on BGP and IGP foundations; BGP VPNs (L3VPN) use MP-BGP
- **Advanced:** [BGP Advanced — Attributes, Policies, Communities](bgp-advanced.md) (`RT-008`) — route-maps, prefix-lists, community policy, confederations
- **Related:** [OSPF Fundamentals](ospf-fundamentals.md) (`RT-004`) / [IS-IS Fundamentals](isis-fundamentals.md) (`RT-006`) — the IGP that runs under BGP in every AS
- **Applied context:** [Learning Path: Data Network Engineer](../../../learning-paths/data-network-engineer.md) — Stage 3, position 15 in the DNE path

---

## Standards & Certifications

**Relevant standards:**
- [RFC 4271 — BGP-4](https://www.rfc-editor.org/rfc/rfc4271)
- [RFC 4456 — BGP Route Reflection](https://www.rfc-editor.org/rfc/rfc4456)
- [RFC 1997 — BGP Communities Attribute](https://www.rfc-editor.org/rfc/rfc1997)
- [RFC 8092 — BGP Large Communities](https://www.rfc-editor.org/rfc/rfc8092)
- [RFC 6793 — BGP Support for Four-Octet AS Numbers](https://www.rfc-editor.org/rfc/rfc6793)
- [RFC 4760 — Multiprotocol Extensions for BGP-4 (MP-BGP)](https://www.rfc-editor.org/rfc/rfc4760)

**Benchmark certifications** — use these to self-assess your understanding, not as a study guide:

| Cert | Vendor | Relevant Section |
|---|---|---|
| CCNA 200-301 | Cisco | 3.5 — BGP awareness; eBGP/iBGP concepts |
| CCNP ENCOR 350-401 | Cisco | BGP attributes; path selection; route reflectors |
| JNCIS-SP JN0-362 | Juniper | BGP fundamentals; eBGP/iBGP; attributes |
| Nokia NRS II | Nokia | BGP in SP context; attributes; RR design |

---

## References

- IETF — [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- IETF — [RFC 4456: BGP Route Reflection](https://www.rfc-editor.org/rfc/rfc4456)
- IETF — [RFC 4760: Multiprotocol Extensions for BGP-4](https://www.rfc-editor.org/rfc/rfc4760)
- Odom, W. — *CCNA 200-301 Official Cert Guide, Volume 2*, Cisco Press, 2019 — Ch. 14 (BGP awareness)
- Doyle, J.; Carroll, J. — *Routing TCP/IP, Volume II*, Cisco Press, 2001 — Ch. 9–13 (BGP)
- Halabi, S. — *Internet Routing Architectures*, 2nd ed., Cisco Press, 2000

---

## Attribution & Licensing

**Author:** [@geekazoid80]
**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — content
**AI assistance:** Draft written by Claude Sonnet 4.6. RFC citations verified against IETF RFC index. Technical accuracy to be verified by human reviewer before `human_reviewed` is set to true.

---

<!-- XREF-START -->
## Internal Cross-References

### Modules That Reference This Module

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [CT-001](../carrier-transport/mpls-fundamentals.md) | MPLS Fundamentals | MP-BGP used for MPLS VPN signalling | 2026-04-19 |
| [RT-008](bgp-advanced.md) | BGP Advanced | Builds on all concepts introduced here | 2026-04-19 |

### Modules This Module References

| Module ID | Title | Context | Last Checked |
|---|---|---|---|
| [RT-001](routing-fundamentals.md) | Routing Fundamentals | Routing table, AD (eBGP=20, iBGP=200) | 2026-04-19 |
| [RT-004](ospf-fundamentals.md) | OSPF Fundamentals | OSPF as the IGP under BGP in enterprise networks | 2026-04-19 |
| [RT-006](isis-fundamentals.md) | IS-IS Fundamentals | IS-IS as the IGP under BGP in carrier networks | 2026-04-19 |
| [IP-001](../ip/ip-addressing.md) | IP Addressing Fundamentals | CIDR notation for BGP prefix advertisement | 2026-04-19 |
| [IP-002](../ip/subnetting.md) | IP Subnetting & VLSM | Prefix aggregation and summarisation in BGP | 2026-04-19 |
| [IP-003](../ip/ipv6-addressing.md) | IPv6 Addressing | MP-BGP carries IPv6 prefixes (address-family ipv6) | 2026-04-19 |

### Vendor Mapping

| Concept | Standard | Cisco IOS-XE | Juniper Junos | Nokia SR-OS | Arista EOS | Huawei VRP | MikroTik RouterOS |
|---|---|---|---|---|---|---|---|
| Configure eBGP peer | RFC 4271 | `neighbor X remote-as Y` | `group type external; peer-as Y; neighbor X` | `group type external; peer-as Y; neighbor X` | `neighbor X remote-as Y` | `peer X as-number Y` | `/routing bgp connection local.role=ebgp` |
| Configure iBGP peer | RFC 4271 | `neighbor X remote-as <own-AS>` | `group type internal; neighbor X` | `group type internal; neighbor X` | `neighbor X remote-as <own-AS>` | `peer X as-number <own-AS>` | `local.role=ibgp` |
| Route Reflector client | RFC 4456 | `neighbor X route-reflector-client` | `cluster <id>` on group | `cluster <id>` on group | `neighbor X route-reflector-client` | `peer X reflect-client` | `local.role=rr-client` |
| View BGP session summary | RFC 4271 | `show bgp summary` | `show bgp summary` | `show router bgp summary` | `show bgp summary` | `display bgp peer` | `/routing bgp session print` |
| View BGP routes | RFC 4271 | `show bgp ipv4 unicast` | `show route protocol bgp` | `show router bgp routes` | `show bgp ipv4 unicast` | `display bgp routing-table` | `/ip route print where bgp` |

### Maintenance Notes

- When CT-001 (MPLS Fundamentals) is written, update the RT-007 XREF to note which MPLS features use MP-BGP (L3VPN, EVPN)
- When RT-008 (BGP Advanced) is written, this module should be its primary prerequisite

<!-- XREF-END -->
