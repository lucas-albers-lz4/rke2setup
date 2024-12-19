terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
    }
  }
}

provider "proxmox" {
  endpoint = var.proxmox_endpoint
  insecure = true
  ssh {
    agent       = true
    private_key = file(var.ssh_private_key_path)
  }
}