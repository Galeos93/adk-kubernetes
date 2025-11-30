from typing import Any

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """Request model for running an agent - following ADK web server pattern."""

    app_name: str
    user_id: str
    session_id: str
    new_message: str  # Simplified to string instead of types.Content
    streaming: bool = False
    state_delta: dict[str, Any] | None = None
