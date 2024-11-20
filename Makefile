.PHONY: lint clean generate-inventory deploy

lint:
	ansible-lint --profile production

clean:
	ansible-playbook cleanup.yml

generate-inventory:
	./scripts/generate_inventory.py inventory/hosts.txt

deploy: generate-inventory
	ansible-playbook -i inventory/rke2.yml verify_hosts.yml rke2.yml