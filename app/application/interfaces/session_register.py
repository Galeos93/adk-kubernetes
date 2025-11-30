import abc

from domain.entities.session import Session


class RegisterSessionInterface(abc.ABC):
    """Interface for session repository implementations."""

    @abc.abstractmethod
    async def register_session(self, session: Session) -> Session:
        """Register a new session."""
        pass
