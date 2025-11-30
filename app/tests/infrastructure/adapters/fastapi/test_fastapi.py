"""
Tests for FastAPI AppBuilder adapter.

This module contains tests for the AppBuilder class that creates and configures
the FastAPI application with agent and health routes.

Test Categories
---------------
- Unit tests for AppBuilder functionality
- Route registration testing
- FastAPI app configuration testing
- Integration with health and agent APIs

Examples
--------
Run these tests:
    pytest tests/infrastructure/adapters/fastapi/test_fastapi.py -v
"""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

from infrastructure.adapters.fastapi.fastapi import AppBuilder
from infrastructure.adapters.fastapi.models import AgentRequest


class TestAppBuilder:
    """Test suite for AppBuilder class."""

    @pytest.fixture
    def mock_health_api(self):
        """Create a mock health API."""
        health_api = Mock()

        def health_check():
            return {"status": "healthy"}

        health_api.health_check = health_check

        return health_api

    @pytest.fixture
    def mock_create_session_api(self):
        """Create a mock create session API."""
        create_session_api = Mock()
        return create_session_api

    @pytest.fixture
    def mock_agent_api(self):
        """Create a mock agent API."""
        agent_api = Mock()

        async def mock_run_agent_sse(request: AgentRequest) -> StreamingResponse:
            return StreamingResponse(
                content=iter(["data: test\n\n"]), media_type="text/event-stream"
            )

        agent_api.run_agent_sse = mock_run_agent_sse

        return agent_api

    @pytest.fixture
    def app_builder(self, mock_health_api, mock_agent_api, mock_create_session_api):
        """Create AppBuilder instance with mocked dependencies."""
        return AppBuilder(
            health_api=mock_health_api,
            agent_api=mock_agent_api,
            create_session_api=mock_create_session_api,
        )

    @pytest.fixture
    def sample_fastapi_app(self):
        """Create a sample FastAPI app for testing."""
        return FastAPI(title="Test App")

    @pytest.mark.unit
    def test_register_health_routes(self, app_builder, sample_fastapi_app):
        """Test that health routes are registered correctly."""
        # Act
        app_builder.register_health_routes(sample_fastapi_app)

        # Assert
        routes = [route.path for route in sample_fastapi_app.routes]
        assert "/health" in routes

        # Verify the route is configured correctly
        health_route = next(
            route
            for route in sample_fastapi_app.routes
            if hasattr(route, "path") and route.path == "/health"
        )
        assert "GET" in health_route.methods

    @pytest.mark.unit
    def test_register_agent_routes(self, app_builder, sample_fastapi_app):
        """Test that agent routes are registered correctly."""
        # Act
        app_builder.register_agent_routes(sample_fastapi_app)

        # Assert
        routes = [route.path for route in sample_fastapi_app.routes]
        assert "/run_sse" in routes

        # Verify the route is configured correctly
        agent_route = next(
            route
            for route in sample_fastapi_app.routes
            if hasattr(route, "path") and route.path == "/run_sse"
        )
        assert "POST" in agent_route.methods

    @pytest.mark.unit
    def test_health_endpoint(self, app_builder):
        """Test for health endpoint."""
        # Arrange
        app = app_builder.create_app()

        with TestClient(app) as client:
            response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.unit
    def test_agent_endpoint(self, app_builder):
        """Test for agent SSE endpoint."""
        # Arrange
        app = app_builder.create_app()
        client = TestClient(app)

        query = AgentRequest(
            app_name="test_agent",
            new_message="test",
            session_id="session123",
            user_id="user456",
        )

        # Act
        response = client.post("/run_sse", json=query.model_dump())

        # Assert
        assert response.status_code == 200
