from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx

app = FastAPI()

class FeedbackInput(BaseModel):
    session_id: str
    utg: dict
    question: str
    negotiation: str = None  # UX 협상 결과(예: "더 쉬운 경로를 원함" 등)
    feedback_type: str
    comment: str

MODERATOR_AGENT_URL = "http://localhost:10010/"

@app.post("/feedback")
async def receive_feedback(feedback: FeedbackInput):
    # Moderator Agent로 피드백 전달
    payload = {
        "id": feedback.session_id,
        "sessionId": feedback.session_id,
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": feedback.question}]
        },
        "metadata": {
            "utg": feedback.utg,
            "feedback": {
                "type": feedback.feedback_type,
                "comment": feedback.comment,
                "negotiation": feedback.negotiation
            }
        }
    }
    async with httpx.AsyncClient() as client:
        await client.post(MODERATOR_AGENT_URL, json=payload)
    return {"status": "ok"}
