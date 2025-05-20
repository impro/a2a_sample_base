# =============================================================================
# agents/domain_agent_weather/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a WeatherAgent that provides weather information using Google's ADK.
# =============================================================================

from typing import List, Dict, Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

class WeatherAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "application/json"]

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = "weather_agent_user"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_agent(self) -> LlmAgent:
        return LlmAgent(
            model="gemini-1.5-flash-latest",
            name="weather_info_agent",
            description="Provides current weather information",
            instruction=(
                "You are a weather information expert. "
                "When asked about the weather, provide current temperature, condition, and tips. "
                "Format responses as structured data when possible."
            )
        )

    def get_supported_representation(self) -> List[str]:
        return ["card", "table", "list"]
        #return ["list_images", "markdown", "list"]

    def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        session = self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )
        if session is None:
            session = self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={}
            )
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )
        events = list(self._runner.run(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ))

        # 실제로는 외부 API 연동, 여기선 예시 데이터
        if "weather" in query.lower() or "forecast" in query.lower():
            return {
                "data": [
                    {"city": "Seoul", "temp": "22°C", "condition": "Sunny", "tip": "Wear sunglasses!"},
                    {"city": "London", "temp": "16°C", "condition": "Rainy", "tip": "Take an umbrella!"}
                ],
                "desired_representation": "table"
            }
        return {
            "data": [],
            "desired_representation": "list"
        }

    async def stream(self, query: str, session_id: str):
        yield {
            "is_task_complete": True,
            "content": {
                "data": [
                    {"city": "Seoul", "temp": "22°C", "condition": "Sunny"}
                ],
                "desired_representation": "table"
            }
        }
