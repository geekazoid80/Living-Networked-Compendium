---
module_id: SEC-005
title: "Encryption Standards & PKI"
description: "Symmetric and asymmetric encryption, certificate authorities, X.509 certificates, and how PKI enables trust in IPSec, TLS, and 802.1X deployments."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 45
prerequisites:
  - SEC-003
  - SEC-004
learning_path_tags:
  - DNE
difficulty: advanced
tags:
  - encryption
  - pki
  - certificates
  - tls
  - symmetric
  - asymmetric
  - ca
  - security
created: 2026-04-19
updated: 2026-04-19
---

# SEC-005 - Encryption Standards & PKI
## Learning Objectives

After completing this module you will be able to:

1. Explain the difference between symmetric and asymmetric encryption and when each is used.
2. Describe the structure of an X.509 certificate and its key fields.
3. Explain how a certificate chain provides verifiable trust.
4. Describe CA hierarchy (root CA, intermediate CA, end-entity certificates).
5. Explain CRL and OCSP for certificate revocation.
6. Describe how PKI is used in IPSec IKE, TLS, and 802.1X EAP-TLS.

---
## Prerequisites

- SEC-003 - VPN & IPSec (IKE certificate authentication)
- SEC-004 - AAA (EAP-TLS for 802.1X)

---
## The Problem

IPSec IKE can authenticate peers using pre-shared keys. This works for two sites. It doesn't scale to 200 branch offices - you'd need 200 different pre-shared keys, distributed securely to each device, rotated periodically. If one key is compromised, only that one tunnel is compromised - but the key management overhead is enormous.

### Step 1: Asymmetric cryptography - keys in pairs

Instead of a shared secret, each device generates a **key pair**: a **private key** (kept secret, never shared) and a **public key** (shared freely). A message encrypted with the public key can only be decrypted by the matching private key. A message signed with the private key can be verified by anyone with the public key.

For key exchange: I encrypt a secret with your public key; only you (holding the private key) can decrypt it. We've established a shared secret without ever transmitting it over the wire.

### Step 2: How do I know your public key is really yours?

If an attacker replaces your public key with their own, I'll encrypt to the attacker instead of you. I need a way to verify that a public key belongs to who it claims to belong to. A trusted third party - a **Certificate Authority (CA)** - signs your public key along with your identity information. This signed package is a **certificate**. Anyone trusting the CA can verify any certificate the CA signed.

### Step 3: From certificates to PKI

The CA itself has a certificate, signed by a Root CA. The Root CA signs Intermediate CAs. Intermediate CAs sign end-entity certificates (for routers, servers, users). The chain from the end certificate back to the Root CA is the **certificate chain**. Verifying the chain - signature by signature - is **certificate validation**. If any signature fails, the certificate is rejected.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Same key for encrypt and decrypt | Symmetric encryption |
| Public/private key pair | Asymmetric encryption |
| Signed public key + identity | X.509 certificate |
| Organisation that signs certificates | Certificate Authority (CA) |
| Self-verifiable trust hierarchy | PKI (Public Key Infrastructure) |
| Certificate that signs others | CA certificate |
| Device/user certificate | End-entity certificate |
| List of revoked certificates | CRL / OCSP |

---
## Core Content

### Symmetric Encryption

Both parties share the **same key** for encryption and decryption. Fast - hardware-accelerated. Used for bulk data encryption.

Common symmetric algorithms:

| Algorithm | Key size | Status |
|---|---|---|
| **AES** (Advanced Encryption Standard) | 128, 192, 256 bit | Current standard - use AES-256 |
| 3DES | 168 bit effective | Deprecated - avoid |
| ChaCha20 | 256 bit | Used in TLS 1.3 |
| DES | 56 bit | Broken - never use |

**Problem:** How do both parties securely exchange the symmetric key? If you transmit the key, an attacker who intercepts it can decrypt everything. This is the key exchange problem - solved by asymmetric cryptography.

### Asymmetric Encryption

Uses two mathematically related keys:
- **Public key:** Share freely. Encrypt data or verify signatures.
- **Private key:** Never share. Decrypt data or create signatures.

Common asymmetric algorithms:

| Algorithm | Key size | Use case |
|---|---|---|
| **RSA** | 2048, 3072, 4096 bit | Key exchange, signatures |
| **ECDSA** | 256, 384 bit (ECC) | Signatures (faster, smaller keys than RSA) |
| **Diffie-Hellman** | Groups 14–21 | Key exchange (IKE) |
| **ECDH** | ECC variant of DH | Key exchange (TLS 1.3, IKEv2) |

**Asymmetric is slow** - used only to exchange a symmetric key or create a signature. After the key exchange, symmetric encryption (AES) is used for bulk data.

### Hash Functions / HMAC

A **hash function** computes a fixed-length digest from arbitrary input. Properties: deterministic, one-way (can't reverse), collision-resistant (different inputs produce different digests).

| Algorithm | Output | Status |
|---|---|---|
| SHA-256 | 256 bit | Current standard |
| SHA-384 | 384 bit | Stronger, used in high-security |
| SHA-512 | 512 bit | Strongest common |
| SHA-1 | 160 bit | Deprecated for signatures |
| MD5 | 128 bit | Broken - never use for security |

**HMAC (Hash-based Message Authentication Code):** Hash with a shared key. Used in IPSec ESP and TLS for integrity verification. The receiver recomputes the HMAC and compares - any modification to the packet is detected.

### X.509 Certificates

An X.509 certificate is a digital document containing:

| Field | Content |
|---|---|
| **Version** | X.509 v3 |
| **Serial number** | Unique number assigned by CA |
| **Subject** | Identity: CN (Common Name), O (Organisation), C (Country) |
| **Issuer** | The CA that signed this certificate |
| **Validity** | Not Before / Not After (certificate lifetime) |
| **Public key** | The subject's public key (RSA or EC) |
| **Extensions** | Subject Alternative Name (SAN), Key Usage, Extended Key Usage, CRL/OCSP endpoints |
| **Signature** | CA's signature over the certificate content (verifies authenticity) |

Certificates are encoded in PEM (Base64 text) or DER (binary) format.

**Common Name (CN) vs Subject Alternative Name (SAN):** Modern TLS relies on SAN for hostname matching. CN is deprecated for this purpose but still present.

### Certificate Chain - Trust Hierarchy

```
Root CA (self-signed, in OS/browser trust store)
    └── Intermediate CA (signed by Root CA)
            └── End-entity certificate (signed by Intermediate CA)
```

Validation:
1. Verify end-entity signature using Intermediate CA's public key.
2. Verify Intermediate CA's signature using Root CA's public key.
3. Verify Root CA is in the trust store (self-signed, pre-trusted).
4. All signatures valid + chain complete → certificate trusted.

**Root CA private key security:** Root CAs are kept offline (air-gapped) - the private key is used only to sign intermediate CA certificates. The intermediate CA is the online signing authority for end-entity certificates. If the intermediate CA is compromised, the root CA can revoke it without destroying the root of trust.

### Certificate Revocation

Certificates have a validity period, but may need to be revoked early (private key compromised, device stolen, employee left). Two mechanisms:

**CRL (Certificate Revocation List):** The CA publishes a periodically updated list of revoked serial numbers. Clients download the CRL and check it. Problem: CRLs can be large; updates may lag reality by hours.

**OCSP (Online Certificate Status Protocol, RFC 6960):** A client queries the CA's OCSP responder in real time: "Is certificate serial 12345 revoked?" The OCSP responder answers good/revoked/unknown. Faster and more current than CRL. **OCSP Stapling** moves the OCSP check to the server - the server periodically queries its own OCSP and includes the response in the TLS handshake.

### PKI in Network Security

**IPSec IKE with certificates:**
- Each VPN gateway has a certificate issued by a shared CA.
- During IKE Phase 1, each peer sends its certificate.
- The other peer verifies the certificate chain and the peer's identity.
- No pre-shared key needed - scales to any number of sites.

**TLS (Transport Layer Security):**
- Server presents a certificate to the client.
- Client verifies the certificate chain and server hostname.
- After verification, ECDH key exchange establishes a session key.
- All subsequent data encrypted with AES session key.

**EAP-TLS (802.1X):**
- Both the client (supplicant) and RADIUS server present certificates.
- Mutual authentication - the client verifies the server is the legitimate RADIUS, and the server verifies the client's certificate.
- No username/password - certificate = identity credential.
- Considered the strongest 802.1X authentication method.

### TLS Versions

| Version | Status |
|---|---|
| TLS 1.0 | Deprecated (RFC 8996) |
| TLS 1.1 | Deprecated (RFC 8996) |
| TLS 1.2 | Current - widely deployed |
| TLS 1.3 | Current - preferred; fewer cipher suites, mandatory forward secrecy |

TLS 1.3 eliminates weak cipher suites (no RSA key exchange, no static DH, no RC4, no 3DES) and mandates ECDHE for key exchange - ensuring forward secrecy (session keys derived independently; past sessions cannot be decrypted even if private key is later compromised).

---
## Common Pitfalls

1. **Expired certificates causing outages.** A certificate with an expired Not-After date is rejected by all verifying peers - VPN tunnels drop, TLS handshakes fail, 802.1X authentication refuses clients. Implement certificate expiry monitoring (alert 30–60 days before expiry). Automate renewal where possible (ACME protocol / Let's Encrypt for public-facing services).

2. **Root CA not in all device trust stores.** An internal PKI's root CA certificate must be pushed to all devices (OS trust store, browser, network device, RADIUS server) that need to validate certificates signed by that CA. Missing root CA = "untrusted certificate" errors.

3. **Private key not protected.** The private key must never be transmitted, stored unencrypted, or backed up to insecure locations. If a private key is compromised, revoke the certificate immediately and generate a new key pair.

4. **Using MD5 or SHA-1 for signatures.** MD5 is cryptographically broken; SHA-1 is deprecated for certificate signatures (browsers reject SHA-1 certificates). Use SHA-256 or higher for all new certificates and HMAC operations.

5. **Not validating the full chain.** A certificate signed by an intermediate CA requires the client to also trust the intermediate CA's certificate (included in the TLS handshake or separately pre-loaded). A missing intermediate CA in the chain causes validation failure even if the root is trusted.

---
## Practice Problems

**Q1.** Why is symmetric encryption used for bulk data and asymmetric only for key exchange?

??? answer
    Asymmetric encryption (RSA, ECDH) is computationally expensive - encrypting large amounts of data with RSA is 100–1000× slower than AES. Asymmetric is used once at the start of a session to securely exchange a symmetric session key; after that, all bulk data is encrypted with the fast symmetric key (AES). This hybrid approach gets the security benefit of asymmetric key exchange and the performance of symmetric encryption.

**Q2.** What is the purpose of the Intermediate CA in a PKI hierarchy, and why is the Root CA kept offline?

??? answer
    The intermediate CA is the online signing authority for end-entity certificates (servers, users, devices). If the intermediate CA's private key is compromised, the root CA can revoke the intermediate CA's certificate and issue a new one - limiting the blast radius. The root CA is kept offline (air-gapped) because its private key is irreplaceable; if the root is compromised, the entire PKI must be rebuilt from scratch.

**Q3.** What is forward secrecy, and why does TLS 1.3 mandate it?

??? answer
    Forward secrecy means that the compromise of the server's private key at some future point cannot be used to decrypt recorded past sessions. In TLS 1.2 with RSA key exchange, the session key was encrypted with the server's public key - if the private key is later obtained, all past recorded sessions can be decrypted. TLS 1.3 mandates ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) - a new DH key pair is generated per session and discarded afterwards. The session key derivation is independent of the server's long-term private key.

---
## Summary & Key Takeaways

- **Symmetric encryption (AES):** Same key for encrypt/decrypt; fast; used for bulk data.
- **Asymmetric encryption (RSA, ECDSA):** Public/private key pair; slow; used for key exchange and signatures only.
- Hybrid approach: asymmetric for key exchange → symmetric for data.
- **X.509 certificates** bind a public key to an identity, signed by a CA.
- **Certificate chain:** End-entity → Intermediate CA → Root CA. Validation walks the chain to the trusted root.
- **Root CA** stays offline - compromise would destroy the entire PKI.
- **CRL/OCSP:** Revocation mechanisms - OCSP Stapling preferred for performance.
- **TLS 1.3** mandates ECDHE (forward secrecy) and eliminates all weak cipher suites.
- PKI is the foundation of IPSec certificate auth, TLS, and EAP-TLS for 802.1X.
- Use SHA-256+ for all new certificates; never use MD5 or SHA-1.

---
## Where to Next

- **SEC-006 - Network Segmentation & DMZ:** PKI placement within a segmented architecture.
- **AUTO-002 - REST APIs & Network Automation:** TLS certificates used to secure API endpoints.
- **CT-001 - MPLS Fundamentals:** RSVP-TE signalling may use certificate-based authentication in some deployments.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 5280 | X.509 PKI Certificate and CRL Profile |
| RFC 6960 | Online Certificate Status Protocol (OCSP) |
| RFC 8446 | TLS 1.3 |
| NIST SP 800-57 | Key Management Recommendations |
| Cisco CCNP Security | PKI, certificate management, EAP-TLS |
| CompTIA Security+ | Encryption, PKI, certificate types |

---
## References

- RFC 5280 - Internet X.509 PKI Certificate and CRL Profile. [https://www.rfc-editor.org/rfc/rfc5280](https://www.rfc-editor.org/rfc/rfc5280)
- RFC 6960 - OCSP. [https://www.rfc-editor.org/rfc/rfc6960](https://www.rfc-editor.org/rfc/rfc6960)
- RFC 8446 - TLS 1.3. [https://www.rfc-editor.org/rfc/rfc8446](https://www.rfc-editor.org/rfc/rfc8446)

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
| SEC-003 | VPN & IPSec | Certificate-based IKE authentication |
| SEC-004 | AAA - TACACS+ & RADIUS | EAP-TLS certificates for 802.1X |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SEC-003 | VPN & IPSec | IPSec uses PKI for IKE peer authentication |
| SEC-004 | AAA - TACACS+ & RADIUS | EAP-TLS 802.1X uses certificates |
<!-- XREF-END -->
