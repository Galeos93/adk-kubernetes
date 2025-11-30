from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.interfaces.session_register import RegisterSessionInterface
from domain.entities.session import Session


class CreateSessionAPIBase(ABC):
    """Abstract base class for session creation endpoints."""

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Create a new session endpoint."""
        pass


@dataclass
class CreateSessionAPIImpl(CreateSessionAPIBase):
    """Implementation of the CreateSessionAPIBase."""

    session_register: RegisterSessionInterface

    async def create_session(self, session: Session) -> Session:
        """Create a new session endpoint implementation."""
        return await self.session_register.register_session(session)
