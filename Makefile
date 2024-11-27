.PHONY: test generate clean help verify cleanup reboot setup-control setup-workers setup-cluster verify-cluster deploy-workflow configure-kubectl verify-kubectl verify-all-hosts verify-control-hosts verify-worker-hosts

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PYTEST := pytest
ANSIBLE := ansible-playbook
INVENTORY_FILE := inventory/hosts.txt
INVENTORY_YML := inventory/rke2.yml
OUTPUT_DIR := generated_configs

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	$(PYTEST) tests/ -v -s

generate-inventory:  ## Generate inventory from hosts.txt
	$(PYTHON) scripts/generate_inventory.py $(INVENTORY_FILE)

generate-configs:  ## Generate RKE2 configs from inventory
	$(PYTHON) scripts/generate_rke2_configs.py

generate: generate-inventory generate-configs  ## Generate both inventory and configs

verify-all-hosts:  ## Verify all hosts connectivity and configuration
	$(ANSIBLE) -i $(INVENTORY_YML) verify_hosts.yml

verify-control-hosts:  ## Verify control plane hosts connectivity and configuration
	$(ANSIBLE) -i $(INVENTORY_YML) verify_hosts.yml --limit control_plane_nodes

verify-worker-hosts:  ## Verify worker hosts connectivity and configuration
	$(ANSIBLE) -i $(INVENTORY_YML) verify_hosts.yml --limit worker_nodes

setup-control: generate  ## Setup control plane nodes with kubectl access
	$(ANSIBLE) -i $(INVENTORY_YML) rke2.yml --limit control_plane_nodes
	$(MAKE) configure-kubectl
	$(MAKE) verify-kubectl

setup-workers:  ## Setup worker nodes
	$(ANSIBLE) -i $(INVENTORY_YML) rke2.yml --limit worker_nodes

setup-cluster: setup-control setup-workers  ## Setup entire cluster (control plane first, then workers)

cleanup:  ## Clean up hosts (remove RKE2, configs, etc.)
	$(ANSIBLE) -i $(INVENTORY_YML) cleanup.yml

reboot:  ## Reboot all hosts
	$(ANSIBLE) -i $(INVENTORY_YML) reboot.yml 

clean:  ## Clean generated files
	rm -rf $(OUTPUT_DIR)/*
	rm -f $(INVENTORY_YML)

validate:  ## Run validation on inventory and configs
	$(PYTHON) scripts/generate_rke2_configs.py --validate-only

setup:  ## Create necessary directories
	mkdir -p $(OUTPUT_DIR) inventory tests

verify-all: generate verify  ## Generate inventory and verify hosts

cleanup-all: cleanup reboot  ## Clean up and reboot hosts

deploy: verify-all setup-cluster  ## Full deployment: verify hosts and setup cluster

verify-cluster:  ## Verify cluster health (read-only checks)
	$(ANSIBLE) -i $(INVENTORY_YML) verify_cluster.yml

deploy-workflow:  ## Show typical deployment workflow
	@echo "Typical deployment workflow:"
	@echo "1. make verify-all        # Verify hosts"
	@echo "2. make setup-control     # Setup control plane"
	@echo "3. make verify-cluster    # Verify cluster health"
	@echo "4. make setup-workers     # Setup worker nodes"

configure-kubectl:  ## Setup kubectl access on control plane nodes
	$(ANSIBLE) -i $(INVENTORY_YML) configure_kubectl.yml

verify-kubectl: configure-kubectl  ## Verify kubectl access and cluster status
	$(ANSIBLE) -i $(INVENTORY_YML) verify_cluster.yml