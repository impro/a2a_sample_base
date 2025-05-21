import uuid
import logging
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool
from google.genai import types

#from utilities.agent_registry import load_agent_registry  # 유틸리티에서 agent registry 로드 함수 필요
#from utilities.agent_connect import AgentConnector        # 각 agent에 task를 보낼 커넥터
from utilities.a2a.agent_connect import AgentConnector        # 각 agent에 task를 보낼 커넥터
from utilities.a2a.agent_discovery import DiscoveryClient
from agents.aster_agent.task_manager import AsterTaskManager
#from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
import asyncio

logger = logging.getLogger(__name__)

class AsterAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"] ##????
    #capabilities = ['orchestrate', 'render']

    def __init__(self, agent_cards):
        # 1. AgentConnector 생성
        self.connectors = {}
        for agent_id, card in agent_cards.items():
            self.connectors[agent_id] = AgentConnector(agent_id, card.url)
            logger.info(f"Registered connector for: {agent_id}")

        # 2. (선택) MCP/Tool 래핑 (여기선 생략, 필요시 FunctionTool 패턴 추가)
        self._tools = [
            self._list_agents,
            self._delegate_task
        ]

        # 3. LlmAgent/Runner 통합
        self._agent = self._build_agent()
        self._user_id = "aster_orchestrator_user"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_agent(self) -> LlmAgent:
        return LlmAgent(
            model="gemini-1.5-flash-latest",
            name="aster_orchestrator_agent",
            description="Orchestrates and routes tasks to domain agents.",
            instruction=self._root_instruction,
            tools=self._tools,
        )

    def _root_instruction(self, context: ReadonlyContext) -> str:
        return (
            "You are an orchestrator. Use list_agents() to see available agents. "
            "Use delegate_task(agent_name, message) to route user queries."
        )

    def _list_agents(self) -> list[str]:
        return list(self.connectors.keys())

    async def _delegate_task(self, agent_name: str, message: str, tool_context: ToolContext) -> str:
        if agent_name not in self.connectors:
            raise ValueError(f"Unknown agent: {agent_name}")
        state = tool_context.state
        if "session_id" not in state:
            state["session_id"] = str(uuid.uuid4())
        session_id = state["session_id"]
        task = await self.connectors[agent_name].send_task(message, session_id)
        if task.history and len(task.history) > 1:
            return task.history[-1].parts[0].text
        return ""

    def invoke(self, query: str, session_id: str) -> str:
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
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )
        events = list(self._runner.run(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ))
        if not events or not events[-1].content or not events[-1].content.parts:
            return ""
        return "\n".join(p.text for p in events[-1].content.parts if p.text)

def main(host, port, registry):
    discovery = DiscoveryClient(registry_file=registry)
    agent_cards = asyncio.run(discovery.list_agent_cards())
    aster_agent = AsterAgent(agent_cards=agent_cards)
    task_manager = AsterTaskManager(agent=aster_agent)
    # ... (agent_card 메타데이터 생성)
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    server.start()