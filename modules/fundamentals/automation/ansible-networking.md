---
module_id: AUTO-004
title: "Ansible for Network Automation"
description: "How to use Ansible playbooks, network modules, and roles to declaratively manage network device configuration at scale."
version: "1.0.0"
status: draft
human_reviewed: false
ai_assisted: "drafting"
module_type: concept
estimated_time: 55
prerequisites:
  - AUTO-001
learning_path_tags:
  - DNE
difficulty: intermediate
tags:
  - automation
  - ansible
  - playbooks
  - network-automation
  - declarative
  - idempotent
created: 2026-04-19
updated: 2026-04-19
---

# AUTO-004 - Ansible for Network Automation
## Learning Objectives

After completing this module you will be able to:

1. Explain Ansible's architecture - control node, managed nodes, inventory, playbooks, modules.
2. Write a basic inventory and playbook to configure network devices.
3. Use Cisco IOS and Juniper Junos network modules.
4. Use variables, host_vars, and group_vars to manage per-device and per-group configuration.
5. Implement a network role for a reusable configuration pattern.
6. Explain idempotency and why it matters for network automation.

---
## Prerequisites

- AUTO-001 - Python for Network Engineers (Python context; Ansible uses Python internally)

---
## The Problem

You have a working Python/Netmiko script that pushes VLAN configuration to 200 switches. It works - but six months later:

- A new engineer doesn't know what state the switches are supposed to be in without reading the script.
- Running the script twice risks pushing duplicate commands.
- Different engineers wrote different scripts for different platforms - there's no consistency.
- You need to track which version of the script was applied to which devices.
- You need to apply the change to only a subset of switches (production vs lab) without editing the script.

### Step 1: Describe desired state, not steps

Instead of writing "send these commands in this order", describe *what the device should look like*: "VLAN 100 should exist, named AUTOMATION". If it already exists, do nothing. This is **declarative** automation - you state the outcome, not the procedure.

### Step 2: Separate inventory from logic

Your devices are listed in an **inventory** file (static or dynamic from NetBox/CMDB). Your logic is in a **playbook**. A playbook can run against `all` devices, or a named group (`switches`, `production-core`), or a single host - without changing the playbook. Limiting scope is an inventory and command-line decision, not a code edit.

### Step 3: Reuse across projects

Common configuration patterns (NTP configuration, SNMP configuration, AAA) are packaged as **roles** - self-contained, reusable bundles. You write a role once, apply it across all playbooks. Other engineers can use the same role without knowing its internals.

### What You Just Built

| Scenario element | Technical term |
|---|---|
| Describe what should be, not how to do it | Declarative automation |
| Running the same playbook twice is safe | Idempotency |
| Inventory defines which devices to target | Ansible inventory |
| Ordered list of tasks to execute | Playbook |
| Individual action (send config, register output) | Task |
| Reusable packaged set of tasks | Role |
| Per-device or per-group variable definitions | Host vars / Group vars |
| Ansible's collection of network modules | ansible.netcommon / cisco.ios / junipernetworks.junos |

---
## Core Content

### Ansible Architecture

Ansible runs from a **control node** (your laptop or a CI/CD server). It connects to **managed nodes** (network devices) and executes **modules** - small Python programs that implement each task. For network devices, Ansible typically connects via SSH (using Netmiko or Paramiko under the hood) or NETCONF/REST.

No agent is required on managed devices - Ansible is agentless.

```
Control Node (Ansible)
├── inventory/           # Which devices exist
│   ├── hosts.yml        # Static host definitions
│   └── group_vars/      # Variables per group
├── playbooks/           # What to do
│   └── site.yml
└── roles/               # Reusable task bundles
    └── ntp/
        ├── tasks/main.yml
        └── defaults/main.yml
```

### Inventory

```yaml
# inventory/hosts.yml
all:
  children:
    switches:
      hosts:
        sw-01:
          ansible_host: 192.168.1.1
        sw-02:
          ansible_host: 192.168.1.2
      vars:
        ansible_network_os: cisco.ios.ios
        ansible_connection: network_cli
        ansible_user: admin
        ansible_password: "{{ vault_password }}"
        ansible_become: yes
        ansible_become_method: enable
        ansible_become_password: "{{ vault_enable }}"

    routers:
      hosts:
        rtr-01:
          ansible_host: 192.168.1.10
          ansible_network_os: junipernetworks.junos.junos
          ansible_connection: netconf
          ansible_user: admin
          ansible_password: "{{ vault_password }}"
```

### Playbooks

```yaml
# playbooks/vlan.yml
---
- name: Configure VLANs on all switches
  hosts: switches
  gather_facts: no

  tasks:
    - name: Ensure VLAN 100 exists
      cisco.ios.ios_vlans:
        config:
          - vlan_id: 100
            name: AUTOMATION
            state: active
        state: merged      # merge with existing — idempotent

    - name: Save running config to startup
      cisco.ios.ios_command:
        commands: write memory
```

Key playbook elements:
- `hosts:` - which inventory group or host to target
- `gather_facts: no` - skip fact gathering (saves time on network devices)
- `state: merged` - merge with existing config (don't wipe); `replaced` replaces the full resource; `deleted` removes it
- Module names are namespaced: `cisco.ios.ios_vlans`, `junipernetworks.junos.junos_vlans`

### Network Modules - Resource Modules

Ansible network collections (installed via `ansible-galaxy collection install`) include **resource modules** that manage specific configuration resources idempotently.

Common Cisco IOS resource modules:

| Module | Manages |
|---|---|
| `cisco.ios.ios_vlans` | VLAN database |
| `cisco.ios.ios_interfaces` | Interface configuration |
| `cisco.ios.ios_l2_interfaces` | Layer 2 interface (access/trunk/native VLAN) |
| `cisco.ios.ios_l3_interfaces` | Layer 3 interface (IP addresses) |
| `cisco.ios.ios_bgp_global` | BGP global configuration |
| `cisco.ios.ios_ospfv2` | OSPFv2 configuration |
| `cisco.ios.ios_acls` | Access control lists |
| `cisco.ios.ios_ntp_global` | NTP configuration |
| `cisco.ios.ios_command` | Run arbitrary show commands |
| `cisco.ios.ios_config` | Push raw config lines (fallback) |

All resource modules support `state`: `merged`, `replaced`, `overridden`, `deleted`, `gathered` (read current state), `rendered` (generate config without applying).

### Variables - host_vars and group_vars

```yaml
# inventory/group_vars/switches.yml
ntp_servers:
  - 192.168.0.1
  - 192.168.0.2
snmp_community: "public_ro"
snmp_location: "Singapore DC1"

# inventory/host_vars/sw-01.yml
mgmt_vlan: 10
hostname: sw-01.example.com
```

Variables are referenced in playbooks using Jinja2 syntax: `{{ ntp_servers }}`.

### Roles

A role packages related tasks, defaults, and templates:

```
roles/ntp/
├── tasks/
│   └── main.yml         # The task list
├── defaults/
│   └── main.yml         # Default variable values
├── handlers/
│   └── main.yml         # Tasks triggered by notify
└── templates/
    └── ntp.conf.j2      # Jinja2 templates for config files
```

```yaml
# roles/ntp/tasks/main.yml
---
- name: Configure NTP servers
  cisco.ios.ios_ntp_global:
    config:
      servers:
        - server: "{{ item }}"
          prefer: "{{ loop.first }}"
    state: merged
  loop: "{{ ntp_servers }}"
```

```yaml
# playbooks/site.yml — apply role to all devices
---
- name: Apply base configuration
  hosts: all
  gather_facts: no
  roles:
    - ntp
    - snmp
    - aaa
```

### Ansible Vault - Secrets Management

Never store passwords in plaintext inventory files. Use `ansible-vault`:

```bash
# Encrypt a file
ansible-vault encrypt inventory/group_vars/all/vault.yml

# Reference encrypted variables
vault_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...

# Run playbook, provide vault password
ansible-playbook site.yml --ask-vault-pass
# or via file: --vault-password-file ~/.vault_pass
```

### Running Playbooks

```bash
# Install required collections
ansible-galaxy collection install cisco.ios junipernetworks.junos

# Run playbook against all switches
ansible-playbook -i inventory/hosts.yml playbooks/vlan.yml

# Limit to one host
ansible-playbook -i inventory/ playbooks/vlan.yml --limit sw-01

# Dry run (check mode — no changes applied)
ansible-playbook -i inventory/ playbooks/vlan.yml --check

# Diff mode — show what would change
ansible-playbook -i inventory/ playbooks/vlan.yml --check --diff

# Verbose output
ansible-playbook -i inventory/ playbooks/vlan.yml -v
```

### Idempotency

A playbook is **idempotent** if running it multiple times produces the same result as running it once - if the desired state already exists, nothing changes. Resource modules implement idempotency by reading the current device state, comparing it to the desired state, and only applying changes that are needed. `ios_config` (raw config lines) is not idempotent - use resource modules wherever possible.

---
## Common Pitfalls

1. **Using `ios_config` instead of resource modules.** `ios_config` pushes raw config lines and is not idempotent - it always applies the lines regardless of current state, may push duplicate commands, and does not validate correctness. Use resource modules (`ios_vlans`, `ios_interfaces`) for all new automation. Use `ios_config` only for configuration not covered by any resource module.

2. **Storing passwords in plaintext inventory.** `ansible_password: mypassword` in a YAML file committed to git is a security incident. Use Ansible Vault for all credentials. Never commit unencrypted secrets.

3. **`gather_facts: yes` on network devices.** Ansible's default fact gathering runs a setup module that is not compatible with network devices - it causes an error. Always set `gather_facts: no` for network device plays.

4. **Wrong `ansible_connection` for the platform.** Cisco IOS devices use `ansible_connection: network_cli`; Juniper Junos uses `ansible_connection: netconf`; some REST-based platforms use `ansible_connection: httpapi`. Wrong connection type causes connection failures that look like SSH errors. Check the collection documentation for the correct connection plugin.

5. **Not using check mode before applying.** `--check --diff` shows exactly what Ansible would change without applying anything. Always run check mode against production devices first, especially with `state: replaced` or `state: overridden` - these can delete existing configuration not specified in your playbook.

---
## Practice Problems

**Q1.** You run an Ansible playbook with `cisco.ios.ios_vlans` state: `merged`. It reports `changed: false` for every device. What does this mean?

??? answer
    `changed: false` means the desired state already matches the current device state - no changes were needed. This is idempotency working correctly. Ansible read the current VLAN database from each device, compared it to the desired config in the playbook, found no differences, and made no changes. This is safe - you can run the playbook on a schedule to continuously enforce the desired state without risk of pushing duplicate commands.

**Q2.** What is the difference between `state: merged`, `state: replaced`, and `state: overridden` in a resource module?

??? answer
    `merged`: Add the specified config to the existing config - items in the playbook are added or updated; existing items not mentioned are left alone. `replaced`: Replace the specified resource (e.g., a specific interface's L2 config) with exactly what is in the playbook - items on the device but not in the playbook are deleted for that resource. `overridden`: Replace ALL instances of the resource type across the device - anything not in the playbook is deleted. `overridden` is the most destructive; use with extreme care. `merged` is safe for incremental changes.

**Q3.** How do you ensure different groups of devices (production vs lab) use different NTP server addresses without maintaining two separate playbooks?

??? answer
    Use `group_vars`. Create `inventory/group_vars/production/ntp.yml` with production NTP servers and `inventory/group_vars/lab/ntp.yml` with lab NTP servers. Put both groups in the inventory. The playbook references `{{ ntp_servers }}` - Ansible resolves the variable to the correct group's value at runtime based on which hosts are targeted. The playbook itself is unchanged - inventory and group_vars provide environment-specific values.

---
## Summary & Key Takeaways

- Ansible is **declarative** and **idempotent** - describe desired state; Ansible applies only what's needed.
- **Inventory** defines devices and groups; **playbooks** define what to do; **roles** package reusable patterns.
- Use **resource modules** (`ios_vlans`, `junos_interfaces`) for idempotency - avoid `ios_config` for new automation.
- `state: merged` (safe, additive), `state: replaced` (replaces resource), `state: overridden` (replaces all instances - destructive).
- Always use **Ansible Vault** for credentials - never commit plaintext passwords.
- Set `gather_facts: no` for all network device plays.
- Run `--check --diff` before applying changes to production devices.
- **Roles** enable reuse across projects; install vendor collections via `ansible-galaxy collection install`.

---
## Where to Next

- **AUTO-003 - NETCONF, YANG & gRPC:** Ansible NETCONF connection uses ncclient; gNMI telemetry is the complementary monitoring approach.
- **AUTO-002 - REST APIs:** Ansible httpapi connection uses REST internally for some platforms.
- **DC-001 - Data Centre Network Design:** Ansible is the standard automation layer for spine-leaf fabric provisioning.

---
## Standards & Certifications

| Standard / Cert | Relevance |
|---|---|
| Cisco DevNet Associate | Ansible basics, network automation |
| Cisco CCNP Enterprise | Network automation tools including Ansible |
| Red Hat Certified Specialist in Ansible Automation | Dedicated Ansible certification |
| CompTIA Network+ | Automation concepts |

---
## References

- Ansible Network Automation documentation: [https://docs.ansible.com/ansible/latest/network/index.html](https://docs.ansible.com/ansible/latest/network/index.html)
- cisco.ios collection: [https://docs.ansible.com/ansible/latest/collections/cisco/ios/](https://docs.ansible.com/ansible/latest/collections/cisco/ios/)
- junipernetworks.junos collection: [https://docs.ansible.com/ansible/latest/collections/junipernetworks/junos/](https://docs.ansible.com/ansible/latest/collections/junipernetworks/junos/)
- Ansible Vault: [https://docs.ansible.com/ansible/latest/vault_guide/index.html](https://docs.ansible.com/ansible/latest/vault_guide/index.html)

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
| DC-001 | Data Centre Network Design | Ansible is standard for spine-leaf provisioning |

### Modules This Module References

| Module ID | Title | Relationship |
|---|---|---|
| AUTO-001 | Python for Network Engineers | Python skills; Ansible uses Python internally |
| AUTO-003 | NETCONF, YANG & gRPC | Ansible NETCONF connection; complementary telemetry |
<!-- XREF-END -->
