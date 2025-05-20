import click
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.greeting_agent.task_manager import GreetingTaskManager
from agents.greeting_agent.agent import GreetingAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10011, help="Port number for the server")
def main(host, port):
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="greet",
        name="Greeting Tool",
        description="Returns a greeting.",
        tags=["greeting"],
        examples=["hello", "hi"]
    )
    agent_card = AgentCard(
        name="GreetingAgent",
        description="Agent that greets the user.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=GreetingAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=GreetingAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=GreetingTaskManager(agent=GreetingAgent())
    )
    server.start()

if __name__ == "__main__":
    main()
