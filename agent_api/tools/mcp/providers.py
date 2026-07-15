

from tools.decorators import register_external_tool
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import threading
import inspect


class AsyncRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()



class McpToolProvider:
    def __init__(self, server_config: dict):
        self.server_config = server_config

    async def load_tools(self, conf):
        client = MultiServerMCPClient(conf)
        return await client.get_tools()
    
    async def register_tools(self):
        for k, v in self.server_config.items():
            tools = await self.load_tools(conf = {k: v})
            for tool_obj in tools:
                register_external_tool(tool_obj, 'mcp', k)



