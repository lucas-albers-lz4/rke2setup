import sys
import pytest
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.generate_rke2_configs import generate_config_file, write_config

@pytest.fixture
def sample_inventory():
    return {
        'rke2_config': {
            'control_plane_nodes': ['192.168.1.23', '192.168.1.24', '192.168.1.25'],
            'tls-san': [
                'K1.home.arpa',
                'K2.home.arpa',
                'K3.home.arpa',
                '192.168.1.23',
                '192.168.1.24',
                '192.168.1.25',
                'kubernetes',
                'kubernetes.default',
                'kubernetes.default.svc',
                'kubernetes.default.svc.cluster.local'
            ]
        }
    }

@pytest.fixture
def alternative_inventory():
    return {
        'rke2_config': {
            'control_plane_nodes': ['10.0.0.10', '10.0.0.11', '10.0.0.12'],
            'tls-san': [
                'master1.example.com',
                'master2.example.com',
                'master3.example.com',
                '10.0.0.10',
                '10.0.0.11',
                '10.0.0.12',
                'kubernetes',
                'kubernetes.default',
                'kubernetes.default.svc',
                'kubernetes.default.svc.cluster.local'
            ]
        }
    }

def test_first_server_config(tmp_path, sample_inventory):
    """Test generation of first control plane node config"""
    print("\nTesting first server (k1) configuration:")
    
    hostname = "k1"
    config = generate_config_file(hostname, sample_inventory, is_first=True)
    config_file = tmp_path / f"config.yaml.{hostname}"
    write_config(config, config_file)
    
    with open(config_file) as f:
        written_config = yaml.safe_load(f)
    
    # Test required fields presence
    print("\nChecking required fields:")
    required_fields = ["write-kubeconfig-mode", "token", "tls-san", "node-name", "node-label", "node-taint", "cluster-init"]
    for field in required_fields:
        assert field in written_config, f"Missing required field: {field}"
        print(f"✓ Found field: {field}")
    
    # Test field values
    print("\nValidating field values:")
    print(f"✓ write-kubeconfig-mode: {written_config['write-kubeconfig-mode']}")
    print(f"✓ token: {written_config['token']}")
    print(f"✓ node-name: {written_config['node-name']}")
    assert written_config["cluster-init"] is True
    print("✓ cluster-init is True")
    
    # Test node labels
    print("\nChecking node labels:")
    expected_labels = [
        "node.kubernetes.io/instance-type=control-plane",
        f"kubernetes.io/hostname={hostname}",
        "workload.type=control-plane"
    ]
    for label in expected_labels:
        assert label in written_config["node-label"], f"Missing label: {label}"
        print(f"✓ Found label: {label}")
    
    # Test node taints
    print("\nChecking node taints:")
    assert "CriticalAddonsOnly=true:NoSchedule" in written_config["node-taint"]
    print("✓ Found correct node taint")
    
    # Test TLS SANs
    print("\nChecking TLS SANs:")
    for san in written_config["tls-san"]:
        print(f"✓ Found TLS SAN: {san}")

def test_subsequent_server_config(tmp_path, sample_inventory):
    """Test generation of subsequent control plane node configs"""
    print("\nTesting subsequent server (k2) configuration:")
    
    hostname = "k2"
    config = generate_config_file(hostname, sample_inventory, is_first=False)
    config_file = tmp_path / f"config.yaml.{hostname}"
    write_config(config, config_file)
    
    with open(config_file) as f:
        written_config = yaml.safe_load(f)
    
    # Test required fields presence
    print("\nChecking required fields:")
    required_fields = ["write-kubeconfig-mode", "token", "tls-san", "node-name", "node-label", "node-taint", "server"]
    for field in required_fields:
        assert field in written_config, f"Missing required field: {field}"
        print(f"✓ Found field: {field}")
    
    # Test field values
    print("\nValidating field values:")
    print(f"✓ write-kubeconfig-mode: {written_config['write-kubeconfig-mode']}")
    print(f"✓ token: {written_config['token']}")
    print(f"✓ node-name: {written_config['node-name']}")
    assert written_config["server"] == "https://192.168.1.23:9345"
    print(f"✓ server URL is correct: {written_config['server']}")
    
    # Test node labels
    print("\nChecking node labels:")
    expected_labels = [
        "node.kubernetes.io/instance-type=control-plane",
        f"kubernetes.io/hostname={hostname}",
        "workload.type=control-plane"
    ]
    for label in expected_labels:
        assert label in written_config["node-label"], f"Missing label: {label}"
        print(f"✓ Found label: {label}")
    
    # Test node taints
    print("\nChecking node taints:")
    assert "CriticalAddonsOnly=true:NoSchedule" in written_config["node-taint"]
    print("✓ Found correct node taint")
    
    # Test TLS SANs
    print("\nChecking TLS SANs:")
    for san in written_config["tls-san"]:
        print(f"✓ Found TLS SAN: {san}")

def test_yaml_validity(tmp_path, sample_inventory):
    """Test that generated YAML is valid for both first and subsequent servers"""
    print("\nTesting YAML validity for all server configurations:")
    
    for hostname, is_first in [("k1", True), ("k2", False)]:
        print(f"\nTesting {hostname} YAML validity:")
        config = generate_config_file(hostname, sample_inventory, is_first=is_first)
        config_file = tmp_path / f"config.yaml.{hostname}"
        
        # Test YAML writing
        write_config(config, config_file)
        print(f"✓ Successfully wrote YAML file for {hostname}")
        
        # Test YAML reading
        try:
            with open(config_file) as f:
                yaml.safe_load(f)
            print(f"✓ Successfully validated YAML syntax for {hostname}")
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML generated for {hostname}: {e}")

def test_first_server_config_alternative(tmp_path, alternative_inventory):
    """Test generation of first control plane node config with alternative hostnames"""
    print("\nTesting first server (master1) configuration with alternative names:")
    
    hostname = "master1"
    config = generate_config_file(hostname, alternative_inventory, is_first=True)
    config_file = tmp_path / f"config.yaml.{hostname}"
    write_config(config, config_file)
    
    with open(config_file) as f:
        written_config = yaml.safe_load(f)
    
    # Test required fields presence
    print("\nChecking required fields:")
    required_fields = ["write-kubeconfig-mode", "token", "tls-san", "node-name", "node-label", "node-taint", "cluster-init"]
    for field in required_fields:
        assert field in written_config, f"Missing required field: {field}"
        print(f"✓ Found field: {field}")
    
    # Test field values
    print("\nValidating field values:")
    print(f"✓ write-kubeconfig-mode: {written_config['write-kubeconfig-mode']}")
    print(f"✓ token: {written_config['token']}")
    print(f"✓ node-name: {written_config['node-name']}")
    assert written_config["cluster-init"] is True
    print("✓ cluster-init is True")
    assert written_config["node-name"] == "master1"
    print("✓ node-name is correct: master1")
    
    # Test node labels
    print("\nChecking node labels:")
    expected_labels = [
        "node.kubernetes.io/instance-type=control-plane",
        "kubernetes.io/hostname=master1",
        "workload.type=control-plane"
    ]
    for label in expected_labels:
        assert label in written_config["node-label"], f"Missing label: {label}"
        print(f"✓ Found label: {label}")
    
    # Test node taints
    print("\nChecking node taints:")
    assert "CriticalAddonsOnly=true:NoSchedule" in written_config["node-taint"]
    print("✓ Found correct node taint")
    
    # Test TLS SANs
    print("\nChecking TLS SANs:")
    for san in written_config["tls-san"]:
        print(f"✓ Found TLS SAN: {san}")

def test_subsequent_server_config_alternative(tmp_path, alternative_inventory):
    """Test generation of subsequent control plane node configs with alternative hostnames"""
    print("\nTesting subsequent server (master2) configuration with alternative names:")
    
    hostname = "master2"
    config = generate_config_file(hostname, alternative_inventory, is_first=False)
    config_file = tmp_path / f"config.yaml.{hostname}"
    write_config(config, config_file)
    
    with open(config_file) as f:
        written_config = yaml.safe_load(f)
    
    # Test required fields presence
    print("\nChecking required fields:")
    required_fields = ["write-kubeconfig-mode", "token", "tls-san", "node-name", "node-label", "node-taint", "server"]
    for field in required_fields:
        assert field in written_config, f"Missing required field: {field}"
        print(f"✓ Found field: {field}")
    
    # Test field values
    print("\nValidating field values:")
    print(f"✓ write-kubeconfig-mode: {written_config['write-kubeconfig-mode']}")
    print(f"✓ token: {written_config['token']}")
    print(f"✓ node-name: {written_config['node-name']}")
    assert written_config["server"] == "https://10.0.0.10:9345"
    print(f"✓ server URL is correct: {written_config['server']}")
    assert written_config["node-name"] == "master2"
    print("✓ node-name is correct: master2")
    
    # Test node labels
    print("\nChecking node labels:")
    expected_labels = [
        "node.kubernetes.io/instance-type=control-plane",
        "kubernetes.io/hostname=master2",
        "workload.type=control-plane"
    ]
    for label in expected_labels:
        assert label in written_config["node-label"], f"Missing label: {label}"
        print(f"✓ Found label: {label}")
    
    # Test node taints
    print("\nChecking node taints:")
    assert "CriticalAddonsOnly=true:NoSchedule" in written_config["node-taint"]
    print("✓ Found correct node taint")
    
    # Test TLS SANs
    print("\nChecking TLS SANs:")
    for san in written_config["tls-san"]:
        print(f"✓ Found TLS SAN: {san}")

def test_yaml_validity_alternative(tmp_path, alternative_inventory):
    """Test that generated YAML is valid for both first and subsequent servers with alternative names"""
    print("\nTesting YAML validity for all server configurations with alternative names:")
    
    for hostname, is_first in [("master1", True), ("master2", False)]:
        print(f"\nTesting {hostname} YAML validity:")
        config = generate_config_file(hostname, alternative_inventory, is_first=is_first)
        config_file = tmp_path / f"config.yaml.{hostname}"
        
        # Test YAML writing
        write_config(config, config_file)
        print(f"✓ Successfully wrote YAML file for {hostname}")
        
        # Test YAML reading
        try:
            with open(config_file) as f:
                yaml.safe_load(f)
            print(f"✓ Successfully validated YAML syntax for {hostname}")
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML generated for {hostname}: {e}")