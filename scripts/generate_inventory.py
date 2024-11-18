#!/usr/bin/env python3

import yaml
import argparse
from typing import Dict, List

WARNING_HEADER = """#####################################################################
# WARNING: THIS IS A GENERATED FILE. DO NOT EDIT DIRECTLY!
# 
# This file is automatically generated by scripts/generate_inventory.py
# To make changes, modify the generation script and regenerate this file.
#####################################################################

"""

def generate_inventory(control_plane_ips: List[str], worker_ips: List[str]) -> Dict:
    inventory = {
        'all': {
            'children': {
                'three_node_cluster': {
                    'children': {
                        'three_node_control_plane': {
                            'hosts': {}
                        },
                        'three_node_workers': {
                            'hosts': {}
                        }
                    },
                    'vars': {
                        'cluster_type': 'three_node',
                        'first_server_ip': control_plane_ips[0],
                        'tls_sans': control_plane_ips + worker_ips
                    }
                }
            },
            'vars': {
                'ansible_python_interpreter': '/usr/bin/python3',
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                'ansible_user': 'ubuntu'
            }
        }
    }

    # Add control plane nodes
    for idx, ip in enumerate(control_plane_ips, 1):
        inventory['all']['children']['three_node_cluster']['children']['three_node_control_plane']['hosts'][f'K{idx}'] = {
            'ansible_host': ip
        }

    # Add worker nodes
    for idx, ip in enumerate(worker_ips, len(control_plane_ips) + 1):
        inventory['all']['children']['three_node_cluster']['children']['three_node_workers']['hosts'][f'K{idx}'] = {
            'ansible_host': ip
        }

    return inventory

def write_inventory(inventory: Dict, output_file: str):
    """Write inventory to file with warning header."""
    with open(output_file, 'w') as f:
        f.write(WARNING_HEADER.rstrip() + '\n\n')  # Ensure exactly one blank line after header
        yaml.dump(inventory, f, default_flow_style=False, sort_keys=False, indent=2, width=1000)
        f.write('\n')  # Ensure single newline at end of file

def main():
    parser = argparse.ArgumentParser(description='Generate RKE2 cluster inventory')
    parser.add_argument('--control-plane-ips', nargs='+', required=True,
                      help='List of control plane node IPs')
    parser.add_argument('--worker-ips', nargs='+', required=True,
                      help='List of worker node IPs')
    parser.add_argument('--output', default='inventory/rke2.yml',
                      help='Output inventory file path')

    args = parser.parse_args()
    
    inventory = generate_inventory(args.control_plane_ips, args.worker_ips)
    write_inventory(inventory, args.output)
    print(f"Inventory generated at {args.output}")

if __name__ == '__main__':
    main()