# RKE2 Cluster Ansible Role

An Ansible role for deploying and managing RKE2 Kubernetes clusters with high availability. This role automates the deployment of a production-like RKE2 cluster with comprehensive validation and monitoring features, implementing a fixed six-node architecture.

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

- Ubuntu 22.04 or 22.04, Debian 12
- Ansible 8.7.0+
- Python 3.x
- SSH key-based authentication configured
- Sudo access on all nodes

## Quick Start

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure inventory:
These are the ip addresses of the nodes you want to deploy.

```bash
cp inventory/hosts.txt.example inventory/hosts.txt
vi inventory/hosts.txt
```

3. Generate the inventory file: rke2.yaml by running the following command:

```bash
make inventory
```
Then push out your keys and update your ssh local keys so ansible can connect to the nodes.


## Status
[![Ansible Lint](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## License

MIT

## Author

Lucas Albers
