
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from tools.decorators import registry_tool
from core.contracts import AppRuntimeContext
import re
import asyncio
import copy


@registry_tool(tags = ['plnner_tool'],
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner'],
        server_name = None)
@tool
async def sql_specialist(query: str, runtime: ToolRuntime):
    """You are specialized text-to-sql Agent to Generate SQL query from user question."""
    
  
    clean_state = copy.deepcopy(runtime.state)
    clean_state['messages'] = [HumanMessage(content = query)]

    sub_config = {"configurable": {}}
    sub_config['configurable']['thread_id'] = 'thread-sql-' + re.search(r'\-(\d+)$', runtime.config['configurable']['thread_id']).group(1)
    sub_config['configurable']['user_id'] = runtime.config['configurable']['user_id']


    result = await runtime.context.agent_registry.get('sql').ainvoke({'messages': [HumanMessage(content = query)]}, config = sub_config, context = runtime.context)
    state = await runtime.context.agent_registry.get('sql').aget_state(config = sub_config)

    print('messages from sql_specialist',state.values['messages'])
    
    sub_agent_state = {i: state.values[i] for i in state.values if i not in ['messages', 'structured_response']}
    sub_agent_state['messages'] = [ToolMessage(content = result['messages'][-1].content, tool_call_id = runtime.tool_call_id, name = 'sql_specialist')]
    return Command(update = sub_agent_state)



@registry_tool(tags = ['plnner_tool'],
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner'],
        server_name = None)
@tool
async def visualization_tool(query: str, runtime: ToolRuntime[AppRuntimeContext]):
    """
    You are specialized Visualizer + Validator for sql query using plotly.
    args:
        query - instructions to visualization agent
    """
    try:
        clean_state = {k: v for k, v in runtime.state.items() if k not in ('messages', 'structured_response')}

        viz_config = {"configurable": {**runtime.config.get("configurable", {})}}
        viz_config['configurable']['thread_id'] = 'thread-visual-' + re.search(r'\-(\d+)$', runtime.config['configurable']['thread_id']).group(1)

        result = await runtime.context.agent_registry.get('visualization').ainvoke({**clean_state, 'messages' : [HumanMessage(content = query)]}, config = viz_config)

        return Command(update = {**result.model_dump(exclude={"messages", "structured_response"}),
                                'messages': [ToolMessage(content = result['messages'][-1].content, tool_call_id = runtime.tool_call_id)]})

    except Exception as e:
            return str(e)
