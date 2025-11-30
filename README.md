# ADK Kubernetes

A complete sample repository demonstrating how to deploy a Google ADK (Agent Development Kit) Gmail agent application on Kubernetes using AWS infrastructure and modern DevOps practices.

## Overview

This repository showcases a production-ready deployment of a FastAPI application that integrates with Google ADK agents for Gmail operations. The architecture follows clean architecture principles and includes:

- **Application Layer**: FastAPI server with Google ADK Gmail agent integration
- **Infrastructure Layer**: AWS EKS, ECR, RDS PostgreSQL, VPC networking
- **Deployment Layer**: Helm charts with encrypted secrets management
- **Security**: SOPS encryption, AWS Secrets Manager, IAM roles

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Google ADK     │    │   PostgreSQL    │
│   Application   │───▶│   Gmail Agent    │───▶│   Database      │
│   (Clean Arch)  │    │                  │    │   (AWS RDS)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kubernetes    │    │   Helm Charts    │    │   AWS EKS       │
│   (Deployment)  │    │   (Encrypted     │    │   Cluster       │
│                 │    │    Secrets)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Repository Structure

### 📁 [`app/`](./app/)
FastAPI application with Google ADK Gmail agent integration. See [app/README.md](./app/README.md) for details.

### 📁 [`deploy/`](./deploy/)
Kubernetes deployment configuration using Helm and Helmfile. See [deploy/README.md](./deploy/README.md) for details.

### 📁 [`infra/`](./infra/)
AWS infrastructure as code using Terraform. See [infra/README.md](./infra/README.md) for details.

## Quick Start

1. **Set up infrastructure**: `cd infra && terraform init && terraform apply`
2. **Deploy application**: `cd ../deploy && make deploy`
3. **Develop locally**: `cd ../app && python main.py`

## Security Considerations

### 🚨 Critical Security Notes

1. **Private Keys**: AGE private keys in `*/key.txt` files should **NEVER** be committed to version control
2. **Terraform State**: `terraform.tfstate` files contain infrastructure state and should **NEVER** be committed
3. **Environment Variables**: Real API keys should not be committed - use placeholder values
4. **Secrets Management**: Use AWS Secrets Manager or similar for production secrets

### Security Features

- **Encrypted Secrets**: All sensitive data encrypted with SOPS
- **IAM Roles**: Least privilege access for AWS services
- **Network Security**: VPC isolation, security groups
- **OAuth2**: Secure authentication flows
- **HTTPS**: SSL/TLS encryption for all endpoints

## Prerequisites

- **Python 3.11+**: For application development
- **Docker**: Container building and testing
- **AWS CLI**: Configured with appropriate credentials
- **Terraform 1.x**: Infrastructure provisioning
- **kubectl & Helm 3.x**: Kubernetes operations
- **SOPS**: Secrets encryption/decryption

## API Endpoints

Once deployed, access:
- **API Documentation**: `https://your-domain.com/docs`
- **Health Check**: `https://your-domain.com/health`
- **Agent Endpoint**: `POST https://your-domain.com/run_sse`

## Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes following clean architecture principles
4. **Test** thoroughly (unit tests, integration tests)
5. **Update** documentation as needed
6. **Submit** a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use Terraform best practices
- Include security considerations in changes
- Update READMEs for any architectural changes

## License

This project is provided as a sample implementation. Please review and adapt security configurations for your specific use case.

---

**⚠️ Security Notice**: This repository contains sample configurations. Never commit real secrets, private keys, or sensitive infrastructure state to version control. Always use secure secret management practices in production.
