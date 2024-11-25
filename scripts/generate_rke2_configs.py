#!/usr/bin/env python3

import yaml
import os
from datetime import datetime

def generate_base_vars(inventory_data):
    """Generate base variables for all nodes."""
    return {
        'tls_san': inventory_data.get('rke2_config', {}).get('tls-san', []),
        'rke2_token': inventory_data.get('rke2_config', {}).get('token', 'test123'),
    }

def validate_inventory_data(inventory_data):
    """Validate inventory data structure and required fields"""
    required_fields = [
        ('all', 'children', 'six_node_cluster', 'children', 'control_plane_nodes', 'hosts'),
        ('rke2_config', 'tls-san'),
    ]
    
    for field_path in required_fields:
        current = inventory_data
        for field in field_path:
            if not isinstance(current, dict) or field not in current:
                raise ValueError(f"Missing required field: {' -> '.join(field_path)}")
            current = current[field]
    return True

def write_group_vars(vars_data):
    """Write variables to group_vars/all.yml"""
    os.makedirs('inventory/group_vars', exist_ok=True)
    with open('inventory/group_vars/all.yml', 'w') as f:
        yaml.dump(vars_data, f, default_flow_style=False)

def main():
    # Load inventory
    with open('inventory/rke2.yml', 'r') as f:
        inventory_data = yaml.safe_load(f)

    # Validate inventory
    validate_inventory_data(inventory_data)

    # Generate base variables
    vars_data = generate_base_vars(inventory_data)

    # Write to group_vars
    write_group_vars(vars_data)
    
    print(f"\nGenerated group variables in inventory/group_vars/all.yml:")
    print("------------------------")
    print(yaml.dump(vars_data))

if __name__ == "__main__":
    main()
