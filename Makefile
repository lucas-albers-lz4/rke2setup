.PHONY: lint clean generate-inventory six-node-cluster

lint:
	ansible-lint --profile production

clean:
	ansible-playbook cleanup.yml

generate-inventory:
	./scripts/generate_inventory.py inventory/hosts.txt

six-node-cluster: generate-inventory
	ansible-playbook -i inventory/rke2.yml six-node-cluster.yml