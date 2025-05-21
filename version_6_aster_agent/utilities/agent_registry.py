import json

def load_agent_registry(path="utilities/agent_registry.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

