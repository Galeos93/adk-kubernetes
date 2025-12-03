# Gmail Agent FastAPI Application

This application demonstrates a clean architecture implementation of a FastAPI server that uses Google ADK agents for Gmail operations, following hexagonal architecture principles.

## Quick Start

Get up and running quickly with Docker:

```bash
# 1. Set up Google Cloud (see Google Cloud Setup section below)
# 2. Configure environment variables in .env file
# 3. Run in development mode
make docker-run-dev

# 4. Test the API
curl http://localhost:8000/health
```

For detailed setup instructions, see [Google Cloud Setup](#google-cloud-setup) and [Development Setup](#development-setup).

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
- **ChatWithAgent Use Case**: Orchestrates agent conversations, manages session state, handles streaming responses
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

## Key Features

### ✅ **Clean Architecture**
- **Web Layer**: FastAPI handles HTTP/SSE concerns
- **Application Layer**: Use case orchestrates agent execution  
- **Infrastructure Layer**: Google ADK handles agent implementation

### ✅ **Framework Independence**
- Use case has no FastAPI dependencies
- Can be used with any web framework or CLI
- Easy to test in isolation

### ✅ **Server-Sent Events (SSE)**
- Real-time streaming responses from Gmail agent
- Follows same pattern as Google ADK web server
- Proper error handling and completion events

### ✅ **OAuth2 Integration**
- Secure authentication with Google OAuth2
- Callback handling for authorization codes
- In-memory or Redis-based OAuth state management

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

## External Application Integration Tools

### Gmail Access Configuration

To access Gmail (a Google application), configure the ApplicationIntegrationToolset with the following required roles:

- `roles/integrations.integrationEditor`
- `roles/connectors.invoker`
- `roles/connectors.viewer`
- `roles/secretmanager.secretAccessor`

These roles can be assigned to:
- The user executing the application (for local development)
- A service account (for production deployment).

## Integration Connectors Implementation

Integration Connectors provide a standardized interface for connecting to various data sources.
To access Gmail data, follow the official configuration guide:

[Gmail Connector Configuration Guide](https://cloud.google.com/integration-connectors/docs/connectors/gsc_gmail/configure?hl=es)

### Service Account Setup

The implementation requires creating a service account with roles mentioned on section [Gmail Access Configuration](#gmail-access-configuration).

Additionally, assign the `roles/connectors.admin` role to the person creating the connector.

### Authentication Configuration

**Important:** Enable "Authentication Override" to allow for delegated authorization.

When your service account or personal credentials have authorization to access the Gmail account,
the agent will inherit access to Gmail. Specifically, it will have access to the actions defined
during connector creation (e.g., reading emails).

## Development Setup

### 1. Set up configuration

You need to set up the environment variables and configuration files, specially for local development. Regarding the environment variables, you will need to create a `.env` file in the root directory with the following content:

GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
GOOGLE_GENAI_USE_VERTEXAI
GEMINI_API_KEY
SQL_URI
FASTAPI_HOST
FASTAPI_PORT
FASTAPI_LOG_LEVEL
FASTAPI_WORKERS
OAUTH_REDIRECT_URI
GOOGLE_APP_CLIENT_ID
GOOGLE_APP_CLIENT_SECRET
REDIS_URL

### 2. Start docker in development mode

Next, you can start the application using docker. If you set-up the google cloud correctly, you will have some user credentials that will be used by the application.


```bash
make docker-run-dev
```

### 3. Test the API

To test the API, you can make use fo the postman collection provided in the `postman-collection.json` file. Bear in mind that you need to create a user session first using the `/create_session` endpoint, before calling the `/run_sse` endpoint.

## Development

This section is for developers who want to contribute to the codebase.

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- Docker for containerized development
- Google Cloud SDK

### Setup

```bash
# Install production dependencies
make install

# Install development dependencies (includes testing tools)
make install-dev
```

### Local Development

```bash
# Install dependencies
poetry install

# Run linting
make lint

# Format code
make format

# Run all quality checks (lint + test)
make quality

# Run tests
make test

# Run specific test types
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-e2e         # End-to-end tests only

# Clean up generated files
make clean

# Start development server (if available)
python main.py
```

### Testing Strategy

The application includes comprehensive tests following the testing pyramid:

#### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user journeys
- **Contract Tests**: Verify API contracts

#### Test Files

- `tests/conftest.py`: Test fixtures and configuration
- `tests/infrastructure/adapters/fastapi/test_fastapi.py`: Web layer tests
- `tests/infrastructure/adapters/fastapi/test_agent_endpoints.py`: API endpoint tests
- `tests/application/use_cases/test_google_agent_caller.py`: Use case tests

#### Running Tests

```bash
# Install test dependencies
poetry install

# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run tests with verbose output
poetry run pytest -vv

# Run specific test file
poetry run pytest tests/infrastructure/adapters/fastapi/test_fastapi.py

# Run tests in watch mode (requires pytest-watch)
make watch-test
```

### Code Quality

```bash
# Run linting checks (ruff + mypy)
make lint

# Format code with ruff
make format

# Run all quality checks at once
make quality

# Format and lint in one command
make check

# Run full CI pipeline (format, lint, test)
make ci
```

### Docker Development

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Run Docker container in development mode (with GCP credentials)
make docker-run-dev
```

### Poetry Commands

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

### Development Workflow

1. **Setup**: `make install-dev`
2. **Code**: Make your changes
3. **Quality**: `make check` (format + lint)
4. **Test**: `make test`
5. **Clean**: `make clean` when done

For faster development:
- Use `make watch-test` to run tests automatically on file changes
