from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart

class AsterTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def _get_user_query(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    def _get_metadata(self, request: SendTaskRequest):
        return getattr(request.params, "metadata", None)

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)
        session_id = request.params.sessionId
        # invoke()를 통해 LLM 오케스트레이션 및 agent 연결
        reply = self.agent.invoke(query, session_id)
        agent_message = Message(role="agent", parts=[TextPart(text=str(reply))])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)
        return SendTaskResponse(id=request.id, result=task)
