from langchain.agents.middleware import wrap_tool_call, after_model, before_agent
from langgraph.runtime import Runtime
from agents.planner.state import PlnnerState
from langchain.tools.tool_node import ToolCallRequest
from typing import Callable
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
import json
import hashlib
import uuid
import json
import plotly.io as pio
from pathlib import Path
from agents.guard_agent.builder import guard_llm
from agents.guard_agent.prompt import final_prompt

@wrap_tool_call
async def store_artifact(request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage | Command]):
    result = await handler(request)
    runtime = request.runtime
    config = runtime.config['configurable']

    if (
        request.tool_call
        and request.tool_call["name"].lower() == "get_sql_table_schema"
    ):

        payload = json.loads(result.content[0]["text"])
        if payload['status'].lower() == 'success':
        
            data = json.dumps(payload['data'])
            artifact_id = hashlib.sha256(data.encode('utf-8')).hexdigest()

            await request.runtime.store.aput(('artifact', config['user_id']), artifact_id, data)

            mime_type = "application/json"
            artifact_type = "json"

            await request.runtime.store.aput(
                ('manifest', config['user_id']),
                artifact_id,
                {
                    "schema_version": "1.0",
                    'description': 'Database Table schema',
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "mime_type": mime_type,
                    "source_tool_name": request.tool_call['name'],
                    "source_tool_call_id": request.tool_call['id'],
                    "visibility": 'assistant',
                    "rendering": False
                }
            )
            
            artifact_ref = {
                'description': 'Database Table schema',
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "mime_type": mime_type,
                "visibility": 'assistant',
                "rendering": False
            }

            payload["data"] = artifact_ref
            result.content[0]["text"] = json.dumps(payload)
            result.artifact = artifact_ref

            return result
    if (
        request.tool_call
        and request.tool_call['name'].lower() == 'execute_graph'
    ):
        payload = json.loads(result.content[0]['text'])

        if payload['status'].lower() == 'success': 
            artifact_id = hashlib.sha256(payload['data'].encode('utf-8')).hexdigest()
            html = pio.to_html(pio.from_json(payload['data']), include_plotlyjs=True, full_html=True)
            
            await request.runtime.store.aput(('artifact', config['user_id']), artifact_id, html)
            
            mime_type = "text/html"
            artifact_type = "plotly_html"
            
            await request.runtime.store.aput(('manifest', config['user_id']), artifact_id,
                {   
                    "schema_version": "1.0",
                    'description': 'Plolty visualization Graph',
                    'artifact_id': artifact_id,
                    'artifact_type': artifact_type,
                    'mime_type': mime_type,
                    'uri': f"http://localhost:8000/view/{config['user_id']}/{artifact_id}",
                    "source_tool_name": request.tool_call['name'],
                    "source_tool_call_id": request.tool_call['id'],
                    "visibility": 'user',
                    "rendering": True
                })

            artifact_ref = {
                'description': 'Plolty visualization Graph',
                'artifact_id': artifact_id,
                'artifact_type': artifact_type,
                'mime_type': mime_type,
                'uri': f"http://localhost:8000/view/{config['user_id']}/{artifact_id}",
                "visibility": 'user',
                "rendering": True
            }
            
            payload['data'] = artifact_ref
            result.content[0]['text'] = json.dumps(payload)
            result.artifact = artifact_ref
        
        return result

    return result


@before_agent(can_jump_to=['end'])
async def query_sanitizer(state: PlnnerState, runtime: Runtime):
    
    if len(state['messages']) > 0 and isinstance(state['messages'][-1], AIMessage):
        return {'jump_to': 'end'}
    
    all_histry = [i for i in state['messages'] if isinstance(i, HumanMessage)]

    if all_histry:
        last_user_query = all_histry[-1].content

    else:
        return {'jump_to': 'end'}
    
    if len(all_histry) > 1 and all_histry[-2]:
        previous_user_query =  all_histry[-2].content

    else:
        previous_user_query = None
    
    prompt = final_prompt.format(last_user_query, previous_user_query, state.get('user_session_summary', None), state.get('intent', None), state.get('last_validated_sql', None))
    prompt = """RETURN JSON ONLY:
        {
        "label": "SAME_SQL_CONTINUE_OR_MODIFY|NEW_SQL_REQUEST",
        "reason": "short reason"
        }"""
    
    result = guard_llm.invoke(prompt)

    if result.content.strip().split()[-1] == 'safe':
        return {}
    
    else:
        return {'messages': [AIMessage(content = 'Special result not allowed')], 'jump_to': 'end'}