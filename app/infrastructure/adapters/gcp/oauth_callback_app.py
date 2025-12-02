"""Minimal FastAPI app for handling OAuth2 callbacks."""

import os

import uvicorn
from fastapi import FastAPI

from infrastructure.adapters.gcp.oauth_callback_handler import (
    InMemoryOAuthCallbackHandler,
)


def create_oauth_callback_app(
    oauth_handler: InMemoryOAuthCallbackHandler | None = None,
) -> tuple[FastAPI, InMemoryOAuthCallbackHandler]:
    """Create a minimal FastAPI app for OAuth2 callbacks.

    Parameters
    ----------
    oauth_handler : OAuthCallbackHandler | None
        Shared OAuth handler instance. If None, creates a new one.

    Returns
    -------
    tuple[FastAPI, OAuthCallbackHandler]
        Configured FastAPI application and the oauth_handler instance.
    """
    app = FastAPI(title="OAuth2 Callback Handler")

    if oauth_handler is None:
        oauth_handler = InMemoryOAuthCallbackHandler()

    app.get("/callback")(oauth_handler.handle_callback)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app, oauth_handler


def main():
    """Run the OAuth callback server."""
    app, _ = create_oauth_callback_app()

    uvicorn.run(
        app,
        host=os.getenv("OAUTH_HOST", "0.0.0.0"),
        port=int(os.getenv("OAUTH_PORT", 8001)),
        log_level=os.getenv("OAUTH_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
