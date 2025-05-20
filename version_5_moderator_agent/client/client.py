import json
from uuid import uuid4
import httpx
from typing import Any
from models.request import SendTaskRequest, GetTaskRequest
from models.json_rpc import JSONRPCRequest
from models.task import Task, TaskSendParams
from models.agent import AgentCard

class A2AClient:
    def __init__(self, agent_card: AgentCard = None, url: str = None):
        if agent_card:
            self.url = agent_card.url
        elif url:
            self.url = url
        else:
            raise ValueError("Must provide either agent_card or url")

    async def send_task(self, payload: dict[str, Any]) -> Task:
        request = SendTaskRequest(
            id=uuid4().hex,
            params=TaskSendParams(**payload)
        )
        response = await self._send_request(request)
        return Task(**response["result"])

    async def get_task(self, payload: dict[str, Any]) -> Task:
        request = GetTaskRequest(params=payload)
        response = await self._send_request(request)
        return Task(**response["result"])

    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json=request.model_dump(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
