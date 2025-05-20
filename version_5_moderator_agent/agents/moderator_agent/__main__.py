import click
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.moderator_agent.task_manager import ModeratorTaskManager
from agents.moderator_agent.agent import ModeratorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10010, help="Port number for the server")
def main(host, port):
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="moderate",
        name="Moderator Tool",
        description="Collects human feedback and applies self-correction.",
        tags=["moderation", "feedback", "HITL"],
        examples=["Please moderate this response.", "Apply self-correction"]
    )
    agent_card = AgentCard(
        name="Version4ModeratorAgent",
        description="Agent that collects human feedback and enables self-correction.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=ModeratorAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=ModeratorAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=ModeratorTaskManager(agent=ModeratorAgent())
    )
    server.start()

if __name__ == "__main__":
    main()
