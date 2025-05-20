class DomainAgentWeather:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def get_supported_representation(self):
        return ["list_images", "markdown", "list"]

    def receive(self, from_aster, user_input):
        # 실제로는 외부 API 호출 등
        if "seoul" in user_input.lower():
            return {
                "data": [{"city": "Seoul", "weather": "Sunny", "temp": "25°C"}],
                "desired_representation": "list_images"
            }
        return {
            "data": [],
            "desired_representation": "list"
        }
