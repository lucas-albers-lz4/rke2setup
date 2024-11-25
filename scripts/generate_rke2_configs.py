#!/usr/bin/env python3

import yaml
import os
from pathlib import Path
from datetime import datetime

def read_inventory(inventory_path):
    """Read the RKE2 inventory file."""
    with open(inventory_path, 'r') as f:
        return yaml.safe_load(f)

def generate_base_config(inventory_data, hostname, is_first=False):
    """Generate base configuration dictionary from inventory data."""
    rke2_config = inventory_data.get('rke2_config', {})
    
    config = {
        "write-kubeconfig-mode": rke2_config.get('write_kubeconfig_mode', '0644'),
        "tls-san": rke2_config.get('tls-san', []),
        "node-name": hostname.lower()
    }
    
    # Add token for all nodes
    config["token"] = rke2_config.get('token', 'test123')
    
    # First server node specific config
    if is_first:
        config["cluster-init"] = True
    else:
        first_node_ip = rke2_config.get('control_plane_nodes', ['192.168.1.23'])[0]
        config["server"] = f"https://{first_node_ip}:9345"
    
    return config

def add_node_specific_config(config, hostname, inventory_data):
    """Add node-specific labels and taints from inventory."""
    rke2_config = inventory_data.get('rke2_config', {})
    
    # Get node-specific settings from inventory if available
    node_settings = rke2_config.get('node_settings', {}).get(hostname, {})
    
    config["node-label"] = node_settings.get('labels', [
        "node.kubernetes.io/instance-type=control-plane",
        f"kubernetes.io/hostname={hostname.lower()}",
        "workload.type=control-plane"
    ])
    
    config["node-taint"] = node_settings.get('taints', [
        "CriticalAddonsOnly=true:NoSchedule"
    ])
    
    return config

def generate_config_file(hostname, inventory_data, is_first=False):
    """Generate complete config for a node using inventory data."""
    config = generate_base_config(inventory_data, hostname, is_first=is_first)
    config = add_node_specific_config(config, hostname, inventory_data)
    return config

def write_config(config, filename):
    """Write config to file with proper formatting."""
    with open(filename, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

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

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    output_dir = project_root / 'generated_configs'
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Read and validate inventory
        inventory_path = project_root / 'inventory' / 'rke2.yml'
        if not inventory_path.exists():
            raise FileNotFoundError(f"Inventory file not found at {inventory_path}")
        
        inventory_data = read_inventory(inventory_path)
        validate_inventory_data(inventory_data)
        
        # Get list of control plane nodes with their actual hostnames
        control_plane_nodes = inventory_data['all']['children']['six_node_cluster']['children']['control_plane_nodes']['hosts'].keys()
        
        # Create timestamp for this generation run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate config for each node
        for i, hostname in enumerate(control_plane_nodes):
            is_first = (i == 0)
            
            config = generate_config_file(hostname, inventory_data, is_first=is_first)
            
            # Create consistent output filename
            output_file = output_dir / f"rke2_config_{hostname}_{timestamp}.yaml"
            
            write_config(config, output_file)
            print(f"Generated config file: {output_file}")
            
            # Print config for verification
            print(f"\nGenerated configuration for {hostname}:")
            print("------------------------")
            print(yaml.dump(config, default_flow_style=False))
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    main()
