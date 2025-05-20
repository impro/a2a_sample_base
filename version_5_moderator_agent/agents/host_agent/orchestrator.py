import httpx

class OrchestratorAgent:
    def __init__(self, agent_cards):
        self.agent_cards = agent_cards

    async def route(self, query, session_id, metadata=None):
        # 간단 라우팅: "hello"면 GreetingAgent, "moderate"면 ModeratorAgent
        if "hello" in query.lower():
            agent = next(a for a in self.agent_cards if a.name == "GreetingAgent")
        else:
            agent = next(a for a in self.agent_cards if a.name == "ModeratorAgent")
        async with httpx.AsyncClient() as client:
            payload = {
                "id": session_id,
                "sessionId": session_id,
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": query}]
                },
                "metadata": metadata
            }
            resp = await client.post(agent.url, json=payload)
            return resp.json()
