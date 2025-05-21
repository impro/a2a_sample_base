curl -X POST http://localhost:10020/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tasks/send",
    "params": {
      "id": "task-001",
      "sessionId": "session-001",
      "message": {
        "role": "user",
        "parts": [
          {"type": "text", "text": "서울 날씨 알려줘"}
        ]
      }
    }
  }'