from __future__ import annotations

from pydantic import BaseModel, ConfigDict, alias_generators


class Session(BaseModel):
    """Represents a series of interactions between a user and agents.

    Notes
    -----
    This has been adapted from google.adk.sessions.session.Session

    """

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )
    """The pydantic model config."""

    id: str
    """The unique identifier of the session."""
    app_name: str
    """The name of the app."""
    user_id: str
