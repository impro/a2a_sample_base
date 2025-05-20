from uuid import uuid4

async def send_task_to_moderator_agent(payload, response):
    # response: Autonomous Agent의 실제 행동 결과(예: "SettingsScreen으로 이동 완료")
    payload["metadata"]["response"] = response
    # 실제로는 httpx.AsyncClient 등으로 POST 요청
    # 예시: await client.post("http://localhost:10010/", json=payload)
    pass

# 사용 예시 (async 함수 내에서)
session_id = uuid4().hex
payload = {
    "id": uuid4().hex,
    "sessionId": session_id,
    "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "작업 실행 결과: 설정 화면으로 이동"}]
    },
    "metadata": {
        "utg": {
            "current_state": "HomeScreen",
            "next_state": "SettingsScreen",
            "transition_reason": "user_clicked_settings"
        },
        "feedback": {
            "type": "positive",
            "comment": "전환이 자연스러움",
            "negotiation": "더 쉬운 경로를 원함"  # UX 협상 결과 예시
        }
    }
}
response = "SettingsScreen으로 정상 이동"
await send_task_to_moderator_agent(payload, response)
