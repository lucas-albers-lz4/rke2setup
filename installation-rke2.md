RKE2 Three-Node Kubernetes Cluster Installation Guide
Overview
This guide provides step-by-step instructions for installing a three-node RKE2 Kubernetes cluster where all nodes can serve as both control plane and worker nodes. The installation uses Ubuntu 22.04 VMs named K7, K8, and K9.

Prerequisites
Three Ubuntu 22.04 VMs with hostnames K7, K8, K9
Known IP addresses for all three nodes
Root or sudo access on all nodes
Installation Steps
Step 1: Prepare All Nodes
Run these commands on all three nodes (K7, K8, K9):
```
# Update system
sudo apt update && sudo apt upgrade -y

# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Load required kernel modules
sudo tee /etc/modules-load.d/containerd.conf <<EOF
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# Configure kernel parameters
sudo tee /etc/sysctl.d/99-kubernetes.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system

# Disable firewall
sudo systemctl stop ufw
sudo systemctl disable ufw
```
Step 2: Install First Server Node (K7)
Run on K7:
```
#!/bin/bash

# Create configuration directory
sudo mkdir -p /etc/rancher/rke2

# Create configuration script
cat << 'EOF' > create_config.sh
#!/bin/bash
HOSTNAME=$(hostname)

# Define IP addresses
FIRST_IP="<K7-IP>"  # Replace with K7's IP
SECOND_IP="<K8-IP>" # Replace with K8's IP
THIRD_IP="<K9-IP>"  # Replace with K9's IP

# Configure based on hostname
if [ "$HOSTNAME" == "K7" ]; then
    sudo tee /etc/rancher/rke2/config.yaml <<CONF
token: "my-shared-secret-token"
tls-san:
  - "${FIRST_IP}"
  - "${SECOND_IP}"
  - "${THIRD_IP}"
  - "K7"
  - "K8"
  - "K9"
node-name: "${HOSTNAME}"
cluster-init: true
CONF
else
    sudo tee /etc/rancher/rke2/config.yaml <<CONF
server: "https://${FIRST_IP}:9345"
token: "my-shared-secret-token"
tls-san:
  - "${FIRST_IP}"
  - "${SECOND_IP}"
  - "${THIRD_IP}"
  - "K7"
  - "K8"
  - "K9"
node-name: "${HOSTNAME}"
CONF
fi
EOF

# Make script executable
chmod +x create_config.sh

# Edit script and replace IP addresses, then run it
vi create_config.sh
./create_config.sh

# Install RKE2
curl -sfL https://get.rke2.io | sh -

# Enable and start RKE2
systemctl enable rke2-server.service
systemctl start rke2-server.service

# Wait for the server to start
if [ "$HOSTNAME" == "K7" ]; then
    echo "First node (K7) - watching logs. Wait until node is ready..."
    journalctl -u rke2-server -f
else
    echo "Additional node ($HOSTNAME) - starting service..."
fi

# Set up kubectl access
sudo ln -s $(find /var/lib/rancher/rke2/data/ -name kubectl) /usr/local/bin/kubectl
mkdir -p ~/.kube
sudo cp /etc/rancher/rke2/rke2.yaml ~/.kube/config
sudo chown -R $USER: ~/.kube
sudo chmod 600 ~/.kube/config
echo "export KUBECONFIG=~/.kube/config" >> ~/.bashrc
source ~/.bashrc
```
Note: Wait until you see messages indicating the node is ready (usually takes 1-2 minutes)

Step 3: Install Additional Server Nodes (K8 and K9)
Run on both K8 and K9:
```
# Create configuration directory
sudo mkdir -p /etc/rancher/rke2

# Create configuration script
cat << 'EOF' > create_config.sh
#!/bin/bash
FIRST_IP="<K7-IP>"  # Replace with K7's IP
SECOND_IP="<K8-IP>" # Replace with K8's IP
THIRD_IP="<K9-IP>"  # Replace with K9's IP
HOSTNAME=$(hostname)

sudo tee /etc/rancher/rke2/config.yaml <<CONF
server: "https://${FIRST_IP}:9345"
token: "my-shared-secret-token"
tls-san:
  - "${FIRST_IP}"
  - "${SECOND_IP}"
  - "${THIRD_IP}"
  - "K7"
  - "K8"
  - "K9"
node-name: "${HOSTNAME}"
CONF
EOF

# Make script executable
chmod +x create_config.sh

# Edit script and replace IP addresses, then run it
vi create_config.sh
./create_config.sh

# Install RKE2
curl -sfL https://get.rke2.io | sh -

# Enable and start RKE2
systemctl enable rke2-server.service
systemctl start rke2-server.service
```

Step 4: Set Up kubectl Access
Run on each node:

```
# Create symbolic link for kubectl
sudo ln -s $(find /var/lib/rancher/rke2/data/ -name kubectl) /usr/local/bin/kubectl

# Set up kubeconfig
mkdir -p ~/.kube
sudo cp /etc/rancher/rke2/rke2.yaml ~/.kube/config
sudo chown -R $USER: ~/.kube
sudo chmod 600 ~/.kube/config

# Set KUBECONFIG environment variable
echo "export KUBECONFIG=~/.kube/config" >> ~/.bashrc
source ~/.bashrc
Step 5: Verify Installation
Run these commands on any node:

# Check node status
kubectl get nodes

# Check pod status
kubectl get pods -A

# Check cluster info
kubectl cluster-info
```

Important Notes
Wait for each node to be fully initialized before adding the next one
The token should be the same across all nodes
Replace <K7-IP>, <K8-IP>, and <K9-IP> with your actual IP addresses
The cluster uses Canal (Calico + Flannel) for networking by default
All nodes will function as both control plane and worker nodes