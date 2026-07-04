

from config.agent_mcp_config import AGENT_MCP_ACCESS_CONF

class ToolSelector:
    def __init__(self, tools: list):
        self.tools = tools
    
    async def for_agent(self, agent_name: str):
        selected_tools = []

        for tool_obj in self.tools:
            meta =  getattr(tool_obj, '_tool_meta', None)

            if not meta:
                continue
            
            if meta.source == 'local':
                if agent_name in meta.allowed_agents:
                    selected_tools.append(tool_obj)
             
            if meta.source == 'mcp':
                if not AGENT_MCP_ACCESS_CONF.get(agent_name)['enable_mcp']:
                    continue

                allowed_servers = AGENT_MCP_ACCESS_CONF.get(agent_name)['mcp_servers']
                if meta.server_name in allowed_servers:
                    selected_tools.append(tool_obj)
        return selected_tools
