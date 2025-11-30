"""Domain interface for agent calling capability."""
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class AgentCallerInterface(ABC):
    """Domain interface for calling an agent.

    Notes
    -----
    This interface represents the core business capability of communicating
    with an AI agent. It belongs in the domain layer as it defines what
    the business needs without specifying how it's implemented.

    """

    @abstractmethod
    async def call_agent_async(
        self,
        message: str,
        session_id: str,
        user_id: str,
    ) -> AsyncGenerator[str, None]:
        """Call an agent with a message and stream responses.

        Parameters
        ----------
        message : str
            The message to send to the agent
        session_id : str
            Unique identifier for the conversation session
        user_id : str
            Unique identifier for the user

        Yields
        ------
        str
            Stream of responses from the agent
        """
        pass
