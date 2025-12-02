from unittest.mock import AsyncMock, MagicMock

import pytest
from google.adk.agents import Agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.models.lite_llm import (
    LiteLlm,  # TODO: Importing this is so slow, adds 20 seconds easily
)
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from infrastructure.adapters.gcp.google_agent_caller.google_agent_caller import (
    AgentCallerGoogle,
)


class TestAgentCallerGoogleUseCase:
    @staticmethod
    @pytest.fixture
    def sample_request() -> str:
        """Provide sample agent request for testing."""
        return "What is the weather like today in New York?"

    @staticmethod
    @pytest.fixture
    def auth_interceptor():
        """Create a simple test Auth Interceptor."""
        auth_interceptor = AsyncMock()
        auth_interceptor.is_auth_event = MagicMock(return_value=False)

        return auth_interceptor

    @staticmethod
    @pytest.fixture
    def model():
        """Create a simple test LLM model with a mocked response."""
        return LiteLlm(model="gemini-2.0-flash", mock_response="LiteLLM is awesome")

    @staticmethod
    @pytest.fixture
    def agent(model):
        """Create a simple test Agent."""
        return Agent(
            name="test_agent",
            model=model,
            description="A test agent for unit testing",
            instruction="You are a helpful test agent.",
            tools=[],
        )

    @staticmethod
    @pytest.fixture
    def memory_service():
        """Create a session service."""
        return InMemoryMemoryService()

    @staticmethod
    @pytest.fixture
    def artifact_service():
        """Create a artifact service."""
        return InMemoryArtifactService()

    @staticmethod
    @pytest.fixture
    async def session_service():
        """Create a memory service."""
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            state={},
            session_id="test_session",
        )
        return session_service

    @staticmethod
    @pytest.fixture
    def mock_runner(monkeypatch):
        """Mock the Runner's run_async method to yield predefined outputs."""

        async def mock_run_async(*args, **kwargs):
            yield "LiteLLM is awesome"

        monkeypatch.setattr(
            "app.application.use_cases.google_agent_caller.Runner.run_async",
            mock_run_async,
        )

    @staticmethod
    @pytest.mark.integration
    async def test_call_agent_async_with_all_services(
        agent,
        auth_interceptor,
        memory_service,
        artifact_service,
        session_service,
        sample_request,
    ):
        """Test the call_agent_async method of AgentCallerGoogleUseCase."""
        use_case = AgentCallerGoogle(
            agent=agent,
            auth_interceptor=auth_interceptor,
            app_name="test_app",
            session_service=session_service,
            memory_service=memory_service,
            artifact_service=artifact_service,
        )

        responses = []
        async for response in use_case.call_agent_async(
            message=sample_request, session_id="test_session", user_id="test_user"
        ):
            responses.append(response)

        # Verify that the responses match the mocked stream output
        assert len(responses) == 1
        assert isinstance(responses[0], str)
        assert len(responses[0]) > 0
        assert "LiteLLM is awesome" in responses[0]

    @staticmethod
    @pytest.mark.unit
    async def test_given_runner_then_call_agent_async_returns_responses(
        agent,
        auth_interceptor,
        session_service,
        sample_request,
    ):
        """Test that call_agent_async returns responses using only session service."""

        use_case = AgentCallerGoogle(
            agent=agent,
            auth_interceptor=auth_interceptor,
            app_name="test_app",
            session_service=session_service,
        )

        responses = []
        async for response in use_case.call_agent_async(
            message=sample_request, session_id="test_session", user_id="test_user"
        ):
            responses.append(response)

        # Verify that the responses match the mocked stream output
        assert len(responses) == 1
        assert isinstance(responses[0], str)
        assert len(responses[0]) > 0
        assert "LiteLLM is awesome" in responses[0]
