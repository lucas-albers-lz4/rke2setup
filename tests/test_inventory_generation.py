import pytest
from scripts.generate_inventory import (
    generate_inventory_structure,
    validate_node_data,
    write_inventory_file
)
import os
import yaml

@pytest.fixture
def sample_nodes():
    return {
        'control_plane': [
            ('k1', '192.168.1.23'),
            ('k2', '192.168.1.24'),
            ('k3', '192.168.1.25')
        ],
        'workers': [
            ('node7', '192.168.1.55'),
            ('node8', '192.168.1.54'),
            ('node9', '192.168.1.52')
        ]
    }

def test_generate_inventory_structure(sample_nodes):
    """Test inventory structure generation"""
    inventory = generate_inventory_structure(
        sample_nodes['control_plane'],
        sample_nodes['workers']
    )
    
    assert 'all' in inventory
    assert 'six_node_cluster' in inventory['all']['children']
    assert 'control_plane_nodes' in inventory['all']['children']['six_node_cluster']['children']
    assert 'worker_nodes' in inventory['all']['children']['six_node_cluster']['children']
    
    # Verify control plane nodes
    control_plane = inventory['all']['children']['six_node_cluster']['children']['control_plane_nodes']['hosts']
    assert len(control_plane) == 3
    assert control_plane['k1']['ansible_host'] == '192.168.1.23'

def test_validate_node_data():
    """Test node data validation"""
    valid_data = [('node1', '192.168.1.1'), ('node2', '192.168.1.2')]
    assert validate_node_data(valid_data) == True
    
    with pytest.raises(ValueError):
        validate_node_data([('node1', '256.256.256.256')])
    
    with pytest.raises(ValueError):
        validate_node_data([('', '192.168.1.1')])

def test_write_inventory_file(tmp_path):
    """Test inventory file writing"""
    inventory_data = {
        'all': {
            'children': {
                'six_node_cluster': {
                    'children': {
                        'control_plane_nodes': {
                            'hosts': {
                                'k1': {'ansible_host': '192.168.1.23'}
                            }
                        }
                    }
                }
            }
        }
    }
    
    file_path = tmp_path / "test_inventory.yml"
    write_inventory_file(inventory_data, str(file_path))
    
    assert file_path.exists()
    with open(file_path) as f:
        loaded_data = yaml.safe_load(f)
        assert loaded_data == inventory_data
