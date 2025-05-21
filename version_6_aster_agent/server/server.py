# =============================================================================
# server.py
# =============================================================================
# 📌 Purpose:
# This file defines an A2A (Agent-to-Agent) server that supports multiple agents:
# - Aster Agent (Orchestrator)
# - Domain Agent (City)
# - Domain Agent (Weather)
# It supports:
# - Receiving task requests via POST ("/")
# - Letting clients discover agents via GET ("/.well-known/agent.json")
# =============================================================================

# -----------------------------------------------------------------------------
# 🧱 Required Imports
# -----------------------------------------------------------------------------

# 🌐 Starlette is a lightweight web framework for building ASGI applications
from starlette.applications import Starlette            
from starlette.responses import JSONResponse            
from starlette.requests import Request                  

# 📦 Importing our custom models and logic
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from models.request import A2ARequest, SendTaskRequest  
from models.json_rpc import JSONRPCResponse, InternalError  
from server import task_manager              

# 🤖 Agent imports
from agents.aster_agent.agent import AsterAgent
from agents.aster_agent.task_manager import AsterTaskManager
from agents.domain_agent_city.agent import CityAgent
from agents.domain_agent_city.task_manager import CityTaskManager
from agents.domain_agent_weather.agent import WeatherAgent
from agents.domain_agent_weather.task_manager import WeatherTaskManager

# 🛠️ General utilities
import json                                              
import logging                                           
from datetime import datetime
from typing import Dict, Tuple, Optional
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 🔧 Agent Registration Functions
# -----------------------------------------------------------------------------

def register_aster_agent(host: str, port: int) -> Tuple[AgentCard, AsterTaskManager]:
    """Register and configure the Aster Agent (Orchestrator)"""
    capabilities = AgentCapabilities(
        streaming=True,
        structured_output=True
    )
    skill = AgentSkill(
        id="orchestrator",
        name="Orchestration",
        description="Orchestrates and coordinates other agents",
        tags=["orchestrator", "coordinator"],
        examples=[
            "Coordinate task execution between agents",
            "Manage agent communication flow"
        ]
    )
    agent_card = AgentCard(
        name="AsterAgent",
        description="Orchestrator agent for coordinating multi-agent interactions",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=AsterAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=AsterAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    aster_agent = AsterAgent()
    task_manager = AsterTaskManager(agent=aster_agent)
    return agent_card, task_manager

def register_city_agent(host: str, port: int) -> Tuple[AgentCard, CityTaskManager]:
    """Register and configure the City Information Agent"""
    capabilities = AgentCapabilities(
        streaming=True,
        structured_output=True
    )
    skill = AgentSkill(
        id="city_info",
        name="City Information",
        description="Provides detailed information about cities worldwide",
        tags=["city", "travel", "tourism"],
        examples=[
            "Tell me about Paris",
            "What are the attractions in Tokyo?"
        ]
    )
    agent_card = AgentCard(
        name="CityAgent",
        description="AI agent providing comprehensive city information",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=CityAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=CityAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    city_agent = CityAgent()
    task_manager = CityTaskManager(agent=city_agent)
    return agent_card, task_manager

def register_weather_agent(host: str, port: int) -> Tuple[AgentCard, WeatherTaskManager]:
    """Register and configure the Weather Information Agent"""
    capabilities = AgentCapabilities(
        streaming=True,
        structured_output=True
    )
    skill = AgentSkill(
        id="weather_info",
        name="Weather Information",
        description="Provides current weather and forecast information worldwide",
        tags=["weather", "forecast", "climate"],
        examples=[
            "What's the weather in Seoul?",
            "Give me the weather forecast for London"
        ]
    )
    agent_card = AgentCard(
        name="WeatherAgent",
        description="AI agent providing weather and forecast information",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    weather_agent = WeatherAgent()
    task_manager = WeatherTaskManager(agent=weather_agent)
    return agent_card, task_manager

# -----------------------------------------------------------------------------
# 🚀 A2AServer Class: The Core Server Logic
# -----------------------------------------------------------------------------
class A2AServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        """Initialize the A2A server with multiple agent support"""
        self.host = host
        self.port = port
        self.agents: Dict[str, Tuple[AgentCard, task_manager]] = {}
        self.app = Starlette()
        
        # Register routes
        self.app.add_route("/", self._handle_request, methods=["POST"])
        self.app.add_route("/.well-known/agent.json", self._get_agent_cards, methods=["GET"])
        self.app.add_route("/agents/{agent_id}", self._handle_agent_request, methods=["POST"])

    def register_agent(self, agent_id: str, agent_card: AgentCard, agent_task_manager: task_manager):
        """Register an agent with the server"""
        self.agents[agent_id] = (agent_card, agent_task_manager)
        logger.info(f"Registered agent: {agent_id} ({agent_card.name})")

    async def _handle_agent_request(self, request: Request):
        """Handle requests for specific agents"""
        agent_id = request.path_params["agent_id"]
        if agent_id not in self.agents:
            return JSONResponse({"error": f"Agent {agent_id} not found"}, status_code=404)
        
        _, task_manager = self.agents[agent_id]
        try:
            body = await request.json()
            json_rpc = A2ARequest.validate_python(body)
            if isinstance(json_rpc, SendTaskRequest):
                result = await task_manager.on_send_task(json_rpc)
                return self._create_response(result)
            raise ValueError(f"Unsupported method for agent {agent_id}")
        except Exception as e:
            logger.error(f"Error handling request for agent {agent_id}: {e}")
            return JSONResponse(
                JSONRPCResponse(id=None, error=InternalError(message=str(e))).model_dump(),
                status_code=400
            )

    async def _handle_request(self, request: Request):
        """Handle general requests (delegated to Aster Agent)"""
        try:
            # Orchestrator(aster_agent)인 경우
            if "aster" in self.agents:
                _, task_manager = self.agents["aster"]
            # 도메인 에이전트(자기 자신만 등록된 경우)
            elif len(self.agents) == 1:
                _, task_manager = list(self.agents.values())[0]
            else:
                raise ValueError("No suitable agent registered")
            body = await request.json()
            logger.info(f"🔍 Incoming JSON: {json.dumps(body, indent=2)}")
            json_rpc = A2ARequest.validate_python(body)
            if isinstance(json_rpc, SendTaskRequest):
                result = await task_manager.on_send_task(json_rpc)
                return self._create_response(result)
            raise ValueError("Unsupported A2A method")
        except Exception as e:
            logger.error(f"Exception: {e}")
            return JSONResponse(
                JSONRPCResponse(id=None, error=InternalError(message=str(e))).model_dump(),
                status_code=400
            )

    def _get_agent_cards(self, request: Request) -> JSONResponse:
        """Return metadata for all registered agents"""
        return JSONResponse({
            agent_id: card.model_dump(exclude_none=True)
            for agent_id, (card, _) in self.agents.items()
        })

    def _create_response(self, result):
        """Create JSON response from result"""
        if isinstance(result, JSONRPCResponse):
            return JSONResponse(content=jsonable_encoder(result.model_dump(exclude_none=True)))
        raise ValueError("Invalid response type")

    def start(self):
        """Start the A2A server"""
        if not self.agents:
            raise ValueError("No agents registered")
        
        logger.info(f"🚀 Starting A2A server on {self.host}:{self.port}")
        logger.info(f"📋 Registered agents: {', '.join(self.agents.keys())}")
        
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)

# -----------------------------------------------------------------------------
# 🎯 Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create server instance
    server = A2AServer(host="localhost", port=10020)
    
    # Register all agents
    aster_card, aster_manager = register_aster_agent("localhost", 10021)
    city_card, city_manager = register_city_agent("localhost", 10022)
    weather_card, weather_manager = register_weather_agent("localhost", 10023)
    
    server.register_agent("aster", aster_card, aster_manager)
    server.register_agent("city", city_card, city_manager)
    server.register_agent("weather", weather_card, weather_manager)
    
    # Start serving
    server.start()
