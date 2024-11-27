#!/usr/bin/env python3

import yaml
import os
from datetime import datetime

def validate_yaml_structure(data):
    """Validate the basic structure of the YAML data."""
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a dictionary")
    
    if 'all' not in data:
        raise ValueError("Missing required field 'all' in YAML structure")
    
    if 'children' not in data['all']:
        raise ValueError("Missing required field 'children' in 'all' section")
    
    return True

def backup_file(file_path):
    """Create a backup of the specified file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.{timestamp}.bak"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    return backup_path

def fix_yaml_file(file_path):
    """Fix and validate a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")
    
    validate_yaml_structure(data)
    return data
