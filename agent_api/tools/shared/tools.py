from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from agents.state import PlannerStateUpdate
from tools.decorators import registry_tool
from langchain.tools import ToolException
from typing import Optional, Literal
import re
import json

@registry_tool(tags = ['all'],
        domains = ['tool'],
        source = 'local',
        visibility = 'shared',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool
async def get_artifact(artifact_id: str, runtime: ToolRuntime):
    """
    Load artifact using artifact_id.
    """
    result = await runtime.store.aget(('manifest', runtime.config["configurable"]["user_id"]), artifact_id)
    manifest = result.value

    if manifest['mime_type'] == 'application/json':
        result = await runtime.store.aget(('artifact', runtime.config["configurable"]["user_id"]), artifact_id)
        data = result.value

        return json.dumps(
            {
                'artifact_id': artifact_id,
                'artifact_type': 'json',
                'data': data
            },
            ensure_ascii = False,
            default = str
        )

@registry_tool(tags = 'all',
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool
async def update_state(
    runtime: ToolRuntime,
    intent: Optional[Literal["SQL_ONLY", "SQL_AND_VIZ", "CLARITY"]] = None,
    viz_requested: Optional[Literal["bar_chart", "line_chart", "pie_chart", "table", "none"]] = None,
    clarifying_question: Optional[str] = None,
    assumptions: Optional[str] = None,
    user_session_summary: Optional[str] = None,
    last_invocation_query: Optional[str] = None,
    table_schema_artifact: Optional[str] = None,
    last_validated_sql: Optional[str] = None,
    final_query_status: Optional[Literal["SUCCESS", "FAIL_NEEDS_CLARIFICATION", "FAIL_MAX_RETRIES"]] = None,
    viz_status: Optional[Literal["SUCCESS", "FAIL_MAX_RETRIES", "NOT_GENERATED"]] = None,
    viz_artifact: Optional[str] = None,
):
    """Update the planner state. Only supplied fields are modified."""
    try:
        patch = PlannerStateUpdate(
            intent=intent,
            viz_requested=viz_requested,
            clarifying_question=clarifying_question,
            assumptions=assumptions,
            user_session_summary=user_session_summary,
            last_invocation_query=last_invocation_query,
            table_schema_artifact=table_schema_artifact,
            last_validated_sql=last_validated_sql,
            final_query_status=final_query_status,
            viz_status=viz_status,
            viz_artifact=viz_artifact,
        )

        update = patch.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        update["messages"] = [
            ToolMessage(
                content="State updated successfully",
                tool_call_id=runtime.tool_call_id,
            )
        ]

        return Command(update=update)

    except Exception as e:
        raise ToolException(str(e))


@registry_tool(tags = 'all',
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = ['planner', 'sql', 'visualization'],
        server_name = None)
@tool
async def get_state(runtime: ToolRuntime):
    "get values of state variables"
    try:
        return json.dumps({k: v for k, v in runtime.state.items() if k not in ('messages', 'structured_response')})
    except Exception as e:
        return str(e)