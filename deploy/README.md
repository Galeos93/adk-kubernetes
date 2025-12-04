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

1. **Kubernetes Cluster**: Access to a Kubernetes cluster (EKS, GKE, etc.). You can use the infrastructure from the `infra/` folder.
2. **Helm**: Install Helm 3.x
3. **Helmfile**: Install Helmfile
4. **SOPS**: Install SOPS with AGE support
5. **AGE**: Install AGE encryption tool

## Deployment

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

- `GEMINI_API_KEY`: Google Gemini API key
- `GOOGLE_APP_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_APP_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_APP_SA`: Google Service Account JSON.
- `DB_USERNAME`: Database username used by the app
- `DB_PASSWORD`: Database password used by the app
- `REDIS_URL`: Redis connection URL

```bash
sops secrets.yaml
```

You can see more details about the permissions needed for the service account in the [app/README.md](../app/README.md) file.

### 2. Update values in `values.yaml.gotmpl`

You can modify the `values.yaml.gotmpl` file to set configuration values such as domain names, ports, and other application settings. Concretely, you may want to adjust:

- `OAUTH_REDIRECT_URI`: Update to match your domain (e.g., `https://your-domain.com/oauth/callback`)
- `database.host`: Update if your database host is different
- `database.port`: Update if your database port is different
- `database.name`: Update if your database name is different
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GOOGLE_CLOUD_LOCATION`: GCP location
- `GOOGLE_GENAI_USE_VERTEXAI`: Whether to use Vertex AI
- `FASTAPI_HOST`: FastAPI host
- `FASTAPI_PORT`: FastAPI port
- `FASTAPI_LOG_LEVEL`: FastAPI log level
- `FASTAPI_WORKERS`: Number of FastAPI workers

### 3. Deploy Application

```bash
make deploy
```

### 4. Check Status

```bash
kubectl get pods
kubectl get services
```

### 5. Destroy Deployment

```bash
make destroy
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

Or from unencrypted values in `values.yaml.gotmpl`:

- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GOOGLE_CLOUD_LOCATION`: GCP location
- `GOOGLE_GENAI_USE_VERTEXAI`: Whether to use Vertex AI
- `FASTAPI_HOST`: FastAPI host
- `FASTAPI_PORT`: FastAPI port
- `FASTAPI_LOG_LEVEL`: FastAPI log level
- `FASTAPI_WORKERS`: Number of FastAPI workers
- `OAUTH_REDIRECT_URI`: OAuth redirect URI
- `database.host`: Database host
- `database.port`: Database port
- `database.name`: Database name

The database host is set to a fixed DNS name `db.your-domain.com` created by the infrastructure in the `infra/` folder. You will also have to modify the oauth redirect
URI to match your domain (e.g., `https://your-domain.com/oauth/callback`).

### Database Configuration

- Host: `db.your-domain.com`
- Port: `5432`
- Database: `fastapi_agent_db`

### OAuth Configuration

- Redirect URI: `https://your-domain.com/oauth/callback`

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