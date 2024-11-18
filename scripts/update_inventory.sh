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
python3 scripts/generate_inventory.py inventory/hosts.txt

echo -e "${GREEN}Inventory updated successfully!${NC}"