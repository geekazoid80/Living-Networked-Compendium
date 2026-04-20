---
id: AUTO-003
title: "NETCONF, YANG & gRPC"
description: "How NETCONF, YANG data models, and gRPC/gNMI provide structured, transactional, and streaming-capable network management protocols."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 50
prerequisites:
  - AUTO-002
learning_path_tags:
  - DNE
  - CE
difficulty: advanced
tags:
  - netconf
  - yang
  - grpc
  - gnmi
  - gnoi
  - network-automation
  - programmability
created: 2026-04-19
updated: 2026-04-19
---

# AUTO-003 — NETCONF, YANG & gRPC

## The Problem

RESTCONF (AUTO-002) solved structured data retrieval — but it has limitations. You cannot subscribe to streaming telemetry (you must poll). Changes are applied but validation errors may only appear after you try to commit. Large-scale data collection via HTTP polling creates high overhead. High-frequency operational data (interface counters every second) is impractical over REST.

### Step 1: A transactional management protocol

**NETCONF** (RFC 6241) predates RESTCONF. It operates over SSH (or TLS), uses XML as its data encoding, and provides a transactional model: you edit a candidate configuration, validate it against the YANG schema, then commit — all as an atomic operation. If validation fails, nothing is applied. If you commit and need to undo, NETCONF supports confirmed-commit (auto-rollback if you don't re-confirm within a timeout).

NETCONF uses **RPCs** (Remote Procedure Calls): `get-config`, `edit-config`, `validate`, `commit`, `discard-changes`, `get` (operational data), `lock`/`unlock` (lock the config during a change window).

### Step 2: YANG — the common schema

The data in NETCONF (and RESTCONF) is structured by **YANG** (RFC 7950). YANG defines modules — hierarchical data models that specify what containers, lists, leaf nodes, and types exist on the device. A YANG-validated device rejects any configuration that doesn't conform to the model before it can cause a problem.

The same YANG model can be serialised to XML (for NETCONF), JSON (for RESTCONF), or Protocol Buffers (for gRPC). The schema is the same; the transport and encoding differ.

### Step 3: Streaming telemetry — from polling to push

For high-frequency operational data (BGP session states, interface error counters, CPU/memory, BFD sessions), polling REST APIs every second is too slow and too expensive. **gRPC** (Google Remote Procedure Call) and the **gNMI** (gRPC Network Management Interface) protocol allow a device to **push** data to a collector on a schedule you define — without the collector needing to ask each time. This is streaming telemetry.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| XML-based, transactional config management over SSH | NETCONF |
| Hierarchical data schema for network devices | YANG |
| Edit + validate + commit as atomic operation | Candidate/commit model |
| Auto-rollback if commit not confirmed | Confirmed-commit |
| HTTP REST version of NETCONF/YANG | RESTCONF |
| High-performance binary RPC protocol | gRPC |
| gRPC protocol for network device management | gNMI |
| Device pushing data to collector | Streaming telemetry |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain NETCONF architecture, datastores, and the candidate/commit model.
2. Use `ncclient` in Python to execute NETCONF RPCs.
3. Explain YANG models — modules, containers, lists, leaves, and types.
4. Describe RESTCONF as a REST-over-HTTP exposure of the same YANG data.
5. Explain gRPC and gNMI — how they differ from NETCONF/RESTCONF.
6. Describe streaming telemetry — subscriptions, sample intervals, and encodings.

---

## Prerequisites

- AUTO-002 — REST APIs & Network Automation (RESTCONF and YANG context)

---

## Core Content

### NETCONF Architecture

NETCONF (RFC 6241) is a management protocol based on:
- **Transport:** SSH (port 830) or TLS
- **Data encoding:** XML (always)
- **Operations:** RPC-based (`<get>`, `<get-config>`, `<edit-config>`, `<commit>`, `<validate>`, `<lock>`, `<unlock>`, `<discard-changes>`)

NETCONF uses datastores:

| Datastore | Purpose |
|---|---|
| `running` | The active, running configuration |
| `candidate` | A staging area for edits (requires capability `:candidate`) |
| `startup` | Config loaded at boot (may differ from running) |

Workflow with candidate:
1. `lock` the candidate datastore (prevents concurrent edits).
2. `edit-config` to the candidate.
3. `validate` — device checks the candidate against YANG schema.
4. `commit` — candidate becomes running (atomic).
5. `unlock`.

If validation fails: errors are returned; nothing applied. Use `discard-changes` to reset the candidate.

### Python ncclient

```python
from ncclient import manager
from ncclient.xml_ import to_ele

conn_params = {
    'host': '192.168.1.1',
    'port': 830,
    'username': 'admin',
    'password': 'password',
    'hostkey_verify': False,    # lab only
    'device_params': {'name': 'iosxe'},
}

with manager.connect(**conn_params) as m:
    # Get running configuration
    config = m.get_config(source='running')
    print(config.xml)

    # Get operational data (interfaces)
    filter_xml = '''
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name/>
          <enabled/>
        </interface>
      </interfaces>
    </filter>
    '''
    result = m.get(filter=('subtree', filter_xml))
    print(result.xml)
```

```python
    # Edit-config to candidate, then commit
    config_payload = '''
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet1</name>
          <description>NETCONF-MANAGED</description>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
            ianaift:ethernetCsmacd
          </type>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    '''
    with m.locked('candidate'):
        m.edit_config(target='candidate', config=config_payload)
        m.validate(source='candidate')
        m.commit()
```

### YANG Models — Structure

A YANG module defines:

```
module ietf-interfaces {
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  prefix if;

  container interfaces {          // container: a single instance of a group
    list interface {              // list: multiple instances, keyed
      key "name";
      leaf name { type string; }  // leaf: single value
      leaf description { type string; }
      leaf enabled { type boolean; }
      leaf-list alias { type string; } // leaf-list: multiple values of same type
    }
  }
}
```

Key constructs:

| Construct | Meaning |
|---|---|
| `container` | Grouping node — no key, single instance |
| `list` | Repeating node — has a `key` leaf |
| `leaf` | Single data value with a type |
| `leaf-list` | Multiple values of the same type |
| `choice` / `case` | Mutually exclusive data branches |
| `typedef` | Reusable type definition |
| `grouping` / `uses` | Reusable schema fragments |

YANG namespaces identify the module. When using NETCONF XML, the namespace must be specified on nodes to identify which module they belong to.

**Model sources:**
- **IETF models:** `ietf-interfaces`, `ietf-routing`, `ietf-ip` — standard, cross-vendor
- **OpenConfig models:** `openconfig-interfaces`, `openconfig-bgp` — industry consortium, broader vendor support
- **Vendor native models:** `Cisco-IOS-XE-*`, `Cisco-IOS-XR-*`, `junos-conf-root` — platform-specific, most complete

### gRPC and gNMI

**gRPC** (Google RPC) is a high-performance, binary-encoded RPC framework using Protocol Buffers (protobuf) as its schema and encoding. It runs over HTTP/2 — supports streaming natively (unidirectional and bidirectional).

**gNMI** (gRPC Network Management Interface, OpenConfig) uses gRPC for network device management. Operations:

| gNMI RPC | Equivalent |
|---|---|
| `Get` | Read operational or config data |
| `Set` | Write configuration (replace, update, delete) |
| `Subscribe` | Streaming telemetry — device pushes data to collector |
| `Capabilities` | Discover supported models and encodings |

gNMI supports three subscription modes:
- **STREAM SAMPLE:** Push data at a fixed interval (e.g., every 10 seconds).
- **STREAM ON_CHANGE:** Push only when the value changes.
- **ONCE:** Single snapshot, then close.

### Streaming Telemetry with gNMI

```python
# Using pygnmi library
from pygnmi.client import gNMIclient

with gNMIclient(target=('192.168.1.1', 57400),
                username='admin',
                password='password',
                insecure=True) as gc:

    # Capabilities
    caps = gc.capabilities()
    print(caps)

    # Get operational data
    result = gc.get(path=['openconfig-interfaces:interfaces'])
    print(result)

    # Subscribe — streaming sample every 10 seconds
    subscriptions = [
        {
            'path': 'openconfig-interfaces:interfaces/interface/state/counters',
            'mode': 'SAMPLE',
            'sample_interval': 10_000_000_000,  # nanoseconds
        }
    ]
    for update in gc.subscribe(subscribe={'subscription': subscriptions}):
        print(update)
```

### gNOI — gRPC Network Operations Interface

gNOI (OpenConfig) provides gRPC-based operations for network device management beyond config: ping, traceroute, OS install, certificate management, file operations. These replace SSH-based operational tasks in fully programmable environments.

### Protocol Comparison

| Property | NETCONF | RESTCONF | gNMI |
|---|---|---|---|
| Transport | SSH port 830 | HTTPS | gRPC / HTTP/2 |
| Encoding | XML | JSON or XML | Protocol Buffers (protobuf) |
| Schema | YANG | YANG | YANG (protobuf-encoded) |
| Transactions | Candidate/commit | Per-request (no transaction) | Set (atomic per call) |
| Streaming | No | No (polling only) | Yes — native streaming subscriptions |
| Primary use | Config management | Config + operational query | Telemetry collection + config |

---

## Common Pitfalls

1. **Missing NETCONF capability on device.** `ncclient` will fail to connect if NETCONF is not enabled. On Cisco IOS-XE: `netconf-yang` (global config). On Junos: `set system services netconf ssh`. Always verify the device has the capability before attempting connection.

2. **Namespace errors in NETCONF XML.** Every YANG module has a namespace URI. If the XML payload omits the namespace or uses the wrong one, the edit-config fails with a parse error. Check the YANG module header for the exact namespace string.

3. **Not locking before editing.** Without `lock()` on the candidate datastore, concurrent scripts or operators can modify the candidate simultaneously, producing unpredictable merges. Always lock, edit, commit, unlock — in that order.

4. **gNMI path syntax errors.** gNMI paths use `/` separators and `[key=value]` for list elements: `openconfig-interfaces:interfaces/interface[name=GigabitEthernet0/1]/state`. A syntax error typically returns a generic "path not found" error. Use a tool like `gnmic` CLI to test paths before coding them.

5. **Protobuf encoding not matching receiver.** gNMI supports JSON_IETF, JSON, and PROTO encodings. The telemetry collector must support the same encoding the device sends. Mismatch results in garbled data. Prefer JSON_IETF (human-readable, standard).

---

## Practice Problems

**Q1.** What is the advantage of NETCONF's candidate/commit model over RESTCONF's per-request model?

??? answer
    With NETCONF candidate/commit: all changes are staged in the candidate datastore first; `validate` checks the entire candidate against the YANG schema before anything is applied; `commit` makes all changes atomic (all-or-nothing). If any part fails validation, nothing is applied. RESTCONF applies each PATCH/PUT immediately to the running config — there is no staging or atomic multi-step transaction. For complex multi-parameter config changes (e.g., configuring a BGP peer with multiple related attributes), NETCONF's transactional model is safer.

**Q2.** Why is gNMI preferred over RESTCONF polling for interface counters monitored every 10 seconds across 500 devices?

??? answer
    REST polling requires your collector to send an HTTP GET request to every device every 10 seconds — 500 requests × 6 per minute = 3000 HTTP transactions per minute. This scales poorly: each request has connection overhead (TLS handshake if not persistent), and the device must respond to each individually. gNMI streaming telemetry uses a persistent HTTP/2 connection per device; the device pushes updates on the agreed schedule without being asked. The collector receives data with lower latency, less CPU load on both ends, and no polling overhead. gNMI is the standard for modern network telemetry.

**Q3.** A script using `ncclient` successfully connects and edits the candidate config, but `commit()` fails with an error referencing a missing mandatory leaf. How do you investigate?

??? answer
    Run `m.validate(source='candidate')` before `commit()` — validate returns the specific YANG validation error, including the path of the missing mandatory leaf and its YANG module. This tells you exactly which field is required. Review the YANG model for that container/list (using YANG browser or `pyang`) to find all mandatory leaves. Add the missing value to your edit-config payload and retry. Making validate explicit in the workflow (not relying on commit to discover errors) gives clearer error messages.

---

## Summary & Key Takeaways

- **NETCONF** is an XML/SSH-based management protocol with a transactional candidate/commit model — safer for complex config changes.
- **YANG** models define the data schema — the same schema used by NETCONF, RESTCONF, and gNMI.
- IETF, OpenConfig, and vendor-native YANG models differ in portability and completeness.
- **RESTCONF** is YANG data over HTTP REST — simpler than NETCONF but no transactions or streaming.
- **gRPC / gNMI** provides streaming telemetry — devices push data on a schedule without polling overhead.
- gNMI supports SAMPLE (periodic), ON_CHANGE, and ONCE subscription modes.
- For high-frequency monitoring at scale, gNMI streaming is far more efficient than REST polling.
- Always lock the candidate datastore, validate, commit, unlock — in that order.

---

## Where to Next

- **AUTO-004 — Ansible for Network Automation:** Ansible network modules use NETCONF and REST internally.
- **CT-001 — MPLS Fundamentals:** SR-MPLS provisioning uses NETCONF/YANG in modern carrier NOS.
- **AUTO-002 — REST APIs:** RESTCONF is the HTTP face of the same YANG data.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 6241 | NETCONF Protocol |
| RFC 7950 | YANG 1.1 |
| RFC 8040 | RESTCONF |
| OpenConfig gNMI | gRPC Network Management Interface specification |
| Cisco DevNet Associate | NETCONF, YANG, gRPC basics |
| Cisco DevNet Professional | gNMI telemetry, YANG models |

---

## References

- RFC 6241 — NETCONF Protocol. [https://www.rfc-editor.org/rfc/rfc6241](https://www.rfc-editor.org/rfc/rfc6241)
- RFC 7950 — YANG 1.1. [https://www.rfc-editor.org/rfc/rfc7950](https://www.rfc-editor.org/rfc/rfc7950)
- OpenConfig gNMI spec: [https://github.com/openconfig/gnmi](https://github.com/openconfig/gnmi)
- ncclient documentation: [https://ncclient.readthedocs.io/](https://ncclient.readthedocs.io/)
- gnmic CLI tool: [https://gnmic.openconfig.net/](https://gnmic.openconfig.net/)

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
| AUTO-004 | Ansible for Network Automation | Ansible NETCONF modules use ncclient |
| CT-001 | MPLS Fundamentals | SR-MPLS provisioning via NETCONF/YANG |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| AUTO-002 | REST APIs & Network Automation | RESTCONF is REST-over-HTTP layer above YANG |
<!-- XREF-END -->
