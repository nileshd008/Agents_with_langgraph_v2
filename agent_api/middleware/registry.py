

from .tools import *
from config.agent_mcp_config import AGENT_MCP_ACCESS_CONF

class MiddlewareRegistry:

    def __init__(self):
        self._builders = {'store_artifact': store_artifact}

    def get_middlewares(self, agent_name):
        return [self._builders[k] for k in AGENT_MCP_ACCESS_CONF[agent_name]['middleware']]