import pytest
from scripts.fix_yaml import (
    fix_yaml_file,
    validate_yaml_structure,
    backup_file
)
import os
import yaml
import tempfile

@pytest.fixture
def sample_yaml_file(tmp_path):
    content = """
all:
  children:
    six_node_cluster:
      children:
        control_plane_nodes:
          hosts:
            k1:
              ansible_host: 192.168.1.23
    """
    file_path = tmp_path / "test.yml"
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

def test_validate_yaml_structure():
    """Test YAML structure validation"""
    valid_structure = {
        'all': {
            'children': {
                'six_node_cluster': {
                    'children': {}
                }
            }
        }
    }
    assert validate_yaml_structure(valid_structure) == True
    
    invalid_structure = {'wrong_key': {}}
    with pytest.raises(ValueError):
        validate_yaml_structure(invalid_structure)

def test_validate_yaml_structure_with_invalid_types():
    """Test YAML structure validation with invalid types"""
    # Test with list instead of dict
    with pytest.raises(ValueError, match="YAML root must be a dictionary"):
        validate_yaml_structure([1, 2, 3])
    
    # Test with missing children
    with pytest.raises(ValueError, match="Missing required field 'children'"):
        validate_yaml_structure({'all': {}})

def test_backup_file(tmp_path):
    """Test file backup functionality"""
    # Create test file
    test_file = tmp_path / "test.yml"
    with open(test_file, 'w') as f:
        f.write("test content")
    
    backup_path = backup_file(str(test_file))
    assert os.path.exists(backup_path)
    assert backup_path.endswith('.bak')

def test_backup_file_nonexistent():
    """Test backup_file with nonexistent file"""
    backup_path = backup_file("/nonexistent/file.yml")
    assert backup_path.endswith('.bak')
    assert not os.path.exists(backup_path)

def test_fix_yaml_file(sample_yaml_file):
    """Test YAML file fixing"""
    fixed_content = fix_yaml_file(str(sample_yaml_file))
    assert isinstance(fixed_content, dict)
    assert 'all' in fixed_content
    assert 'children' in fixed_content['all']

def test_fix_yaml_file_with_invalid_file():
    """Test fix_yaml_file with invalid file"""
    # Test nonexistent file
    with pytest.raises(FileNotFoundError):
        fix_yaml_file("/nonexistent/file.yml")
    
    # Test invalid YAML content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tf:
        tf.write("invalid: yaml: content:\n  - missing: quote'")
        temp_path = tf.name
    
    try:
        with pytest.raises(ValueError, match="Invalid YAML format"):
            fix_yaml_file(temp_path)
    finally:
        os.unlink(temp_path)
