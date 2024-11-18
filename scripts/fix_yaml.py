#!/usr/bin/env python3
"""
YAML formatting fix utility for RKE2 setup repository.
Handles empty lines and newline issues according to ansible-lint requirements.
"""
import os
import sys
from pathlib import Path
import ruamel.yaml

def get_repo_root() -> Path:
    """Get the repository root directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent
    return Path.cwd()

def fix_yaml_file(file_path: Path, strict_empty_lines: bool = False) -> bool:
    """Fix YAML file formatting issues."""
    try:
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()

        # Remove trailing whitespace and normalize newlines
        lines = [line.rstrip() for line in content.splitlines()]
        
        # Handle empty lines more strictly for specific files
        new_lines = []
        prev_empty = False
        
        for i, line in enumerate(lines):
            if not line.strip():
                # For strict files, only allow empty lines between content blocks
                if strict_empty_lines:
                    # Check if this empty line is between content blocks
                    prev_has_content = i > 0 and lines[i-1].strip()
                    next_has_content = i < len(lines)-1 and lines[i+1].strip()
                    if prev_has_content and next_has_content and not prev_empty:
                        new_lines.append('')
                    prev_empty = True
                else:
                    if not prev_empty:
                        new_lines.append('')
                    prev_empty = True
            else:
                new_lines.append(line)
                prev_empty = False

        # Remove any trailing empty lines before adding final newline
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()

        # Ensure exactly one newline at end of file
        content = '\n'.join(new_lines) + '\n'

        # Write back to file
        with open(file_path, 'w') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function to process YAML files."""
    repo_root = get_repo_root()
    
    # Files that need strict empty line handling
    strict_files = {
        'inventory/rke2.yml',
        'roles/rke2_cluster/tasks/main.yml'
    }

    success_count = 0
    error_count = 0

    print(f"Starting YAML file fixes from repository root: {repo_root}")

    for file_path in strict_files:
        path = repo_root / file_path
        if not path.exists():
            print(f"Warning: File not found: {file_path}")
            continue

        print(f"Processing {file_path}...")
        if fix_yaml_file(path, strict_empty_lines=True):
            success_count += 1
            print(f"✓ Fixed {file_path}")
        else:
            error_count += 1
            print(f"✗ Failed to fix {file_path}")

    print(f"\nCompleted with {success_count} successes and {error_count} errors")

if __name__ == "__main__":
    # Add command line argument for dry run
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("Dry run mode - no files will be modified")
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
