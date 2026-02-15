# OpenClaw Ansible Deployment

.PHONY: help deploy check ping master osint ai

help:  ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check:  ## Check ansible connection to all hosts
	ansible all -i inventories/production.yml -m ping

deploy:  ## Deploy to all systems
	ansible-playbook -i inventories/production.yml site.yml --ask-vault-pass

master:  ## Deploy only to Mac Mini master
	ansible-playbook -i inventories/production.yml playbooks/deploy-master.yml --ask-vault-pass

osint:  ## Deploy only to Kali Y2K OSINT agent  
	ansible-playbook -i inventories/production.yml playbooks/deploy-osint.yml --ask-vault-pass

ai:  ## Deploy only to Jetson Orin AI agent
	ansible-playbook -i inventories/production.yml playbooks/deploy-ai.yml --ask-vault-pass

dry-run:  ## Dry run deployment (check mode)
	ansible-playbook -i inventories/production.yml site.yml --check --ask-vault-pass

vault-edit:  ## Edit encrypted secrets
	ansible-vault edit vault.yml