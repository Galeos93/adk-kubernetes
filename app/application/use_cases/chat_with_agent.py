"""Chat with agent use case implementation."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from application.interfaces.agent_caller import AgentCallerInterface
from application.interfaces.chat_with_agent import ChatWithAgentInterface
from domain.entities.request import RunAgentRequest


@dataclass
class ChatWithAgentUseCase(ChatWithAgentInterface):
    """Application use case for chatting with an agent.

    This use case orchestrates the business logic around agent communication,
    including validation, session management, and response processing.
    It acts as the application layer that coordinates domain services.
    """

    agent_caller: AgentCallerInterface

    async def execute(self, request: RunAgentRequest) -> AsyncGenerator[str, None]:
        """Execute a chat session with the agent.

        This method orchestrates the agent conversation by:
        1. Validating the request
        2. Delegating to the domain agent caller
        3. Processing and formatting responses
        4. Handling any business logic around the conversation

        Parameters
        ----------
        request : RunAgentRequest
            The request containing chat parameters and message

        Yields
        ------
        str
            Stream of responses from the agent conversation

        Raises
        ------
        ValueError
            If the request is invalid or missing required fields
        """
        # Validate the request
        self._validate_request(request)

        # Delegate to the domain agent caller
        async for response in self.agent_caller.call_agent_async(
            message=request.new_message,
            session_id=request.session_id,
            user_id=request.user_id,
        ):
            # Here we could add additional business logic:
            # - Response filtering
            # - Content moderation
            # - Response enhancement
            # - Logging/analytics
            yield response

    def _validate_request(self, request: RunAgentRequest) -> None:
        """Validate the chat request.

        Parameters
        ----------
        request : RunAgentRequest
            The request to validate

        Raises
        ------
        ValueError
            If the request is invalid
        """
        if not request.new_message or not request.new_message.strip():
            raise ValueError("Message cannot be empty")

        if not request.session_id or not request.session_id.strip():
            raise ValueError("Session ID is required")

        if not request.user_id or not request.user_id.strip():
            raise ValueError("User ID is required")

        if not request.app_name or not request.app_name.strip():
            raise ValueError("App name is required")
