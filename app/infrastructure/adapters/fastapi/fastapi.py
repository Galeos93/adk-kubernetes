"""A FastAPI adapter for the weather and time agent."""

from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from infrastructure.adapters.fastapi.create_session_api import CreateSessionAPIBase
from infrastructure.adapters.fastapi.health_api import HealthAPIBase
from infrastructure.adapters.fastapi.run_agent_sse_api import RunAgentSSEAPIBase
from domain.exceptions import SessionAlreadyExistsError


@dataclass
class AppBuilder:
    # raise error if either api is None
    health_api: HealthAPIBase
    agent_api: RunAgentSSEAPIBase
    create_session_api: CreateSessionAPIBase

    def register_agent_routes(self, app: FastAPI):
        """Register agent-related routes."""
        app.post("/run_sse")(self.agent_api.run_agent_sse)

    def register_health_routes(self, app: FastAPI):
        """Register health and status routes."""
        app.get("/health")(self.health_api.health_check)

    def register_create_session_routes(self, app: FastAPI):
        """Register session creation routes."""
        app.post("/create_session")(self.create_session_api.create_session)

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI app with the given agent caller use case."""
        # Create the FastAPI instance
        app = FastAPI(title="Weather and Time Agent API")

        # Register exception handlers
        @app.exception_handler(SessionAlreadyExistsError)
        async def session_already_exists_handler(request: Request, exc: SessionAlreadyExistsError):
            return JSONResponse(
                status_code=409,
                content={"detail": str(exc), "session_id": exc.session_id}
            )

        # Register routes
        self.register_agent_routes(app)
        self.register_health_routes(app)
        self.register_create_session_routes(app)

        return app


class CredentialsRedirectionApp:
    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI app for credentials redirection."""
        app = FastAPI(title="Credentials Redirection API")

        @app.get("/redirect_credentials")
        async def redirect_credentials(code: str, state: str):
            """Handle redirection after user authenticates and provide credentials."""
            # Here you would process the code and state to obtain credentials
            # and then return them or store them as needed.
            return {"status": "ok", "code": code, "state": state}

        return app
