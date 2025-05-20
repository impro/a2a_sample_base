# =============================================================================
# agents/domain_agent_weather/__main__.py
# =============================================================================
# 🎯 Purpose:
# Entry point for the WeatherAgent service.
# =============================================================================

import click
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.domain_agent_weather.agent import WeatherAgent
from agents.domain_agent_weather.task_manager import WeatherTaskManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10023, help="Port number for the server")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(host: str, port: int, debug: bool):
    try:
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        capabilities = AgentCapabilities(
            streaming=True,
            structured_output=True
        )
        skill = AgentSkill(
            id="weather_info",
            name="Weather Information",
            description="Provides current weather and forecast.",
            tags=["weather", "forecast", "climate"],
            examples=[
                "What's the weather in Seoul?",
                "Give me the weather forecast for London."
            ]
        )
        agent_card = AgentCard(
            name="WeatherAgent",
            description="AI agent providing weather and forecast information.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill]
        )
        weather_agent = WeatherAgent()
        task_manager = WeatherTaskManager(agent=weather_agent)
        server = A2AServer(
            host=host,
            port=port,
            agent_card=agent_card,
            task_manager=task_manager
        )
        logger.info(f"🚀 Starting WeatherAgent server on {host}:{port}")
        server.start()
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
