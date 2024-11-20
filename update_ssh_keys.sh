#!/bin/bash

# Function to parse hosts from inventory file
parse_inventory() {
    while IFS= read -r line; do
        # Skip empty lines, comments, and section headers
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]] || [[ "$line" =~ ^\[ ]]; then
            continue
        fi
        
        # Extract hostname and IP
        if [[ "$line" =~ ^[[:alnum:]]+ ]]; then
            host=$(echo "$line" | awk '{print $1}')
            ip=$(echo "$line" | awk '{print $2}')
            
            echo "Processing $host ($ip)"
            # Remove old keys
            ssh-keygen -R $host 2>/dev/null
            ssh-keygen -R $ip 2>/dev/null
            
            # Add new keys
            ssh-keyscan -H $host >> ~/.ssh/known_hosts 2>/dev/null
            ssh-keyscan -H $ip >> ~/.ssh/known_hosts 2>/dev/null
        fi
    done < "inventory/hosts.txt"
}

# Main execution
echo "Starting SSH key scanning..."
parse_inventory
echo "SSH key scanning complete!"