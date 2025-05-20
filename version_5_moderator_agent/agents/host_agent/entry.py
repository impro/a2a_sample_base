import click
import logging
import asyncio
import json
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.host_agent.orchestrator import OrchestratorAgent
from server.task_manager import InMemoryTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def _get_user_query(self, request):
        return request.params.message.parts[0].text

    def _get_metadata(self, request):
        return getattr(request.params, "metadata", None)

    async def on_send_task(self, request):
        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)
        metadata = self._get_metadata(request)
        session_id = request.params.sessionId
        result = await self.agent.route(query, session_id, metadata)
        # result는 하위 agent의 JSON-RPC 응답
        agent_message = task.history[-1] if task.history else None
        if agent_message:
            async with self.lock:
                task.status.state = "completed"
                task.history.append(agent_message)
        return type(request).Response(id=request.id, result=task)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10012, help="Port number for the server")
@click.option("--registry", default="utilities/agent_registry.json", help="Agent registry file")
def main(host, port, registry):
    with open(registry, "r") as f:
        agent_cards = [AgentCard(**a) for a in json.load(f)]
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="orchestrate",
        name="Orchestrator",
        description="Routes tasks to the appropriate agent.",
        tags=["orchestration"],
        examples=["hello", "moderate this"]
    )
    agent_card = AgentCard(
        name="HostAgent",
        description="Routes tasks to child agents.",
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
        task_manager=OrchestratorTaskManager(agent=OrchestratorAgent(agent_cards))
    )
    server.start()

if __name__ == "__main__":
    main()
