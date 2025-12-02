"""Application interface for chat with agent use case."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from domain.entities.request import RunAgentRequest


class ChatWithAgentInterface(ABC):
    """Interface for the chat with agent use case.

    This interface defines the contract for executing agent conversations
    and handling the business logic around agent communication.
    """

    @abstractmethod
    async def execute(self, request: RunAgentRequest) -> AsyncGenerator[str, None]:
        """Execute a chat session with the agent.

        Parameters
        ----------
        request : RunAgentRequest
            The request containing chat parameters and message

        Yields
        ------
        str
            Stream of responses from the agent conversation
        """
        pass
