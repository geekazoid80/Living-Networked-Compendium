---
module_id: SV-001
title: "DNS - Domain Name System"
description: "How DNS translates human-readable names into IP addresses through a distributed hierarchical database."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - IP-001
  - RT-001
learning_path_tags:
  - DNE
difficulty: beginner
tags:
  - dns
  - services
  - name-resolution
  - layer7
created: 2026-04-19
updated: 2026-04-19
---

# SV-001 - DNS - Domain Name System
## Learning Objectives

After completing this module you will be able to:

1. Describe the DNS hierarchy: root, TLD, second-level domain, subdomain.
2. Explain the difference between recursive resolvers and authoritative name servers.
3. Trace a full DNS resolution from a client's perspective.
4. List the common DNS record types and their purpose.
5. Explain TTL and its role in caching and change propagation.
6. Interpret the output of `nslookup` and `dig`.

---
## Prerequisites

- IP-001 - IP Addressing Fundamentals (IP addresses, subnets)
- RT-001 - Routing Fundamentals (IP reachability)

---
## The Problem

You want to reach a web server. You know it as `www.example.com`. Your computer must send an IP packet - which requires an IP address. There is no direct mapping stored on your machine. You need a way to convert the name into an address.

### Step 1: A single lookup file

You maintain a file on your computer listing every name and its IP address. It works perfectly for ten servers. When you add the eleventh, you edit the file on every machine in the office. When a server changes IP, you update every file. At a thousand machines, this is unmanageable. This file still exists - it's `/etc/hosts` - but it cannot scale globally.

### Step 2: A central server

One server holds the name-to-IP table for the entire organisation. Every machine queries it. When a name changes, you update one place. This works for one company. The internet has billions of names updated thousands of times per second. No single server can hold all of them or respond fast enough.

### Step 3: Delegation - break the problem into zones

Divide the namespace into a hierarchy: root, top-level domain (.com, .org, .net), domain (example.com), subdomain (www.example.com). Each level is responsible only for its own zone and delegates the next level to another server. The root servers know who handles .com; the .com servers know who handles example.com; example.com's own server knows www's IP. No single server knows everything - each knows only its zone and where to send queries it can't answer. This is **DNS**.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Name-to-IP mapping file | hosts file |
| Query process walking the hierarchy | Recursive resolution |
| Server that holds zone authority | Authoritative name server |
| Server that queries on behalf of clients | Recursive resolver |
| Cached answer from a prior query | TTL-bounded cache entry |

---
## Core Content

### The DNS Hierarchy

DNS is a **distributed hierarchical database**. The namespace is a tree:

```
                    . (root)
                   / \
                .com  .org  .net  ...
               /
          example.com
         /
    www.example.com
```

- **Root zone:** Managed by IANA; 13 root server clusters (a.root-servers.net through m.root-servers.net). They know the addresses of all TLD servers.
- **TLD (Top-Level Domain):** `.com`, `.org`, `.net`, country codes (`.uk`, `.sg`), new gTLDs (`.io`, `.cloud`). Managed by registries (Verisign for `.com`).
- **Second-level domain:** `example.com` - registered by an organisation. The organisation controls the authoritative DNS servers for this zone.
- **Subdomain:** `www.example.com`, `mail.example.com` - the organisation adds these in their own zone.

### Resolvers and Authoritative Servers

**Recursive resolver** (also: recursive nameserver, DNS resolver): The server your device queries. Usually provided by your ISP or a public service (8.8.8.8 Google, 1.1.1.1 Cloudflare, 9.9.9.9 Quad9). The resolver does the work of walking the hierarchy on your behalf, caching results.

**Authoritative name server:** Holds the definitive records for a zone. Answers are authoritative (AA bit set). Returns NXDOMAIN if the name doesn't exist in the zone.

### DNS Resolution - Full Walk

1. Client queries its configured recursive resolver for `www.example.com A`.
2. Resolver checks cache - miss.
3. Resolver queries a root server: "Who handles `.com`?"
4. Root server returns the addresses of `.com` TLD servers.
5. Resolver queries a `.com` TLD server: "Who handles `example.com`?"
6. TLD server returns the addresses of `example.com`'s authoritative servers.
7. Resolver queries `example.com`'s authoritative server: "What is the A record for `www.example.com`?"
8. Authoritative server returns: `93.184.216.34`, TTL 3600.
9. Resolver caches the answer (TTL 3600 seconds = 1 hour) and returns it to the client.
10. Subsequent queries within the TTL window are answered from cache - steps 3–8 are skipped.

This is an **iterative** walk (resolver asks each server directly). Some resolvers use **recursive** queries against upstream servers that do the full walk.

### DNS Record Types

| Record | Purpose | Example |
|---|---|---|
| **A** | IPv4 address for a hostname | `www.example.com → 93.184.216.34` |
| **AAAA** | IPv6 address for a hostname | `www.example.com → 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Canonical name (alias) | `mail.example.com → mailserver.example.com` |
| **MX** | Mail exchanger | `example.com → 10 mail.example.com` |
| **NS** | Authoritative name server for a zone | `example.com → ns1.example.com` |
| **PTR** | Reverse lookup: IP → hostname | `34.216.184.93.in-addr.arpa → www.example.com` |
| **SOA** | Start of Authority - zone metadata | Serial, refresh, retry, expire, minimum TTL |
| **TXT** | Arbitrary text; used for SPF, DKIM, DMARC | `v=spf1 include:_spf.example.com ~all` |
| **SRV** | Service location | `_sip._tcp.example.com → 10 5 5060 sip.example.com` |

### TTL - Time to Live

Every DNS record carries a **TTL** in seconds. Resolvers cache the record until the TTL expires; after that, they query the authoritative server again.

- Low TTL (60–300s): fast propagation of changes; high query load on authoritative servers.
- High TTL (3600–86400s): efficient caching; slow propagation if you need to change a record.

Before a planned IP address change: lower the TTL days in advance (to 60–300s) so caches expire quickly when the change is made. After the change stabilises, raise the TTL back.

### Reverse DNS (PTR Records)

Forward DNS: name → IP. Reverse DNS: IP → name.

Reverse lookups are stored in the `in-addr.arpa` zone (IPv4) or `ip6.arpa` (IPv6). The IP address octets are reversed:

- `93.184.216.34` → PTR record in `34.216.184.93.in-addr.arpa`

Used for: server verification, spam filtering, log enrichment, SMTP server reputation.

### DNS over TCP vs UDP

DNS typically uses **UDP port 53** for queries (fast, no handshake overhead). TCP port 53 is used for:
- Responses > 512 bytes (EDNS0 raises this limit to ~4096 bytes; DNSSEC responses are large).
- Zone transfers (AXFR/IXFR) between authoritative servers.

??? supplementary "DNSSEC - DNS Security Extensions"
    Standard DNS has no authentication - a resolver cannot verify that a response came from the legitimate authoritative server (DNS spoofing / cache poisoning). **DNSSEC** adds cryptographic signatures to DNS records. The resolver validates the chain of signatures from the root down to the queried zone. DNSSEC does not encrypt queries - it only authenticates them. **DNS over HTTPS (DoH)** and **DNS over TLS (DoT)** encrypt the query transport to prevent eavesdropping.

---
## Vendor Implementations

=== "Cisco IOS-XE"

    ```
    ! Configure DNS server for the device itself
    ip domain-lookup
    ip name-server 8.8.8.8 1.1.1.1
    ip domain-name example.com

    ! Verify
    ping www.example.com
    show hosts
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_dns/configuration/xe-17/dns-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_dns/configuration/xe-17/dns-xe-17-book.html)

=== "MikroTik RouterOS"

    ```
    # Configure upstream DNS servers
    /ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes

    # Static DNS entry
    /ip dns static add name=myserver.local address=192.168.1.100

    # Verification
    /ip dns cache print
    /tool dns-lookup address=www.example.com
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/DNS](https://help.mikrotik.com/docs/display/ROS/DNS)

---
## Common Pitfalls

1. **Forgetting to lower TTL before a DNS change.** If you change a record while TTL is 86400s, resolvers worldwide cache the old record for up to 24 hours. Lower TTL to 300s at least one TTL-cycle before making changes.

2. **CNAME at the zone apex.** A CNAME record at the domain root (e.g., `example.com CNAME something`) conflicts with SOA and NS records - not permitted by RFC 1034. Use A/AAAA records or ALIAS/ANAME (vendor-specific flattening) at the apex.

3. **PTR record not matching A record.** Many mail servers reject email from servers whose reverse DNS (PTR) doesn't match the forward A record. Always ensure PTR and A are consistent for mail infrastructure.

4. **Split-horizon DNS.** Internal and external views of a name return different IPs (internal: private IP; external: public IP). Misconfiguration causes internal hosts to get the external IP (routed through the internet or firewalled) or external hosts to get the internal IP (unreachable). Keep split-horizon zones strictly separated.

5. **Stale cache after TTL change.** A resolver caches the old TTL value, not the new one. If you lower TTL from 86400 to 300, resolvers that cached the record 23 hours ago will hold it for another hour. You cannot force remote cache expiry - wait for the full old TTL to elapse.

---
## Practice Problems

**Q1.** A client queries its resolver for `mail.example.com`. The resolver has a cached A record for `mail.example.com` with 5 seconds remaining on the TTL. What does the resolver return?

??? answer
    The cached answer - the resolver returns the IP address from its cache without querying the authoritative server. The client gets an answer immediately (with the remaining TTL = 5s), and the resolver's cache entry expires 5 seconds later.

**Q2.** What is the difference between an authoritative answer and a non-authoritative (cached) answer?

??? answer
    An authoritative answer comes directly from the nameserver that holds the zone - the AA (Authoritative Answer) bit is set in the DNS response. A non-authoritative (cached) answer comes from a resolver's cache - the AA bit is not set, the TTL reflects remaining cache lifetime, and the answer may be up to one full TTL cycle old.

**Q3.** You need to do a reverse DNS lookup for IP `10.20.30.40`. What is the PTR record name to query?

??? answer
    `40.30.20.10.in-addr.arpa` - the octets are reversed and `.in-addr.arpa` is appended.

**Q4.** A new engineer sets TTL on all records to 60 seconds "for flexibility." What is the operational cost?

??? answer
    Every 60 seconds, every resolver worldwide re-queries the authoritative server for each name. For a high-traffic domain, this massively increases query load on authoritative servers and increases latency for resolvers that always cache-miss. High TTL values (hours to days) are appropriate for stable records; low TTLs (minutes) only when frequent changes are planned.

---
## Summary & Key Takeaways

- DNS is a **distributed hierarchical database** translating names to IP addresses (and more).
- The hierarchy: **root → TLD → domain → subdomain** - each level delegates to the next.
- **Recursive resolvers** walk the hierarchy on behalf of clients and cache results.
- **Authoritative servers** hold zone records and return definitive answers.
- Key record types: **A** (IPv4), **AAAA** (IPv6), **CNAME** (alias), **MX** (mail), **PTR** (reverse), **NS** (delegation), **TXT** (metadata).
- **TTL** controls cache lifetime - lower before planned changes, higher for stable records.
- DNS uses **UDP port 53** (queries) and **TCP port 53** (large responses, zone transfers).

---
## Where to Next

- **SV-002 - DHCP:** How devices get IP addresses assigned - DHCP uses DNS server info in its responses.
- **SEC-001 - Access Control Lists:** DNS traffic filtering at the firewall.
- **PROTO-001 - DNS Deep Dive:** Full record type coverage, DNSSEC, DoH/DoT, zone transfer mechanics.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 1034 | Domain Names - Concepts and Facilities |
| RFC 1035 | Domain Names - Implementation and Specification |
| RFC 3596 | DNS Extensions to Support IPv6 (AAAA records) |
| RFC 4034 | Resource Records for DNSSEC |
| Cisco CCNA | DNS configuration, troubleshooting with nslookup/dig |
| CompTIA Network+ | DNS hierarchy, record types |

---
## References

- RFC 1034 - Domain Names Concepts and Facilities. [https://www.rfc-editor.org/rfc/rfc1034](https://www.rfc-editor.org/rfc/rfc1034)
- RFC 1035 - Domain Names Implementation and Specification. [https://www.rfc-editor.org/rfc/rfc1035](https://www.rfc-editor.org/rfc/rfc1035)
- RFC 3596 - DNS Extensions to Support IPv6. [https://www.rfc-editor.org/rfc/rfc3596](https://www.rfc-editor.org/rfc/rfc3596)

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
| SV-002 | DHCP | DHCP provides DNS server address to clients |
| SEC-001 | Access Control Lists | DNS traffic filtering |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| IP-001 | IP Addressing Fundamentals | DNS resolves names to IP addresses |
| RT-001 | Routing Fundamentals | IP reachability required for DNS queries |
<!-- XREF-END -->
