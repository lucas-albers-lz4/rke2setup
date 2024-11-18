#!/bin/bash

# Generate inventory from hosts file
python3 scripts/generate_inventory.py inventory/hosts.txt > inventory/rke2.yml

echo "Inventory updated successfully!"