from dataclasses import dataclass

from application.interfaces.session_register import RegisterSessionInterface
from domain.entities.session import Session
from domain.interfaces.session_repository import SessionRepositoryInterface


@dataclass
class RegisterSessionUseCase(RegisterSessionInterface):
    """Use case for registering a session."""

    session_repository: SessionRepositoryInterface

    async def register_session(self, session: Session):
        """Register a new session."""
        return await self.session_repository.create_session(session)
