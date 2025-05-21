class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, name, agent):
        self.agents[name] = agent

    def discover(self, capability):
        return [agent for agent in self.agents.values() if capability in agent.capabilities]