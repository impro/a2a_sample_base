from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart

class ModeratorTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def _get_user_query(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    def _get_feedback(self, request: SendTaskRequest) -> dict:
        meta = getattr(request.params, "metadata", None)
        if meta and "feedback" in meta:
            return meta["feedback"]
        return None

    def _get_utg(self, request: SendTaskRequest) -> dict:
        meta = getattr(request.params, "metadata", None)
        if meta and "utg" in meta:
            return meta["utg"]
        return None

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)
        feedback = self._get_feedback(request)
        utg = self._get_utg(request)
        result_text = self.agent.invoke(query, request.params.sessionId, feedback, utg)
        agent_message = Message(role="agent", parts=[TextPart(text=result_text)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)
        return SendTaskResponse(id=request.id, result=task)
