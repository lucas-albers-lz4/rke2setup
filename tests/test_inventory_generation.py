import pytest
import os
import yaml
from scripts.generate_inventory import (
    generate_inventory,
    parse_host_line,
    validate_node_data,
    write_inventory_file,
)


@pytest.fixture
def sample_hosts_file(tmp_path):
    hosts_file = tmp_path / "hosts.txt"
    hosts_file.write_text(
        """
[vars]
ssh_public_key_path=~/.ssh/id_ed25519.pub
rke2_version=v1.31.4+rke2r1

[six_node]
k1 192.168.1.23
k2 192.168.1.24
k3 192.168.1.25
node7 192.168.1.55 agent_mount_device=/dev/sdb
node8 192.168.1.54
node9 192.168.1.52

[control_plane_nodes]
k1
k2
k3

[worker_nodes]
node7
node8
node9
"""
    )
    return str(hosts_file)


def test_parse_host_line_basic():
    hostname, host_vars = parse_host_line("k1 192.168.1.23")
    assert hostname == "k1"
    assert host_vars["ansible_host"] == "192.168.1.23"


def test_parse_host_line_with_mount():
    hostname, host_vars = parse_host_line("node7 192.168.1.55 agent_mount_device=/dev/sdb")
    assert hostname == "node7"
    assert host_vars["ansible_host"] == "192.168.1.55"
    assert host_vars["mounts"]["agent"]["enabled"] is True
    assert host_vars["mounts"]["agent"]["device"] == "/dev/sdb"


def test_generate_inventory(sample_hosts_file):
    inventory = generate_inventory(sample_hosts_file)

    assert "all" in inventory
    children = inventory["all"]["children"]["six_node_cluster"]["children"]
    assert "control_plane_nodes" in children
    assert "worker_nodes" in children

    control_plane = children["control_plane_nodes"]["hosts"]
    assert len(control_plane) == 3
    assert control_plane["k1"]["ansible_host"] == "192.168.1.23"

    workers = children["worker_nodes"]["hosts"]
    assert len(workers) == 3
    assert workers["node7"]["mounts"]["agent"]["device"] == "/dev/sdb"

    assert inventory["all"]["vars"]["rke2_version"] == "v1.31.4+rke2r1"
    assert inventory["all"]["vars"]["ansible_user"] == "ubuntu"


def test_validate_node_data():
    valid_data = [("node1", "192.168.1.1"), ("node2", "192.168.1.2")]
    assert validate_node_data(valid_data) is True

    with pytest.raises(ValueError):
        validate_node_data([("node1", "256.256.256.256")])

    with pytest.raises(ValueError):
        validate_node_data([("", "192.168.1.1")])


def test_write_inventory_file(tmp_path):
    inventory_data = {
        "all": {
            "children": {
                "six_node_cluster": {
                    "children": {
                        "control_plane_nodes": {
                            "hosts": {
                                "k1": {"ansible_host": "192.168.1.23"}
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
        content = f.read()
        assert "WARNING: THIS IS A GENERATED FILE" in content
        loaded_data = yaml.safe_load(content)
        assert loaded_data == inventory_data
