# Gmail Agent FastAPI Application

This application demonstrates a clean architecture implementation of a FastAPI server that uses Google ADK agents for Gmail operations, following hexagonal architecture principles.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Use Case       │    │  Google ADK     │
│   (Web Layer)   │───▶│  (Application)   │───▶│ (Gmail Agent)   │
│                 │    │                  │    │                 │
│ • app.py        │    │ • AgentCaller    │    │ • Gmail Agent   │
│ • /run_sse      │    │   GoogleUseCase  │    │ • Runner        │
│ • SSE streaming │    │                  │    │ • Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Files Structure

- **`app.py`** - FastAPI application with SSE streaming endpoint
- **`agent_runner_use_case_vanilla.py`** - Clean use case implementation  
- **`config.py`** - Dependency injection and configuration
- **`main.py`** - Application startup script
- **`client_example.py`** - Example client for testing SSE

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

## Usage

### 1. Start the Development Server

```bash
python main.py
```

This starts the server with mock services at `http://localhost:8000`

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs
```

### 3. Test SSE Streaming

```bash
python client_example.py
```

Or use curl:
```bash
curl -X POST http://localhost:8000/run_sse \\
  -H "Content-Type: application/json" \\
  -d '{
    "app_name": "weather-time-app",
    "user_id": "test_user", 
    "session_id": "test_session",
    "new_message": "What'\''s the weather like?"
  }'
```

## API Endpoints

### `POST /run_sse`
Stream agent responses via Server-Sent Events.

**Request:**
```json
{
  "app_name": "weather-time-app",
  "user_id": "string",
  "session_id": "string", 
  "new_message": "string",
  "streaming": true
}
```

**Response:** SSE stream with events:
```json
{"type": "agent_response", "content": "...", "session_id": "...", "user_id": "..."}
{"type": "completion", "session_id": "...", "user_id": "..."}
```

### `GET /health`
Health check endpoint.

### `GET /`
Root endpoint with API information.

## Configuration

### Development (Mock Services)
```python
from config import configure_app_for_development
configure_app_for_development()
```

### Production (Real Services)
```python
from config import configure_app_for_production
configure_app_for_production(
    session_service=your_session_service,
    artifact_service=your_artifact_service,
    memory_service=your_memory_service,
    credential_service=your_credential_service,
)
```

## Benefits of This Architecture

1. **Separation of Concerns**: Web framework logic separate from business logic
2. **Testability**: Easy to unit test use cases without FastAPI
3. **Flexibility**: Can swap web frameworks or use in CLI applications
4. **Google ADK Integration**: Proper use of Google ADK patterns without coupling
5. **SSE Streaming**: Real-time responses following web server patterns

## Testing

The architecture makes testing easy:

```python
# Test use case independently
agent_caller = AgentCallerGoogleUseCase(...)
async for response in agent_caller.call_agent_async("test", "session", "user"):
    assert response is not None

# Test FastAPI with mocked use case
# Mock the agent_caller and test endpoints
```

## Security

This application handles sensitive data including API keys and OAuth credentials. Follow these security best practices:

### Environment Variables
- Never commit `.env` files containing real secrets to version control
- Use environment variables for all sensitive configuration
- The `.env` file is already ignored in `.gitignore`

### API Keys and Secrets
- Store API keys (e.g., `GEMINI_API_KEY`, `GOOGLE_APP_CLIENT_SECRET`) securely
- Use secret management services in production (e.g., AWS Secrets Manager, Google Secret Manager)
- Rotate keys regularly

### OAuth2 Security
- OAuth callbacks are handled securely with state validation
- Use HTTPS in production to protect OAuth flows
- Store OAuth state in Redis for production scalability

### Database Security
- SQLite is used for development; use PostgreSQL or similar in production
- The `session_db.sqlite` file contains session data and should not be committed
- Ensure database files are properly secured and backed up

## Production Deployment

For production, implement real Google ADK services:

1. **Session Service**: Real database-backed session management
2. **Artifact Service**: File/blob storage for artifacts  
3. **Memory Service**: Persistent memory storage
4. **Credential Service**: Secure credential management
5. **Gmail Integration**: Configure Gmail API access and OAuth2 flows

Then configure with `configure_app_for_production()` and deploy with a production ASGI server like Gunicorn.