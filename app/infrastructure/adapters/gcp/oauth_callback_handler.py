"""Minimal OAuth2 callback handler for authentication flow."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import redis
from fastapi import Request
from fastapi.responses import HTMLResponse
from vyper import v


class OAuthCallbackHandlerBase(ABC):
    """Abstract base class for OAuth2 callback handlers."""

    @abstractmethod
    async def handle_callback(self, request: Request) -> HTMLResponse:
        """Handle OAuth2 callback from authentication provider.

        Parameters
        ----------
        request : Request
            FastAPI request containing code and state parameters.

        Returns
        -------
        HTMLResponse
            Response to be sent back to the user.
        """
        pass

    @abstractmethod
    def get_code(self, state: str) -> str | None:
        """Retrieve authorization code for a given state.

        Parameters
        ----------
        state : str
            The state parameter to look up.

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.
        """
        pass

    @abstractmethod
    def consume_code(self, state: str) -> str | None:
        """Retrieve and remove authorization code (single use).

        Parameters
        ----------
        state : str
            The state parameter to look up.

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.
        """
        pass


@dataclass
class InMemoryOAuthCallbackHandler(OAuthCallbackHandlerBase):
    """Handles OAuth2 callbacks and stores authorization codes.

    Parameters
    ----------
    auth_codes : Dict[str, str]
        In-memory storage for authorization codes keyed by state.
    """

    auth_codes: dict[str, str] = field(default_factory=dict)

    async def handle_callback(self, request: Request) -> HTMLResponse:
        """Handle OAuth2 callback from authentication provider.

        Parameters
        ----------
        request : Request
            FastAPI request containing code and state parameters.

        Returns
        -------
        HTMLResponse
            Success page for user.
        """
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        if error:
            return HTMLResponse(
                content=f"""
                <html>
                    <body>
                        <h1>Authentication Failed</h1>
                        <p>Error: {error}</p>
                    </body>
                </html>
                """,
                status_code=400,
            )

        if not code or not state:
            return HTMLResponse(
                content="""
                <html>
                    <body>
                        <h1>Invalid Request</h1>
                        <p>Missing code or state parameter.</p>
                    </body>
                </html>
                """,
                status_code=400,
            )

        self.auth_codes[state] = code

        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can now close this window and return to the application.</p>
                    <script>window.close();</script>
                </body>
            </html>
            """
        )

    def get_code(self, state: str) -> str | None:
        """Retrieve authorization code for a given state.

        Parameters
        ----------
        state : str
            The state parameter to look up.

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.
        """
        return self.auth_codes.get(state)

    def consume_code(self, state: str) -> str | None:
        """Retrieve and remove authorization code (single use).

        Parameters
        ----------
        state : str
            The state parameter to look up.

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.
        """
        return self.auth_codes.pop(state, None)


@dataclass
class RedisOAuthCallbackHandler(OAuthCallbackHandlerBase):
    """Handles OAuth2 callbacks and stores authorization codes in Redis.

    Parameters
    ----------
    redis_client : Any
        Redis client instance for storing authorization codes.

    """

    ttl: int = 300  # Time to live for codes in seconds

    def __post_init__(self):
        self.redis_client = redis.Redis.from_url(v.get("redis.url"))

    async def handle_callback(self, request: Request) -> HTMLResponse:
        """Handle OAuth2 callback from authentication provider.

        Parameters
        ----------
        request : Request
            FastAPI request containing code and state parameters.

        Returns
        -------
        HTMLResponse
            Success page for user.
        """
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        if error:
            return HTMLResponse(
                content=f"""
                <html>
                    <body>
                        <h1>Authentication Failed</h1>
                        <p>Error: {error}</p>
                    </body>
                </html>
                """,
                status_code=400,
            )

        if not code or not state:
            return HTMLResponse(
                content="""
                <html>
                    <body>
                        <h1>Invalid Request</h1>
                        <p>Missing code or state parameter.</p>
                    </body>
                </html>
                """,
                status_code=400,
            )

        self.redis_client.set(state, code, ex=self.ttl)  # Set expiration time

        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can now close this window and return to the application.</p>
                    <script>window.close();</script>
                </body>
            </html>
            """
        )

    def get_code(self, state: str) -> str | None:
        """Retrieve authorization code for a given state.

        Parameters
        ----------
        state : str
            The state parameter to look up.

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.

        """
        code = self.redis_client.get(state)
        return code.decode("utf-8") if code else None

    def consume_code(self, state: str) -> str | None:
        """Retrieve and remove authorization code (single use).

        Parameters
        ----------
        state : str
            The state parameter

        Returns
        -------
        str | None
            Authorization code if found, None otherwise.
        """
        code = self.redis_client.get(state)
        if code:
            self.redis_client.delete(state)
            return code.decode("utf-8")
        return None
