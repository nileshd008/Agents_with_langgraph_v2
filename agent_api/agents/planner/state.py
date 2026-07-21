from pydantic import ConfigDict, Field
from typing import Annotated, List, Optional, Literal
from langgraph.graph.message import add_messages
from langchain.agents import AgentState

class PlnnerState(AgentState):
    model_config = ConfigDict(extra="ignore")
    intent: Literal['SQL_ONLY', 'SQL_AND_VIZ', 'CLARITY'] = 'SQL_ONLY'
    viz_requested: Optional[Literal['bar_chart','line_chart','pie_chart','table','none']] = None
    clarifying_question: Optional[str] = None
    assumptions: Optional[str] = None
    user_session_summary: Optional[str] = None
    last_invocation_query: Optional[str] = None
    current_invocation_query: Optional[str] = None
    table_schema_artifact: Optional[str] = None
    last_validated_sql: Optional[str] = None
    final_query_status: Optional[Literal['SUCCESS','FAIL_NEEDS_CLARIFICATION','FAIL_MAX_RETRIES']] = None
    viz_status: Literal['SUCCESS','FAIL_MAX_RETRIES','NOT_GENERATED'] = 'NOT_GENERATED'
    viz_artifact: Optional[str] = None
