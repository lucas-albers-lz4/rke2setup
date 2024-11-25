#!/usr/bin/env python3

import pytest
import yaml
import os
from scripts.generate_rke2_configs import generate_base_vars, validate_inventory_data
from jinja2 import Template, Environment
from jinja2.loaders import FileSystemLoader

@pytest.fixture
def sample_inventory():
    """Provide sample inventory data for testing."""
    return {
        'all': {
            'children': {
                'six_node_cluster': {
                    'children': {
                        'control_plane_nodes': {
                            'hosts': {
                                'k1': {'ansible_host': '192.168.1.23'},
                                'k2': {'ansible_host': '192.168.1.24'},
                                'k3': {'ansible_host': '192.168.1.25'}
                            }
                        }
                    }
                }
            }
        },
        'rke2_config': {
            'tls-san': [
                '127.0.0.1',
                '192.168.1.23',
                'kubernetes',
                'kubernetes.default'
            ],
            'token': 'test123'
        }
    }

def test_validate_inventory(sample_inventory):
    """Test inventory validation"""
    assert validate_inventory_data(sample_inventory) is True

def test_generate_base_vars(sample_inventory):
    """Test generation of base variables"""
    vars_data = generate_base_vars(sample_inventory)
    assert 'tls_san' in vars_data
    assert 'rke2_token' in vars_data
    assert vars_data['rke2_token'] == 'test123'
    assert '127.0.0.1' in vars_data['tls_san']

def test_template_rendering(tmp_path):
    """Test template rendering for different node types"""
    # Create test template directory
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    
    # Copy template file for testing
    template_content = """
write-kubeconfig-mode: '0644'
tls-san: {{ tls_san | to_yaml }}
node-name: {{ inventory_hostname }}
token: {{ rke2_token }}
{% if inventory_hostname == groups['control_plane_nodes'][0] %}
cluster-init: true
{% else %}
server: https://{{ hostvars[groups['control_plane_nodes'][0]].ansible_host }}:9345
{% endif %}
node-label:
{% if inventory_hostname in groups['control_plane_nodes'] %}
- node.kubernetes.io/instance-type=control-plane
- kubernetes.io/hostname={{ inventory_hostname }}
- workload.type=control-plane
node-taint:
- CriticalAddonsOnly=true:NoSchedule
{% else %}
- node.kubernetes.io/instance-type=worker
- kubernetes.io/hostname={{ inventory_hostname }}
- workload.type=mixed
{% endif %}
"""
    template_file = template_dir / "config.yaml.j2"
    template_file.write_text(template_content)

    # Test variables
    test_vars = {
        'inventory_hostname': 'k1',
        'groups': {
            'control_plane_nodes': ['k1', 'k2', 'k3']
        },
        'hostvars': {
            'k1': {'ansible_host': '192.168.1.23'}
        },
        'tls_san': ['127.0.0.1', '192.168.1.23'],
        'rke2_token': 'test123'
    }

    # TODO: Add actual template rendering test using Jinja2
    # This would require setting up Ansible test fixtures or using Jinja2 directly
    # For now, we're just verifying our variable generation

def test_group_vars_generation(tmp_path, sample_inventory):
    """Test group_vars file generation"""
    vars_data = generate_base_vars(sample_inventory)
    group_vars_dir = tmp_path / "group_vars"
    group_vars_dir.mkdir()
    
    vars_file = group_vars_dir / "all.yml"
    with open(vars_file, 'w') as f:
        yaml.dump(vars_data, f)

    assert vars_file.exists()
    with open(vars_file) as f:
        written_vars = yaml.safe_load(f)
    
    assert written_vars['rke2_token'] == 'test123'
    assert '127.0.0.1' in written_vars['tls_san']

def test_node_specific_config(sample_inventory):
    """Test node-specific configuration generation"""
    vars_data = generate_base_vars(sample_inventory)
    
    # Test first control plane node config
    test_vars = {
        'inventory_hostname': 'k1',
        'groups': {
            'control_plane_nodes': ['k1', 'k2', 'k3']
        },
        'hostvars': {
            'k1': {'ansible_host': '192.168.1.23'},
            'k2': {'ansible_host': '192.168.1.24'},
            'k3': {'ansible_host': '192.168.1.25'}
        },
        'tls_san': vars_data['tls_san'],
        'rke2_token': vars_data['rke2_token'],
        'rke2_config': vars_data['rke2_config']
    }
    assert 'cluster-init: true' in render_template(test_vars)

def test_additional_control_plane_config(sample_inventory):
    """Test additional control plane node configuration"""
    vars_data = generate_base_vars(sample_inventory)
    
    test_vars = {
        'inventory_hostname': 'k2',
        'groups': {
            'control_plane_nodes': ['k1', 'k2', 'k3']
        },
        'hostvars': {
            'k1': {'ansible_host': '192.168.1.23'},
            'k2': {'ansible_host': '192.168.1.24'},
            'k3': {'ansible_host': '192.168.1.25'}
        },
        'tls_san': vars_data['tls_san'],
        'rke2_token': vars_data['rke2_token'],
        'rke2_config': vars_data['rke2_config']
    }
    rendered = render_template(test_vars)
    assert 'workload.type=control-plane' in rendered
    assert 'server: https://192.168.1.23:9345' in rendered
    assert 'CriticalAddonsOnly=true:NoSchedule' in rendered

def test_worker_node_config(sample_inventory):
    """Test worker node configuration"""
    vars_data = generate_base_vars(sample_inventory)
    
    test_vars = {
        'inventory_hostname': 'worker1',
        'groups': {
            'control_plane_nodes': ['k1', 'k2', 'k3'],
            'worker_nodes': ['worker1']
        },
        'hostvars': {
            'k1': {'ansible_host': '192.168.1.23'},
            'k2': {'ansible_host': '192.168.1.24'},
            'k3': {'ansible_host': '192.168.1.25'},
            'worker1': {'ansible_host': '192.168.1.26'}
        },
        'tls_san': vars_data['tls_san'],
        'rke2_token': vars_data['rke2_token'],
        'rke2_config': vars_data['rke2_config']
    }
    rendered = render_template(test_vars)
    assert 'server: https://192.168.1.23:9345' in rendered
    assert 'node.kubernetes.io/instance-type=worker' in rendered

def render_template(test_vars):
    """Helper function to render the config template with test variables."""
    # Ensure rke2_config is properly structured
    if 'rke2_config' in test_vars:
        test_vars['rke2_token'] = test_vars['rke2_config'].get('token', '')
        test_vars['tls_san'] = test_vars['rke2_config'].get('tls-san', [])
    
    template_path = os.path.join(
        os.path.dirname(__file__), 
        '../roles/rke2_cluster/templates/config.yaml.j2'
    )
    with open(template_path) as f:
        template = Environment(loader=FileSystemLoader('/')).from_string(f.read())
    return template.render(**test_vars)

def test_rke2_config_defaults():
    """Test default RKE2 configuration generation"""
    minimal_inventory = {
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
    
    vars_data = generate_base_vars(minimal_inventory)
    assert 'rke2_config' in vars_data
    assert vars_data['rke2_config']['write_kubeconfig_mode'] == '0644'
    assert isinstance(vars_data['rke2_config']['tls-san'], list)

def test_invalid_inventory_structure():
    """Test handling of invalid inventory structure"""
    invalid_inventory = {
        'all': {
            'children': {
                'wrong_group': {}
            }
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        validate_inventory_data(invalid_inventory)
    assert "Missing required field" in str(exc_info.value)

def test_template_rendering_with_minimal_config():
    """Test template rendering with minimal configuration"""
    minimal_config = {
        'inventory_hostname': 'k1',
        'groups': {
            'control_plane_nodes': ['k1']
        },
        'hostvars': {
            'k1': {'ansible_host': '192.168.1.23'}
        },
        'rke2_config': {
            'write_kubeconfig_mode': '0644',
            'token': 'test123',
            'tls-san': ['127.0.0.1']
        },
        'rke2_token': 'test123'
    }
    
    rendered = render_template(minimal_config)
    assert 'write-kubeconfig-mode: "0644"' in rendered
    assert 'cluster-init: true' in rendered
    assert 'token: test123' in rendered

def test_generate_rke2_configs_with_custom_paths():
    """Test RKE2 configuration generation with custom paths"""
    inventory_data = {
        'paths': {
            'rke2': {
                'config': '/custom/path/rke2',
                'bin': '/custom/path/bin',
                'data': '/custom/path/data'
            }
        }
    }
    vars_data = generate_base_vars(inventory_data)
    assert vars_data['paths']['rke2']['config'] == '/custom/path/rke2'
    assert vars_data['paths']['rke2']['bin'] == '/custom/path/bin'
    assert vars_data['paths']['rke2']['data'] == '/custom/path/data'

def test_generate_rke2_configs_with_custom_commands():
    """Test RKE2 configuration generation with custom commands"""
    inventory_data = {
        'commands': {
            'rke2': '/custom/path/to/rke2'
        }
    }
    vars_data = generate_base_vars(inventory_data)
    assert vars_data['commands']['rke2'] == '/custom/path/to/rke2'

def test_generate_rke2_configs_with_empty_inventory():
    """Test RKE2 configuration generation with empty inventory"""
    vars_data = generate_base_vars({})
    assert 'paths' in vars_data
    assert 'commands' in vars_data
    assert 'rke2_config' in vars_data
    assert vars_data['rke2_config']['write_kubeconfig_mode'] == '0644'