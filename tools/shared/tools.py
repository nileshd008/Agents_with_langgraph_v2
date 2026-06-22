

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from agents.state import MainRouter
from tools.decorators import registry_tool
import re
import json



@registry_tool(tags = 'all',
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool
def get_artifact(artifact_id: str, runtime: ToolRuntime):
    """
    Load artifact using artifact_id.
    
    """
    result = runtime.store.get(('manifest', runtime.config["configurable"]["user_id"]), artifact_id)
    manifest = result.value

    if manifest['mime_type'] == 'application/json':
        result = runtime.store.get(('artifact', runtime.config["configurable"]["user_id"]), artifact_id)
        data = result.value

        return {'messages': [ToolMessage(content = json.dumps(
            {
                'artifact_id': artifact_id,
                'artifact_type': 'json',
                'data': data
            },
            ensure_ascii = False,
            default = str
        )
        )]}


@registry_tool(tags = 'all',
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool(args_schema=MainRouter)
def update_state(runtime: ToolRuntime, **kwargs):
    """Update the application state with specific allowed keys."""
    try:
        patch = MainRouter(**kwargs)
        return Command(update = {**patch.model_dump(exclude_unset = True, exclude_none = True),
                                'messages': [ToolMessage(content = 'State Updated Successfully', tool_call_id = runtime.tool_call_id)]})
    except Exception as e:
        return {'messages': [ToolMessage(content = f'update schema error: {str(e)}')]}


@registry_tool(tags = 'all',
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool
def get_state(runtime: ToolRuntime):
    "get values of state variables"
    try:
        return {'messages': [ToolMessage(content = json.dumps({k: v for k, v in runtime.state.items() if k not in ('messages', 'structured_response')}), tool_call_id = runtime.tool_call_id)]}
    except Exception as e:
        return {'messages': [ToolMessage(content = f'update schema error: {str(e)}', tool_call_id = runtime.tool_call_id)]}
        