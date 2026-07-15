

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.contracts import AppRuntimeContext
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
import asyncio
from contextlib import AsyncExitStack
import aiosqlite
import inspect
from persistence.contracts import CheckPointerConfig, StoreConfig
from persistence.checkpointer_factory import CheckpointerFactory, StoreFactory
from core.selectors import ToolSelector
from tools.planner import tools
from tools.shared import tools
from fastapi import Request
from middleware.registry import MiddlewareRegistry
from middleware.selector import MiddlewaresSelectors
from tools.decorators import TOOL_REGISTRY
from langchain_openai import ChatOpenAI
from core.contracts import AppRuntimeContext
from config.mcp_servers import MCP_SERVER_CONFIG
from tools.mcp.providers import McpToolProvider
import os
from agents.registry import AgentRegistry
from agents.sql.builder import sql_builder
from agents.visualization.builder import visualization_builder
from agents.planner.builder import planner_builder
import threading
from langchain.agents import create_agent
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from contextlib import AsyncExitStack
from pydantic import BaseModel
from typing import Optional
import uvicorn

#from dotenv import load_dotenv

class AgentA:
    def __init__(self):
        self.checkpoint = None
        self.stack = None
        self.store = None
        self.context = None
        self.planner_agent = None
        self.mcp_provider = None

    async def runtime(self):
        self.stack = AsyncExitStack()

        cp_config = CheckPointerConfig(kind=os.environ['CHECKPOINT_KIND'], connection_str=os.environ['CHECKPOINT_URL'])
        store_config = StoreConfig(kind=os.environ['CHECKPOINT_KIND'], connection_str=os.environ['CHECKPOINT_URL'])

        self.checkpoint = await CheckpointerFactory(cp_config).create(self.stack)
        self.store = await StoreFactory(store_config).create(self.stack)

        llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL'),
            api_key=os.environ["DEEPINFRA_API_KEY"],
            base_url=os.environ['LLM_BASE_URL'],
            temperature=0.1,
            model_kwargs={"tool_choice": "auto"}
        )

        gllm = ChatOpenAI(
            model=os.getenv('LLM_MODEL'),
            api_key=os.environ["DEEPINFRA_API_KEY"],
            base_url=os.environ['LLM_BASE_URL'],
            temperature=0.1
        )

        self.mcp_provider = McpToolProvider(MCP_SERVER_CONFIG)
        await self.mcp_provider.register_tools()

        tools_selector = ToolSelector(TOOL_REGISTRY)
        middlewares = MiddlewaresSelectors(MiddlewareRegistry())

        sql_agent = sql_builder(
            llm,
            tools=await tools_selector.for_agent('sql'),
            checkpointer=self.checkpoint,
            middlewares=middlewares.for_agent('sql'),
            store=self.store,
            context_schema=AppRuntimeContext
        )
        
        visualization_agent = visualization_builder(
            llm,
            tools=await tools_selector.for_agent('visualization'),
            checkpointer=self.checkpoint,
            middlewares=middlewares.for_agent('visualization'),
            store=self.store
        )
        
        agent_registry = AgentRegistry()
        agent_registry.register('sql', sql_agent)
        agent_registry.register('visualization', visualization_agent)
        agent_registry.register('gen_llm', gllm)

        self.context = AppRuntimeContext(
            user_id='nil',
            tenant_id='8888',
            project_id='agent',
            agent_registry=agent_registry
        )

        self.planner_agent = planner_builder(
            llm,
            tools=await tools_selector.for_agent('planner'),
            checkpointer=self.checkpoint,
            middlewares=middlewares.for_agent('planner'),
            store=self.store,
            context_schema=AppRuntimeContext
        )
        
        return self

    async def get_state_messages(self, thread_id: str, user_id: str):
        try:
            result = await self.planner_agent.aget_state(
                config={'configurable': {'thread_id': thread_id, 'user_id': user_id}}
            )
            messages = result.values.get('messages', [])
            return [{"type": type(m).__name__, "content": m.content} for m in messages]
        except Exception as e:
            return [{"type": "AIMessage", "content": str(e)}]

    async def get_state_history(self, thread_id: str, user_id: str):
        try:
            async for state in self.planner_agent.aget_state_history(
                config={'configurable': {'thread_id': thread_id, 'user_id': user_id}}
            ):
                return {
                    "values": {"messages": [{"type": type(m).__name__, "content": m.content} for m in state.values.get('messages', [])]},
                    "config": state.config,
                    "metadata": state.metadata
                }
        except Exception as e:
            return {"error": str(e)}
        return {}
    
    async def time_travel(self, config: dict):
        result = await self.planner_agent.ainvoke(None, config=config)
        return result

    async def invoke(self, thread_id: str, user_id: str, tenant_id: str, project_id: str, user_input: Optional[str] = None):
        try:
            query = {'messages': [HumanMessage(content=user_input)]} if user_input else None
            
            result = await self.planner_agent.ainvoke(
                query, 
                config={'configurable': {'thread_id': thread_id, 'user_id': user_id}}, 
                context=self.context
            )

            if isinstance(result, dict) and 'messages' in result:
                result['messages'] = [{"type": type(m).__name__, "content": m.content} for m in result['messages']]
            return result
        except Exception as e:
            return {'messages': [{"type": "AIMessage", "content": str(e)}]}

    async def aclose(self):

        if self.mcp_provider and hasattr(self.mcp_provider, 'close'):
            try:
                await self.mcp_provider.close()
            except Exception:
                pass

        if self.stack:
            await self.stack.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = AgentA()
    await agent.runtime()
    app.state.agent = agent
    yield
    await app.state.agent.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

class InvokeRequest(BaseModel):
    thread_id: str
    user_id: str
    tenant_id: str
    project_id: str
    user_input: Optional[str] = None

class StateRequest(BaseModel):
    thread_id: str
    user_id: str


@app.post("/agent/invoke")
async def invoke_agent(req: InvokeRequest, request: Request):
    agent: AgentA = request.app.state.agent
    return await agent.invoke(
        thread_id=req.thread_id,
        user_id=req.user_id,
        tenant_id=req.tenant_id,
        project_id=req.project_id,
        user_input=req.user_input
    )

@app.post("/agent/state/messages")
async def get_messages(req: StateRequest, request: Request):
    agent: AgentA = request.app.state.agent
    return await agent.get_state_messages(thread_id=req.thread_id, user_id=req.user_id)

@app.post("/agent/state/history")
async def get_history(req: StateRequest, request: Request):
    agent: AgentA = request.app.state.agent
    return await agent.get_state_history(thread_id=req.thread_id, user_id=req.user_id)

@app.post("/agent/time-travel")
async def time_travel(config: dict, request: Request):
    agent: AgentA = request.app.state.agent
    return await agent.time_travel(config=config)


# if __name__ == '__main__':
#     # Pass the local app instantiation context directly, with port explicitly parsed as an int
#     uvicorn.run(app, host='127.0.0.1', port=8050, loop='asyncio')