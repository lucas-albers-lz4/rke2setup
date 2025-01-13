# RKE2 Cluster Ansible Role

An Ansible role for deploying and managing RKE2 Kubernetes clusters with high availability. This role automates the deployment of a production-like RKE2 cluster with comprehensive validation and monitoring features, implementing a fixed six-node architecture.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Upgrade Instructions](#upgrade-instructions)
- [License](#license)

## Overview

-  Automated 6-node HA cluster deployment (3 control plane, 3 workers)
-  Secure token and certificate management
-  Built-in health validation
-  Production-like configuration

## Features

### Cluster Verification
The role includes comprehensive verification capabilities:
- Control plane component health validation
- etcd cluster status monitoring
- Node readiness verification
- Automated kubectl configuration

### Health Checks
- API Server health validation
- etcd cluster health monitoring
- Control plane pod status
- Node status verification
- Service availability checks

### System Requirements

Control Plane Nodes (each):
- CPU: 2 vCPU minimum
- RAM: 4GB minimum
- Storage: 12GB minimum


Worker Nodes (each):
- CPU: 2 vCPU minimum
- RAM: 2GB minimum
- Storage: 7GB minimum


## Prerequisites

- Ubuntu 20.04 or 22.04
- Ansible 8.7.0+
- Python 3.10+
- SSH key-based authentication configured (Our playbook sets this)
- Sudo access on all nodes (Our playbook sets this.)


## Quick Start

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure inventory:
```bash
cp inventory/hosts.txt.example inventory/hosts.txt
vi inventory/hosts.txt
```

Example hosts.txt:
```ini
[vars]
ssh_public_key_path=~/.ssh/id_ed25519.pub
rke2_version=v1.31.4+rke2r1

# Six Node Cluster
[six_node]
k1 192.168.0.11
k2 192.168.0.12
k3 192.168.0.13
l4 192.168.1.4
node6 192.168.0.16
node7 192.168.0.17
node8 192.168.0.18

[control_plane_nodes]
k1
k2
k3

[worker_nodes]
l4
node6
node7
node8
```

Set rke2 version you want to install
```bash
vi roles/rke2_cluster/defaults/main.yml
```

3. Generate the inventory file: rke2.yaml by running the following command:

```bash
make inventory
```

Push out your keys and update your ssh local keys so ansible can connect to the nodes and update sudoers file
```bash
ansible-playbook -i inventory/rke2.yml distribute_keys.yml sudo_setup.yml
```

If it fails because you are missing keys then run it again with -k and -K

```bash
ansible-playbook -i inventory/rke2.yml distribute_keys.yml sudo_setup -k -K
```

Note k1 is the first control node in my examples, it is the one that will be used to build the cluster.
So we build the first control node first, and then build the rest of the cluster

check that the network and host configuration is correct on all the nodes
```bash
ansible-playbook -i inventory/rke2.yml verify_hosts.yml
```

build the first control node
```bash
ansible-playbook -i inventory/rke2.yml rke2.yml --limit k1 
```

build the rest of the control nodes
```bash
ansible-playbook -i inventory/rke2.yml rebuild_node.yml --limit '!k1'
```
note if you want to use helm charts that align with how rke2 uses them (for cilium) for example use this format
```bash
helm repo add rke2-charts https://rke2-charts.rancher.io/
helm repo add cilium https://helm.cilium.io/
helm get values rke2-cilium -n kube-system > helm-cilium-current-values.yaml
helm upgrade rke2-cilium rke2-charts/rke2-cilium --namespace kube-system --version 1.16.400 --values helm-cilium-current-values.yaml
```

By default we use airgap to download the initial images as zst images for arm64 and amd64which rke2 then unpacks and uses for the initial container images
To disable that pass into the play like such
```bash
-e "rke2_airgap_images=false"
```

To wipe everything and reboot to start fresh
```bash 
ansible-playbook -i inventory/rke2.yml cleanup.yml reboot.yml
```

[![Ansible Lint](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## License

MIT

## Author

Lucas Albers

## Troubleshooting

Common issues and solutions:

1. SSH Connection Issues
   ```bash
   # Verify SSH connectivity
   ansible all -i inventory/rke2.yml -m ping
   ```

2. Node Registration Failures
   [Add troubleshooting steps...]

## Security Considerations

1. Network Security
   - Use private network for inter-node communication
   - Enable firewall rules
   - [Add more security recommendations...]

## Upgrade Instructions

1. Upgrading RKE2 Version
   ```bash
   # Update rke2_version in inventory/rke2.yml
   ansible-playbook -i inventory/rke2.yml upgrade.yml
   ```
