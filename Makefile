.PHONY: lint clean generate-inventory

lint:
	ansible-lint --profile production

clean:
	ansible-playbook cleanup.yml

generate-inventory:
	./scripts/generate_inventory.py \
		--control-plane-ips 192.168.1.48 \
		--worker-ips 192.168.1.49 192.168.1.50 \
		--output inventory/rke2.yml

setup: generate-inventory
	ansible-playbook bootstrap-cluster.yml