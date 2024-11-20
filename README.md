# RKE2 Cluster Ansible Role

Ansible role for deploying and managing RKE2 Kubernetes clusters with high availability. This role automates the deployment of a production-like RKE2 Kubernetes cluster with comprehensive validation, monitoring, and security features. The role implements a fixed six-node architecture that matches basic production configuration for starting point, learning, and development purposes.

## Overview

- 🚀 Automated 6-node HA cluster deployment
- 🔒 Secure token and certificate management
- 📊 Built-in monitoring and validation
- 🔄 Intelligent node recovery
- ⚡ Production-like configuration

[View Documentation](#quick-start) | [Report Bug](https://github.com/lucas-albers-lz4/rke2setup/issues) | [Request Feature](https://github.com/lucas-albers-lz4/rke2setup/issues)

## Status
[![Ansible Lint](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/lucas-albers-lz4/rke2setup/actions/workflows/ansible-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Prerequisites

- Ubuntu 22.04 or 24.04
- Ansible 8.7.0+
- Python 3.x
- SSH access to all nodes
  - SSH key-based authentication configured
  - SSH keys installed on all target nodes
  - User with sudo privileges
- Sudo access on all nodes
- Minimum hardware requirements as specified in Architecture section

### SSH Key Setup

1. Generate SSH key if needed:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Copy SSH key to all nodes:
```bash
# For each node in your inventory
ssh-copy-id -i ~/.ssh/id_ed25519.pub ubuntu@node_ip
```

3. Verify SSH access:
```bash
# Test connection to each node
ssh ubuntu@node_ip

# Or use the provided script
./scripts/update_ssh_keys.sh
```

4. Common SSH Issues:
- Ensure proper permissions on SSH keys (600 for private key, 644 for public key)
- Verify the SSH user has sudo privileges
- Check that SSH agent is running (`eval $(ssh-agent)` if needed)
- Test connectivity with `ssh -v` for verbose output

## Architecture

### Six Node Cluster
- 3 Control plane nodes (HA setup)
- 3 Worker nodes

#### System Requirements

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

## Inventory Configuration

### Example Inventory Structure
```ini
# Six Node Cluster
[six_node]
k7 192.168.1.48
k8 192.168.1.49
k9 192.168.1.50
node7 192.168.1.55
node8 192.168.1.54
node9 192.168.1.52

[control_plane_nodes]
k7
k8
k9

[worker_nodes]
node7
node8
node9
```

### Inventory Requirements

1. **Node Groups**:
   - `[six_node]`: Lists all nodes with their IP addresses
   - `[control_plane_nodes]`: First three nodes for control plane
   - `[worker_nodes]`: Last three nodes for workers

2. **Naming Convention**:
   - Use consistent hostname patterns
   - Ensure hostnames match system configurations
   - IP addresses must be reachable from deployment host

3. **IP Address Format**:
   - Use static IP addresses
   - Ensure IPs are in proper format (IPv4)
   - Avoid conflicts with existing network services

### Inventory Validation

The deployment process includes automatic inventory validation:

1. **Pre-deployment Checks**:
   - Host connectivity verification
   - DNS resolution testing
   - IP address validation
   - Group membership verification

2. **Validation Commands**:
```bash
# Generate and validate inventory
make generate-inventory

# Verify hosts connectivity
ansible-playbook -i inventory/rke2.yml verify_hosts.yml
```

3. **Common Issues**:
   - Ensure all hosts are reachable via SSH
   - Verify correct group assignments
   - Check for IP address conflicts
   - Validate DNS resolution for all nodes

### Advanced Configuration

The inventory supports additional configurations through group variables:

1. **Custom SSH Users**:
   ```yaml
   all:
     vars:
       ansible_user: ubuntu
       ansible_ssh_private_key_file: ~/.ssh/id_rsa
   ```

2. **Node Labels**:
   - Control plane nodes automatically labeled
   - Worker nodes configured for workload distribution
   - Custom labels can be added through configuration

3. **Network Configuration**:
   - Default cluster network: 10.42.0.0/16
   - Service CIDR: 10.43.0.0/16
   - Customize through RKE2 configuration

## Quick Start

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set up inventory:
```bash
# Copy example inventory file
cp inventory/hosts.txt.example inventory/hosts.txt

# Edit inventory/hosts.txt with your node information
vi inventory/hosts.txt
```

3. Generate inventory:
```bash
make generate-inventory
```

4. Deploy cluster:
```bash
# Clean existing deployment and deploy
make clean deploy

# Deploy only
make deploy
```

## Validation Steps

The role performs extensive validation:
- Host connectivity verification
- System requirements checking
- Network configuration validation
- Service state monitoring
- Cluster health verification

## Available Tags

- `prereq`: Run prerequisites tasks
- `ssh`: Configure SSH access
- `control-plane`: Deploy control plane nodes
- `workers`: Deploy worker nodes
- `addons`: Deploy cluster add-ons
- `validate`: Run validation tasks

## Post-Installation

1. Access cluster:
```bash
export KUBECONFIG=~/.kube/config
kubectl get nodes
```

2. Verify deployment:
```bash
kubectl get pods -A
kubectl cluster-info
```

## Troubleshooting

1. Check node status:
```bash
kubectl get nodes -o wide
```

2. View service logs:
```bash
journalctl -u rke2-server.service
```

3. Check configuration:
```bash
cat /etc/rancher/rke2/config.yaml
```

4. Verify network:
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

Please [open an issue](https://github.com/lucas-albers-lz4/rke2setup/issues/new) for support.

## License

MIT

## Author

Lucas Albers
