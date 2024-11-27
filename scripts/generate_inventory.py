#!/usr/bin/env python3

import yaml
import os
import ipaddress

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
    inventory = {
        'all': {
            'children': {
                'six_node_cluster': {
                    'children': {
                        'control_plane_nodes': {'hosts': {}},
                        'worker_nodes': {'hosts': {}}
                    }
                }
            }
        }
    }
    
    for hostname, ip in control_plane_nodes:
        inventory['all']['children']['six_node_cluster']['children']['control_plane_nodes']['hosts'][hostname] = {
            'ansible_host': ip
        }
    
    for hostname, ip in worker_nodes:
        inventory['all']['children']['six_node_cluster']['children']['worker_nodes']['hosts'][hostname] = {
            'ansible_host': ip
        }
    
    return inventory

def write_inventory_file(inventory_data, file_path):
    """Write inventory data to a YAML file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        yaml.dump(inventory_data, f, default_flow_style=False)