---
id: RT-008
title: "BGP Advanced — Communities, Policy & Filtering"
description: "BGP community tagging, route-maps, prefix-lists, AS-path filters, and traffic engineering with local preference, MED, and prepending."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 60
prerequisites:
  - RT-007
learning_path_tags:
  - DNE
  - CE
difficulty: advanced
tags:
  - bgp
  - routing
  - communities
  - route-map
  - policy
  - traffic-engineering
created: 2026-04-19
updated: 2026-04-19
---

# RT-008 — BGP Advanced — Communities, Policy & Filtering

## The Problem

You're a network operator connected to two ISPs. You want routes learned from ISP-A to be preferred over ISP-B for customer traffic, but you want your own prefixes to be preferred via ISP-B for outbound traffic. You also want to tag routes from certain customers so that upstream peers can apply their own preferences without you hardcoding every case in your own router's policy.

BGP's path selection algorithm (RT-007) determines best path — but its inputs are all attributes. **Policy** means systematically modifying those attributes as routes enter or leave your network. **Communities** allow you to attach arbitrary signals to routes so that distant peers can act on them without knowing your internal topology.

### Step 1: Route-maps — the policy engine

A route-map is an ordered list of match conditions and set actions. "If this route matches community X and prefix-list Y → set local-preference 200." BGP applies route-maps at the point where routes enter or leave the BGP table — at `neighbor <ip> route-map <name> in|out`.

### Step 2: Communities — scalable signalling

Without communities, you'd need to write separate policy for every prefix. With communities, you tag a group of routes with a well-known or custom value (e.g., `65000:100`) and write policy against the tag. When the set of routes changes, you only update the tagging — the policy at the consumer remains unchanged. Communities propagate with the route, surviving multiple AS hops (unless stripped).

### Step 3: Traffic engineering

Influencing outbound traffic: adjust **local preference** (higher = preferred). Influencing inbound traffic (how other ASes send traffic to you): adjust **MED** (lower = preferred, only advisory) or **AS-path prepending** (add copies of your own AS to make a path appear longer → less preferred).

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Match + set ordered policy engine | Route-map |
| Ordered prefix match tool | Prefix-list |
| Regular expression match on AS_PATH | AS-path filter |
| Arbitrary tag attached to a route | BGP community |
| Influence inbound traffic via path length | AS-path prepending |
| Hint to a peer about preferred entry point | MED |
| Standard community format (AS:value) | RFC 1997 community |
| Extended community (larger value space) | RFC 4360 extended community |

---

## Learning Objectives

After completing this module you will be able to:

1. Write route-maps that match BGP prefixes and set BGP attributes.
2. Configure prefix-lists and AS-path filters for BGP route filtering.
3. Explain BGP communities (standard, extended, large) and common well-known communities.
4. Use communities to implement inbound and outbound traffic engineering.
5. Configure AS-path prepending for inbound traffic engineering.
6. Implement a simple multi-homed BGP policy (prefer one ISP for inbound, one for outbound).

---

## Prerequisites

- RT-007 — BGP Fundamentals (eBGP/iBGP, path-vector, AS_PATH, 12-step best-path algorithm, attributes)

---

## Core Content

### Route-Maps

A route-map consists of numbered **clauses** (sequences), each with:
- **match** statements: conditions that must be true (prefix-list, community, AS-path, IP address)
- **set** statements: attribute modifications to apply if all matches pass
- **permit** or **deny** action for the clause

Processing: top-to-bottom, first match wins. A `deny` clause drops the route from BGP (does not forward it). A `permit` clause applies the set actions and passes the route. A route not matching any clause is **implicitly denied** by the route-map — use a final `permit 65535` with no match to create a "permit all else" default.

```
route-map MY-POLICY permit 10
 match prefix-list IMPORTANT-PREFIXES
 set local-preference 200
!
route-map MY-POLICY permit 20
 match community 65000:100
 set local-preference 150
!
route-map MY-POLICY permit 65535
 ! No match — permit everything else (default)
```

### Prefix-Lists

Prefix-lists match BGP prefixes with optional length qualifiers. More efficient than ACLs for BGP because prefix-lists are specifically designed for prefix matching and binary-search optimised.

```
ip prefix-list ALLOW-SPECIFICS seq 5 permit 10.0.0.0/8 ge 24 le 28
```

`ge 24 le 28`: match any prefix within 10.0.0.0/8 with prefix length ≥24 and ≤28.

```
ip prefix-list DEFAULT-ONLY seq 5 permit 0.0.0.0/0
ip prefix-list DEFAULT-ONLY seq 10 deny 0.0.0.0/0 le 32
```

Use prefix-lists in `neighbor <ip> prefix-list <name> in|out` for simple filtering, or within route-maps for more complex policy.

### AS-Path Filters

AS-path filter uses **regular expressions** to match the AS_PATH string. Applied with `ip as-path access-list`.

Common patterns:

| Pattern | Matches |
|---|---|
| `^$` | Empty AS_PATH — routes originated locally or by direct eBGP peer |
| `^65001$` | Routes originated by AS 65001 only (not transited) |
| `^65001_` | Routes where AS 65001 is the first AS (directly from AS 65001) |
| `_65001$` | Routes originated in AS 65001 (regardless of transit) |
| `.*` | Any AS_PATH — match all |
| `^(65001\|65002)$` | Routes originated directly by AS 65001 or AS 65002 |

```
ip as-path access-list 1 permit ^65001_
neighbor 10.1.1.1 filter-list 1 in
```

### BGP Communities

A **BGP community** is a 32-bit value attached to a route, formatted as `AS:value` (e.g., `65000:100`). Communities are transitive within the BGP domain by default (they propagate unless stripped).

**Well-known communities (RFC 1997):**

| Community | Meaning |
|---|---|
| `no-export` (0xFFFFFF01) | Do not advertise outside this AS — stays within confederation |
| `no-advertise` (0xFFFFFF02) | Do not advertise to any peer (including iBGP) |
| `local-as` (0xFFFFFF03) | Do not export outside the local AS (including confederation peers) |
| `internet` (0x00000000) | Advertise to all (default; no restriction) |

**Custom communities:** Operators define their own schemes. Example: `65000:100` = "learned from customer," `65000:200` = "learned from peer," `65000:300` = "learned from transit."

**Extended communities (RFC 4360):** 8-byte communities used for MPLS VPNs (Route Target, Route Distinguisher), EVPN, and other advanced applications. Format: type-dependent (e.g., RT `1:100`).

**Large communities (RFC 8092):** 12-byte communities for large ASN deployments. Format: `ASN:DAtA:vALUE` (three 32-bit fields). Resolves ambiguity in 32-bit AS environments where standard communities' 16-bit AS field is too small.

#### Setting and Matching Communities

```
! Set community on outbound routes
route-map SET-COMM permit 10
 set community 65000:100 additive     ! additive: adds to existing; without additive: replaces

! Match community
ip community-list standard CUSTOMER-ROUTES permit 65000:100
route-map PROCESS-CUSTOMER permit 10
 match community CUSTOMER-ROUTES
 set local-preference 200
```

On Cisco: communities are not sent to eBGP peers by default. Enable with:
```
neighbor <ip> send-community [both|extended|standard]
```

### Outbound Traffic Engineering (Influencing Traffic Out)

Operators control which exit point traffic uses by adjusting **local preference**:
- Higher local preference = route more preferred in the BGP best-path algorithm (step 4 of 12).
- Set local preference inbound on the neighbor receiving routes from the preferred upstream.

```
! Routes from ISP-A (preferred for internet exit)
neighbor 10.1.1.1 route-map PREFER-ISP-A in
route-map PREFER-ISP-A permit 10
 set local-preference 200

! Routes from ISP-B (backup)
neighbor 10.2.2.1 route-map BACKUP-ISP-B in
route-map BACKUP-ISP-B permit 10
 set local-preference 100
```

### Inbound Traffic Engineering (Influencing Others' Routing to You)

Operators influence how traffic from other networks reaches them:

**MED (Multi-Exit Discriminator):** A hint to eBGP peers about the preferred entry point among multiple paths into your AS. Lower MED = preferred. Only advisory — the peer may ignore it. Effective only between same AS peers (MED comparison is limited by `bgp always-compare-med` or `deterministic-med` policies).

```
route-map SET-MED permit 10
 set metric 50    ! MED value (lower = preferred entry)
neighbor <isp-peer-1> route-map SET-MED out
```

**AS-Path Prepending:** Add extra copies of your own ASN to the AS_PATH of routes advertised to a specific peer. Makes the path appear longer → less preferred by the peer's best-path algorithm (step 6: shortest AS_PATH wins).

```
route-map PREPEND-FOR-ISP-B permit 10
 set as-path prepend 65000 65000 65000    ! Add AS 65000 three times
neighbor <isp-b-peer> route-map PREPEND-FOR-ISP-B out
```

Use sparingly — excessive prepending can cause asymmetric routing and complicate troubleshooting.

### Common Multi-Homed Policy Pattern

Two ISPs, active/standby:

```
! From ISP-A (primary): accept all, set high local-pref
neighbor ISP-A route-map FROM-ISP-A in
route-map FROM-ISP-A permit 10
 set local-preference 200

! From ISP-B (backup): accept all, set low local-pref
neighbor ISP-B route-map FROM-ISP-B in
route-map FROM-ISP-B permit 10
 set local-preference 100

! To ISP-B (secondary): prepend our ASN to discourage inbound via ISP-B
neighbor ISP-B route-map TO-ISP-B out
route-map TO-ISP-B permit 10
 set as-path prepend 65000 65000
```

---

## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Prefix list
    ip prefix-list CUSTOMER-PREFIXES seq 5 permit 10.0.0.0/8 ge 24

    ! AS-path filter
    ip as-path access-list 1 permit ^65001_

    ! Community list
    ip community-list standard CUST permit 65000:100

    ! Route-map
    route-map INBOUND-POLICY permit 10
     match ip address prefix-list CUSTOMER-PREFIXES
     match community CUST
     set local-preference 200
    route-map INBOUND-POLICY permit 65535

    ! Apply to neighbor
    router bgp 65000
     neighbor 10.1.1.1 route-map INBOUND-POLICY in
     neighbor 10.1.1.1 send-community both
     neighbor 10.1.1.1 filter-list 1 in

    ! Verification
    show bgp ipv4 unicast neighbors 10.1.1.1 received-routes
    show bgp ipv4 unicast community 65000:100
    show bgp ipv4 unicast regexp ^65001_
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bgp/configuration/xe-17/irg-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bgp/configuration/xe-17/irg-xe-17-book.html)

=== "Juniper (Junos)"

    ```
    # Prefix list
    set policy-options prefix-list CUSTOMER-PREFIXES 10.0.0.0/8

    # AS-path regular expression
    set policy-options as-path CUST-AS "^65001 .*"

    # Community
    set policy-options community CUST-COMM members 65000:100

    # Policy (route-map equivalent)
    set policy-options policy-statement INBOUND-POLICY term MATCH from prefix-list CUSTOMER-PREFIXES
    set policy-options policy-statement INBOUND-POLICY term MATCH from community CUST-COMM
    set policy-options policy-statement INBOUND-POLICY term MATCH then local-preference 200
    set policy-options policy-statement INBOUND-POLICY term MATCH then accept
    set policy-options policy-statement INBOUND-POLICY term DEFAULT then accept

    # Apply
    set protocols bgp group UPSTREAMS neighbor 10.1.1.1 import INBOUND-POLICY
    set protocols bgp group UPSTREAMS neighbor 10.1.1.1 export OUTBOUND-POLICY

    # Verification
    show route receive-protocol bgp 10.1.1.1
    show route community 65000:100
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/bgp/topics/topic-map/bgp-policy-community.html](https://www.juniper.net/documentation/us/en/software/junos/bgp/topics/topic-map/bgp-policy-community.html)

=== "Nokia SR-OS"

    ```
    configure router policy-options
        prefix-list "CUSTOMER-PREFIXES"
            prefix 10.0.0.0/8 longer

        community "CUST-COMM"
            member "65000:100"

        policy-statement "INBOUND-POLICY"
        entry 10
            from
                prefix-list "CUSTOMER-PREFIXES"
                community "CUST-COMM"
            action accept
                local-preference 200
        exit
        entry 65535
            action accept

    configure router bgp
        group "UPSTREAMS"
            neighbor 10.1.1.1
                import "INBOUND-POLICY"
    ```

    Full configuration reference: [https://documentation.nokia.com/sr/23-3/titles/bgp.html](https://documentation.nokia.com/sr/23-3/titles/bgp.html)

---

## Common Pitfalls

1. **Missing `permit all` at end of route-map.** A route-map without a final `permit <high-seq>` (no match conditions) implicitly denies all routes not matched by previous clauses. In a BGP inbound route-map, this drops all unmatched routes from the BGP table. Always include a catch-all permit unless intent is to deny everything else.

2. **`send-community` not enabled (Cisco).** Communities are not sent to eBGP peers by default in Cisco IOS. A community set on a route is silently stripped before it leaves the AS unless `neighbor <ip> send-community` is configured. Communities between iBGP peers are sent by default.

3. **Local preference scope.** Local preference is significant only within a single AS — it is stripped before routes are advertised to eBGP peers. Trying to influence another AS's routing with local preference doesn't work; use MED or prepending instead.

4. **MED comparison across different ASes.** By default, OSPF/IOS only compares MED values for routes learned from the same AS. Routes from different ASes are not compared by MED. Use `bgp always-compare-med` to compare MEDs from all ASes — but this can cause routing instability if ASes don't set MED consistently.

5. **AS-path prepending overuse.** Prepending your own AS many times makes your routes look very long. If an alternative path exists without prepending, traffic should naturally prefer it — excessive prepending is mostly useful when you need a dramatic preference shift. Two or three prepends are usually sufficient.

---

## Practice Problems

**Q1.** A route-map has three clauses: seq 10 (match prefix-list A, set local-pref 200), seq 20 (match community X, set local-pref 150), seq 30 (permit — no match). A route matches both prefix-list A and community X. What local-preference does it get?

??? answer
    Local preference 200 — seq 10 matches first (first match wins). Seq 20 is never evaluated for this route.

**Q2.** You want to accept only your customer's prefixes (a specific /24) from an eBGP peer and reject everything else. Write the prefix-list and apply it to the neighbor.

??? answer
    ```
    ip prefix-list CUST-ONLY seq 5 permit 10.1.2.0/24
    ip prefix-list CUST-ONLY seq 10 deny 0.0.0.0/0 le 32

    router bgp 65000
     neighbor 10.1.1.1 prefix-list CUST-ONLY in
    ```
    The first entry permits the exact /24. The second denies all other prefixes (any prefix from /0 to /32). Without the deny, the implicit deny at the end still blocks everything, but the explicit deny makes the intent clear.

**Q3.** What is the difference between AS-path prepending and setting MED for inbound traffic engineering?

??? answer
    **MED** is advisory — it signals your preferred entry point to a peer, but the peer may ignore it. It's effective when the peer honours MED and both routes are learned from the same AS. **AS-path prepending** makes your route appear longer in the AS_PATH attribute, which directly affects the best-path algorithm (step 6 — shorter AS_PATH preferred). Prepending is more universally effective but less surgical — it affects all ASes that receive the prepended route, not just the direct peer.

---

## Summary & Key Takeaways

- **Route-maps** are the BGP policy engine: ordered match+set clauses; first match wins; implicit deny at end — always add a final permit clause.
- **Prefix-lists** filter BGP routes by prefix; use `ge`/`le` for range matching.
- **AS-path filters** use regular expressions to match the AS_PATH string.
- **BGP communities** (RFC 1997 standard, RFC 4360 extended, RFC 8092 large) tag routes with arbitrary signals for policy automation.
- Communities are not sent to eBGP peers by default on Cisco — enable with `send-community`.
- **Local preference** (higher = preferred) influences **outbound** traffic (exit selection); local to the AS.
- **MED** (lower = preferred) influences **inbound** traffic; advisory to the peer.
- **AS-path prepending** makes a path appear longer → less preferred; effective for inbound traffic engineering across multiple ASes.

---

## Where to Next

- **RT-009 — Route Redistribution & Policy:** Mutual redistribution between BGP and IGPs.
- **CT-002 — MPLS VPNs (L3VPN):** BGP extended communities (Route Target) underpin MPLS L3VPN.
- **CT-006 — EVPN Fundamentals:** BGP extended communities drive EVPN MAC/IP advertisement.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 1997 | BGP Communities Attribute |
| RFC 4360 | BGP Extended Communities Attribute |
| RFC 8092 | BGP Large Communities Attribute |
| RFC 4271 | BGP-4 (base specification — attribute definitions) |
| Cisco CCNP Enterprise | BGP policy, communities, route-maps |
| Juniper JNCIP-SP | BGP policy design and communities |

---

## References

- RFC 1997 — BGP Communities Attribute. [https://www.rfc-editor.org/rfc/rfc1997](https://www.rfc-editor.org/rfc/rfc1997)
- RFC 4360 — BGP Extended Communities Attribute. [https://www.rfc-editor.org/rfc/rfc4360](https://www.rfc-editor.org/rfc/rfc4360)
- RFC 8092 — BGP Large Communities Attribute. [https://www.rfc-editor.org/rfc/rfc8092](https://www.rfc-editor.org/rfc/rfc8092)

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
| RT-009 | Route Redistribution & Policy | BGP policy tools used in redistribution scenarios |
| CT-002 | MPLS VPNs L3VPN | BGP extended communities (Route Target) |
| CT-006 | EVPN Fundamentals | BGP extended communities drive EVPN |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| RT-007 | BGP Fundamentals | Prerequisite — BGP sessions, attributes, best-path algorithm |
<!-- XREF-END -->
