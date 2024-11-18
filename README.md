[![Ansible Lint](https://github.com/yourusername/rke2-ansible-role/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/yourusername/rke2-ansible-role/actions/workflows/ansible-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# RKE2 Cluster Ansible Role

This role deploys RKE2 clusters in either 3-node or 6-node configurations.

## Requirements

- Ubuntu 22.04 or 24.04 target nodes
- Ansible 2.9+
- Python 3.x
- SSH access to target nodes

## Configurations

### Three Node Cluster
- 1 Control plane node (also runs workloads and add-ons)
- 2 Worker nodes

Minimum Requirements:
Control Plane Node:
- CPU: 4 vCPU
- RAM: 10GB
- Storage: 64GB
  - OS: 20GB
  - Containers: 10GB
  - etcd: 10GB
  - Monitoring: 20GB
  - System: 4GB

Worker Nodes:
- CPU: 2 vCPU
- RAM: 4GB
- Storage: 34GB
  - OS: 20GB
  - Containers: 10GB
  - System: 4GB

### Six Node Cluster
- 3 Dedicated control plane nodes
- 3 Worker nodes

Minimum Requirements:
Control Plane Nodes (each):
- CPU: 2 vCPU
- RAM: 8GB
- Storage: 44GB
  - OS: 20GB
  - Containers: 10GB
  - etcd: 10GB
  - System: 4GB

Worker Nodes (each):
- CPU: 2 vCPU
- RAM: 4GB
- Storage: 34GB
  - OS: 20GB
  - Containers: 10GB
  - System: 4GB

## Quick Start Guide

1. Create a simple inventory file (`inventory/hosts.txt`):
```plaintext
# Three Node Cluster
[three_node]
node1 192.168.1.11
node2 192.168.1.12
node3 192.168.1.13

# Six Node Cluster
[six_node]
cp1 192.168.1.21
cp2 192.168.1.22
cp3 192.168.1.23
worker1 192.168.1.24
worker2 192.168.1.25
worker3 192.168.1.26
```

2. Generate the Ansible inventory:
```bash
./scripts/update_inventory.sh
```

3. Deploy your chosen cluster type:
```bash
# For three-node cluster
ansible-playbook -i inventory/rke2.yml three-node-cluster.yml

# For six-node cluster
ansible-playbook -i inventory/rke2.yml six-node-cluster.yml
```

## Prerequisites Setup

The following system configurations are automatically handled by the playbook:

1. System Updates
2. Kernel Module Configuration
   - overlay
   - br_netfilter
3. Kernel Parameters
   - bridge-nf-call-iptables
   - ip_forward
   - bridge-nf-call-ip6tables
4. Firewall Configuration
5. SSH Key Setup

## Available Tags

The following tags can be used to run specific parts of the deployment:

- prereq: Run prerequisites tasks
- ssh: Configure SSH access
- control-plane: Deploy control plane nodes
- workers: Deploy worker nodes
- addons: Deploy cluster add-ons
- validate: Run validation tasks

## Add-ons

The following add-ons are included:
- MetalLB (~ 100MB RAM)
- NGINX Ingress Controller (~ 500MB RAM)
- Monitoring Stack
  - Prometheus (~ 1GB RAM, 50GB Storage)
  - Grafana (~ 500MB RAM)

## Node Configuration

Each node is configured with:
1. RKE2 Configuration Directory
2. Node-specific Configuration
3. Cluster Token Management
4. TLS Certificate Configuration

### Control Plane Configuration

The first control plane node is initialized with:
- Cluster initialization parameters
- TLS SANs for all nodes
- Token configuration
- kubectl access setup

### Worker Node Configuration

Workers are configured with:
- Agent mode setup
- Connection to control plane
- Node readiness verification

## Post-Installation

After successful deployment:

1. Access the cluster:
```bash
export KUBECONFIG=~/.kube/config
kubectl get nodes
```

2. Verify add-ons:
```bash
kubectl get pods -n monitoring    # Check Prometheus stack
kubectl get pods -n ingress-nginx # Check NGINX Ingress
kubectl get pods -n metallb-system # Check MetalLB
```

## Validation

After deployment, the role will:
1. Verify all nodes are Ready
2. Check pod status across all namespaces
3. Display cluster version information

## Troubleshooting

Common verification steps:
1. Check node status: `kubectl get nodes`
2. View pod status: `kubectl get pods -A`
3. Check service logs: `journalctl -u rke2-server.service`
4. Verify network connectivity: `kubectl get pods -n kube-system`

## Notes

- Wait for each node to be fully initialized before proceeding
- The cluster uses Canal (Calico + Flannel) for networking by default
- Control plane nodes in three-node setup also run workloads
- Token configuration is automatically handled by the playbook

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

Please [open an issue](https://github.com/yourusername/rke2-ansible-role/issues/new) for support.

## License

MIT

## Author

Your Name <your.email@example.com>
