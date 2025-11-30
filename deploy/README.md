# Deploy Folder

This folder contains the Kubernetes deployment configuration for the FastAPI Agent application using Helm, Helmfile, and SOPS for secret management.

## Overview

The deployment uses:
- **Helm**: Package manager for Kubernetes applications
- **Helmfile**: Declarative spec for deploying Helm charts
- **SOPS**: Encrypts sensitive data in YAML files

## Structure

```
deploy/
├── .sops.yaml              # SOPS configuration for encryption
├── helmfile.yaml           # Helmfile configuration
├── secrets.yaml            # Encrypted secrets (SOPS)
├── key.txt                 # AGE private key for decryption (KEEP SECURE!)
├── Makefile                # Deployment shortcuts
├── charts/fastapi_agent/   # Helm chart for the FastAPI agent
│   ├── Chart.yaml
│   └── templates/
│       ├── agent-deployment.yaml
│       ├── agent-service.yaml
│       ├── redis.yaml
│       └── secret.yaml
└── fastapi_agent/
    └── values.yaml.gotmpl  # Helm values template
```

## Prerequisites

1. **Kubernetes Cluster**: Access to a Kubernetes cluster (EKS, GKE, etc.)
2. **Helm**: Install Helm 3.x
3. **Helmfile**: Install Helmfile
4. **SOPS**: Install SOPS with AGE support
5. **AGE**: Install AGE encryption tool

## Security Notes

### 🚨 Critical Security Considerations

- **AGE Private Key**: The `key.txt` file contains your AGE private key. **NEVER commit this file to version control**. It allows decryption of all secrets.
- **Encrypted Secrets**: `secrets.yaml` contains encrypted sensitive data (API keys, database credentials, etc.)
- **Production Keys**: In production, use secure key management (AWS KMS, GCP KMS, etc.) instead of local AGE keys.

### Secret Management Best Practices

1. **Never commit `key.txt`** to git
2. Use different keys for different environments
3. Rotate keys regularly
4. Store keys in secure vaults (HashiCorp Vault, AWS Secrets Manager, etc.)
5. Use `.gitignore` to exclude sensitive files

## Deployment

### 1. Decrypt Secrets (Development Only)

For local development, you may need to decrypt secrets:

```bash
sops --decrypt secrets.yaml > secrets_decrypted.yaml
```

**⚠️ WARNING**: Never commit decrypted secrets!

### 2. Deploy Application

```bash
make deploy
# or
helmfile apply
```

### 3. Check Status

```bash
kubectl get pods
kubectl get services
```

### 4. Destroy Deployment

```bash
make destroy
# or
helmfile destroy
```

## Configuration

### Environment Variables

The application is configured via environment variables injected as Kubernetes secrets:

- `GEMINI_API_KEY`: Google Gemini API key
- `GOOGLE_APP_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_APP_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_APP_SA`: Google Service Account JSON
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `REDIS_URL`: Redis connection URL

### Database Configuration

- Host: `db.agent-playground.online`
- Port: `5432`
- Database: `fastapi_agent_db`

### OAuth Configuration

- Redirect URI: `https://agent-playground.online/oauth/callback`

## Troubleshooting

### Common Issues

1. **SOPS Decryption Fails**
   - Ensure `key.txt` exists and contains the correct AGE private key
   - Check `.sops.yaml` configuration

2. **Helm Deployment Fails**
   - Verify Kubernetes cluster access: `kubectl cluster-info`
   - Check Helm version: `helm version`

3. **Secrets Not Available**
   - Ensure `secrets.yaml` is properly encrypted
   - Check that AGE key matches the one in `.sops.yaml`

### Logs

```bash
# Application logs
kubectl logs -l app=agent-service

# Helm release status
helm list -n default
```

## Production Deployment

For production:

1. **Use KMS**: Configure SOPS to use cloud KMS (AWS KMS, GCP KMS) instead of AGE keys
2. **Separate Environments**: Create separate `secrets.yaml` files for each environment
3. **CI/CD Integration**: Integrate with your CI/CD pipeline for automated deployments
4. **RBAC**: Ensure proper Kubernetes RBAC permissions
5. **Network Security**: Configure network policies and security contexts

## Development

### Local Testing

For local development with minikube or kind:

1. Start local cluster
2. Update `values.yaml.gotmpl` with local configurations
3. Deploy using `helmfile apply`

### Adding New Secrets

1. Edit `secrets.yaml` (it will be encrypted automatically if you have SOPS configured)
2. Or use SOPS directly:

```bash
sops secrets.yaml
# Edit in your editor, save, and it will be re-encrypted
```

3. Update `values.yaml.gotmpl` and `secret.yaml` template if needed.