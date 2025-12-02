import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.auth import AuthConfig
from google.adk.auth.credential_service.base_credential_service import (
    BaseCredentialService,
)
from google.adk.events import Event
from google.adk.memory.base_memory_service import BaseMemoryService
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.runners import Runner
from google.adk.sessions.base_session_service import BaseSessionService
from google.genai import types

from application.interfaces.agent_caller import AgentCallerInterface
from domain.exceptions import SessionNotFoundError
from infrastructure.adapters.gcp.oauth_callback_handler import (
    InMemoryOAuthCallbackHandler,
)

logger = logging.getLogger(__name__)


# FIXME: Decide what to do with function calls.
def default_event_parser(event: Event) -> str:
    """Implement default event parser to convert Event to string."""
    if hasattr(event, "content") and event.content:
        if hasattr(event.content, "parts"):
            return " ".join(
                part.text
                for part in event.content.parts
                if hasattr(part, "text") and part.text is not None
            )
        elif hasattr(event.content, "text"):
            return event.content.text
    return str(event)


def default_event_filter(event: Event) -> bool:
    """Filter that allows all events that have text on any Part."""
    if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
        for part in event.content.parts:
            if hasattr(part, "text") and part.text is not None:
                return False
    return True


@dataclass
class AuthConfigHandler:
    """Handles AuthConfig updates with OAuth2 authorization codes.

    Parameters
    ----------
    auth_config : AuthConfig
        The authentication configuration to manage.
    oauth_handler : OAuthCallbackHandler | None
        Handler that stores OAuth2 authorization codes from callbacks.
    redirect_uri : str
        OAuth2 callback URI where auth provider will redirect.
    poll_interval : float
        Seconds to wait between polling attempts.
    """

    auth_config: AuthConfig
    oauth_handler: InMemoryOAuthCallbackHandler
    redirect_uri: str = "http://localhost:8001/callback"
    poll_interval: float = 2.0

    def set_auth_config(self, auth_config: dict):
        """Set the current auth_config to manage.

        Parameters
        ----------
        auth_config : dict
            The authentication configuration to manage.
        """
        self.auth_config = AuthConfig.model_validate(auth_config)

    async def wait_for_user_authentication(self, timeout: int = 300) -> AuthConfig:
        """Wait for user to complete authentication and update auth_config.

        Parameters
        ----------
        timeout : int, optional
            Maximum time to wait in seconds, by default 300.

        Returns
        -------
        AuthConfig
            Updated auth_config with auth_response_uri set.
        """
        state = self.auth_config.exchanged_auth_credential.oauth2.state

        if not state:
            raise ValueError("State not found in auth_config")

        logger.info(f"Waiting for authentication with state: {state}")

        elapsed = 0.0
        while elapsed < timeout:
            code = self.oauth_handler.consume_code(state)
            if code:
                logger.info(f"Authentication code received for state: {state}")
                logger.debug(f"Authorization code: {code}")
                auth_response_uri = f"{self.redirect_uri}?code={code}&state={state}"

                self.auth_config.exchanged_auth_credential.oauth2.auth_response_uri = (
                    auth_response_uri
                )
                self.auth_config.exchanged_auth_credential.oauth2.redirect_uri = (
                    self.redirect_uri
                )
                return self.auth_config

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(
            f"Authentication timeout after {timeout}s for state: {state}"
        )


@dataclass
class AuthInterceptor:
    """Intercepts authentication events and manages OAuth2 flow.

    Parameters
    ----------
    auth_config_handler : AuthConfigHandler | None
        Handler that manages AuthConfig and waits for OAuth2 codes.
    """

    auth_config_handler: AuthConfigHandler | None = None
    agent_name: str | None = None

    @staticmethod
    def is_auth_event(event: Event) -> bool:
        """Check if event requires authentication.

        Parameters
        ----------
        event : Event
            The event to check.

        Returns
        -------
        bool
            True if event requires authentication.
        """
        return AuthInterceptor.get_auth_request_function_call(event) is not None

    @staticmethod
    def get_auth_request_function_call(event: Event) -> types.FunctionCall | None:
        """Extract auth request function call from event.

        Parameters
        ----------
        event : Event
            The event to check.

        Returns
        -------
        types.FunctionCall | None
            FunctionCall if event contains auth request, None otherwise.
        """
        if not event.content or not event.content.parts:
            return None

        for part in event.content.parts:
            if (
                part
                and part.function_call
                and part.function_call.name == "adk_request_credential"
                and event.long_running_tool_ids
                and part.function_call.id in event.long_running_tool_ids
            ):
                return part.function_call

        return None

    def ask_user_for_authentication(self) -> Event:
        """Build authentication request event with OAuth2 URL.

        Parameters
        ----------
        auth_config : AuthConfig
            The auth config containing the auth URI and state.

        Returns
        -------
        Event
            Event containing AUTH_REQUIRED:{url}:{state}.
        """
        auth_config = self.auth_config_handler.auth_config
        base_auth_uri = auth_config.exchanged_auth_credential.oauth2.auth_uri
        state = auth_config.exchanged_auth_credential.oauth2.state

        redirect_uri = self.auth_config_handler.redirect_uri

        if not base_auth_uri:
            raise ValueError("Auth URI not found in auth_config")

        if not state:
            raise ValueError("State not found in auth_config")

        auth_request_uri = base_auth_uri + f"&redirect_uri={redirect_uri}"

        return Event(
            author=self.agent_name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"AUTH_REQUIRED: {auth_request_uri}")],
            ),
        )

    def create_event_with_code_credentials(
        self, auth_request_function_call_id: str, auth_config: AuthConfig
    ) -> Event:
        """Create event with authentication credentials response.

        Parameters
        ----------
        auth_request_function_call_id : str
            ID of the original auth request function call.
        auth_config : AuthConfig
            Updated auth config with credentials.

        Returns
        -------
        Event
            Event containing the function response with credentials.
        """
        auth_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        id=auth_request_function_call_id,
                        name="adk_request_credential",
                        response=auth_config.model_dump(),
                    )
                )
            ],
        )
        return Event(author=self.agent_name, content=auth_content)

    async def intercept_auth_event(self, event: Event) -> AsyncGenerator[Event, None]:
        """Intercept authentication event and handle OAuth2 flow.

        Parameters
        ----------
        event : Event
            Event that may contain auth request.

        Yields
        ------
        Event
            Auth request event, then auth response event.
        """
        if not self.is_auth_event(event):
            raise ValueError("Event does not contain an auth request")

        auth_request_function_call = self.get_auth_request_function_call(event)

        if not (function_call_id := auth_request_function_call.id):
            raise ValueError(
                f"Cannot get function call id from: {auth_request_function_call}"
            )

        if not auth_request_function_call.args or not (
            auth_config := auth_request_function_call.args.get("authConfig")
        ):
            raise ValueError(
                f"Cannot get auth config from: {auth_request_function_call}"
            )

        if isinstance(auth_config, dict):
            self.auth_config_handler.set_auth_config(auth_config)
        else:
            raise ValueError(f"authConfig is not a dict: {type(auth_config)}")

        yield self.ask_user_for_authentication()

        updated_auth_config = (
            await self.auth_config_handler.wait_for_user_authentication()
        )

        response_event = self.create_event_with_code_credentials(
            auth_request_function_call_id=function_call_id,
            auth_config=updated_auth_config,
        )
        yield response_event


@dataclass
class AgentCallerGoogle(AgentCallerInterface):
    """Google ADK implementation of AgentCallerInterface.

    This use case encapsulates the Google ADK agent execution logic
    following the same patterns as the adk_web_server.py file.
    """

    agent: Agent
    auth_interceptor: AuthInterceptor
    app_name: str
    session_service: BaseSessionService
    event_parser: Callable[[Event], str] = default_event_parser
    event_filter: Callable[[Event], bool] = default_event_filter
    artifact_service: BaseArtifactService | None = None
    memory_service: BaseMemoryService | None = None
    credential_service: BaseCredentialService | None = None
    plugins: list[BasePlugin] | None = None

    def __post_init__(self):
        """Initialize the Google ADK Runner after dataclass initialization."""
        # Create the App wrapper (following adk_web_server pattern)
        self.agentic_app = App(
            name=self.app_name,
            root_agent=self.agent,
            plugins=self.plugins or [],
        )

        # Create the Runner (core Google ADK execution engine)
        self.runner = Runner(
            app=self.agentic_app,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
            memory_service=self.memory_service,
            credential_service=self.credential_service,
        )

    def _is_event_auth_response(self, event: Event) -> bool:
        """Check if event is an auth response event.

        Parameters
        ----------
        event : Event
            The event to check.

        Returns
        -------
        bool
            True if event is an auth response event.
        """
        return (
            event.content is not None
            and event.content.parts is not None
            and any(
                part.function_response is not None
                and part.function_response.name == "adk_request_credential"
                for part in event.content.parts
            )
        )

    async def check_session_exists(self, session_id: str, user_id: str) -> bool:
        """Check if a session exists for the given session_id and user_id.

        Parameters
        ----------
        session_id : str
            The ID of the session to check.
        user_id : str
            The ID of the user associated with the session.

        Returns
        -------
        bool
            True if the session exists, False otherwise.
        """
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                session_id=session_id,
                user_id=user_id,
            )
            return session is not None
        except ValueError as e:
            logger.error(f"Error checking session existence: {e}")
            return False

    async def call_agent_async(
        self,
        message: str,
        session_id: str,
        user_id: str,
    ) -> AsyncGenerator[str, None]:
        """Call the Google ADK agent and yield string responses.

        This method follows the same execution pattern as the adk_web_server
        but converts the Event objects to strings for the domain interface.
        """
        new_message = types.Content(parts=[types.Part(text=message)])

        if not await self.check_session_exists(session_id, user_id):
            raise SessionNotFoundError(session_id)

        credentials_needed = False
        first_call = True

        while credentials_needed or first_call:
            first_call = False
            credentials_needed = False

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                if self.auth_interceptor.is_auth_event(event):
                    credentials_needed = True

                    async for auth_event in self.auth_interceptor.intercept_auth_event(
                        event
                    ):
                        if self._is_event_auth_response(auth_event):
                            new_message = auth_event.content
                        else:
                            if not self.event_filter(auth_event):
                                yield self.event_parser(auth_event)
                    break
                else:
                    if not self.event_filter(event):
                        yield self.event_parser(event)
