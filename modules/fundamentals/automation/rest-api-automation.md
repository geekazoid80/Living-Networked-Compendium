---
id: AUTO-002
title: "REST APIs & Network Automation"
description: "How to use HTTP-based APIs (RESTCONF, eAPI, NX-API, Meraki API) to retrieve structured data and automate network device configuration without SSH."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 50
prerequisites:
  - AUTO-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - automation
  - rest-api
  - restconf
  - http
  - json
  - python
  - network-automation
created: 2026-04-19
updated: 2026-04-19
---

# AUTO-002 — REST APIs & Network Automation

## The Problem

Netmiko works well — but it still operates like a human operator. You send CLI commands; you receive CLI text. The device doesn't know you're a script rather than a human. You must parse that text (fragile). You must know the exact CLI syntax of every platform. You must handle pagination, prompts, enable mode.

What if the device could provide data in a structured format — already in JSON, already labelled, ready to use without any parsing?

### Step 1: The device speaks HTTP

Modern network operating systems embed a web server. Instead of opening an SSH session and typing commands, your script sends an HTTP request to a URL on the device — and receives JSON or XML back. No prompt handling. No pagination. No text parsing.

This is a **REST API** (Representational State Transfer Application Programming Interface): a standard way of accessing resources over HTTP using structured data.

### Step 2: Standard verbs, standard data

REST uses HTTP verbs to express intent:
- **GET** — read data (show equivalent)
- **POST** — create a new resource (add config)
- **PUT** — replace a resource (overwrite config)
- **PATCH** — update part of a resource (modify config)
- **DELETE** — remove a resource (delete config)

The device returns JSON (or XML). Your script reads it as a Python dictionary — no parsing required. You can extract `response['interfaces']['GigabitEthernet0/1']['oper-status']` directly.

### Step 3: Standardise across platforms

Each vendor's REST API uses a different URL structure and data format. **RESTCONF** (RFC 8040) standardises this: a YANG-modelled API over HTTP. The same URL patterns and data schemas work across any RESTCONF-compliant device. YANG models define what data exists and what format it must be in — the device validates your payload before applying it.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Device provides structured data over HTTP | REST API |
| HTTP read / write / update / delete operations | GET / POST / PUT / PATCH / DELETE |
| Structured data format from device | JSON / XML |
| IETF standard REST API for network devices | RESTCONF (RFC 8040) |
| Data schema that defines the API structure | YANG model |
| Arista's proprietary JSON API | eAPI |
| Cisco NX-OS JSON API | NX-API |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain what a REST API is and how HTTP verbs map to network operations.
2. Use Python `requests` to send REST API calls and process JSON responses.
3. Use RESTCONF to retrieve and modify device configuration and operational data.
4. Explain YANG models as the schema behind RESTCONF.
5. Demonstrate use of vendor REST APIs (eAPI, NX-API, Meraki).
6. Explain when REST APIs are preferable to SSH/CLI automation.

---

## Prerequisites

- AUTO-001 — Python for Network Engineers (Python basics, SSH automation context)

---

## Core Content

### REST Fundamentals

A REST API uses HTTP as its transport. Every resource has a URL:

```
https://device-ip/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F1
```

HTTP headers specify:
- `Accept: application/yang-data+json` — request JSON response
- `Content-Type: application/yang-data+json` — sending JSON payload
- `Authorization: Basic <base64-encoded username:password>` — authentication

### Python `requests` Library

```python
import requests
import json

# Disable SSL warnings for self-signed certs in lab
import urllib3
urllib3.disable_warnings()

BASE_URL = 'https://192.168.1.1'
AUTH = ('admin', 'password')
HEADERS = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json',
}

# GET — read interface data
url = f'{BASE_URL}/restconf/data/ietf-interfaces:interfaces'
response = requests.get(url, auth=AUTH, headers=HEADERS, verify=False)
response.raise_for_status()    # raise exception on HTTP error

data = response.json()
for iface in data['ietf-interfaces:interfaces']['interface']:
    print(f"{iface['name']}: {iface.get('description', 'no description')}")
```

```python
# PATCH — update interface description
url = f'{BASE_URL}/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F1'
payload = {
    "ietf-interfaces:interface": {
        "name": "GigabitEthernet0/1",
        "description": "AUTOMATION-MANAGED",
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": True
    }
}
response = requests.patch(url, auth=AUTH, headers=HEADERS,
                          data=json.dumps(payload), verify=False)
response.raise_for_status()
print(f"PATCH status: {response.status_code}")    # 204 No Content on success
```

### RESTCONF — IETF Standard REST API

RESTCONF (RFC 8040) defines URL conventions for accessing YANG-modelled data:

| URL pattern | Resource |
|---|---|
| `/restconf/data/` | Root of the data store |
| `/restconf/data/<module>:<container>` | Top-level YANG container |
| `/restconf/data/<module>:<container>/<list>={key}` | List element by key |
| `/restconf/operations/<module>:<rpc>` | YANG RPC (action) |

YANG models are identified by module name. Common IETF models:
- `ietf-interfaces` — interface configuration and state
- `ietf-routing` — routing configuration
- `ietf-ip` — IP address configuration
- `ietf-network-instance` — VRF/network instances

Cisco also publishes native YANG models (`Cisco-IOS-XE-*`, `Cisco-IOS-XR-*`) that expose more platform-specific data.

**Discovering what's available:** The RESTCONF capability endpoint lists supported models:

```python
caps_url = f'{BASE_URL}/restconf/data/netconf-state/capabilities'
response = requests.get(caps_url, auth=AUTH, headers=HEADERS, verify=False)
print(json.dumps(response.json(), indent=2))
```

### YANG — The Schema Behind RESTCONF

YANG (RFC 7950) is a data modelling language. A YANG model defines:
- What data exists on the device
- What data types and values are valid
- The hierarchical structure of the data

You do not need to write YANG to use RESTCONF — but understanding the model tells you what URLs and data structures are valid. Tools like `pyang` and Cisco's YANG Suite let you explore models visually.

### Arista eAPI

Arista EOS exposes a JSON-RPC API (`eAPI`) over HTTPS (or HTTP in lab). Send CLI commands; receive structured JSON responses. eAPI is simpler than RESTCONF for Arista-specific work.

```python
import requests
import json

payload = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {
        "version": 1,
        "cmds": ["show version", "show ip interface brief"],
        "format": "json"
    },
    "id": "1"
}

response = requests.post(
    'https://192.168.1.10/command-api',
    auth=('admin', 'password'),
    json=payload,
    verify=False
)
result = response.json()['result']
print(f"EOS version: {result[0]['version']}")
for iface, data in result[1]['interfaces'].items():
    print(f"  {iface}: {data['interfaceAddress'].get('primaryIp', {}).get('address', 'no IP')}")
```

### Cisco NX-API

Cisco NX-OS provides NX-API: a JSON (or XML) REST interface to NX-OS CLI or object model.

```python
import requests

url = 'https://192.168.1.20/ins'
headers = {
    'content-type': 'application/json-rpc',
    'cache-control': 'no-cache',
}
payload = [
    {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show version", "ver": 1}, "id": 1}
]

response = requests.post(url, auth=('admin', 'password'),
                         json=payload, headers=headers, verify=False)
print(response.json()[0]['result']['body']['sys_ver_str'])
```

### Meraki Dashboard API

For Meraki (cloud-managed), all configuration goes through the Meraki Dashboard API — there is no SSH or RESTCONF on the devices. The API is hosted on `api.meraki.com`.

```python
import requests

API_KEY = 'your-meraki-api-key'
ORG_ID = 'your-org-id'

headers = {
    'X-Cisco-Meraki-API-Key': API_KEY,
    'Content-Type': 'application/json',
}

# Get all networks in the organisation
response = requests.get(
    f'https://api.meraki.com/api/v1/organizations/{ORG_ID}/networks',
    headers=headers
)
for network in response.json():
    print(f"{network['id']}: {network['name']}")
```

### REST vs SSH/CLI — When to Use Each

| Scenario | Preferred approach |
|---|---|
| Retrieving structured operational data | REST API / RESTCONF |
| Cross-vendor config management with standard schema | RESTCONF + YANG |
| Arista EOS single-vendor | eAPI |
| Cisco NX-OS | NX-API or RESTCONF |
| Meraki cloud-managed devices | Meraki Dashboard API |
| Devices with no REST API (older platforms) | Netmiko (SSH) |
| Complex multi-step config with platform-specific commands | Netmiko |
| Bulk config changes with declarative state | Ansible / NAPALM (may use REST internally) |

---

## Common Pitfalls

1. **Self-signed certificate errors.** Network devices use self-signed TLS certificates. `requests` validates SSL by default — `verify=False` disables this in lab. In production, install the device's CA certificate and pass `verify='/path/to/ca.crt'`. Never use `verify=False` in production; it opens the connection to MITM attacks.

2. **URL-encoding interface names.** Interface names contain `/` (e.g., `GigabitEthernet0/1`). In a RESTCONF URL, `/` must be percent-encoded as `%2F`. Python's `requests` does not do this automatically for path components — encode it manually or use `urllib.parse.quote(name, safe='')`.

3. **404 on valid RESTCONF paths.** RESTCONF may not be enabled by default. On Cisco IOS-XE: `restconf` (global config command). On NX-OS: `feature restconf`. Verify the device's YANG model support — not all models work on all OS versions.

4. **Checking only HTTP status, not error body.** A 400 Bad Request includes an error description in the response body (JSON). Always print `response.text` or `response.json()` when you get a non-2xx response — the device tells you exactly what was wrong with the payload.

5. **Not paginating large responses.** Some APIs paginate large results (e.g., Meraki returns a `Link: <url>; rel=next` header when there are more results). Fetch all pages before processing; don't assume the first response is complete.

---

## Practice Problems

**Q1.** You use `requests.get()` against a device's RESTCONF endpoint and receive a 401 status code. What is the most likely cause and how do you fix it?

??? answer
    A 401 Unauthorized status means authentication failed. Most common causes: wrong username/password in the `auth=` parameter, or RESTCONF is configured to use a specific authentication method (e.g., token-based rather than basic auth) that your request doesn't match. Check the device's RESTCONF authentication configuration. Also verify the user account has the required privilege level for REST API access (some platforms require a separate API access role).

**Q2.** You PATCH an interface description via RESTCONF and receive a 204 No Content response. You then do a GET on the same resource and the description has not changed. What might be wrong?

??? answer
    A 204 means the request was syntactically accepted, but the change may not have been committed or saved. On some platforms, RESTCONF changes are applied to the running config but not automatically saved to startup config — run `write memory` or equivalent. Also check if the device uses a candidate/commit model (NETCONF-style) where changes are staged; in that case you may need to commit. Additionally, verify you're reading the same datastore you wrote to (running vs startup vs candidate).

**Q3.** What is the difference between RESTCONF and NX-API or eAPI?

??? answer
    RESTCONF (RFC 8040) is an IETF standard that exposes YANG-modelled data over HTTP. It uses standardised URL conventions and YANG schemas — the same code structure works on any RESTCONF-compliant device (Cisco, Juniper, Nokia). NX-API and Arista eAPI are proprietary REST APIs specific to their platforms. They typically expose CLI commands as JSON-RPC calls or a platform-specific object model. They are easier to use for single-vendor environments but not portable across vendors.

---

## Summary & Key Takeaways

- REST APIs expose network device data and configuration over HTTP using structured JSON/XML — no CLI text parsing required.
- HTTP verbs: **GET** (read), **POST** (create), **PUT** (replace), **PATCH** (update), **DELETE** (remove).
- **RESTCONF** (RFC 8040) is the IETF standard REST API for YANG-modelled network data — portable across vendors.
- **YANG** defines the data schema — understanding it tells you what URLs and payloads are valid.
- **eAPI** (Arista) and **NX-API** (Cisco NX-OS) are proprietary alternatives — simpler for single-vendor use.
- **Meraki Dashboard API** is the only management interface for Meraki; there is no SSH.
- Always URL-encode interface names containing `/` in RESTCONF paths.
- Use `verify=False` only in lab; in production pass a CA certificate for TLS validation.

---

## Where to Next

- **AUTO-003 — NETCONF, YANG & gRPC:** Lower-level structured management protocol; RESTCONF is a REST-over-HTTP wrapper for the same YANG data.
- **AUTO-004 — Ansible for Network Automation:** Declarative automation using modules that call REST APIs internally.
- **CT-001 — MPLS Fundamentals:** RESTCONF/YANG used in SR-MPLS provisioning via modern NOS.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| RFC 8040 | RESTCONF Protocol |
| RFC 7950 | YANG 1.1 Data Modelling Language |
| RFC 7951 | JSON Encoding of YANG Data |
| Cisco DevNet Associate | RESTCONF, YANG, eAPI, REST automation |
| Cisco CCNP Enterprise | Network programmability |
| CompTIA Network+ | Automation concepts |

---

## References

- RFC 8040 — RESTCONF Protocol. [https://www.rfc-editor.org/rfc/rfc8040](https://www.rfc-editor.org/rfc/rfc8040)
- RFC 7950 — YANG 1.1. [https://www.rfc-editor.org/rfc/rfc7950](https://www.rfc-editor.org/rfc/rfc7950)
- Arista eAPI documentation: [https://aristanetworks.github.io/EapiExplorer/](https://aristanetworks.github.io/EapiExplorer/)
- Cisco YANG Suite: [https://developer.cisco.com/yangsuite/](https://developer.cisco.com/yangsuite/)
- Meraki Dashboard API: [https://developer.cisco.com/meraki/api-v1/](https://developer.cisco.com/meraki/api-v1/)

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
| AUTO-003 | NETCONF, YANG & gRPC | RESTCONF is REST-over-HTTP layer above NETCONF/YANG |
| AUTO-004 | Ansible for Network Automation | Ansible modules use REST APIs internally |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| AUTO-001 | Python for Network Engineers | Python scripting foundation for REST API calls |
<!-- XREF-END -->
