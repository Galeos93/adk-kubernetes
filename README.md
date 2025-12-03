# ADK Kubernetes

A complete sample repository demonstrating how to deploy a Google ADK (Agent Development Kit) Gmail agent application on Kubernetes using AWS infrastructure and modern DevOps practices.

## Overview

This repository showcases a production-ready deployment of a FastAPI application that integrates with Google ADK agents for Gmail operations. The architecture follows clean architecture principles and includes:

- **Application Layer**: FastAPI server with Google ADK Gmail agent integration
- **Infrastructure Layer**: AWS EKS, ECR, RDS PostgreSQL, VPC networking
- **Deployment Layer**: Helm charts with encrypted secrets management
- **Security**: SOPS encryption, AWS Secrets Manager, IAM roles

Once you deploy the infrastructure and application, you will be able to talk with an agent to have access to your Gmail account and perform operations like reading emails in a secure manner, using OAuth2 authentication.

## Repository Structure

### 📁 [`app/`](./app/)
FastAPI application with Google ADK Gmail agent integration. See [app/README.md](./app/README.md) for details.

### 📁 [`deploy/`](./deploy/)
Kubernetes deployment configuration using Helm and Helmfile. See [deploy/README.md](./deploy/README.md) for details.

### 📁 [`infra/`](./infra/)
AWS infrastructure as code using Terraform. See [infra/README.md](./infra/README.md) for details.

## Quick Start

1. **Set up infrastructure**: Go to `infra/` and follow the instructions in [infra/README.md](./infra/README.md) to initialize and apply the Terraform configuration.
2. **Develop and build locally**: Go to `app/` and follow the instructions in [app/README.md](./app/README.md) to run the FastAPI application locally and build a Docker image for deployment.
3. **Deploy application**: Go to `deploy/` and follow the instructions in [deploy/README.md](./deploy/README.md) to deploy the application using Helm.

## License

This project is provided as a sample implementation. Please review and adapt security configurations for your specific use case.

---

**⚠️ Security Notice**: This repository contains sample configurations. Never commit real secrets, private keys, or sensitive infrastructure state to version control. Always use secure secret management practices in production.
