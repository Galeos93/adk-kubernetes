export SOPS_AGE_KEY_FILE=./key.txt

# AWS profile to use (default: default)
PROFILE ?= default

# AWS region to use (default: us-west-2)
REGION ?= us-west-2

# Terraform variable defaults
DOMAIN_NAME ?= agent-playground.online
DB_NAME = fastapi_agent_db
DB_USERNAME = postgres
DB_INSTANCE_CLASS = db.t4g.micro
DB_ALLOCATED_STORAGE = 20

set-kubeconfig:
	aws eks update-kubeconfig --region $(REGION) --name eks-cluster --profile $(PROFILE)

ecr-login:
	aws ecr get-login-password --region $(REGION) --profile $(PROFILE) | docker login --username AWS --password-stdin $(shell terraform output -raw ecr_repository_url | cut -d'/' -f1)

build-and-push:
	$(eval ECR_REPO := $(shell terraform output -raw ecr_repository_url))
	@echo "Building and pushing to: $(ECR_REPO)"
	cd ../app && docker build -f docker/Dockerfile -t fastapi-agent:latest .
	docker tag fastapi-agent:latest $(ECR_REPO):latest
	$(MAKE) ecr-login
	docker push $(ECR_REPO):latest


install-addons:
	aws eks create-addon --cluster-name eks-cluster --addon-name vpc-cni --region $(REGION) --profile $(PROFILE)
	aws eks create-addon --cluster-name eks-cluster --addon-name coredns --region $(REGION) --profile $(PROFILE)
	aws eks create-addon --cluster-name eks-cluster --addon-name kube-proxy --region $(REGION) --profile $(PROFILE)


deploy-infra:
	@echo "Stage 1: Deploying infrastructure (excluding DNS A record)..."
	$(eval DB_USER := $(shell sops -d --extract '["db_user"]' secrets.yaml))
	$(eval DB_PASSWORD := $(shell sops -d --extract '["db_password"]' secrets.yaml))
	@if [ -z "$(DB_USER)" ] || [ -z "$(DB_PASSWORD)" ]; then \
		echo "❌ Error: Failed to extract database credentials from secrets.yaml"; \
		echo "Make sure secrets.yaml is properly encrypted and SOPS_AGE_KEY_FILE is set"; \
		exit 1; \
	fi
	@echo "✅ Database credentials extracted successfully"
	terraform init
	terraform apply -auto-approve \
		-var="db_app_username=$(DB_USER)" \
		-var="db_app_password=$(DB_PASSWORD)" \
		-var="domain_name=$(DOMAIN_NAME)" \
		-var="db_name=$(DB_NAME)" \
		-var="db_username=$(DB_USERNAME)" \
		-var="db_instance_class=$(DB_INSTANCE_CLASS)" \
		-var="db_allocated_storage=$(DB_ALLOCATED_STORAGE)" \
		-target=module.vpc \
		-target=module.eks
	@echo ""
	@echo "Updating kubeconfig for EKS cluster..."
	$(MAKE) set-kubeconfig
	@echo ""
	@echo "Continuing infrastructure deployment..."
	terraform apply -auto-approve \
		-var="db_app_username=$(DB_USER)" \
		-var="db_app_password=$(DB_PASSWORD)" \
		-var="domain_name=$(DOMAIN_NAME)" \
		-var="db_name=$(DB_NAME)" \
		-var="db_username=$(DB_USERNAME)" \
		-var="db_instance_class=$(DB_INSTANCE_CLASS)" \
		-var="db_allocated_storage=$(DB_ALLOCATED_STORAGE)" \
		-target=aws_iam_role.fastapi_agent_role \
		-target=aws_iam_role_policy_attachment.fastapi_agent_ecr_access \
		-target=kubernetes_service_account.fastapi_agent \
		-target=aws_ecr_repository.fastapi_agent \
		-target=aws_db_subnet_group.postgres \
		-target=aws_security_group.rds \
		-target=aws_db_instance.postgres \
		-target=data.aws_secretsmanager_secret.db_password \
		-target=data.aws_secretsmanager_secret_version.db_password \
		-target=kubernetes_secret.db_init \
		-target=kubernetes_job.db_init \
		-target=aws_route53_zone.main \
		-target=aws_acm_certificate.api \
		-target=aws_route53_record.cert_validation \
		-target=aws_acm_certificate_validation.api \
		-target=helm_release.aws_load_balancer_controller \
		-target=kubernetes_ingress_v1.agent_ingress
	@echo ""
	@echo "Waiting for AWS Load Balancer Controller to create ALB..."
	@bash -c 'for i in {1..30}; do \
		ALB=$$(kubectl get ingress agent-ingress -n default -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" 2>/dev/null || echo ""); \
		if [ -n "$$ALB" ]; then \
			echo "✅ ALB ready: $$ALB"; \
			break; \
		fi; \
		echo "Waiting for ALB... ($$i/30)"; \
		sleep 10; \
	done'
	@echo ""
	@echo "Stage 2: Deploying DNS records..."
	terraform apply -auto-approve \
		-var="db_app_username=$(DB_USER)" \
		-var="db_app_password=$(DB_PASSWORD)" \
		-var="domain_name=$(DOMAIN_NAME)" \
		-var="db_name=$(DB_NAME)" \
		-var="db_username=$(DB_USERNAME)" \
		-var="db_instance_class=$(DB_INSTANCE_CLASS)" \
		-var="db_allocated_storage=$(DB_ALLOCATED_STORAGE)" \
		-target=aws_route53_record.api \
		-target=aws_route53_record.db
	@echo ""
	@echo "✅ Deployment complete!"
	@echo "Your domain: $$(terraform output -raw domain_name 2>/dev/null || echo 'not configured')"
	@echo "Database endpoint: db.$$(terraform output -raw domain_name 2>/dev/null || echo 'not configured')"


destroy-infra:
	@echo "Destroying all infrastructure except Route 53 hosted zone and DNS records..."
	$(eval DB_USER := $(shell sops -d --extract '["db_user"]' secrets.yaml))
	$(eval DB_PASSWORD := $(shell sops -d --extract '["db_password"]' secrets.yaml))
	# Step 1: Get ELB hostname before destroying Ingress
	$(eval ELB_HOSTNAME := $(shell kubectl get ingress agent-ingress -n default -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" 2>/dev/null || echo ""))
	@echo "ELB hostname: $(ELB_HOSTNAME)"
	# Destroy Ingress first (removes ELB)
	terraform destroy -auto-approve \
		-var="db_app_username=$(DB_USER)" \
		-var="db_app_password=$(DB_PASSWORD)" \
		-var="domain_name=$(DOMAIN_NAME)" \
		-var="db_name=$(DB_NAME)" \
		-var="db_username=$(DB_USERNAME)" \
		-var="db_instance_class=$(DB_INSTANCE_CLASS)" \
		-var="db_allocated_storage=$(DB_ALLOCATED_STORAGE)" \
		-target=kubernetes_ingress_v1.agent_ingress
	@echo "Waiting for ELB to be deleted..."
	@bash -c 'for i in {1..30}; do \
	  if [ -z "$(ELB_HOSTNAME)" ]; then \
	    echo "✅ No ELB hostname found, assuming deleted."; \
	    break; \
	  fi; \
	  ELB_EXISTS=$$(aws elbv2 describe-load-balancers --region $(REGION) --profile $(PROFILE) | jq -r ".LoadBalancers[] | select(.DNSName == \"$(ELB_HOSTNAME)\") | .LoadBalancerArn" 2>/dev/null || echo ""); \
	  if [ -z "$$ELB_EXISTS" ]; then \
	    echo "✅ ELB deleted."; \
	    break; \
	  fi; \
	  echo "Waiting for ELB deletion... ($$i/30)"; \
	  sleep 10; \
	done'
	# Step 2: Destroy controller and remaining resources
	terraform destroy -auto-approve \
		-var="db_app_username=$(DB_USER)" \
		-var="db_app_password=$(DB_PASSWORD)" \
		-var="domain_name=$(DOMAIN_NAME)" \
		-var="db_name=$(DB_NAME)" \
		-var="db_username=$(DB_USERNAME)" \
		-var="db_instance_class=$(DB_INSTANCE_CLASS)" \
		-var="db_allocated_storage=$(DB_ALLOCATED_STORAGE)" \
		-target=helm_release.aws_load_balancer_controller \
		-target=kubernetes_service_account.fastapi_agent \
		-target=aws_iam_role.fastapi_agent_role \
		-target=aws_iam_role_policy_attachment.fastapi_agent_ecr_access \
		-target=aws_db_subnet_group.postgres \
		-target=aws_security_group.rds \
		-target=aws_db_instance.postgres \
		-target=data.aws_secretsmanager_secret.db_password \
		-target=data.aws_secretsmanager_secret_version.db_password \
		-target=kubernetes_secret.db_init \
		-target=kubernetes_job.db_init \
		-target=aws_acm_certificate.api \
		-target=aws_acm_certificate_validation.api \
		-target=module.vpc \
		-target=module.eks
	@echo "✅ Destroy complete! Route 53 hosted zone and DNS records are preserved."
