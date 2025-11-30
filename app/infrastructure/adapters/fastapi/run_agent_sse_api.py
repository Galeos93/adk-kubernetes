import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from application.interfaces.chat_with_agent import ChatWithAgentInterface
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from infrastructure.adapters.fastapi.models import AgentRequest


class AgentResponseMapper:
    """Maps agent responses to Server-Sent Events format."""

    @staticmethod
    def map_response_to_sse(response: str, req: AgentRequest) -> str:
        """Map a single agent response to SSE format."""
        sse_data = {
            "type": "agent_response",
            "content": response,
            "session_id": req.session_id,
            "user_id": req.user_id,
        }
        return f"data: {json.dumps(sse_data)}\n\n"


@dataclass
class SSEStreamGenerator:
    """Handles Server-Sent Events stream generation."""

    chat_use_case: ChatWithAgentInterface
    agent_response_mapper: AgentResponseMapper = field(
        default_factory=AgentResponseMapper
    )

    async def generate_stream(self, req: AgentRequest):
        """Generate Server-Sent Events stream from agent responses."""
        try:
            async for response in self.chat_use_case.execute(req):
                sse_data = self.agent_response_mapper.map_response_to_sse(response, req)
                yield sse_data

                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)

        except Exception as e:
            # Send error as SSE event
            raise e
            error_data = {
                "type": "error",
                "error": str(e),
                "session_id": req.session_id,
                "user_id": req.user_id,
            }
            yield f"data: {json.dumps(error_data)}\n\n"

        finally:
            # Send completion event
            completion_data = {
                "type": "completion",
                "session_id": req.session_id,
                "user_id": req.user_id,
            }
            yield f"data: {json.dumps(completion_data)}\n\n"


class RunAgentSSEAPIBase(ABC):
    """Abstract base class for agent endpoints."""

    @abstractmethod
    async def run_agent_sse(self, req: AgentRequest) -> StreamingResponse:
        """Server-Sent Events endpoint for streaming agent responses."""
        pass


@dataclass
class RunAgentSSEAPI(RunAgentSSEAPIBase):
    """Handles agent-related HTTP endpoints."""

    chat_use_case: ChatWithAgentInterface

    def __post_init__(self):
        # TODO: Revisit the role of the stream generator
        self.sse_generator = SSEStreamGenerator(self.chat_use_case)

    async def run_agent_sse(self, req: AgentRequest) -> StreamingResponse:
        """Server-Sent Events endpoint for streaming agent responses."""
        if self.chat_use_case is None:
            raise HTTPException(
                status_code=500,
                detail="Chat use case not configured. Please initialize the service.",
            )

        return StreamingResponse(
            self.sse_generator.generate_stream(req),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )
