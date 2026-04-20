---
module_id: SEC-003
title: "VPN & IPSec"
description: "How VPNs create encrypted tunnels across untrusted networks, and how IPSec provides authentication and encryption through IKE, ESP, and AH."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - SEC-001
  - SEC-002
  - IP-001
learning_path_tags:
  - DNE
difficulty: advanced
tags:
  - vpn
  - ipsec
  - ike
  - esp
  - security
  - tunneling
  - encryption
created: 2026-04-19
updated: 2026-04-19
---

# SEC-003 - VPN & IPSec
## Learning Objectives

After completing this module you will be able to:

1. Explain the purpose of a VPN and the tunnelling concept.
2. Describe IPSec's two protocols: ESP and AH.
3. Distinguish tunnel mode from transport mode.
4. Explain IKE Phase 1 and Phase 2 and what each establishes.
5. Describe the difference between pre-shared key and certificate-based authentication.
6. Configure a site-to-site IPSec VPN on at least two vendor platforms.
7. Explain how NAT-T enables IPSec through NAT devices.

---
## Prerequisites

- SEC-001 - ACLs (crypto ACL / interesting traffic definition)
- SEC-002 - Firewall Concepts (security zones; VPN endpoints behind firewalls)
- IP-001 - IP Addressing Fundamentals

---
## The Problem

Two offices - one in Singapore, one in London - need to share internal network resources as if they were on the same LAN. The connection between them is the internet - an untrusted public network where anyone can intercept, modify, or inject traffic.

### Step 1: Create a logical tunnel

The routers at each office create a logical path between them. Traffic entering the tunnel on one side exits on the other, encapsulated in a new IP packet - the payload is the original packet, the outer header addresses the remote router. This is **tunnelling** - the internet sees only the outer envelope.

### Step 2: Encrypt the payload

Tunnelling alone doesn't protect against eavesdropping - the encapsulated packet is still readable. The tunnel must encrypt the payload before transmission. Only the two endpoints - holding the right keys - can decrypt it.

### Step 3: Establish and manage keys securely

Encrypting requires both endpoints to agree on the same key without that key being intercepted during exchange. The **IKE (Internet Key Exchange)** protocol handles this: it authenticates the peers and negotiates a shared key using public-key cryptography (Diffie-Hellman) so that even if an attacker captures the exchange, they cannot derive the key.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Logical path across an untrusted network | VPN (Virtual Private Network) |
| Encapsulation in a new IP header | Tunnelling |
| Payload encryption + integrity protection | IPSec ESP |
| Key exchange protocol | IKE (Internet Key Exchange) |
| Phase 1: authenticate peers, establish management SA | IKE Phase 1 (ISAKMP SA) |
| Phase 2: establish data SAs | IKE Phase 2 (IPSec SA) |
| Bidirectional security agreement | SA (Security Association) |

---
## Core Content

### VPN Types

| VPN type | Use case | Protocol |
|---|---|---|
| **Site-to-site** | Office-to-office always-on tunnel | IPSec, GRE, DMVPN |
| **Remote access** | Individual user to corporate network | SSL/TLS (AnyConnect), IPSec/IKEv2 |
| **MPLS L3VPN** | Carrier-managed VPN across MPLS core | BGP + MPLS (see CT-002) |
| **SD-WAN** | Software-controlled VPN overlay | IPSec, DTLS |

This module focuses on **site-to-site IPSec** - the foundational mechanism.

### IPSec Protocols

**ESP - Encapsulating Security Payload (IP protocol 50)**

Provides: confidentiality (encryption), integrity (HMAC), anti-replay protection.
ESP encrypts the payload - the interceptor sees only ciphertext.

**AH - Authentication Header (IP protocol 51)**

Provides: integrity (HMAC over the entire IP packet, including outer header), anti-replay.
AH does NOT encrypt. Rarely used in modern deployments because it breaks NAT (NAT changes the source IP which AH's integrity check covers - see SV-003/NAT). ESP with authentication (the default) provides all practical security needs.

### Tunnel Mode vs Transport Mode

| Mode | Outer header | Use case |
|---|---|---|
| **Tunnel mode** | New outer IP header added; entire original packet is encrypted | Site-to-site VPN (gateway to gateway) |
| **Transport mode** | Original IP header preserved; only payload encrypted | Host-to-host (rare); GRE over IPSec |

Site-to-site VPNs always use tunnel mode - the VPN gateways add new IP headers for the outer internet path; the original private IP packet is encrypted inside.

### Security Associations (SAs)

An **SA** is a one-way agreement on security parameters between two peers. Because communication is bidirectional, a pair of SAs exists: one for each direction.

SA parameters:
- Encryption algorithm (AES-128, AES-256, ChaCha20)
- Integrity algorithm (HMAC-SHA-256, HMAC-SHA-384)
- Key material
- Lifetime (seconds or kilobytes before rekeying)

The collection of SAs is stored in the **SAD (Security Association Database)**.

### IKE - Internet Key Exchange

IKE establishes SAs without manually configuring keys. Two versions:

- **IKEv1:** Older; two phases; aggressive mode (faster but less secure) or main mode. Widely deployed but being replaced.
- **IKEv2 (RFC 7296):** Simpler, faster, more robust; built-in mobility support (MOBIKE); preferred for new deployments.

#### IKE Phase 1 (IKEv1) / IKE_SA_INIT + IKE_AUTH (IKEv2)

**Goal:** Authenticate the two peers and establish a secure, encrypted channel for Phase 2 negotiation.

1. **Agree on parameters:** Encryption, hash, DH group, authentication method.
2. **Diffie-Hellman exchange:** Both sides compute a shared secret without transmitting it directly.
3. **Authenticate:** Using pre-shared key (PSK) or digital certificates (PKI).
4. **Result:** **ISAKMP SA** (IKEv1) or **IKE SA** (IKEv2) - a management channel.

#### IKE Phase 2 (IKEv1) / CREATE_CHILD_SA (IKEv2)

**Goal:** Establish the actual IPSec SAs for data encryption.

1. Using the secure channel from Phase 1, negotiate: encryption/integrity algorithms, traffic selectors (which traffic to encrypt), lifetimes.
2. Generate new keying material (optionally with Perfect Forward Secrecy / PFS - new DH exchange so Phase 2 keys are independent of Phase 1 keys).
3. **Result:** **IPSec SA** pair - actual encryption SAs for data traffic.

#### Authentication Methods

| Method | Description | Security |
|---|---|---|
| **Pre-shared key (PSK)** | Both sides configured with the same secret string | Simple; key distribution is manual; if key is compromised, session can be decrypted |
| **Digital certificates (PKI)** | Each peer has a certificate signed by a CA; private key proves identity | Scalable; key rotation via certificate renewal; preferred for enterprise/large scale |
| **EAP (IKEv2)** | Remote access authentication via RADIUS (username/password, OTP) | Used for remote-access VPN |

#### Diffie-Hellman Groups

DH groups determine the strength of the key exchange. Higher group number = stronger but slower:

| DH Group | Type | Bits | Recommendation |
|---|---|---|---|
| Group 1 | MODP | 768 | Obsolete |
| Group 2 | MODP | 1024 | Avoid |
| Group 14 | MODP | 2048 | Minimum acceptable |
| Group 19 | ECP (NIST P-256) | 256 ECC | Recommended |
| Group 20 | ECP (NIST P-384) | 384 ECC | Recommended |
| Group 21 | ECP (NIST P-521) | 521 ECC | High security |

Use Group 19 or 20 for IKEv2 deployments.

### NAT Traversal (NAT-T)

IPSec ESP is an IP-layer protocol (not TCP/UDP). NAT devices track TCP/UDP sessions - they can't translate an ESP packet (no ports). ESP packets silently fail through most NAT.

**NAT-T (RFC 3948):** Both IKE peers detect if NAT is present. If yes, they encapsulate ESP in UDP port 4500 - NAT devices treat it as a UDP session and translate it successfully. The receiving peer strips the UDP wrapper and processes the ESP packet normally.

IKE negotiation itself uses UDP 500 initially; after NAT detection, switches to UDP 4500.

### Crypto ACL - Interesting Traffic

For policy-based IPSec (traditional site-to-site), a **crypto ACL** (interesting traffic ACL) defines which traffic should be encrypted. Traffic matching the ACL is sent through the VPN; traffic not matching is sent unencrypted.

```
ip access-list extended CRYPTO-ACL
 permit ip 192.168.1.0 0.0.0.255 10.0.0.0 0.255.255.255
```

This is the traffic selector - symmetrically configured on both ends (source/destination are mirrored).

GRE tunnel + IPSec (or DMVPN) eliminates the need for crypto ACLs by routing traffic through the tunnel interface explicitly.

### GRE over IPSec

GRE (Generic Routing Encapsulation) tunnels carry routing protocol traffic (including multicast for OSPF/EIGRP hellos) - standard IPSec cannot. **GRE over IPSec** encapsulates GRE in IPSec:

- GRE tunnel: carries any traffic type, including routing protocols.
- IPSec transport mode: encrypts the GRE payload.
- Result: encrypted tunnel that supports dynamic routing.

---
## Vendor Implementations

=== "Cisco IOS-XE (IKEv2 Site-to-Site)"

    ```
    ! IKEv2 Proposal
    crypto ikev2 proposal PROP-1
     encryption aes-cbc-256
     integrity sha256
     group 19

    ! IKEv2 Policy
    crypto ikev2 policy POL-1
     proposal PROP-1

    ! IKEv2 Keyring (PSK)
    crypto ikev2 keyring KEYRING-1
     peer REMOTE-PEER
      address 203.0.113.10
      pre-shared-key local Str0ngKey! remote Str0ngKey!

    ! IKEv2 Profile
    crypto ikev2 profile IKEv2-PROFILE
     match address local 203.0.113.5
     match identity remote address 203.0.113.10
     authentication remote pre-share
     authentication local pre-share
     keyring local KEYRING-1

    ! IPSec Transform Set
    crypto ipsec transform-set XFORM esp-aes 256 esp-sha256-hmac
     mode tunnel

    ! IPSec Profile
    crypto ipsec profile IPSEC-PROF
     set transform-set XFORM
     set ikev2-profile IKEv2-PROFILE

    ! Tunnel Interface
    interface Tunnel0
     ip address 10.99.0.1 255.255.255.252
     tunnel source GigabitEthernet0/0
     tunnel destination 203.0.113.10
     tunnel mode ipsec ipv4
     tunnel protection ipsec profile IPSEC-PROF

    ! Verification
    show crypto ikev2 sa
    show crypto ipsec sa
    show crypto session
    ```

    Full configuration reference: [https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_conn_ikevpn/configuration/xe-17/sec-conn-ikevpn-xe-17-book.html](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_conn_ikevpn/configuration/xe-17/sec-conn-ikevpn-xe-17-book.html)

=== "Juniper SRX (Junos)"

    ```
    # IKE proposal
    set security ike proposal IKE-PROP authentication-method pre-shared-keys
    set security ike proposal IKE-PROP dh-group group19
    set security ike proposal IKE-PROP authentication-algorithm sha-256
    set security ike proposal IKE-PROP encryption-algorithm aes-256-cbc

    # IKE policy
    set security ike policy IKE-POL mode main
    set security ike policy IKE-POL proposals IKE-PROP
    set security ike policy IKE-POL pre-shared-key ascii-text "Str0ngKey!"

    # IKE gateway
    set security ike gateway GW-REMOTE ike-policy IKE-POL
    set security ike gateway GW-REMOTE address 203.0.113.10
    set security ike gateway GW-REMOTE local-identity inet 203.0.113.5
    set security ike gateway GW-REMOTE external-interface ge-0/0/0

    # IPSec proposal
    set security ipsec proposal IPSEC-PROP protocol esp
    set security ipsec proposal IPSEC-PROP encryption-algorithm aes-256-cbc
    set security ipsec proposal IPSEC-PROP authentication-algorithm hmac-sha-256-128

    # IPSec policy and VPN
    set security ipsec policy IPSEC-POL proposals IPSEC-PROP
    set security ipsec vpn SITE-VPN ike gateway GW-REMOTE
    set security ipsec vpn SITE-VPN ike ipsec-policy IPSEC-POL
    set security ipsec vpn SITE-VPN establish-tunnels immediately

    # Verification
    show security ike sa
    show security ipsec sa
    ```

    Full configuration reference: [https://www.juniper.net/documentation/us/en/software/junos/vpn-ipsec/topics/topic-map/vpn-ipsec-overview.html](https://www.juniper.net/documentation/us/en/software/junos/vpn-ipsec/topics/topic-map/vpn-ipsec-overview.html)

=== "MikroTik RouterOS"

    ```
    # IKEv2 IPSec peer
    /ip ipsec peer
    add address=203.0.113.10 exchange-mode=ike2 name=REMOTE-PEER \
        local-address=203.0.113.5

    # Pre-shared key
    /ip ipsec identity
    add peer=REMOTE-PEER auth-method=pre-shared-key secret="Str0ngKey!"

    # IPSec proposal
    /ip ipsec proposal
    set [ find default=yes ] auth-algorithms=sha256 enc-algorithms=aes-256-cbc pfs-group=ecp256

    # Policy
    /ip ipsec policy
    add src-address=192.168.1.0/24 dst-address=10.0.0.0/8 tunnel=yes \
        action=encrypt proposal=default peer=REMOTE-PEER

    # Verification
    /ip ipsec sa print
    /ip ipsec active-peers print
    ```

    Full configuration reference: [https://help.mikrotik.com/docs/display/ROS/IPsec](https://help.mikrotik.com/docs/display/ROS/IPsec)

---
## Common Pitfalls

1. **Mismatched IKE/IPSec proposals.** Both peers must agree on exactly the same encryption, integrity, and DH group parameters. A mismatch causes Phase 1 or Phase 2 to fail - the connection never establishes. Check `debug crypto isakmp` or `show security ike sa detail` for proposal mismatches.

2. **Asymmetric crypto ACLs.** The interesting traffic ACL (crypto ACL) on Site A specifies src=192.168.1.0/24, dst=10.0.0.0/24. Site B must mirror it: src=10.0.0.0/24, dst=192.168.1.0/24. Asymmetric ACLs cause one direction to work while the other sends unencrypted.

3. **NAT interfering with AH.** AH covers the outer IP source address in its integrity check. A NAT device changing the source IP breaks AH. Use ESP (not AH) and enable NAT-T when NAT is present in the path.

4. **SA lifetime mismatch.** If both peers have different SA lifetimes, rekeying is triggered by the peer with the shorter lifetime. This is acceptable; the peers negotiate. But very short lifetimes (< 300s) cause frequent rekeying overhead; very long lifetimes (> 24h) reduce forward secrecy. Use 3600–86400s for Phase 1; 3600s for Phase 2.

5. **Missing route to peer through tunnel.** After the tunnel is established, traffic must be routed into it. If the routing table sends traffic for the remote subnet via the internet interface (not the tunnel interface), the tunnel never carries useful traffic despite being "up."

---
## Practice Problems

**Q1.** What is the purpose of IKE Phase 1 and what does it produce?

??? answer
    IKE Phase 1 authenticates the two VPN peers and establishes a secure, encrypted management channel (the ISAKMP SA or IKE SA). This channel is used to negotiate Phase 2. It does NOT encrypt data traffic - it only establishes the secure channel for further negotiation. Authentication uses PSK or certificates; key material is generated using Diffie-Hellman.

**Q2.** Why does AH break through NAT and how does ESP with NAT-T solve it?

??? answer
    AH computes an integrity check over the entire IP packet, including the outer source IP. When NAT translates the source IP address, the AH integrity check at the destination fails - the packet is discarded. ESP doesn't cover the outer IP header in its integrity check. NAT-T encapsulates ESP in UDP port 4500 so NAT devices can track it as a UDP session, allowing translation without breaking the ESP payload.

**Q3.** A site-to-site VPN shows Phase 1 as UP but Phase 2 as DOWN. What is the most likely cause?

??? answer
    Mismatched Phase 2 parameters (transform set mismatch - encryption/integrity algorithms), or mismatched crypto ACLs (interesting traffic doesn't match on both sides). Check `show crypto ipsec sa` for the specific Phase 2 error, and compare transform sets and crypto ACL definitions on both peers.

---
## Summary & Key Takeaways

- **VPNs** create encrypted tunnels across untrusted networks - traffic looks like any other IP traffic to the network but is encapsulated and encrypted.
- **IPSec** provides confidentiality (ESP encryption), integrity (HMAC), and anti-replay protection.
- **Tunnel mode** (used for site-to-site) encapsulates the entire original packet in a new IP header.
- **IKE Phase 1** authenticates peers and creates a management SA; **Phase 2** creates the actual data encryption SAs.
- **IKEv2** (RFC 7296) is simpler, faster, and more secure than IKEv1 - use it for all new deployments.
- **PSK** is simple but requires secure manual key distribution; **certificates** scale better.
- **NAT-T** enables IPSec through NAT by wrapping ESP in UDP port 4500.
- Both peers must have matching IKE/IPSec proposals and mirrored crypto ACLs.

---
## Where to Next

- **SEC-004 - AAA (TACACS+ & RADIUS):** Authentication for device management access.
- **SEC-005 - Encryption Standards & PKI:** Certificates and CAs used for IKE authentication.
- **CT-002 - MPLS VPNs (L3VPN):** Carrier-managed VPNs using MPLS instead of IPSec.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 4301 | Security Architecture for the Internet Protocol |
| RFC 4303 | IP Encapsulating Security Payload (ESP) |
| RFC 7296 | IKEv2 (Internet Key Exchange Protocol Version 2) |
| RFC 3948 | UDP Encapsulation of IPSec ESP Packets (NAT-T) |
| Cisco CCNP Security | IPSec VPN configuration, IKEv2, DMVPN |
| CompTIA Security+ | VPN types, IPSec components |

---
## References

- RFC 4301 - Security Architecture for the Internet Protocol. [https://www.rfc-editor.org/rfc/rfc4301](https://www.rfc-editor.org/rfc/rfc4301)
- RFC 4303 - IP Encapsulating Security Payload (ESP). [https://www.rfc-editor.org/rfc/rfc4303](https://www.rfc-editor.org/rfc/rfc4303)
- RFC 7296 - Internet Key Exchange Protocol Version 2 (IKEv2). [https://www.rfc-editor.org/rfc/rfc7296](https://www.rfc-editor.org/rfc/rfc7296)
- RFC 3948 - UDP Encapsulation of IPsec ESP Packets. [https://www.rfc-editor.org/rfc/rfc3948](https://www.rfc-editor.org/rfc/rfc3948)

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
| SEC-005 | Encryption Standards & PKI | Certificate-based IKE authentication |
| SEC-006 | Network Segmentation & DMZ | VPN termination in DMZ or trust zone |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SEC-001 | Access Control Lists | Crypto ACL defines interesting traffic |
| SEC-002 | Firewall Concepts | Firewall must permit IKE/ESP for VPN |
| IP-001 | IP Addressing Fundamentals | Tunnel addressing, NAT-T |
<!-- XREF-END -->
