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
3. **SOPS**: For secrets encryption/decryption
4. **kubectl**: For Kubernetes cluster access
5. **AWS Account**: With permissions for EKS, ECR, RDS, etc.

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

## Quick Start

### 1. Initialize Terraform

```bash
terraform init
```

### 2. Plan Deployment

```bash
terraform plan
```

### 3. Apply Infrastructure

```bash
terraform apply
```

### 4. Configure kubectl

```bash
aws eks update-kubeconfig --region us-west-2 --name your-cluster-name
```

## Configuration

### Variables

Key variables in `variables.tf`:

- `aws_region`: AWS region (default: us-west-2)
- `cluster_name`: EKS cluster name
- `vpc_cidr`: VPC CIDR block
- `db_app_username`: Application database user
- `db_app_password`: Application database password (sensitive)
- `domain_name`: Domain for Route53

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

### Database Initialization

The infrastructure includes a Kubernetes job that initializes the database:

1. Creates application user
2. Sets up required permissions
3. Runs on cluster startup

### Application Deployment

After infrastructure is ready:

1. Build and push Docker image to ECR
2. Deploy using Helm (from `../deploy/` folder)
3. Configure ingress and SSL

## Maintenance

### Updates

```bash
# Plan changes
terraform plan

# Apply updates
terraform apply
```

### Database Management

- Backups are automated via RDS
- Manual snapshots can be created via AWS console
- Password rotation requires updating secrets and redeploying

### Cluster Scaling

- Node groups auto-scale based on CPU/memory
- Manual scaling via AWS console or eksctl

## Troubleshooting

### Common Issues

1. **Terraform State Lock**
   ```
   Error: Error acquiring the state lock
   ```
   - Check if another process is running terraform
   - Force unlock if necessary: `terraform force-unlock LOCK_ID`

2. **EKS Cluster Access**
   ```
   Unable to connect to the server
   ```
   - Update kubeconfig: `aws eks update-kubeconfig --region REGION --name CLUSTER`
   - Check AWS credentials and IAM permissions

3. **Secrets Decryption**
   - Ensure `key.txt` exists and matches `.sops.yaml`
   - Check SOPS installation

### Logs and Monitoring

- **CloudWatch**: EKS control plane logs
- **RDS Monitoring**: Performance insights
- **VPC Flow Logs**: Network traffic analysis

## Cost Optimization

- **EKS**: Use spot instances for non-critical workloads
- **RDS**: Right-size instance type, enable auto-scaling
- **NAT Gateways**: Can be expensive; consider VPC endpoints
- **Unused Resources**: Regularly audit and remove unused infrastructure

## Production Considerations

1. **Remote State**: Use S3 backend with DynamoDB locking
2. **State Encryption**: Enable encryption for S3 bucket
3. **Backup Strategy**: Regular state backups and disaster recovery
4. **Multi-Region**: Consider multi-region deployment for high availability
5. **Security Groups**: Least privilege access rules
6. **Monitoring**: Enable CloudTrail, Config, and GuardDuty

## Cleanup

To destroy all infrastructure:

```bash
terraform destroy
```

**⚠️ WARNING**: This will delete all resources including databases and data!</content>
<parameter name="filePath">/home/alejandro_garcia/repos/borrar/adk-kubernetes/infra/README.md