"""Domain-level exceptions."""


class DomainException(Exception):
    """Base exception for domain-level errors."""

    pass


class SessionAlreadyExistsError(DomainException):
    """Raised when attempting to create a session that already exists.

    Parameters
    ----------
    session_id : str
        The ID of the session that already exists.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session with ID '{session_id}' already exists")


class SessionNotFoundError(DomainException):
    """Raised when a session is not found.

    Parameters
    ----------
    session_id : str
        The ID of the session that was not found.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session with ID '{session_id}' not found")
