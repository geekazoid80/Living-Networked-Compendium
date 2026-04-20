---
id: AUTO-001
title: "Python for Network Engineers"
description: "How to use Python with Netmiko, NAPALM, and Paramiko to automate network device configuration, data retrieval, and change management."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - SV-005
  - RT-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - automation
  - python
  - netmiko
  - napalm
  - paramiko
  - network-automation
created: 2026-04-19
updated: 2026-04-19
---

# AUTO-001 — Python for Network Engineers

## The Problem

You have 200 switches. You need to add a new VLAN to all of them. Manual approach: SSH to each switch, enter configuration mode, add the VLAN, save. At 3 minutes per switch, that's 10 hours of repetitive work, with a high probability of a typo on switch 173 that causes an outage at 2am.

### Step 1: SSH programmatically

Python can open SSH connections and send commands just as you would manually, but at machine speed. You write the logic once; the script runs it on 200 devices simultaneously.

### Step 2: A library that understands network devices

Raw SSH (Paramiko) requires you to handle prompts, pagination, login banners, and `--More--` pauses manually — each vendor behaves differently. **Netmiko** wraps Paramiko with per-vendor knowledge: it knows how to log in to a Cisco IOS switch, disable pagination, handle config mode prompts, and enter/exit enable mode.

### Step 3: Vendor-agnostic automation

Even with Netmiko, the commands you send (`interface vlan 10` on Cisco vs `set vlans VLAN10 vlan-id 10` on Junos) differ per platform. **NAPALM** provides a standardised API: `device.get_interfaces()`, `device.load_merge_candidate()`, `device.compare_config()`, `device.commit_config()` — the same function calls work across Cisco IOS, Junos, EOS, and others.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| SSH library for network devices | Netmiko / Paramiko |
| Vendor-agnostic network API | NAPALM |
| Safely staging and comparing config | Configuration candidate / diff |
| Running the same task on many devices | Automation loop |
| Defining tasks in reusable code | Script / function |

---

## Learning Objectives

After completing this module you will be able to:

1. Explain why Python automation is necessary at network scale.
2. Use Netmiko to open SSH connections and send commands to network devices.
3. Use NAPALM to retrieve structured device data and manage configuration changes.
4. Build a simple script that configures a VLAN across multiple switches.
5. Handle errors and device connection failures gracefully.
6. Explain structured vs unstructured data output and when to use TextFSM/Genie parsers.

---

## Prerequisites

- SV-005 — SNMP & Syslog (monitoring context — automation supplements monitoring)
- RT-001 — Routing Fundamentals (context for what you're automating)
- Basic Python familiarity (variables, loops, functions, exception handling) assumed

---

## Core Content

### Why Not Just Use CLI?

CLI is designed for humans. It produces unstructured text that humans can read but programs cannot easily parse. `show ip route` returns many lines of text — extracting the next-hop for a specific prefix requires string parsing that is fragile across software versions.

Automation requires:
- **Reliable connection handling** (reconnect on failure, handle SSH host key changes, handle banners).
- **Structured data** (lists, dicts) — not screen-scraping text.
- **Change safety** (preview, diff, rollback).
- **Scale** — same code runs on 1 or 1000 devices.

### Paramiko — Low-Level SSH

Paramiko is the Python SSH library. It handles the SSH protocol but nothing network-device-specific. You must handle:
- Login prompts and password entry.
- `enable` / `configure terminal` mode transitions.
- Pagination (`--More--` on long outputs).
- Platform-specific prompt detection (to know when the device is ready for the next command).

Paramiko is used when you need full control or when Netmiko doesn't support your device. For most network automation, use Netmiko instead.

### Netmiko — Network-Aware SSH

Netmiko extends Paramiko with per-platform handlers. Supported platforms include: Cisco IOS, IOS-XE, IOS-XR, Junos, EOS, Nokia SR-OS, MikroTik, Huawei VRP, and dozens more.

```python
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'secret': 'enable_secret',    # for enable mode
}

with ConnectHandler(**device) as net_connect:
    # Send show command, returns string
    output = net_connect.send_command('show ip interface brief')
    print(output)

    # Enter config mode, send config commands, exit
    net_connect.enable()
    net_connect.config_mode()
    config_commands = [
        'vlan 100',
        ' name AUTOMATION-TEST',
        ' exit',
    ]
    output = net_connect.send_config_set(config_commands)
    print(output)
```

Key Netmiko features:
- `send_command()`: Sends a show command, waits for prompt, returns output.
- `send_config_set()`: Sends a list of config commands in config mode.
- `find_prompt()`: Returns the current prompt string.
- `save_config()`: Platform-appropriate save (`write mem`, `commit`, etc.).

### Parsing Unstructured Output — TextFSM / Genie

`show` commands return text. To use the data programmatically, parse it into structured form.

**TextFSM:** A template-based parser. A template defines the structure of the expected output; TextFSM applies it and returns a list of dictionaries. The `ntc-templates` library provides pre-built TextFSM templates for hundreds of Cisco, Juniper, and other show commands.

```python
from netmiko import ConnectHandler
import json

with ConnectHandler(**device) as conn:
    output = conn.send_command('show ip bgp summary', use_textfsm=True)
    # output is now a list of dicts (structured data)
    for peer in output:
        print(f"Peer: {peer['bgp_neigh']} State: {peer['state_pfxrcd']}")
```

**Genie / PyATS (Cisco):** A more sophisticated parser and testing framework from Cisco. Genie parsers understand the semantics of the output — not just the structure. Works with Cisco platforms.

### NAPALM — Vendor-Agnostic API

NAPALM provides a unified API across network platforms. The same Python code works on Cisco IOS, IOS-XE, Junos, EOS, and others — NAPALM handles the platform differences internally.

```python
from napalm import get_network_driver

driver = get_network_driver('ios')    # or 'junos', 'eos', 'iosxr'
device = driver('192.168.1.1', 'admin', 'password')
device.open()

# Retrieve structured data
facts = device.get_facts()
print(facts)  # dict: hostname, vendor, model, os_version, uptime, interfaces

interfaces = device.get_interfaces()
bgp_neighbors = device.get_bgp_neighbors()
route_table = device.get_route_to('10.0.0.0/8')

# Configuration management
device.load_merge_candidate(config="interface Loopback100\n ip address 10.100.0.1 255.255.255.255\n")
diff = device.compare_config()    # see what will change
print(diff)
device.commit_config()            # apply
# or device.discard_config()      # abandon

device.close()
```

NAPALM key operations:
- `get_*()`: Retrieve facts, interfaces, BGP, routing table, LLDP neighbours, etc. All return structured Python dicts.
- `load_merge_candidate()` / `load_replace_candidate()`: Stage a configuration change.
- `compare_config()`: Show what will change (like `show | compare` on Junos, or generated diff for IOS).
- `commit_config()` / `discard_config()`: Apply or abandon.
- `rollback()`: Roll back to pre-change state.

### Looping Over Many Devices

```python
from netmiko import ConnectHandler
import json

devices = [
    {'device_type': 'cisco_ios', 'host': '192.168.1.1', 'username': 'admin', 'password': 'pw'},
    {'device_type': 'cisco_ios', 'host': '192.168.1.2', 'username': 'admin', 'password': 'pw'},
    {'device_type': 'arista_eos', 'host': '192.168.1.3', 'username': 'admin', 'password': 'pw'},
]

vlan_config = ['vlan 100', 'name AUTOMATION', 'exit']

results = {}
for dev in devices:
    try:
        with ConnectHandler(**dev) as conn:
            conn.enable()
            output = conn.send_config_set(vlan_config)
            conn.save_config()
            results[dev['host']] = 'SUCCESS'
    except Exception as e:
        results[dev['host']] = f'FAILED: {str(e)}'

print(json.dumps(results, indent=2))
```

**Parallel execution:** For large inventories, use `concurrent.futures.ThreadPoolExecutor` or Netmiko's built-in `Netmiko multi-threaded` functionality to run on many devices simultaneously rather than sequentially.

### Error Handling and Safety

Network automation failures can cause outages. Defensive practices:

1. **Dry-run mode:** Add a `--dry-run` flag. The script connects, generates the commands, and prints them without sending to the device. Review before executing.
2. **Pre/post validation:** Show command before and after the change; compare expected vs actual.
3. **Change window enforcement:** Script checks the current time and refuses to run outside the change window.
4. **Exception handling:** Every connection attempt in a `try/except`; log failures but continue to next device (a script that crashes on device 3 never reaches device 200).
5. **Inventory from files, not hardcoded:** Store device lists in YAML/CSV/NetBox; don't hardcode IPs in scripts.

---

## Vendor Implementations

All implementations use the same Python libraries — the `device_type` parameter selects the vendor handler. Key Netmiko device types:

| Platform | device_type |
|---|---|
| Cisco IOS / IOS-XE | `cisco_ios` |
| Cisco IOS-XR | `cisco_xr` |
| Cisco NX-OS | `cisco_nxos` |
| Juniper Junos | `juniper_junos` |
| Arista EOS | `arista_eos` |
| Nokia SR-OS | `nokia_sros` |
| MikroTik RouterOS | `mikrotik_routeros` |
| Huawei VRP | `huawei` |

NAPALM drivers: `ios`, `iosxr`, `junos`, `eos`, `nxos`.

Full Netmiko documentation: [https://ktbyers.github.io/netmiko/](https://ktbyers.github.io/netmiko/)
Full NAPALM documentation: [https://napalm.readthedocs.io/](https://napalm.readthedocs.io/)

---

## Common Pitfalls

1. **Hardcoded credentials in scripts.** Never put passwords in scripts or commit them to version control. Use environment variables (`os.environ['NET_PASSWORD']`), a secrets vault (HashiCorp Vault, Ansible Vault), or a secrets manager (AWS Secrets Manager).

2. **No timeout handling.** A device that hangs (waiting for a banner, slow console) causes the script to freeze indefinitely. Set `timeout` and `conn_timeout` in Netmiko; use `threading.Timer` for hard timeouts.

3. **Ignoring errors and continuing.** If VLAN 100 was not actually created on switch 5 (error ignored), the network is in an inconsistent state. Log and surface errors; run post-change validation to confirm state.

4. **Running automation during production hours.** A script that pushes configuration to 200 switches simultaneously during business hours will cause packet loss during the config push. Always use maintenance windows.

5. **Screen-scraping instead of structured data.** Parsing `show` command text with regex is fragile — a minor OS upgrade or regional locale change can break the parser. Use TextFSM/ntc-templates or NAPALM getters for any production automation that consumes output data.

---

## Practice Problems

**Q1.** You need to retrieve the BGP neighbour state from 50 routers. What is the most reliable approach?

??? answer
    Use NAPALM's `get_bgp_neighbors()` which returns a structured dictionary per platform. Alternatively, use Netmiko's `send_command('show bgp summary', use_textfsm=True)` with ntc-templates for structured parsing. Avoid raw regex parsing of `show bgp summary` text — it's fragile across OS versions and locale settings.

**Q2.** A script connecting to 100 devices fails on device 30 and crashes, never reaching devices 31–100. How do you fix this?

??? answer
    Wrap each device connection in a `try/except Exception` block. Catch all exceptions, log the error for that device, add it to a failures list, and `continue` to the next device. At the end, report all failures. The script must handle individual device failures gracefully without stopping the entire run.

**Q3.** What is the advantage of NAPALM's `compare_config()` before `commit_config()`?

??? answer
    `compare_config()` shows a diff of what will change — similar to `git diff` before a commit, or `show | compare` on Junos. This lets the operator review the exact configuration changes before applying them. It prevents unintended side effects (accidentally removing an existing config line, introducing a syntax error). Always review the diff before committing, especially in production.

---

## Summary & Key Takeaways

- Python automation eliminates repetitive manual CLI work and reduces human error.
- **Paramiko:** Low-level SSH library — use for unsupported devices or fine-grained control.
- **Netmiko:** Network-aware SSH with per-vendor handlers — the standard for CLI automation.
- **NAPALM:** Vendor-agnostic API — same code for Cisco IOS, Junos, EOS; use for multi-vendor automation.
- **TextFSM / ntc-templates:** Parse unstructured show output into structured Python data.
- Always handle exceptions per device; never let one failure stop the entire run.
- Never hardcode credentials; use environment variables or a secrets vault.
- Always run a dry-run and review diffs before applying config changes in production.

---

## Where to Next

- **AUTO-002 — REST APIs & Network Automation:** Automate via HTTP APIs (eAPI, NETCONF/RESTCONF).
- **AUTO-004 — Ansible for Network Automation:** Declarative automation with playbooks and roles.
- **PROTO-008 — NETCONF & YANG:** Structured configuration management protocol.

---

## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| Cisco DevNet Associate | Python for networking, Netmiko, NAPALM |
| Cisco CCNP Enterprise | Network automation overview |
| CompTIA Network+ | Automation concepts |

---

## References

- Netmiko documentation: [https://ktbyers.github.io/netmiko/](https://ktbyers.github.io/netmiko/)
- NAPALM documentation: [https://napalm.readthedocs.io/](https://napalm.readthedocs.io/)
- ntc-templates: [https://github.com/networktocode/ntc-templates](https://github.com/networktocode/ntc-templates)

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
| AUTO-002 | REST APIs & Network Automation | HTTP API automation builds on Python skills |
| AUTO-004 | Ansible for Network Automation | Ansible modules use Python internally |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| SV-005 | SNMP & Syslog | Monitoring context — automation supplements |
| RT-001 | Routing Fundamentals | Understanding what is being automated |
<!-- XREF-END -->
