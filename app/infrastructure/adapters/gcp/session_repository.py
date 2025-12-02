from dataclasses import dataclass

from google.adk.sessions.base_session_service import BaseSessionService
from sqlalchemy.exc import IntegrityError

from domain.entities.session import Session
from domain.exceptions import SessionAlreadyExistsError
from domain.interfaces.session_repository import SessionRepositoryInterface


@dataclass
class SessionRepositoryGoogleImpl(SessionRepositoryInterface):
    """Google ADK implementation of the SessionRepositoryInterface."""

    session_service: BaseSessionService

    async def create_session(self, session: Session) -> Session:
        """Create a new session in the Google ADK session service.

        Parameters
        ----------
        session : Session
            The session to create.

        Returns
        -------
        Session
            The created session.

        Raises
        ------
        SessionAlreadyExistsError
            If a session with the same ID already exists.
        """
        try:
            return await self.session_service.create_session(
                app_name=session.app_name,
                user_id=session.user_id,
                session_id=session.id,
            )
        except IntegrityError as e:
            # Check if it's a unique constraint violation for the primary key
            if "sessions_pkey" in str(e.orig) or "duplicate key" in str(e.orig):
                raise SessionAlreadyExistsError(session.id) from e
            # Re-raise other integrity errors
            raise
