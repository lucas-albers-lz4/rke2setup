#!/usr/bin/env python3
import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader, exceptions

def check_jinja_file(file_path):
    """Check a single file for Jinja2 syntax errors."""
    try:
        with open(file_path, 'r') as f:
            template_content = f.read()
        
        # Create a Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.dirname(file_path)))
        
        # Try to parse the template
        env.parse(template_content)
        return None
    except exceptions.TemplateSyntaxError as e:
        return f"Error in {file_path}: {str(e)}"
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"

def find_files(directory):
    """Find all potential template files in the directory and its subdirectories."""
    template_files = []
    for root, _, files in os.walk(directory):
        # Skip venv directory
        if 'venv' in root.split(os.path.sep):
            continue
        if '.venv' in root.split(os.path.sep):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Check if the file is a template file
            if file.endswith(('.j2', '.jinja2', '.yml', '.yaml')):
                template_files.append(file_path)
            else:
                # Check if the file contains Jinja2 syntax
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if '{{' in content or '{%' in content or '{#' in content:
                            template_files.append(file_path)
                except (UnicodeDecodeError, IsADirectoryError):
                    # Skip binary files or directories
                    pass
    return template_files

def check_single_file(file_path):
    """Check a single file for Jinja2 syntax errors."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return 1
    
    error = check_jinja_file(file_path)
    if error:
        print(error)
        return 1
    else:
        print(f"No Jinja2 syntax errors found in {file_path}.")
        return 0

def check_all_files(start_dir='.'):
    """Check all potential template files in the project."""
    # Find all potential template files
    template_files = find_files(start_dir)
    
    # Check each file
    errors_found = False
    for file_path in template_files:
        error = check_jinja_file(file_path)
        if error:
            print(error)
            errors_found = True
    
    if not errors_found:
        print("No Jinja2 syntax errors found in template files.")
        return 0
    else:
        return 1

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Check Jinja2 template files for syntax errors.'
    )
    parser.add_argument(
        '-f', '--file',
        help='Path to a specific file to check'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Directory to scan for template files (default: current directory)'
    )
    return parser.parse_args()

def main():
    """Main function to check template files for Jinja2 syntax errors."""
    args = parse_args()
    
    if args.file:
        # Check a single file
        return check_single_file(args.file)
    else:
        # Check all files in the specified directory
        return check_all_files(args.directory)

if __name__ == "__main__":
    sys.exit(main()) 