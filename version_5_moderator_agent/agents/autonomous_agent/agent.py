from uuid import uuid4

async def send_task_to_moderator_agent(payload, response):
    # response: Autonomous Agent의 실제 행동 결과
    payload["metadata"]["response"] = response
    # Implementation of send_task_to_moderator_agent function
    pass

payload = {
    "id": uuid4().hex,
    "sessionId": session_id,
    "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "작업 실행 결과"}]
    },
    "metadata": {
        "utg": {
            "current_state": "HomeScreen",
            "next_state": "SettingsScreen",
            "transition_reason": "user_clicked_settings"
        },
        "feedback": {
            "type": "positive",
            "comment": "전환이 자연스러움"
        }
    }
}
await send_task_to_moderator_agent(payload)
