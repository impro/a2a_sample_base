"""
class DomainAgentCity:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def get_supported_representation(self):
        return ["card", "table", "list"]

    def receive(self, from_aster, user_input):
        # 실제로는 외부 API 호출 등
        if "expedia" in user_input.lower() or "city" in user_input.lower():
            return {
                "data": [
                    {"city": "Paris", "country": "France", "population": "2M"},
                    {"city": "Tokyo", "country": "Japan", "population": "14M"}
                ],
                "desired_representation": "card"
            }
        return {
            "data": [],
            "desired_representation": "list"
        }
"""

# =============================================================================
# agents/domain_agent_city/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a CityAgent that provides city information using Google's ADK.
# It uses Google's ADK (Agent Development Kit) and Gemini model to respond with city data.
# =============================================================================

# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------
from typing import List, Dict, Any

# 🧠 Gemini-based AI agent provided by Google's ADK
from google.adk.agents.llm_agent import LlmAgent

# 📚 ADK services for session, memory, and file-like "artifacts"
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService

# 🏃 The "Runner" connects the agent, session, memory, and files into a complete system
from google.adk.runners import Runner

# 🧾 Gemini-compatible types for formatting input/output messages
from google.genai import types

# 🔐 Load environment variables (like API keys) from a `.env` file
from dotenv import load_dotenv
load_dotenv()  # Load variables like GOOGLE_API_KEY into the system

# -----------------------------------------------------------------------------
# 🏙️ CityAgent: Your AI agent that provides city information
# -----------------------------------------------------------------------------

class CityAgent:
    # This agent supports plain text and structured data
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "application/json"]

    def __init__(self):
        """
        👷 Initialize the CityAgent:
        - Creates the LLM agent (powered by Gemini)
        - Sets up session handling, memory, and a runner to execute tasks
        """
        self._agent = self._build_agent()  # Set up the Gemini agent
        self._user_id = "city_agent_user"  # Use a fixed user ID for simplicity

        # 🧠 The Runner is what actually manages the agent and its environment
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),  # For files (not used here)
            session_service=InMemorySessionService(),    # Keeps track of conversations
            memory_service=InMemoryMemoryService(),      # Optional: remembers past messages
        )

    def _build_agent(self) -> LlmAgent:
        """
        ⚙️ Creates and returns a Gemini agent with city-specific settings.

        Returns:
            LlmAgent: An agent object from Google's ADK
        """
        return LlmAgent(
            model="gemini-1.5-flash-latest",         # Gemini model version
            name="city_info_agent",                  # Name of the agent
            description="Provides detailed city information",    # Description for metadata
            instruction="""
            You are a city information expert. When asked about cities:
            1. Provide accurate demographic data
            2. Include key tourist attractions
            3. Add relevant travel information
            Format responses as structured data when possible.
            """
        )

    def get_supported_representation(self) -> List[str]:
        """Returns the supported representation types for city data"""
        return ["card", "table", "list"]

    def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        📥 Handle a user query about cities and return structured data.

        Args:
            query (str): What the user asked about cities
            session_id (str): Helps group messages into a session

        Returns:
            Dict[str, Any]: Structured city data with representation preference
        """
        # 🔁 Try to reuse an existing session (or create one if needed)
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

        # 📨 Format the user message for Gemini
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        # 🚀 Run the agent and collect response
        events = list(self._runner.run(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ))

        # Process the response into structured data
        if "expedia" in query.lower() or "city" in query.lower():
            return {
                "data": [
                    {"city": "Paris", "country": "France", "population": "2M", 
                     "attractions": ["Eiffel Tower", "Louvre Museum"]},
                    {"city": "Tokyo", "country": "Japan", "population": "14M",
                     "attractions": ["Shibuya Crossing", "Senso-ji Temple"]}
                ],
                "desired_representation": "card"
            }
        
        return {
            "data": [],
            "desired_representation": "list"
        }

    async def stream(self, query: str, session_id: str):
        """
        🌀 Provides streaming responses for city information requests.

        Args:
            query (str): The user's city-related query
            session_id (str): Session identifier

        Yields:
            dict: Response payload with city information
        """
        # Example streaming response
        yield {
            "is_task_complete": True,
            "content": {
                "data": [
                    {"city": "Paris", "country": "France", "population": "2M"}
                ],
                "desired_representation": "card"
            }
        }




