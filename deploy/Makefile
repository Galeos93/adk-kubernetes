export SOPS_AGE_KEY_FILE := $(shell pwd)/key.txt

deploy:
	helmfile apply

destroy:
	helmfile destroy