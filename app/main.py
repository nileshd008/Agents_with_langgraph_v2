
from persistence.contracts import CheckPointerConfig, StoreConfig
from persistence.checkpointer_factory import CheckpointerFactory, StoreFactory
from core.selectors import ToolSelector
from tools.planner import tools
from tools.shared import tools

from middleware.registry import MiddlewareRegistry
from middleware.selector import MiddlewaresSelectors
from tools.decorators import TOOL_REGISTRY
from .bootstrap import initialize
from langchain_openai import ChatOpenAI
from core.contracts import AppRuntimeContext
from config.mcp_servers import MCP_SERVER_CONFIG
from tools.mcp.providers import McpToolProvider
import os
from dotenv import load_dotenv
from .runtime import AppRuntime
load_dotenv()

def run():
    # Mcp tool Registry
    McpToolProvider(MCP_SERVER_CONFIG).register_tools()
    
    # LLM
    llm = ChatOpenAI(
        model="Qwen/Qwen3-VL-235B-A22B-Instruct",
        api_key=os.environ["DEEPINFRA_API_KEY"],
        base_url="https://api.deepinfra.com/v1/openai",
        temperature=0.1,
        model_kwargs={"tool_choice": "auto"}
    )

    return initialize(llm = llm, 
                      selector = ToolSelector(TOOL_REGISTRY), 
                      middleware_selectors =  MiddlewaresSelectors(MiddlewareRegistry()), 
                      store = StoreFactory(StoreConfig(kind = 'sqlite', connection_str='agent.db')).create(), 
                      checkpoint = CheckpointerFactory(CheckPointerConfig(kind = 'sqlite', connection_str='agent.db')).create())
