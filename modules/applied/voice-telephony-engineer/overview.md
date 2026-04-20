---
title: "Applied: Voice / Telephony Network Engineer - Overview"
module_id: "VTE-000"
domain: "applied/voice-telephony-engineer"
difficulty: "intermediate"
prerequisites: ["NW-001", "IP-001", "IP-002", "RT-001", "SV-002", "PROTO-003"]
estimated_time: 15
version: "1.0"
last_updated: "2026-04-15"
maintainer: "@geekazoid80"
human_reviewed: false
ai_assisted: "drafting"
tags: [applied, voice, telephony, voip, sip, pstn, ss7, pbx, uc]
---

## The Analogy

Think of telephony like postal mail that got upgraded to phone calls. In the old days (PSTN), every call had its own dedicated delivery tube - a physical circuit was switched into place just for your conversation and held for the duration. Nobody else could use that tube while you were talking.

VoIP is like switching from dedicated tubes to putting your voice into envelopes (packets) and sending them through the same shared postal system as everyone else's letters. The conversation arrives in order (usually), and it's far cheaper to run - but now you have to manage the quality of the postal service to make sure your voice packets arrive on time, in order, without too much delay.

The modern challenge: making the packet postal system good enough that users can't tell the difference from the dedicated tube.

**Mapping:**
| Analogy | Technical Term |
|---|---|
| Dedicated tube per call | Circuit-switched PSTN (POTS, ISDN) |
| Shared postal system | Packet-switched IP network |
| Envelope | RTP/UDP packet |
| Postal address | IP address + port |
| Postal sorting system | SIP proxy / session border controller |
| Delivery quality (on-time) | Jitter, latency, packet loss (QoS) |
| Post office directory | DNS / ENUM / SIP registrar |

---

## What Is a Voice / Telephony Network Engineer?

A voice and telephony engineer designs, deploys, and operates the systems that carry real-time voice and video communications - from traditional phone systems to modern Unified Communications (UC) platforms.

This spans a wide range:
- Traditional PSTN and ISDN infrastructure
- VoIP (Voice over IP) using SIP, H.323
- PBX (Private Branch Exchange) systems - on-premise and cloud-hosted
- Session Border Controllers (SBCs) - the gatekeepers between enterprise VoIP and carrier networks
- Contact centre telephony infrastructure
- SS7/Signalling System 7 - the legacy telco signalling backbone (still carries billions of calls)
- WebRTC - browser-based real-time voice/video
- Unified Communications platforms (Cisco Webex, Microsoft Teams, Avaya, Zoom Phone)

**Where you'll find these engineers:** Enterprise IT departments managing PBX/UC systems, telcos (voice core network engineering), contact centre operators, SBC/gateway vendors, and cloud UC providers.

---

## Why This Is a Distinct Path

Voice is real-time. Unlike downloading a file - where a brief delay is invisible - a 300ms delay in voice is perceptible. A 1-second delay makes conversation impossible. This makes voice engineering fundamentally different from data networking:

- **QoS is non-negotiable.** Voice packets must be prioritised. QoS mis-configuration that "doesn't matter" for data will destroy call quality.
- **Signalling and media are separate.** SIP sets up the call. RTP carries the voice. Troubleshooting requires understanding both layers simultaneously.
- **PSTN interworking.** Real-world networks still connect to the PSTN. ISDN PRI, SIP trunks, and FXO/FXS interfaces all need to be understood.
- **Security:** VoIP systems are heavily targeted - toll fraud, eavesdropping, SIP brute force. Security is integral, not an afterthought.
- **Codec knowledge:** The choice of codec (G.711, G.729, Opus, iLBC) affects bandwidth, quality, and compatibility. Voice engineers must understand these trade-offs.

---

## Proposed Stage Overview

**Stage 1 - Foundation:**
NW-001, IP-001, IP-002, RT-001 (routing), SV-002 (DHCP - for IP phones), PROTO-003 (NTP - critical for call records), QOS-001 (QoS fundamentals)

**Stage 2 - Voice Protocols:**
SIP (Session Initiation Protocol - RFC 3261), H.323, RTP/RTCP, DTMF handling (RFC 2833 / RFC 4733)

**Stage 3 - PSTN & Legacy:**
PSTN architecture, POTS and ISDN (BRI/PRI), SS7 signalling architecture, PRI/SIP trunk interconnect

**Stage 4 - VoIP Infrastructure:**
SIP PBX design, Session Border Controllers (SBCs), NAT traversal for VoIP (STUN, TURN, ICE), SIP trunking

**Stage 5 - Quality & Troubleshooting:**
MOS (Mean Opinion Score), jitter buffers, codec selection, call quality monitoring (RTCP-XR), Wireshark for VoIP

**Stage 6 - Modern UC:**
WebRTC, Microsoft Teams Direct Routing, Cisco Webex Calling, contact centre architectures, E911 considerations

---

## See Full Learning Path

[learning-paths/voice-telephony-engineer.md](../../../learning-paths/voice-telephony-engineer.md) *(pending)*

## Call for Contributors

Open a GitHub Issue with label `voice-telephony-path`.
