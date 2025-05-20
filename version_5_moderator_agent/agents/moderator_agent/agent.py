class ModeratorAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.feedback_log = []
        self.utg_log = []

    def invoke(self, query: str, session_id: str, feedback: dict = None, utg: dict = None) -> str:
        # 피드백 저장
        if feedback:
            self.feedback_log.append({"session_id": session_id, "feedback": feedback})
        # UTG 상태 전이 저장
        if utg:
            self.utg_log.append({"session_id": session_id, "utg": utg})
        # 자가수정 예시
        if utg and utg.get("transition_reason") == "error":
            return f"Detected abnormal transition from {utg.get('current_state')} to {utg.get('next_state')}. Self-correction triggered."
        if "self-correct" in query:
            return "Self-correction applied based on feedback and UTG."
        return f"Moderator received: {query}"
