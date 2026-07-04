
from core.contracts import AppRuntimeContext
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
import asyncio
from contextlib import AsyncExitStack
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite.aio import AsyncSqliteStore
import aiosqlite
import inspect
from persistence.contracts import CheckPointerConfig, StoreConfig
from persistence.checkpointer_factory import CheckpointerFactory, StoreFactory
from core.selectors import ToolSelector
from tools.planner import tools
from tools.shared import tools

from middleware.registry import MiddlewareRegistry
from middleware.selector import MiddlewaresSelectors
from tools.decorators import TOOL_REGISTRY
# from .bootstrap import initialize
from langchain_openai import ChatOpenAI
from core.contracts import AppRuntimeContext
from config.mcp_servers import MCP_SERVER_CONFIG
from tools.mcp.providers import McpToolProvider
import os
from agents.registry import AgentRegistry
from agents.sql.builder import sql_builder
from agents.visualization.builder import visualization_builder
from agents.planner.builder import planner_builder
from dotenv import load_dotenv
import threading
from langchain.agents import create_agent


load_dotenv()

class AgentA:
    def __init__(self):
        self.checkpoint = None
        self.stack = None
        self.store = None

    async def runtime(self):
        self.stack = AsyncExitStack()

        self.checkpoint = await self.stack.enter_async_context(AsyncSqliteSaver.from_conn_string('agent.db'))

        if hasattr(self.checkpoint, 'setup'):
            await self.checkpoint.setup()
        
        self.store = await self.stack.enter_async_context(AsyncSqliteStore.from_conn_string('agent.db'))
        await self.store.setup()

        llm = ChatOpenAI(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            api_key=os.environ["DEEPINFRA_API_KEY"],
            base_url="https://api.deepinfra.com/v1/openai",
            temperature=0.1,
            model_kwargs={"tool_choice": "auto"}
        )

        await McpToolProvider(MCP_SERVER_CONFIG).register_tools()
        tools = ToolSelector(TOOL_REGISTRY)
        middlewares = MiddlewaresSelectors(MiddlewareRegistry())


        sql_agent = sql_builder(llm,
                            tools = await tools.for_agent('sql'),
                            checkpointer = self.checkpoint,
                            middlewares = middlewares.for_agent('sql'),
                            store = self.store)
        
        visualization_agent = visualization_builder(llm,
                            tools = await tools.for_agent('visualization'),
                            checkpointer = self.checkpoint,
                            middlewares = middlewares.for_agent('visualization'),
                            store = self.store)
        
        agent_registry = AgentRegistry()
        agent_registry.register('sql', sql_agent)
        agent_registry.register('visualization', visualization_agent)

        self.context = AppRuntimeContext(
                            user_id =  'nil',
                            tenant_id = '8888',
                            project_id = 'agent',
                            agent_registry = agent_registry
                        )

        self.planner_agent = planner_builder(llm,
                            tools = await tools.for_agent('planner'),
                            checkpointer = self.checkpoint,
                            middlewares = middlewares.for_agent('planner'),
                            store = self.store,
                            context_schema = AppRuntimeContext)
        
        return self


    async def get_state_messages(self, thread_id: str, user_id:str):
        try:
            result = await self.planner_agent.aget_state(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}})
            return result.values.get('messages', [])
        except Exception as e:
            print('get_messages', str(e))
            return [AIMessage(content = str(e))]

    async def get_state_history(self, thread_id, user_id):
        async for state in self.planner_agent.aget_state_history(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}}):
            return state
    
    async def time_travel(self, config):
        return await self.planner_agent.ainvoke(None, config = config)

    async def invoke(self, thread_id: str, user_id:str, tenant_id:str, project_id:str, user_input:str = None):
        try:
            if user_input:
                query = {'messages': [HumanMessage(content = user_input)]}
            
            else:
                query = None

            return await self.planner_agent.ainvoke(query, config = {'configurable':{'thread_id': thread_id,'user_id': user_id}}, context = self.context)
        except Exception as e:
            return {'messages': [AIMessage(content = str(e))]}




class AppRuntime:
    def __init__(self):

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target = self._run_loop, daemon = True)

        self.thread.start()
        future = asyncio.run_coroutine_threadsafe(AgentA().runtime(), self.loop)

        self.rt = future.result()
    
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def invoke(self, thread_id: str, user_id:str, tenant_id:str, project_id:str, user_input:str = None):
        future = asyncio.run_coroutine_threadsafe(self.rt.invoke(thread_id=thread_id, user_id=user_id, tenant_id=tenant_id, project_id=project_id, user_input=user_input), self.loop)
        return future.result()
     
    def get_state_history(self, thread_id, user_id):
        future = asyncio.run_coroutine_threadsafe(self.rt.get_state_history(thread_id, user_id), self.loop)
        return future.result()
    
    def get_state_messages(self, thread_id: str, user_id:str):
        future = asyncio.run_coroutine_threadsafe(self.rt.get_state_messages(thread_id, user_id), self.loop)
        return future.result()
    
    def time_travel(self, config):
        future = asyncio.run_coroutine_threadsafe(self.rt.time_travel(config = config), self.loop)
        return future.result()
    
    def close(self):
        future = asyncio.run_coroutine_threadsafe(self.rt.aclose(), self.loop)
        future.result()
        self.loop.call_soon_threadsafe(self.loop.stop)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # async def get_state_messages(self, thread_id: str, user_id:str):
    #     result = await self.planner_agent.aget_state(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}})
    #     result = result.values
    #     return result.get('messages', [])
        
            
    
    # async def get_state_history(self, thread_id, user_id):
    #     "fault tolerance implementation in langgraph"
    #     for i in await self.planner_agent.get_state_history(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}}):
    #         return i.next if hasattr(i, 'next') else False
    #     return False

    # async def invoke(self, thread_id: str, user_id:str, tenant_id:str, project_id:str, user_input:str = None):
        
    #     context = AppRuntimeContext(
    #                         user_id =  user_id,
    #                         tenant_id = tenant_id,
    #                         project_id = project_id,
    #                         agent_registry = self.agent_registry
    #                     )
    #     if user_input:  
    #         return await self.planner_agent.ainvoke({'messages': [HumanMessage(content = user_input)]}, 
    #                                         #context = context, 
    #                                         config = {'configurable':{'thread_id': thread_id,'user_id': user_id, 'context': context}})
    #     else:
    #         return await self.planner_agent.ainvoke(None, 
    #                                         #context = context, 
    #                                         config = {'configurable':{'thread_id': thread_id,'user_id': user_id}})

