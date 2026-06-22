


class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def register(self, name: str, agent):
        self._agents[name] = agent

    def get(self, name:str):
        if name not in self._agents:
            raise KeyError(f"Agents not registered: {name}")
        
        return self._agents[name]