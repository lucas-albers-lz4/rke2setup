# RKE2 Cluster Ansible Role

An Ansible role for deploying and managing RKE2 Kubernetes clusters with high availability. This role automates the deployment of a production-like RKE2 cluster with comprehensive validation and monitoring features, implementing a fixed six-node architecture.

## Overview

- 🚀 Automated 6-node HA cluster deployment (3 control plane, 3 workers)
- 🔒 Secure token and certificate management
- 📊 Built-in health validation
- ⚡ Production-like configuration

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
- RAM: 8GB minimum
- Storage: 44GB minimum
  - OS: 20GB
  - Containers: 10GB
  - etcd: 10GB
  - System: 4GB

Worker Nodes (each):
- CPU: 2 vCPU minimum
- RAM: 4GB minimum
- Storage: 34GB minimum
  - OS: 20GB
  - Containers: 10GB
  - System: 4GB

## Prerequisites

- Ubuntu 22.04 or 24.04
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
```bash
cp inventory/hosts.txt.example inventory/hosts.txt
vi inventory/hosts.txt
```

3. Deploy cluster:
```bash
make deploy
```

4. Verify deployment:
```bash
make verify-kubectl
```

## Verification Commands

The role provides several verification targets:

```bash
# Configure kubectl access
make configure-kubectl

# Full verification with kubectl setup
make verify-kubectl
```

### Health Check Output

The verification provides a structured health summary:
```
=== RKE2 Cluster Health Summary ===
API Server: HEALTHY/UNHEALTHY
Etcd: HEALTHY/UNHEALTHY

=== Nodes ===
[Node status details]

=== Control Plane Pods ===
[Control plane pod status]
```

## Architecture

The role implements a fixed six-node architecture:
- 3 Control plane nodes in HA configuration
- 3 Worker nodes for workload distribution

### Network Configuration
- Default cluster network: 10.42.0.0/16
- Service CIDR: 10.43.0.0/16

## Available Make Targets

```bash
make deploy           # Deploy full cluster
make verify-all      # Verify all prerequisites
make setup-control   # Setup control plane nodes
make verify-cluster  # Verify cluster health
make setup-workers   # Setup worker nodes
```

## Status
[![Ansible Lint](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## License

MIT

## Author

Lucas Albers
