# Configure the Proxmox provider with connection details


# Define a virtual machine resource
resource "proxmox_virtual_environment_vm" "sample-server" {
  node_name   = "pve"                     # Proxmox node name
  name        = "sample-server-hostname"   # VM hostname
  description = "Sample Server.  Managed by Terraform."
  tags        = ["sample"]
  started     = true                      # Start VM after creation
  on_boot     = true                      # Auto-start VM on host boot

  # Enable QEMU guest agent for better host-guest integration
  agent {
    enabled = true
  }

  # Clone settings - specifies source template
  clone {
    node_name = "pve"
    vm_id = 9001                          # Source template VM ID
  }

  # VM OS type configuration
  operating_system {
    type = "l26"                          # Linux 2.6+ kernel
  }

  # CPU configuration
  cpu {
    cores = 2                             # Assign 2 CPU cores
  }

  # Memory configuration
  memory {
    dedicated = 4096                      # Assign 4GB RAM
  }

  # Storage configuration
  disk {
    datastore_id = "pve-vms"             # Storage location
    discard      = "on"                  # Enable TRIM/discard
    interface    = "scsi0"               # SCSI interface
    size         = 15                    # 15GB disk size
  }

  # Display configuration
  vga {
    type = "serial0"                     # Use serial console
  }

  # Network configuration
  network_device {
    bridge      = "vmbr0"               # Network bridge device
    enabled     = "true"
    # mac_address = ""                  # Optional static MAC address
  }

  # Initial VM configuration
  initialization {
    datastore_id = "pve-vms"

    # Network configuration
    ip_config {
      ipv4 {
        address = "10.0.0.100/24"        # Static IP address
        gateway = "10.0.0.1"             # Default gateway
      }
    }

    # DNS configuration
    dns {
      servers = ["10.0.0.1", "8.8.8.8"]  # DNS servers
    }

    # User account setup
    user_account {
      keys     = var.public_keys         # SSH public keys
      username = "matt"                  # Initial user account
    }
  }
}