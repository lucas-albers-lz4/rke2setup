#!/bin/bash

# Set strict mode
set -euo pipefail

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check if hosts file exists
if [ ! -f "inventory/hosts.txt" ]; then
    echo -e "${RED}ERROR: hosts.txt file not found in inventory directory${NC}" >&2
    exit 1
fi

# Generate inventory
if python3 scripts/generate_inventory.py inventory/hosts.txt; then
    echo -e "${GREEN}Inventory updated successfully!${NC}"
else
    echo -e "${RED}Failed to update inventory${NC}" >&2
    exit 1
fi

if python3 scripts/generate_rke2_configs.py; then
    echo -e "${GREEN}RKE2 configurations updated successfully!${NC}"
else
    echo -e "${RED}Failed to update RKE2 configurations${NC}" >&2
    exit 1
fi
