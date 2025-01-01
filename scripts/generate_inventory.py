#!/usr/bin/env python3

import yaml
import os
import ipaddress
import sys

def validate_node_data(nodes):
    """Validate node data format and IP addresses."""
    for hostname, ip in nodes:
        if not hostname or not isinstance(hostname, str):
            raise ValueError(f"Invalid hostname: {hostname}")
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip}")
    return True

def generate_inventory_structure(control_plane_nodes, worker_nodes):
    """Generate the inventory structure from node lists."""
    # Read vars section from hosts.txt
    vars_dict = {
        'ansible_user': 'ubuntu',
        'ansible_python_interpreter': '/usr/bin/python3',
        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
    }
    
    # Add the new variables with defaults
    vars_dict.update({
        'ssh_public_key_path': '~/.ssh/id_ed25519.pub',
        'rke2_version': 'v1.31.4+rke2r1'
    })
    
    inventory = {
        'all': {
            'children': {
                'six_node_cluster': {
                    'children': {
                        'control_plane_nodes': {'hosts': {}},
                        'worker_nodes': {'hosts': {}}
                    }
                }
            },
            'vars': vars_dict
        }
    }
    
    # Add control plane nodes
    for hostname, ip in control_plane_nodes:
        inventory['all']['children']['six_node_cluster']['children']['control_plane_nodes']['hosts'][hostname] = {
            'ansible_host': ip
        }
    
    # Add worker nodes
    for hostname, ip in worker_nodes:
        inventory['all']['children']['six_node_cluster']['children']['worker_nodes']['hosts'][hostname] = {
            'ansible_host': ip
        }
    
    return inventory

def parse_hosts_file(hosts_file):
    """Parse hosts.txt file and return control plane and worker nodes."""
    ip_mappings = {}  # Store hostname -> IP mappings
    control_plane_nodes = []
    worker_nodes = []
    
    # Define required variables and their defaults
    required_vars = {
        'ssh_public_key_path': {
            'default': '~/.ssh/id_ed25519.pub',
            'description': 'SSH public key path for cluster communication'
        },
        'rke2_version': {
            'default': 'v1.31.4+rke2r1',
            'description': 'RKE2 version to install'
        }
    }
    
    # Initialize vars_dict with defaults
    vars_dict = {k: v['default'] for k, v in required_vars.items()}
    vars_dict.update({
        'ansible_user': 'ubuntu',
        'ansible_python_interpreter': '/usr/bin/python3',
        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
    })
    
    # Track which variables were explicitly set
    set_vars = set()
    current_section = None
    
    with open(hosts_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line == '[vars]':
                current_section = 'vars'
            elif line == '[six_node]':
                current_section = 'ip_mapping'
            elif line == '[control_plane_nodes]':
                current_section = 'control_plane'
            elif line == '[worker_nodes]':
                current_section = 'worker'
            elif line.startswith('['):
                current_section = None
            elif current_section == 'vars':
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    vars_dict[key] = value
                    set_vars.add(key)
            elif current_section == 'ip_mapping':
                parts = line.split()
                if len(parts) >= 2:
                    hostname, ip = parts[0], parts[1]
                    ip_mappings[hostname] = ip
            elif current_section in ['control_plane', 'worker']:
                hostname = line.strip()
                if hostname in ip_mappings:
                    node_tuple = (hostname, ip_mappings[hostname])
                    if current_section == 'control_plane':
                        control_plane_nodes.append(node_tuple)
                    else:
                        worker_nodes.append(node_tuple)
    
    # Check for missing variables and print warnings
    missing_vars = []
    for var_name, var_info in required_vars.items():
        if var_name not in set_vars:
            missing_vars.append(f"- {var_name}: {var_info['description']} (using default: {var_info['default']})")
    
    if missing_vars:
        print("\nWarning: The following variables were not set in [vars] section:")
        print("\n".join(missing_vars))
        print("\nTo set these variables, add them to the [vars] section in hosts.txt:")
        print("Example:")
        print("[vars]")
        for var_name, var_info in required_vars.items():
            print(f"{var_name}={var_info['default']}")
        print()
    
    return control_plane_nodes, worker_nodes, vars_dict

def write_inventory_file(inventory_data, file_path):
    """Write inventory data to a YAML file."""
    header = """---
#####################################################################
# WARNING: THIS IS A GENERATED FILE. DO NOT EDIT DIRECTLY!
# 
# This file is automatically generated by scripts/generate_inventory.py
# To make changes, modify inventory/hosts.txt and regenerate this file.
#####################################################################
"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(header)
        yaml.dump(inventory_data, f, default_flow_style=False, sort_keys=False)

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_inventory.py <hosts_file>")
        sys.exit(1)
    
    hosts_file = sys.argv[1]
    output_file = 'inventory/rke2.yml'
    
    try:
        # Parse hosts.txt
        control_plane_nodes, worker_nodes, vars_dict = parse_hosts_file(hosts_file)
        
        # Validate node data
        validate_node_data(control_plane_nodes + worker_nodes)
        
        # Generate inventory structure
        inventory = generate_inventory_structure(control_plane_nodes, worker_nodes)
        
        # Update with any vars from hosts.txt
        if vars_dict:
            inventory['all']['vars'].update(vars_dict)
        
        # Write to file
        write_inventory_file(inventory, output_file)
        print(f"Generated inventory file: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()