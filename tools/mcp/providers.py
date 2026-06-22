

from tools.decorators import register_external_tool
from langchain_mcp_adapters.client import MultiServerMCPClient

class McpToolProvider:
    def __init__(self, server_config: dict):
        self.server_config = server_config

    def load_tools(self, conf):
        client = MultiServerMCPClient(conf)
        tools = client.get_tools()
        return tools
    
    def register_tools(self):
        for k, v in self.server_config:
            tools = self.load_tools(conf = {k: v})

            for tool_obj in tools:
                register_external_tool(tool_obj, 'mcp', k)


