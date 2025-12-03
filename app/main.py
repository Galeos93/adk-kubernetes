"""Startup script for the FastAPI weather agent application.

This script shows how to properly initialize and run the FastAPI app
with the clean architecture setup.
"""

import logging
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from google.adk.sessions.database_session_service import DatabaseSessionService
from vyper import v

from application.use_cases.chat_with_agent import ChatWithAgentUseCase
from application.use_cases.session_register import RegisterSessionUseCase
from infrastructure.adapters.fastapi.create_session_api import CreateSessionAPIImpl
from infrastructure.adapters.fastapi.fastapi import AppBuilder
from infrastructure.adapters.fastapi.health_api import HealthAPI
from infrastructure.adapters.fastapi.run_agent_sse_api import RunAgentSSEAPI
from infrastructure.adapters.gcp.google_agent_caller.gmail_agent.agent import load_agent
from infrastructure.adapters.gcp.google_agent_caller.google_agent_caller import (
    AgentCallerGoogle,
    AuthConfigHandler,
    AuthInterceptor,
)
from infrastructure.adapters.gcp.oauth_callback_app import create_oauth_callback_app
from infrastructure.adapters.gcp.oauth_callback_handler import (
    InMemoryOAuthCallbackHandler,
    RedisOAuthCallbackHandler,
)
from infrastructure.adapters.gcp.session_repository import SessionRepositoryGoogleImpl

logger = logging.getLogger(__name__)


# Global OAuth handler that will be shared between main app and callback app
# This must be created at module level to be accessible by both sub-apps
def dispatch_oauth_handler():
    """Dispatch the appropriate OAuth handler based on configuration."""
    if v.get("redis.url") is None:
        logger.info("Using InMemoryOAuthCallbackHandler for OAuth2 callbacks")
        oauth_handler = InMemoryOAuthCallbackHandler()
    else:
        logger.info("Using RedisOAuthCallbackHandler for OAuth2 callbacks")
        oauth_handler = RedisOAuthCallbackHandler(ttl=300)

    return oauth_handler


def load_dotenv_config():
    """Load environment variables from .env file."""
    load_dotenv()


def load_vyper_config():
    """Load configuration files from paths."""
    logging.basicConfig(level=logging.INFO)
    logging.info("[Main] Loading vyper config")
    config_paths = [Path(".."), Path()]

    v.set_env_key_replacer(".", "_")

    v.set_config_type("yaml")
    v.set_config_name("config")

    for path in config_paths:
        v.add_config_path(path)
    try:
        v.read_in_config()  # Find and read the config file
    except Exception as e:
        logging.warning(
            "[Main] No configuration files found: %s",
            e,
        )

    v.automatic_env()
    logging.info(
        "[Main] Vyper config loaded: %s",
        v,
    )


def configure_app():
    """Configure the FastAPI app with all dependencies using clean architecture."""
    # Load the root agent
    root_agent = load_agent()

    # Create Google ADK services
    session_service = DatabaseSessionService(v.get("sql.uri"))
    memory_service = None  # Set to None for now
    artifact_service = None  # Set to None for now

    # Create OAuth2 authentication components
    # Use the global oauth_handler so it can be shared with the callback app
    oauth_handler = _oauth_handler
    fastapi_port = v.get("fastapi.port") or 8000
    redirect_uri = (
        v.get(
            "oauth.redirect_uri",
        )
        or f"http://localhost:{fastapi_port}/oauth/callback"
    )
    auth_config_handler = AuthConfigHandler(
        auth_config=None,  # Will be set dynamically during agent execution
        oauth_handler=oauth_handler,
        redirect_uri=redirect_uri,
    )
    auth_interceptor = AuthInterceptor(
        auth_config_handler=auth_config_handler,
        agent_name=root_agent.name,
    )

    # Create the agent caller adapter (Infrastructure Layer)
    agent_caller = AgentCallerGoogle(
        agent=root_agent,
        auth_interceptor=auth_interceptor,
        app_name="weather-time-app",
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )

    # Create the chat with agent use case (Application Layer)
    chat_use_case = ChatWithAgentUseCase(agent_caller=agent_caller)

    # Create a session registration use case
    session_repository = SessionRepositoryGoogleImpl(session_service=session_service)
    register_session_use_case = RegisterSessionUseCase(
        session_repository=session_repository
    )

    # Create infrastructure adapters
    health_api = HealthAPI()
    agent_api = RunAgentSSEAPI(chat_use_case=chat_use_case)
    create_session_api = CreateSessionAPIImpl(
        session_register=register_session_use_case
    )

    # Create FastAPI app using the infrastructure adapter
    app_builder = AppBuilder(
        health_api=health_api,
        agent_api=agent_api,
        create_session_api=create_session_api,
    )
    main_app = app_builder.create_app()

    # Mount OAuth callback app as a sub-application
    oauth_app, _ = create_oauth_callback_app(_oauth_handler)
    main_app.mount("/oauth", oauth_app)

    return main_app


# Create the app at module level for uvicorn reload
print("Loading configuration...")
load_dotenv_config()
load_vyper_config()
_oauth_handler = dispatch_oauth_handler()
app = configure_app()


def main():
    """Implement entry point for the application."""
    print("🚀 Starting Weather and Time Agent API...")
    print("   - Main API available at /")
    print("   - OAuth2 Callback available at /oauth/callback")

    fastapi_host = v.get("fastapi.host") or "0.0.0.0"
    fastapi_port = v.get("fastapi.port") or 8000
    fastapi_log_level = v.get("fastapi.log_level") or "info"
    fastapi_workers = v.get("fastapi.workers") or 1

    # Start the server using the module-level app
    uvicorn.run(
        "main:app",
        workers=int(fastapi_workers),
        host=fastapi_host,
        port=int(fastapi_port),
        log_level=fastapi_log_level,
        timeout_worker_healthcheck=60,
    )


if __name__ == "__main__":
    main()
