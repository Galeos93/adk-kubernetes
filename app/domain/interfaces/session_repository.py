import abc

from domain.entities.session import Session


class SessionRepositoryInterface(abc.ABC):
    """Interface for session repository implementations."""

    @abc.abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Create a new session.

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
        pass

