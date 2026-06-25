

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from tools.decorators import registry_tool
import re


@registry_tool(tags = ['plnner_tool'],
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner'],
        server_name = None)
@tool
def sql_specialist(query: str, runtime: ToolRuntime):
    """You are specialized text-to-sql Agent to Generate SQL query from user question."""
    
    try:
        clean_state = {k: v for k, v in runtime.state.items() if k not in ('messages', 'structured_response')}
        
        sub_agent_input = {**clean_state, 'messages': [HumanMessage(content = query)]}
        sub_config = {"configurable": {**runtime.config.get("configurable", {})}}
        sub_config['configurable']['thread_id'] = 'thread-sql-' + re.search(r'\-(\d+)$', runtime.config['configurable']['thread_id']).group(1)

        result = runtime.context.agent_registry.get('sql').invoke(sub_agent_input, config = sub_config)
    
        return Command(update = {**result.model_dump(exclude={"messages", "structured_response"}),
                                'messages': [ToolMessage(content = result['messages'][-1].content, tool_call_id = runtime.tool_call_id)]})
        
    except Exception as e:
        print("this is error from tool", str(e))
        return {'messages': [ToolMessage(content = f'update schema error: {str(e)}', tool_call_id = runtime.tool_call_id)]}


@registry_tool(tags = ['plnner_tool'],
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner'],
        server_name = None)
@tool
def visualization_tool(query: str, runtime: ToolRuntime):
    """
    You are specialized Visualizer + Validator for sql query using plotly.
    args:
        query - instructions to visualization agent
    """
    try:
        clean_state = {k: v for k, v in runtime.state.items() if k not in ('messages', 'structured_response')}

        viz_config = {"configurable": {**runtime.config.get("configurable", {})}}
        viz_config['configurable']['thread_id'] = 'thread-visual-' + re.search(r'\-(\d+)$', runtime.config['configurable']['thread_id']).group(1)

        result = runtime.context.agent_registry.get('visualization').invoke({**clean_state, 'messages' : [HumanMessage(content = query)]}, config = viz_config)

        return Command(update = {**result.model_dump(exclude={"messages", "structured_response"}),
                                'messages': [ToolMessage(content = result['messages'][-1].content, tool_call_id = runtime.tool_call_id)]})

    except Exception as e:
            return {'messages': [ToolMessage(content = f'update schema error: {str(e)}')]}
