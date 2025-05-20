# =============================================================================
# agents/domain_agent_weather/task_manager.py
# =============================================================================
# 🎯 Purpose:
# Task manager for the WeatherAgent using Google's ADK standards.
# =============================================================================

from typing import Optional, Dict, Any
import logging

from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart
from google.adk.messages import MessageService

logger = logging.getLogger(__name__)

class WeatherTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self._message_service = MessageService()

    def _get_user_query(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    async def _process_agent_response(self, response: Dict[str, Any]) -> Message:
        formatted_text = self._format_weather_data(response)
        return Message(
            role="agent",
            parts=[TextPart(text=formatted_text)]
        )

    def _format_weather_data(self, response: Dict[str, Any]) -> str:
        if not response.get("data"):
            return "No weather information found."
        result = []
        for weather in response["data"]:
            info = [
                f"🌆 {weather['city']}",
                f"🌡️ Temp: {weather['temp']}",
                f"🌤️ Condition: {weather['condition']}"
            ]
            if "tip" in weather:
                info.append(f"💡 Tip: {weather['tip']}")
            result.append("\n".join(info))
        return "\n\n".join(result)

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = await self.upsert_task(request.params)
        try:
            query = self._get_user_query(request)
            result = self.agent.invoke(
                query=query,
                session_id=str(task.id)
            )
            agent_message = await self._process_agent_response(result)
            async with self.lock:
                task.status = TaskStatus(state=TaskState.COMPLETED)
                task.history.append(agent_message)
            return SendTaskResponse(id=request.id, result=task)
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            async with self.lock:
                task.status = TaskStatus(state=TaskState.FAILED)
                error_message = Message(
                    role="agent",
                    parts=[TextPart(text=f"Error processing request: {str(e)}")]
                )
                task.history.append(error_message)
            return SendTaskResponse(id=request.id, result=task)
