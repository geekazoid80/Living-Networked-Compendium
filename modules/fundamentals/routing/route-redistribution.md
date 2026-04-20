---
id: RT-009
title: "Route Redistribution & Policy"
description: "How routes are moved between different routing protocols, the risks of mutual redistribution, and how route-maps and prefix-lists control what gets redistributed."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - RT-004
  - RT-007
  - RT-008
  - SEC-001
learning_path_tags:
  - DNE
  - CE
difficulty: advanced
tags:
  - redistribution
  - routing
  - route-map
  - policy
  - ospf
  - bgp
  - eigrp
created: 2026-04-19
updated: 2026-04-19
---

# RT-009 — Route Redistribution & Policy

## The Problem

You're merging two companies. Company A runs OSPF; Company B runs EIGRP. You need both to reach each other's networks. They share one border router. That router speaks both protocols. How do you move routes from one protocol's table into the other without creating loops or losing control of what crosses the boundary?

### Step 1: Import routes from one protocol into another

The border router knows OSPF routes and EIGRP routes separately. You tell it to take routes known via OSPF and inject them into the EIGRP process as external routes, and vice versa. This is **redistribution**. Each protocol gets a snapshot of the other's prefixes, tagged as "external" so they're treated with lower preference than internal routes.

### Step 2: Control the flood

Redistributing everything in both directions introduces every route from both networks into both protocols. On large networks this causes LSDB inflation, slow SPF, and — critically — the risk of routing loops where traffic intended for Network A re-enters and circulates.

A **route-map or distribute-list** controls what flows across the boundary: only specific prefixes, only certain next-hops, only routes with a specific tag.

### Step 3: Administrative distance and loop prevention

When a route appears in two protocols simultaneously, the router installs the one with the lower administrative distance. If OSPF has AD 110 and EIGRP has AD 90, the EIGRP version wins — even if that route was originally redistributed from OSPF into EIGRP. This creates a loop: OSPF gets the route from EIGRP, EIGRP gets it from OSPF, traffic circles. **Tagging** breaks this: tag routes as they cross the boundary and filter routes carrying that tag in the reverse direction.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Moving routes between routing protocol domains | Redistribution |
| Router running two protocols at once | Boundary router / ASBR |
| Incoming route from another protocol | External route |
| Routing loop from mutual redistribution | Sub-optimal path / redistribution loop |
| Marker on a redistributed route | Route tag |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why redistribution is necessary and the risks it introduces.
2. Configure one-way and mutual redistribution between OSPF, BGP, and static routes.
3. Use route-maps to filter and control what is redistributed.
4. Apply route tagging to prevent redistribution loops in mutual redistribution scenarios.
5. Explain how administrative distance interacts with redistribution.
6. Describe the seed metric requirement for OSPF and other protocols.

---

## Prerequisites

- RT-004 — OSPF Fundamentals (ASBR concept, Type 5 LSAs)
- RT-007 — BGP Fundamentals (BGP redistribution context)
- RT-008 — BGP Advanced (route-maps, prefix-lists)
- SEC-001 — ACLs (prefix-list and ACL match syntax used in distribute-lists)

---

## Core Content

### Redistribution Basics

Every routing protocol maintains its own routing table (or contributes routes to the RIB). Redistribution moves routes from one protocol's knowledge into another protocol's advertisement.

Key requirements:
- The redistributing router must be running both protocols.
- A **seed metric** must be provided — most protocols cannot accept a metric of 0 or will assign a default (infinite) metric that makes the route unusable.
- The redistributed routes appear as **external** routes in the receiving protocol (OSPF Type 5/7, EIGRP External, BGP routes with ORIGIN of Incomplete).

### Seed Metrics

| Destination protocol | Default seed metric | Required? | Recommendation |
|---|---|---|---|
| OSPF | 20 (if not set) | No, but best practice | Set explicitly: `metric 10 metric-type 1` |
| EIGRP | None (must specify) | Yes — missing = routes not redistributed | Set explicitly with bandwidth/delay |
| RIP | None (must specify) | Yes | Set hop count |
| BGP | 0 (IGP routes) | No | Set MED if needed |
| IS-IS | 0 or default | Platform-dependent | Set explicitly |

For EIGRP, seed metrics require five values: bandwidth, delay, reliability, load, MTU:
```
redistribute ospf 1 metric 1000 100 255 1 1500
```
(bandwidth 1000 kbps, delay 100 µs, reliability 255/255, load 1/255, MTU 1500)

### One-Way Redistribution (Common and Safe)

The simplest case: redistribute routes from one direction only.

**Static to OSPF:** A branch site has a static default route. Redistribute it into OSPF so all OSPF routers know to reach the internet via this router.

```
router ospf 1
 redistribute static subnets metric 10 metric-type 1
```

**BGP to OSPF (at ISP boundary):** An edge router learns customer prefixes via BGP. Redistribute specific customer prefixes into the IGP so internal routers can reach them. (More commonly: keep BGP routes in BGP only and ensure OSPF is used only for loopback reachability. Full table redistribution from BGP to IGP is dangerous at scale.)

**IGP to BGP:** An edge router redistributes internal IGP routes into BGP to advertise them to external peers. Commonly filtered with a prefix-list to allow only the intended public prefixes.

### Mutual Redistribution (OSPF ↔ EIGRP)

When routes must flow in both directions, the boundary router imports OSPF into EIGRP and EIGRP into OSPF. This creates two risks:

**1. Sub-optimal routing:** A route redistributed from OSPF into EIGRP may return from EIGRP back into OSPF — the router now has two paths to the same destination (one native OSPF, one via EIGRP→OSPF). The one with lower administrative distance wins:

- Native OSPF: AD 110
- EIGRP external: AD 170 (higher — less preferred)
- EIGRP internal: AD 90 (lower than OSPF — may override)

If a route was originally OSPF, travelled into EIGRP as EIGRP External (AD 170), and comes back into OSPF — the returning path has higher AD than the original OSPF route. This is benign. But if it becomes an EIGRP Internal route somehow, the EIGRP version (AD 90) overrides the original OSPF (AD 110), causing routing through the boundary router unnecessarily.

**2. Redistribution loops:** Traffic from an OSPF router reaches the boundary, crosses to EIGRP, is redistributed back into OSPF somewhere else, crosses back to EIGRP... The packet circulates until TTL expires. This is rare but destructive when it occurs.

### Loop Prevention: Route Tagging

Apply a **route tag** to routes as they cross the boundary. On the other side, filter out routes carrying that tag before they re-enter the source protocol.

```
! On the OSPF→EIGRP boundary:
route-map OSPF-TO-EIGRP permit 10
 set tag 100    ! Tag routes coming from OSPF

router eigrp 100
 redistribute ospf 1 route-map OSPF-TO-EIGRP metric 1000 100 255 1 1500

! On the EIGRP→OSPF boundary (same or different router):
route-map EIGRP-TO-OSPF deny 10
 match tag 100   ! Block routes tagged 100 (they originated in OSPF)
route-map EIGRP-TO-OSPF permit 20
 ! Everything else passes

router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP-TO-OSPF
```

### Redistribution Between BGP and IGP

**IGP → BGP:** Use a route-map with a prefix-list to allow only intended public prefixes into BGP:

```
route-map IGP-TO-BGP permit 10
 match ip address prefix-list PUBLIC-PREFIXES

router bgp 65000
 redistribute ospf 1 route-map IGP-TO-BGP
```

**BGP → IGP:** Almost never redistribute the full BGP table into an IGP. Even a small ISP's BGP table has 900,000+ prefixes — this would destroy the IGP LSDB. Instead:
- Redistribute only specific prefixes (customer routes) using a tight prefix-list.
- Or: use OSPF/IS-IS only for loopback reachability (for iBGP next-hop resolution); keep customer routes in BGP only.

### Conditional Route Advertisement

Some scenarios require advertising a route only when a specific condition is met (e.g., advertise a backup static route into OSPF only when the primary route is absent). Cisco IOS supports **track objects** with `ip sla` for conditional route tracking; BGP can use `conditional-advertisement` to advertise a prefix only when a condition in the BGP table is met.

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Static → OSPF with metric and tag
    ip prefix-list STATIC-ALLOWED seq 5 permit 10.0.0.0/8 ge 24

    route-map STATIC-TO-OSPF permit 10
     match ip address prefix-list STATIC-ALLOWED
     set metric 10
     set metric-type type-1
     set tag 200

    router ospf 1
     redistribute static subnets route-map STATIC-TO-OSPF

    ! OSPF → BGP (filtered)
    route-map OSPF-TO-BGP permit 10
     match ip address prefix-list PUBLIC-ONLY
    route-map OSPF-TO-BGP deny 20

    router bgp 65000
     redistribute ospf 1 route-map OSPF-TO-BGP

    ! Verification
    show ip ospf database external
    show bgp ipv4 unicast | include >
    show ip route | include E EX
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/configuration/xe-17/iro-ospf-xe-17-book/iro-redist-ospf.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/configuration/xe-17/iro-ospf-xe-17-book/iro-redist-ospf.html)

=== "Juniper (Junos)"

    ```
    # OSPF export policy (OSPF → BGP)
    set policy-options prefix-list PUBLIC-ONLY 203.0.113.0/24

    set policy-options policy-statement OSPF-TO-BGP term ALLOW from protocol ospf
    set policy-options policy-statement OSPF-TO-BGP term ALLOW from prefix-list PUBLIC-ONLY
    set policy-options policy-statement OSPF-TO-BGP term ALLOW then accept
    set policy-options policy-statement OSPF-TO-BGP term DENY then reject

    set protocols bgp group IBGP export OSPF-TO-BGP

    # Static → OSPF
    set policy-options policy-statement STATIC-TO-OSPF term STATIC from protocol static
    set policy-options policy-statement STATIC-TO-OSPF term STATIC then accept

    set protocols ospf export STATIC-TO-OSPF
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/routing-policy/topics/topic-map/policy-route-redistribution.html](https://www.juniper.net/documentation/us/en/software/junos/routing-policy/topics/topic-map/policy-route-redistribution.html)

---

## Common Pitfalls

1. **Redistributing BGP full table into IGP.** The BGP full internet routing table contains 900,000+ prefixes. Redistributing it into OSPF fills the LSDB immediately and crashes every OSPF router in the area. Never redistribute BGP into an IGP without a tight prefix-list filter.

2. **Missing seed metric for EIGRP.** OSPF → EIGRP redistribution without a metric causes routes to be redistributed with an infinite metric — they appear in EIGRP but are unreachable. Always specify `metric bandwidth delay reliability load mtu`.

3. **Forgetting route tags in mutual redistribution.** Without tagging, routes bounce back across the boundary. A symptom is seeing the same prefix multiple times in the routing table with different ADs, or unexpected path selection.

4. **Forgetting `subnets` in OSPF redistribution.** Only classful networks are redistributed without `subnets`. All /25–/32 prefixes are silently omitted.

5. **OSPF AD comparison against EIGRP.** OSPF internal AD is 110; EIGRP external is 170. A prefix redistributed from OSPF into EIGRP (EIGRP external, AD 170) loses to the original OSPF route (AD 110) — correct. But if that EIGRP external somehow gets treated as EIGRP internal (AD 90), it overrides the OSPF route — incorrect and loop-inducing.

---

## Practice Problems

**Q1.** You redistribute static routes into OSPF. A /28 prefix is not appearing in other OSPF routers' routing tables. What are the two most likely causes?

??? answer
    (1) Missing `subnets` keyword — OSPF only redistributes classful routes without it; the /28 is non-classful. Add `redistribute static subnets`. (2) Missing or missing seed metric — some platforms require an explicit metric; without it routes may be redistributed with metric infinity (unusable).

**Q2.** In a mutual OSPF ↔ EIGRP redistribution, you tag all routes redistributed from OSPF with tag 100. What do you do with that tag on the EIGRP → OSPF boundary?

??? answer
    Match and deny routes with tag 100 before the permit-all in the EIGRP → OSPF route-map. This prevents routes that originated in OSPF (tagged with 100 when they crossed to EIGRP) from re-entering OSPF. Only routes that originated natively in EIGRP (no tag 100) are redistributed back into OSPF.

**Q3.** Why is redistributing the BGP full table into OSPF dangerous?

??? answer
    The BGP full internet table has ~900,000+ prefixes. OSPF uses LSA flooding — every OSPF router in the area would receive a Type 5 LSA for each prefix. This inflates the LSDB to millions of entries, triggering SPF recalculations that consume 100% CPU and memory on every OSPF router. The network collapses. BGP should remain separate from the IGP; the IGP carries only loopback and infrastructure routes.

---

## Summary & Key Takeaways

- **Redistribution** moves routes between routing protocol domains — requires a border router running both protocols.
- **Seed metrics** must be set explicitly — missing metrics cause routes to be advertised but unreachable.
- One-way redistribution is simple and safe; **mutual redistribution** requires loop prevention.
- **Route tagging** prevents loops: tag routes crossing the boundary; filter tags on the return direction.
- OSPF redistribution requires `subnets` keyword (Cisco) for non-classful routes.
- **Never redistribute BGP full table into an IGP** without strict prefix-list filtering.
- Administrative distance determines which protocol's version of a route wins; the interaction with redistribution can cause unexpected path selection.

---

## Where to Next

- **CT-002 — MPLS VPNs (L3VPN):** L3VPN uses BGP to carry VPN routes between PE routers.
- **RT-004 — OSPF Fundamentals:** Review Type 5 LSA generation by the ASBR.
- **RT-008 — BGP Advanced:** Route-maps for BGP filtering (used in redistribution policy).

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 2328 | OSPF — ASBR and external routes (Type 5/7 LSA) |
| Cisco CCNP Enterprise | Route redistribution, mutual redistribution, tagging |
| Juniper JNCIP-SP | Policy-based redistribution in Junos |

---

## References

- RFC 2328 — OSPF Version 2 (ASBR and external LSA). [https://www.rfc-editor.org/rfc/rfc2328](https://www.rfc-editor.org/rfc/rfc2328)

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
| CT-002 | MPLS VPNs L3VPN | L3VPN uses BGP redistribution from PE-CE routing |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| RT-004 | OSPF Fundamentals | ASBR concept, Type 5 LSAs |
| RT-007 | BGP Fundamentals | BGP redistribution context |
| RT-008 | BGP Advanced | Route-maps used in redistribution policy |
<!-- XREF-END -->
