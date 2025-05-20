# =============================================================================
# agents/domain_agent_city/task_manager.py
# =============================================================================
# 🎯 Purpose:
# Task manager for the CityAgent that handles task lifecycle and message processing
# using Google's ADK standards.
# =============================================================================

# -----------------------------------------------------------------------------
# 📦 Imports
# -----------------------------------------------------------------------------
from typing import Optional, Dict, Any
import asyncio
import logging

from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart
from google.adk.tasks import Task, TaskResult
from google.adk.messages import MessageService

logger = logging.getLogger(__name__)

class CityTaskManager(InMemoryTaskManager):
    """
    🎯 Manages tasks for the CityAgent, handling:
    - Task creation and updates
    - Message processing
    - Response formatting
    """
    
    def __init__(self, agent):
        """
        Initialize with a CityAgent instance
        
        Args:
            agent: Instance of CityAgent
        """
        super().__init__()
        self.agent = agent
        self._message_service = MessageService()
        
    def _get_user_query(self, request: SendTaskRequest) -> str:
        """
        Extract the user's query from the request
        
        Args:
            request: The incoming task request
            
        Returns:
            str: The extracted user query
        """
        return request.params.message.parts[0].text

    async def _process_agent_response(self, response: Dict[str, Any]) -> Message:
        """
        Process the agent's response into a Message object
        
        Args:
            response: Raw response from the agent
            
        Returns:
            Message: Formatted message with the response
        """
        # Convert the structured response to a formatted message
        formatted_text = self._format_city_data(response)
        return Message(
            role="agent",
            parts=[TextPart(text=formatted_text)]
        )

    def _format_city_data(self, response: Dict[str, Any]) -> str:
        """
        Format city data into a readable string
        
        Args:
            response: The structured city data
            
        Returns:
            str: Formatted string representation
        """
        if not response.get("data"):
            return "No city information found."
            
        result = []
        for city in response["data"]:
            city_info = [
                f"🏙️ {city['city']}, {city['country']}",
                f"👥 Population: {city['population']}"
            ]
            if "attractions" in city:
                attractions = ", ".join(city["attractions"])
                city_info.append(f"🎯 Attractions: {attractions}")
            result.append("\n".join(city_info))
            
        return "\n\n".join(result)

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Handle incoming task requests
        
        Args:
            request: The task request to process
            
        Returns:
            SendTaskResponse: The response containing results
        """
        # Create or update task
        task = await self.upsert_task(request.params)
        
        try:
            # Get the user's query
            query = self._get_user_query(request)
            
            # Get response from the agent
            result = self.agent.invoke(
                query=query,
                session_id=str(task.id)  # Use task ID as session ID
            )
            
            # Process the response
            agent_message = await self._process_agent_response(result)
            
            # Update task status and history
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
