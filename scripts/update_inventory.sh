#!/bin/bash

# Set strict mode for better error handling
set -euo pipefail

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging function
log_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

# Check if hosts file exists
if [ ! -f "inventory/hosts.txt" ]; then
    log_error "hosts.txt file not found in inventory directory"
    exit 1
fi

# Ensure the generate_inventory.py script is executable
chmod +x scripts/generate_inventory.py

# Generate inventory with error handling
if ! python3 scripts/generate_inventory.py inventory/hosts.txt > inventory/rke2.yml.tmp; then
    log_error "Failed to generate inventory"
    exit 1
fi

# Validate YAML
if ! python3 -c "import yaml; yaml.safe_load(open('inventory/rke2.yml.tmp'))" 2>/dev/null; then
    log_error "Generated inventory file is not valid YAML"
    rm inventory/rke2.yml.tmp
    exit 1
fi

# Replace existing inventory file
mv inventory/rke2.yml.tmp inventory/rke2.yml
log_success "Inventory updated successfully!"