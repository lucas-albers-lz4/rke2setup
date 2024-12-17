variable "proxmox_nodes" {
  description = "List of Proxmox nodes"
  type        = list(string)
  default     = ["pve1", "pve2", "pve3"]
}

variable "k8s_nodes" {
  description = "Kubernetes node configurations"
  type = object({
    control_plane_count = number
    worker_count        = number
    control_plane = object({
      cores  = number
      memory = number
      disk   = number
    })
    worker = object({
      cores  = number
      memory = number
      disk   = number
    })
  })
  default = {
    control_plane_count = 3
    worker_count        = 3
    control_plane = {
      cores  = 2
      memory = 4096
      disk   = 20
    }
    worker = {
      cores  = 4
      memory = 8192
      disk   = 40
    }
  }
}

variable "proxmox_endpoint" {
  type        = string
  description = "Proxmox API endpoint URL"
}

variable "ssh_private_key_path" {
  type        = string
  description = "Path to SSH private key"
}
