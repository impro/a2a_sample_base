import asyncclick as click
import asyncio
from uuid import uuid4
from client.client import A2AClient
from models.task import Task

@click.command()
@click.option("--agent", default="http://localhost:10012", help="HostAgent(Orchestrator) URL")
@click.option("--session", default=0, help="Session ID (use 0 to generate a new one)")
@click.option("--history", is_flag=True, help="Print full task history after receiving a response")
async def cli(agent: str, session: str, history: bool):
    client = A2AClient(url=f"{agent}")
    session_id = uuid4().hex if str(session) == "0" else str(session)
    while True:
        prompt = click.prompt("\nWhat do you want to send to the system? (type ':q' or 'quit' to exit)")
        if prompt.strip().lower() in [":q", "quit"]:
            break
        payload = {
            "id": uuid4().hex,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": prompt}]
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
        try:
            task: Task = await client.send_task(payload)
            if task.history and len(task.history) > 1:
                reply = task.history[-1]
                print("\nAgent says:", reply.parts[0].text)
            else:
                print("\nNo response received.")
            if history:
                print("\n========= Conversation History =========")
                for msg in task.history:
                    print(f"[{msg.role}] {msg.parts[0].text}")
        except Exception as e:
            print(f"\n❌ Error while sending task: {e}")

if __name__ == "__main__":
    asyncio.run(cli())
