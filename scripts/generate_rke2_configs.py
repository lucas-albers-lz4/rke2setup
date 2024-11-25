#!/usr/bin/env python3

import yaml
import os
from datetime import datetime

def generate_base_vars(inventory_data):
    """Generate essential variables including RKE2 configuration."""
    base_vars = {
        'ansible_user': inventory_data.get('vars', {}).get('ansible_user', 'ubuntu'),
        'ansible_python_interpreter': inventory_data.get('vars', {}).get('ansible_python_interpreter', '/usr/bin/python3')
    }
    
    # Default RKE2 configuration
    default_rke2_config = {
        'write_kubeconfig_mode': '0644',
        'token': '',
        'tls-san': ['127.0.0.1', 'localhost']
    }
    
    # Default paths
    default_paths = {
        'rke2': {
            'config': '/etc/rancher/rke2',
            'bin': '/var/lib/rancher/rke2/bin',
            'data': '/var/lib/rancher/rke2'
        },
        'system': {
            'bin': '/usr/local/bin'
        }
    }
    
    # Default commands
    default_commands = {
        'rke2': '/usr/local/bin/rke2'
    }
    
    # Get RKE2 configuration from inventory or use defaults
    rke2_config = inventory_data.get('rke2_config', default_rke2_config)
    
    # Merge configurations
    base_vars.update({
        'tls_san': rke2_config.get('tls-san', default_rke2_config['tls-san']),
        'rke2_token': rke2_config.get('token', default_rke2_config['token']),
        'rke2_config': {
            'write_kubeconfig_mode': rke2_config.get('write_kubeconfig_mode', default_rke2_config['write_kubeconfig_mode']),
            'token': rke2_config.get('token', default_rke2_config['token']),
            'tls-san': rke2_config.get('tls-san', default_rke2_config['tls-san'])
        },
        'paths': inventory_data.get('paths', default_paths),
        'commands': inventory_data.get('commands', default_commands)
    })
    
    return base_vars

def validate_inventory_data(inventory_data):
    """Validate inventory data structure and required fields"""
    required_fields = [
        ('all', 'children', 'six_node_cluster', 'children', 'control_plane_nodes', 'hosts'),
    ]
    
    for field_path in required_fields:
        current = inventory_data
        for field in field_path:
            if not isinstance(current, dict) or field not in current:
                raise ValueError(f"Missing required field: {' -> '.join(field_path)}")
            current = current[field]
    return True

def write_group_vars(vars_data):
    """Write only essential variables to group_vars/all.yml"""
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
