

from tools.decorators import register_external_tool
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio



class McpToolProvider:
    def __init__(self, server_config: dict):
        self.server_config = server_config

    async def load_tools(self, conf):
        client = MultiServerMCPClient(conf)
        return await client.get_tools()
    
    def register_tools(self):
        for k, v in self.server_config.items():
            try:
                loop = asyncio.get_event_loop()
            except:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if not loop.is_running():
                try:
                    tools = loop.run_until_complete(self.load_tools(conf = {k: v}))
                except:
                    tools = asyncio.run(self.load_tools(conf = {k: v}))
            else:
                tools = asyncio.run_coroutine_threadsafe(self.load_tools(conf = {k: v}), loop)

            for tool_obj in tools:
                register_external_tool(tool_obj, 'mcp', k)
            


