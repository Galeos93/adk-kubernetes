# Gmail Agent FastAPI Application

This application demonstrates a clean architecture implementation of a FastAPI server that uses Google ADK agents for Gmail operations, following hexagonal architecture principles. After setting it up, you will be able to interact with an agent to access your (or others') Gmail account and perform operations like reading emails securely using OAuth2 authentication.

## Quick Start

Get up and running quickly with Docker:

```bash
# 1. Set up Google Cloud (see Google Cloud Setup section below)

# 2. Create .env file with required environment variables
cat > .env << 'EOF'
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
GEMINI_API_KEY=your-api-key
SQL_URI=sqlite:///./session_db.sqlite
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8080
FASTAPI_LOG_LEVEL=info
FASTAPI_WORKERS=1
OAUTH_REDIRECT_URI=http://localhost:8080/oauth/callback
GOOGLE_APP_CLIENT_ID=your-client-id
GOOGLE_APP_CLIENT_SECRET=your-client-secret
REDIS_URL=redis://redis:6379
EOF

# 3. Run in development mode
make docker-run-dev

# 4. Test the API
curl http://localhost:8080/health
```

For detailed setup instructions, see [Google Cloud Setup](#google-cloud-setup) and [Running the Application Locally](#️-running-the-application-locally).

## ▶️ Running the Application Locally

This section guides you through running the application on your local machine using Docker.

### Prerequisites

- Docker installed on your system
- Google Cloud account with proper setup (see [Google Cloud Setup](#google-cloud-setup))
- `.env` file configured with required environment variables

### Environment Configuration

Create a `.env` file in the root directory with the following variables:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
GEMINI_API_KEY=your-api-key

# Database
SQL_URI=sqlite:///./session_db.sqlite

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8080
FASTAPI_LOG_LEVEL=info
FASTAPI_WORKERS=1

# OAuth2
OAUTH_REDIRECT_URI=http://localhost:8080/oauth/callback
GOOGLE_APP_CLIENT_ID=your-client-id
GOOGLE_APP_CLIENT_SECRET=your-client-secret

# Redis (optional for development)
REDIS_URL=redis://redis:6379
```

### Running with Docker

```bash
# Build the Docker image
make docker-build

# Run in development mode (with GCP credentials mounted)
make docker-run-dev

# The application will be available at http://localhost:8080
```

### Testing the API

Once the application is running, you can test it using the provided Postman collection:

1. Import `postman-collection.json` and `postman-environment.json` into Postman
2. Create a session first: `POST /create_session`
3. Test the agent: `POST /run_sse` with the session ID

Or use curl:

```bash
# Health check
curl http://localhost:8080/health

# View API documentation
open http://localhost:8080/docs
```

## 🧑‍💻 Development Guide

This section is for developers who want to contribute to the codebase, add new features, or modify existing functionality.

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- Docker for containerized development
- Google Cloud SDK

### Initial Setup

```bash
# Install production dependencies
make install

# Install development dependencies (includes testing tools)
make install-dev

# Or install directly with Poetry
poetry install
```

### Development Workflow

1. **Setup**: `make install-dev`
2. **Code**: Make your changes
3. **Quality**: `make check` (format + lint)
4. **Test**: `make test`
5. **Clean**: `make clean` when done

### Code Quality & Formatting

```bash
# Format code with ruff
make format

# Run linting checks (ruff + mypy)
make lint

# Format and lint in one command
make check

# Run all quality checks at once (lint + test)
make quality

# Run full CI pipeline (format, lint, test)
make ci
```

### Dependency Management

```bash
# Activate poetry shell
make poetry-shell

# Show installed packages
make poetry-show

# Update dependencies
make poetry-update

# Generate/update poetry.lock
make poetry-lock

# Export requirements.txt
make poetry-export
```

### Local Development Server

```bash
# Run the application directly (without Docker)
python main.py

# The application will be available at http://localhost:8080
```

### Cleanup

```bash
# Clean up generated files and caches
make clean
```

## 🧪 Testing

The application includes comprehensive tests following the testing pyramid:

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user journeys
- **Contract Tests**: Verify API contracts

### Test Files

- `tests/conftest.py`: Test fixtures and configuration
- `tests/infrastructure/adapters/fastapi/test_fastapi.py`: Web layer tests
- `tests/infrastructure/adapters/fastapi/test_agent_endpoints.py`: API endpoint tests
- `tests/application/use_cases/test_google_agent_caller.py`: Use case tests

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-e2e         # End-to-end tests only

# Run tests with verbose output
poetry run pytest -vv

# Run specific test file
poetry run pytest tests/infrastructure/adapters/fastapi/test_fastapi.py

# Run tests in watch mode (auto-run on file changes)
make watch-test
```

## 🐳 Docker Guide

This section covers building, running, and pushing Docker images for the application.

### Building Docker Images

```bash
# Build the Docker image
make docker-build

# This runs: docker build -f docker/Dockerfile -t fastapi-agent:latest .
```

### Running Docker Containers

```bash
# Run in production mode
make docker-run

# Run in development mode (with GCP credentials mounted)
make docker-run-dev
```

### Development vs Production Mode

**Development Mode (`make docker-run-dev`):**
- Mounts Google Cloud credentials from `~/.config/gcloud/`
- Uses local `.env` file for configuration
- Exposes port 8080
- Runs as root for easier debugging

**Production Mode (`make docker-run`):**
- Uses environment variables directly
- Runs as non-root user for security
- Optimized for production deployment

### Pushing Images to Registry

```bash
# Tag the image for your registry
docker tag fastapi-agent:latest <registry>/<project>/fastapi-agent:latest
docker tag fastapi-agent:latest <registry>/<project>/fastapi-agent:v1.0.0

# Push to registry
docker push <registry>/<project>/fastapi-agent:latest
docker push <registry>/<project>/fastapi-agent:v1.0.0
```

**Example for Google Container Registry:**

```bash
# Tag for GCR
docker tag fastapi-agent:latest gcr.io/your-project-id/fastapi-agent:latest

# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Push to GCR
docker push gcr.io/your-project-id/fastapi-agent:latest
```

**Example for AWS ECR:**

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Tag for ECR
docker tag fastapi-agent:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/fastapi-agent:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/fastapi-agent:latest
```

## Architecture Overview

The application follows **Clean Architecture** (Hexagonal Architecture) with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DOMAIN LAYER                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐                   │
│  │   Entities          │    │  Interfaces         │                   │
│  │                     │    │                     │                   │
│  │ • Session           │    │ • SessionRepository │                   │
│  │ • Request           │    │   Interface         │                   │
│  │                     │    │                     │                   │
│  │                     │    │                     │                   │
│  └─────────────────────┘    └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                              │
│  ┌─────────────────────┐    ┌─────────────────────┐                   │
│  │ Application         │    │   Use Cases         │                   │
│  │ Interfaces          │    │                     │                   │
│  │                     │    │ • ChatWithAgent     │                   │
│  │ • AgentCaller       │    │ • SessionRegister   │                   │
│  │   Interface         │    │                     │                   │
│  │                     │    │                     │                   │
│  └─────────────────────┘    └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE & PRESENTATION                       │
│  ┌─────────────────────┐    ┌─────────────────────┐                   │
│  │   FastAPI REST API  │    │   GCP Services      │                   │
│  │                     │    │                     │                   │
│  │ • /health           │    │ • AgentCallerGoogle │                   │
│  │ • /run_sse          │    │ • SessionRepository │                   │
│  │ • /create_session   │    │ • OAuth2 Handler    │                   │
│  │                     │    │                     │                   │
│  └─────────────────────┘    └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Components

**🎯 Domain Layer**
- **Session Entity**: Represents a user session
- **Request Entity**: Represents an agent request
- **SessionRepository Interface**: Contract for session persistence operations (save, find, update, delete)

**🎯 Application Layer**
- **AgentCaller Interface**: Contract defining how to call external agents
- **ChatWithAgent Use Case**: Orchestrates agent conversations, manages session state,handles streaming responses
- **SessionRegister Use Case**: Creates new sessions, validates session data, persists session information

**🎯 Infrastructure & Presentation Layer**
- **FastAPI REST API**: HTTP endpoints for health checks, session creation, and SSE streaming
- **AgentCallerGoogle**: Google ADK implementation that calls Gmail agents with OAuth2 authentication
- **SessionRepositoryGoogleImpl**: Database implementation for session persistence using Google ADK session service

### Key Benefits

✅ **Testability**: Each layer can be tested in isolation
✅ **Flexibility**: Swap implementations (SQLite ↔ PostgreSQL, FastAPI ↔ CLI)
✅ **Maintainability**: Clear boundaries prevent coupling
✅ **Business Focus**: Domain logic protected from technical changes

### Key Features

#### ✅ **Clean Architecture**
- **Web Layer**: FastAPI handles HTTP/SSE concerns
- **Application Layer**: Use case orchestrates agent execution  
- **Infrastructure Layer**: Google ADK handles agent implementation

#### ✅ **Framework Independence**
- Use case has no FastAPI dependencies
- Can be used with any web framework or CLI
- Easy to test in isolation

#### ✅ **Server-Sent Events (SSE)**
- Real-time streaming responses from Gmail agent
- Follows same pattern as Google ADK web server
- Proper error handling and completion events

#### ✅ **OAuth2 Integration**
- Secure authentication with Google OAuth2
- Callback handling for authorization codes
- In-memory or Redis-based OAuth state management

## Files Structure

```
app/
├── main.py                 # Application startup script
├── config.yaml             # Application configuration
├── pyproject.toml          # Python dependencies and project config
├── Makefile                # Development and build commands
├── postman-collection.json # API testing collection
├── postman-environment.json# Postman environment variables
├── .env                    # Environment variables (not committed)
├── docker/
│   └── Dockerfile          # Container build configuration
├── domain/
│   ├── entities/
│   │   ├── request.py      # Domain entities
│   │   └── session.py
│   ├── interfaces/
│   │   └── session_repository.py  # Domain contracts
│   └── exceptions.py       # Domain exceptions
├── application/
│   ├── interfaces/
│   │   └── agent_caller.py # Application interfaces
│   └── use_cases/
│       ├── chat_with_agent.py    # Business logic
│       └── session_register.py
├── infrastructure/
│   └── adapters/
│       ├── fastapi/
│       │   ├── fastapi.py        # Web framework adapters
│       │   ├── health_api.py
│       │   ├── run_agent_sse_api.py
│       │   ├── create_session_api.py
│       │   └── models.py
│       └── gcp/
│           ├── google_agent_caller/
│           │   ├── google_agent_caller.py  # Google ADK integration
│           │   └── gmail_agent/
│           │       └── agent.py
│           ├── oauth_callback_handler.py   # OAuth2 handling
│           ├── oauth_callback_app.py
│           └── session_repository.py       # Data persistence
└── tests/
    ├── conftest.py         # Test configuration
    ├── config_test.yaml
    └── infrastructure/
        └── adapters/
            └── fastapi/
                ├── test_agent_endpoints.py
                └── test_fastapi.py
```

## Google Cloud Setup

To run the application, you need to set up a Google Cloud project, allow integration with Gmail, and make use of Vertex AI (we will use gemini models).

### Project Creation

First, create a new Google Cloud project.

**Required roles:** `roles/resourcemanager.projectCreator`

### Google Cloud CLI Configuration

Configure the Google Cloud CLI with the following commands:

```bash
gcloud config set project project-id
gcloud auth application-default login
gcloud auth application-default set-quota-project project-id
```

### API Enablement

Enable the Vertex AI API for your project.

**Required roles:** `roles/serviceusage.serviceUsageAdmin`

### Vertex AI Permissions

Grant the necessary roles to access Vertex AI services.

**Required roles:** `Vertex AI User`

### Gmail Access Configuration

To access Gmail (a Google application), configure the ApplicationIntegrationToolset with the following required roles:

- `roles/integrations.integrationEditor`
- `roles/connectors.invoker`
- `roles/connectors.viewer`
- `roles/secretmanager.secretAccessor`

These roles can be assigned to:
- The user executing the application (for local development)
- A service account (for production deployment).

### Integration Connectors Implementation

Integration Connectors provide a standardized interface for connecting to various data sources.
To access Gmail data, follow the official configuration guide:

[Gmail Connector Configuration Guide](https://cloud.google.com/integration-connectors/docs/connectors/gsc_gmail/configure?hl=es)

#### Service Account Setup

The implementation requires creating a service account with roles mentioned on section [Gmail Access Configuration](#gmail-access-configuration).

Additionally, assign the `roles/connectors.admin` role to the person creating the connector.

#### Authentication Configuration

**Important:** Enable "Authentication Override" to allow for delegated authorization.

When your service account or personal credentials have authorization to access the Gmail account,
the agent will inherit access to Gmail. Specifically, it will have access to the actions defined
during connector creation (e.g., reading emails).

### OAuth2 Client Setup

To enable OAuth2 authentication for accessing Gmail, you need to set up an OAuth2 client in the Google Cloud Console. You can control what users can access by configuring the OAuth2 consent screen and specifying authorized redirect URIs. For the redirect URIs, you should include the endpoint that handles OAuth2 callbacks in your application, such as `https://yourdomain.com/oauth/callback` and `http://localhost:8080/oauth/callback` for local development.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the [Development Guide](#-development-guide)
4. Run tests and quality checks: `make ci`
5. Commit your changes: `git commit -m 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Update documentation for new features
- Add tests for new functionality
