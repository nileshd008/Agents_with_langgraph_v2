
from persistence.contracts import CheckPointerConfig, StoreConfig
from persistence.factories.checkpointer_factory import CheckpointerFactory, StoreFactory
from core.selectors import ToolSelector
from middleware.registry import MiddlewareRegistry
from middleware.selector import MiddlewaresSelectors
from tools.decorators import TOOLS_REGISTRY
from bootstrap import bootstrap
from langchain_openai import ChatOpenAI
from core.contracts import AppRuntimeContext
from config.servers import MCP_SERVER_CONFIG
from tools.mcp.providers import McpToolProvider
import os
from dotenv import load_dotenv
load_dotenv()

checkpointer = CheckPointerConfig(kind = 'memory')
store = StoreConfig(kind = 'memory')
McpToolProvider(MCP_SERVER_CONFIG).register_tools()
agent_selector = ToolSelector(TOOLS_REGISTRY)

llm = ChatOpenAI(
        model="Qwen/Qwen3-VL-235B-A22B-Instruct",
        api_key=os.environ["DEEPINFRA_API_KEY"],
        base_url="https://api.deepinfra.com/v1/openai",
        temperature=0.1,
        model_kwargs={"tool_choice": "auto"}
    )

agent_registry, planner_agent = bootstrap(llm=llm, selector = agent_selector, middleware_selectors =  MiddlewaresSelectors(MiddlewareRegistry()), store = store, checkpoint = checkpointer)


planner_agent.invoke({'messages': [{'role': 'user', 'content': 'hi'}]},
                    context = AppRuntimeContext(
                        user_id = 'nil',
                        tenant_id = '8888',
                        project_id = 'sql_gen',
                        agent_registry = agent_registry
                    ),
                     config = {'configuarable': {'thread_id': 'thread-12','user_id': 'nil'}}
                    )










