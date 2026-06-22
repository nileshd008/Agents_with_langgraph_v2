
import yaml

class MiddlewaresSelectors:

    def __init__(self, registry):
        self.registry = registry
    
    def for_agent(self, agent_name: dict):
        agent_spec = yaml.safe_load(open('config/middleware.yaml', 'r'))
        middlewares = agent_spec.get('middleware', [])

        or_keys = []
        or_keys.extend(middlewares.get(agent_name, []))

        return self.registry.create_many(or_keys)



