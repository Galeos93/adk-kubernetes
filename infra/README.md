# Infrastructure Folder

This folder contains the Terraform configuration for provisioning AWS infrastructure for the FastAPI Agent application.

## Overview

The infrastructure includes:
- **EKS Cluster**: Managed Kubernetes cluster
- **ECR Repository**: Container registry for Docker images
- **RDS PostgreSQL**: Database for application data
- **VPC & Networking**: Network configuration with load balancer
- **IAM Roles & Policies**: AWS permissions for services
- **Route53**: DNS configuration
- **Secrets Management**: Encrypted secrets using SOPS

## Structure

```
infra/
├── .sops.yaml              # SOPS configuration for encryption
├── terraform.tf            # Terraform and provider configuration
├── terraform.tfstate       # Terraform state (DO NOT COMMIT)
├── terraform.tfstate.backup # State backup (DO NOT COMMIT)
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── main.tf                 # Main infrastructure resources
├── Makefile                # Infrastructure management commands
├── secrets.yaml            # Encrypted secrets (SOPS)
├── key.txt                 # AGE private key (KEEP SECURE!)
├── .terraform/             # Terraform working directory
├── .terraform.lock.hcl     # Provider lock file
├── aws_load_balancer_controller.tf  # ALB controller
├── ecr.tf                  # Elastic Container Registry
├── eks.tf                  # EKS cluster configuration
├── iam_policies.tf         # IAM policies
├── iam_roles.tf            # IAM roles
├── kubernetes_db_init.tf   # Database initialization job
├── kubernetes_ingress.tf   # Ingress configuration
├── network.tf              # VPC and networking
├── rds.tf                  # RDS PostgreSQL database
└── route53.tf              # DNS configuration
```

## Prerequisites

1. **AWS CLI**: Configure with appropriate credentials
2. **Terraform**: Version 1.x
3. **SOPS and AGE**: For secrets encryption/decryption
4. **kubectl**: For Kubernetes cluster access
5. **jq**: For JSON processing in scripts
6. **AWS Account**: With permissions for EKS, ECR, RDS, etc.
7. **Web domain**: For Route53 and SSL (must be available for registration)

## Quick Start

### 1. Create secrets with AGE and SOPS

Create AGE encryption keys:

```bash
age-keygen -o key.txt
```

Configure SOPS environment variable:

```bash
export SOPS_AGE_KEY_FILE=./key.txt
```

Update the public key in `.sops.yaml` (found in `key.txt`).

Encrypt secrets with the following keys:

- `db_user`: Database username used by the app
- `db_password`: Database password used by the app

```bash
sops secrets.yaml
```

### 2. Deploy Infrastructure

Use make to deploy the infrastructure. You can override default variables as needed:

```bash
# Basic deployment with defaults
make deploy-infra

# Override AWS profile (default: default)
PROFILE=your-profile make deploy-infra

# Override AWS region (default: us-west-2)
REGION=us-east-1 make deploy-infra

# Override domain name (default: agent-playground.online)
DOMAIN_NAME=yourdomain.com make deploy-infra

# Combine multiple overrides
PROFILE=personal REGION=us-west-2 DOMAIN_NAME=myapp.com make deploy-infra
```

This will:
- Initialize Terraform
- Deploy VPC, EKS cluster, and networking
- Set up ECR, RDS, IAM roles
- Configure Route53, ACM certificates
- Deploy Kubernetes resources (ingress, secrets, jobs)
- Wait for ALB creation
- Add DNS records

### 3. Configure Domain Nameservers

After deployment completes, you need to update your domain registrar (e.g., GoDaddy) with the Route53 nameservers:

1. **Get the nameservers** from Route53:
   ```bash
   aws route53 get-hosted-zone --id $(terraform output -raw hosted_zone_id) --query 'DelegationSet.NameServers' --output text
   ```

2. **Update your domain registrar**:
   - Log into your domain registrar's control panel
   - Find the nameserver/DNS settings for your domain
   - Replace the existing nameservers with the ones from Route53
   - Save the changes

3. **Wait for DNS propagation**:
   - DNS changes can take up to 48 hours to propagate globally
   - You can check propagation using tools like `dig` or `nslookup`
   - Your application will be accessible at `https://yourdomain.com` once propagation completes

⚠️ **Important**: Do not proceed with application deployment until DNS propagation is complete, as SSL certificates depend on the domain resolving correctly.

## Security Notes

### 🚨 Critical Security Considerations

- **AGE Private Key**: `key.txt` contains your AGE private key. **NEVER commit this file to version control**.
- **Terraform State**: `terraform.tfstate` and `terraform.tfstate.backup` contain infrastructure state and should **NEVER be committed**. They may contain sensitive information.
- **Encrypted Secrets**: `secrets.yaml` contains encrypted database credentials.

### Security Best Practices

1. **Never commit sensitive files**:
   - `key.txt`
   - `terraform.tfstate*`
   - Any decrypted secrets

2. **Use remote state**: For production, use Terraform Cloud or S3 backend with encryption.

3. **Key Management**: Use cloud KMS for production instead of local AGE keys.

4. **Access Control**: Limit AWS credentials scope to minimum required permissions.


## Configuration

### Makefile Variables

The `Makefile` defines default values for infrastructure variables:

- `PROFILE`: AWS CLI profile (default: `default`)
- `REGION`: AWS region (default: `us-west-2`)
- `DOMAIN_NAME`: Domain for Route53 (default: `agent-playground.online`)
- `DB_NAME`: Database name (default: `fastapi_agent_db`)
- `DB_USERNAME`: Database admin username (default: `postgres`)
- `DB_INSTANCE_CLASS`: RDS instance type (default: `db.t4g.micro`)
- `DB_ALLOCATED_STORAGE`: RDS storage in GB (default: `20`)

Override any variable when running make commands:

```bash
PROFILE=myprofile REGION=us-east-1 make deploy-infra
```

### Terraform Variables

Key variables in `variables.tf` (with defaults):

- `domain_name`: Domain for Route53 (default: `agent-playground.online`)
- `db_name`: Database name (default: `fastapi_agent_db`)
- `db_username`: Database admin username (default: `postgres`)
- `db_instance_class`: RDS instance type (default: `db.t4g.micro`)
- `db_allocated_storage`: RDS storage in GB (default: `20`)
- `db_app_username`: Application database user (from secrets)
- `db_app_password`: Application database password (from secrets)

### Secrets

Encrypted in `secrets.yaml`:
- `db_user`: Database admin username
- `db_password`: Database admin password

## Components

### EKS Cluster
- Managed Kubernetes control plane
- Node groups with auto-scaling
- IAM roles for service accounts (IRSA)

### ECR Repository
- Private container registry
- Automated image scanning
- Lifecycle policies

### RDS PostgreSQL
- Managed database instance
- Multi-AZ deployment
- Encrypted storage
- Automated backups

### Networking
- VPC with public/private subnets
- Internet Gateway and NAT Gateways
- Application Load Balancer
- Security groups

### DNS & SSL
- Route53 hosted zone
- ACM SSL certificates
- HTTPS ingress configuration

## Usage

### Available Make Commands

- `make deploy-infra`: Deploy all infrastructure
- `make destroy-infra`: Destroy all infrastructure (keeps Route53 zone)
- `make set-kubeconfig`: Update kubectl config for EKS cluster
- `make ecr-login`: Login to ECR repository
- `make build-and-push`: Build and push Docker image to ECR
- `make install-addons`: Install EKS add-ons (VPC CNI, CoreDNS, Kube Proxy)

### Database Initialization

The infrastructure includes a Kubernetes job that initializes the database:

1. Creates application user
2. Sets up required permissions
3. Runs on cluster startup

### Application Deployment

After infrastructure is ready:

1. Build and push Docker image: `make build-and-push`
2. Deploy using Helm (from `../deploy/` folder)
3. Configure ingress and SSL

## Cleanup

### Destroying Infrastructure

To destroy all infrastructure while preserving critical resources:

```bash
make destroy-infra
```

**What gets destroyed:**
- EKS cluster and node groups
- RDS PostgreSQL database
- ECR repository
- VPC, subnets, security groups
- IAM roles and policies
- Kubernetes resources (ingress, secrets, jobs)
- ACM certificates
- Application Load Balancer

**What gets preserved:**
- **Route53 hosted zone and DNS records**: Kept to avoid reconfiguring nameservers with your domain registrar (e.g., GoDaddy). This allows you to redeploy without DNS changes.
- **Route53 hosted zone**: The zone itself remains so your domain's DNS configuration stays intact.

### Complete Cleanup

If you want to destroy **everything** including the Route53 hosted zone:

```bash
terraform destroy
```

⚠️ **Warning**:
- This will remove the Route53 hosted zone, requiring you to update nameservers with your domain registrar again.
- **ECR repositories with images will NOT be deleted** by Terraform. AWS protects repositories containing images from automatic deletion.
- Some resources may require manual cleanup if they contain data or dependencies.

#### Manual Cleanup Steps

After `terraform destroy`, you may need to manually delete:

1. **ECR Images**: Empty the repository before deletion
   ```bash
   # List images
   aws ecr list-images --repository-name fastapi-agent

   # Delete images (replace with actual image IDs)
   aws ecr batch-delete-image --repository-name fastapi-agent --image-ids imageDigest=sha256:...

   # Delete repository
   aws ecr delete-repository --repository-name fastapi-agent --force
   ```

2. **Check for remaining resources** in the AWS console or CLI that Terraform couldn't delete.
