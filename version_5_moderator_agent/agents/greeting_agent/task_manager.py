from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart

class GreetingTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def _get_user_query(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)
        result_text = self.agent.invoke(query, request.params.sessionId)
        agent_message = Message(role="agent", parts=[TextPart(text=result_text)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)
        return SendTaskResponse(id=request.id, result=task)
