
import yaml

class MiddlewaresSelectors:

    def __init__(self, registry):
        self.registry = registry
    
    def for_agent(self, agent_name: str):
        return self.registry.get_middlewares(agent_name)



