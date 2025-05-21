# =============================================================================
# agents/domain_agent_city/__main__.py
# =============================================================================
# 🎯 Purpose:
# Entry point for the CityAgent service. Sets up and runs the agent server
# with proper configuration and error handling.
# =============================================================================

# -----------------------------------------------------------------------------
# 📦 Imports
# -----------------------------------------------------------------------------
import os
import click
import logging
import asyncio
from typing import Optional

# 🏃 Server components
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# 🏙️ Agent implementation
from agents.domain_agent_city.agent import CityAgent
from agents.domain_agent_city.task_manager import CityTaskManager

# -----------------------------------------------------------------------------
# 🔧 Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 🚀 CLI Setup and Server Launch
# -----------------------------------------------------------------------------
@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host to bind the server to"
)
@click.option(
    "--port",
    default=10022,
    help="Port number for the server"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode"
)
def main(host: str, port: int, debug: bool):
    """
    🎯 Launch the CityAgent server with the specified configuration
    """
    try:
        # Set debug logging if requested
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        # Configure agent capabilities
        capabilities = AgentCapabilities(
            streaming=True,  # Support streaming responses
            structured_output=True  # Support JSON/structured output
        )
        
        # Define agent skills
        skill = AgentSkill(
            id="city_info",
            name="City Information",
            description="Provides detailed information about cities worldwide.",
            tags=["city", "travel", "expedia", "tourism"],
            examples=[
                "Tell me about Paris",
                "What are the attractions in Tokyo?",
                "Show me city information from Expedia"
            ]
        )
        
        # Create agent card (metadata)
        agent_card = AgentCard(
            name="CityAgent",
            description="AI agent providing comprehensive city information and travel details.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=CityAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=CityAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill]
        )
        
        # Initialize agent and task manager
        city_agent = CityAgent()
        task_manager = CityTaskManager(agent=city_agent)
        
        # Create and start server
        server = A2AServer(host=host, port=port)
        server.register_agent("city_agent", agent_card, task_manager)
        logger.info(f"🚀 Starting CityAgent server on {host}:{port}")
        server.start()
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
