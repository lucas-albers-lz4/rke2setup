#!/usr/bin/env python3

import yaml
import sys

def read_hosts_file(filename):
    hosts = {'three_node': [], 'six_node': []}
    current_section = None
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('['):
                current_section = line[1:-1]
                continue
            hostname, ip = line.split()
            hosts[current_section].append((hostname, ip))
    return hosts

def generate_inventory(hosts):
    inventory = {
        'all': {
            'children': {},
            'vars': {
                'ansible_python_interpreter': '/usr/bin/python3',
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                'ansible_user': 'ubuntu'
            }
        }
    }

    # Three node cluster configuration
    if hosts['three_node']:
        first_node_ip = hosts['three_node'][0][1]  # Get IP of first node
        three_node = {
            'three_node_cluster': {
                'children': {
                    'three_node_control_plane': {'hosts': {}},
                    'three_node_workers': {'hosts': {}}
                },
                'vars': {
                    'cluster_type': 'three_node',
                    'first_server_ip': first_node_ip,
                    'tls_sans': [ip for _, ip in hosts['three_node']]
                }
            }
        }
        
        # First node is control plane
        hostname, ip = hosts['three_node'][0]
        three_node['three_node_cluster']['children']['three_node_control_plane']['hosts'][hostname] = {
            'ansible_host': ip
        }
        
        # Rest are workers
        for hostname, ip in hosts['three_node'][1:]:
            three_node['three_node_cluster']['children']['three_node_workers']['hosts'][hostname] = {
                'ansible_host': ip
            }
        inventory['all']['children'].update(three_node)

    # Six node cluster configuration
    if hosts['six_node']:
        first_node_ip = hosts['six_node'][0][1]
        six_node = {
            'six_node_cluster': {
                'children': {
                    'control_plane_nodes': {'hosts': {}},
                    'worker_nodes': {'hosts': {}}
                },
                'vars': {
                    'cluster_type': 'six_node',
                    'first_server_ip': first_node_ip,
                    'tls_sans': [first_node_ip]
                }
            }
        }
        # First three nodes are control plane
        for hostname, ip in hosts['six_node'][:3]:
            six_node['six_node_cluster']['children']['control_plane_nodes']['hosts'][hostname] = {
                'ansible_host': ip
            }
        # Rest are workers
        for hostname, ip in hosts['six_node'][3:]:
            six_node['six_node_cluster']['children']['worker_nodes']['hosts'][hostname] = {
                'ansible_host': ip
            }
        inventory['all']['children'].update(six_node)

    return inventory

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_inventory.py <hosts_file>")
        sys.exit(1)

    hosts = read_hosts_file(sys.argv[1])
    inventory = generate_inventory(hosts)
    
    print(yaml.dump(inventory, default_flow_style=False))

if __name__ == "__main__":
    main()