import asyncio
import click
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.aster_agent.task_manager import AsterTaskManager
from agents.aster_agent.agent import AsterAgent
#from utilities.agent_registry import DiscoveryClient  # DiscoveryClient로 agent_cards 로드
#from utilities.a2a import DiscoveryClient  # DiscoveryClient로 agent_cards 로드
from utilities.a2a.agent_discovery import DiscoveryClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10020, help="Port number for the server")
@click.option(
    "--registry", default=None,
    help="Path to agent registry JSON. Defaults to utilities/agent_registry.json"
)
def main(host, port, registry):
    # DiscoveryClient로 AgentCard 리스트 비동기 로드
    discovery = DiscoveryClient(registry_file=registry)
    agent_cards = asyncio.run(discovery.list_agent_cards())
    if not agent_cards:
        logger.warning("No agents found in registry. Orchestrator will have nothing to call.")
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="orchestrate",
        name="Aster Orchestrator",
        description="Routes tasks to domain agents.",
        tags=["orchestration"],
        examples=["weather in seoul", "search city"]
    )
    agent_card = AgentCard(
        name="AsterAgent",
        description="Routes tasks to domain agents.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill]
    )
    server = A2AServer(host=host, port=port)
    server.register_agent("aster", agent_card, AsterTaskManager(agent=AsterAgent(agent_cards)))
    server.start()

if __name__ == "__main__":
    main()
