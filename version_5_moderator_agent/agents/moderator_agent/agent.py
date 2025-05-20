from datetime import datetime

class ModeratorAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.feedback_log = []
        self.utg_log = []

    def invoke(self, query: str, session_id: str, feedback: dict = None, utg: dict = None, response: str = None) -> str:
        # 피드백/상태/response 저장
        if feedback or utg or response:
            self.log_feedback(feedback, utg, session_id, response)
        # 자가수정 예시
        if utg and utg.get("transition_reason") == "error":
            return f"Detected abnormal transition from {utg.get('current_state')} to {utg.get('next_state')}. Self-correction triggered."
        if "self-correct" in query:
            return "Self-correction applied based on feedback and UTG."
        return f"Moderator received: {query}"

    def log_feedback(self, feedback, utg, session_id, response=None):
        log_entry = {
            "session_id": session_id,
            "feedback": feedback,
            "utg": utg,
            "negotiation": feedback.get("negotiation") if feedback else None,
            "response": response,  # Autonomous Agent의 행동/응답
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_log.append(log_entry)

    def compute_reward(self, feedback):
        # 예시: 피드백 타입에 따라 reward 산출
        if not feedback:
            return 0
        if feedback.get("type") == "positive":
            return 1
        elif feedback.get("type") == "negative":
            return -1
        return 0

    def export_for_reward_model(self):
        # 보상모델 학습용 데이터로 변환
        return [
            {
                "session_id": entry["session_id"],
                "state": entry["utg"],
                "feedback": entry["feedback"],
                "reward": self.compute_reward(entry["feedback"]),
                "timestamp": entry["timestamp"]
            }
            for entry in self.feedback_log
            if entry["utg"] is not None  # 상태 정보가 있는 경우만
        ]
