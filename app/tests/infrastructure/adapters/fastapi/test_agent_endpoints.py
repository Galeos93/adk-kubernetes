import pytest
from fastapi.responses import StreamingResponse

from infrastructure.adapters.fastapi.models import AgentRequest
from infrastructure.adapters.fastapi.run_agent_sse_api import (
    RunAgentSSEAPI,
    SSEStreamGenerator,
)


@pytest.fixture
def api_request():
    request = AgentRequest(
        app_name="weather_time_agent",
        new_message="Hello, agent!",
        session_id="session123",
        user_id="user456",
    )
    return request


@pytest.fixture
def chat_use_case_mock():
    class ChatUseCaseMock:
        async def execute(self, request):
            for i in range(3):
                yield f"Response {i + 1} to '{request.new_message}'"

    return ChatUseCaseMock()


@pytest.fixture
def faulty_chat_use_case_mock():
    class FaultyChatUseCaseMock:
        async def execute(self, request):
            yield "Initial response"
            raise Exception("Simulated agent failure")

    return FaultyChatUseCaseMock()


class TestSSEStreamGenerator:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_stream_generation_yields_expected_responses(
        api_request,
        chat_use_case_mock,
    ):
        sse_generator = SSEStreamGenerator(chat_use_case=chat_use_case_mock)
        responses = []
        async for sse_event in sse_generator.generate_stream(api_request):
            responses.append(sse_event)

        # Check that we received the expected number of responses
        assert len(responses) >= 3
        # Check that the responses contain expected content
        assert any("Response 1 to 'Hello, agent!'" in data for data in responses)
        assert any("Response 2 to 'Hello, agent!'" in data for data in responses)
        assert any("Response 3 to 'Hello, agent!'" in data for data in responses)

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_stream_includes_error_event_on_exception(
        api_request,
        faulty_chat_use_case_mock,
    ):
        sse_generator = SSEStreamGenerator(chat_use_case=faulty_chat_use_case_mock)
        responses = []
        async for sse_event in sse_generator.generate_stream(api_request):
            responses.append(sse_event)

        # Check that we received the initial response, error, and completion
        assert any("Initial response" in data for data in responses)
        assert any("Simulated agent failure" in data for data in responses)
        assert any("completion" in data for data in responses)


class TestAgentEndpoints:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_given_request_output_is_expected(api_request, chat_use_case_mock):
        agent_endpoint = RunAgentSSEAPI(chat_use_case=chat_use_case_mock)
        response = await agent_endpoint.run_agent_sse(api_request)

        assert isinstance(response, StreamingResponse)
        # Collect streamed responses
        streamed_data = []
        async for chunk in response.body_iterator:
            streamed_data.append(chunk)

        # Check that we received the expected number of responses
        assert len(streamed_data) >= 4
        # Check that the responses contain expected content
        assert any("Response 1 to 'Hello, agent!'" in data for data in streamed_data)
        assert any("Response 2 to 'Hello, agent!'" in data for data in streamed_data)
        assert any("Response 3 to 'Hello, agent!'" in data for data in streamed_data)
        assert any("completion" in data for data in streamed_data)
