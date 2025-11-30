from abc import ABC, abstractmethod


class HealthAPIBase(ABC):
    """Abstract base class for health endpoints."""

    @abstractmethod
    async def health_check(self) -> dict:
        """Health check endpoint."""
        pass


class HealthAPI(HealthAPIBase):
    """Handles health and status endpoints."""

    @staticmethod
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}
