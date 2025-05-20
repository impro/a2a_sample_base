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
        metadata = self._get_metadata(request)
        session_id = request.params.sessionId
        # 실제로는 from_user, user_input, metadata 등 전달
        rendered = self.agent.receive(from_user="user", user_input=query)
        agent_message = Message(role="agent", parts=[TextPart(text=str(rendered))])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)
        return SendTaskResponse(id=request.id, result=task)
