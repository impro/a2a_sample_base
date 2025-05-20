class GreetingAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def invoke(self, query: str, session_id: str) -> str:
        if "hello" in query.lower():
            return "Hello! How can I help you today?"
        return "GreetingAgent received: " + query
