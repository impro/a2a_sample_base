import click
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.aster_agent.task_manager import AsterTaskManager
from agents.aster_agent.agent import AsterAgent
from ADK.discovery import AgentRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10020, help="Port number for the server")
def main(host, port):
    registry = AgentRegistry()  # 실제로는 agent_registry.json 등에서 로드
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
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AsterTaskManager(agent=AsterAgent(registry))
    )
    server.start()

if __name__ == "__main__":
    main()
