from langchain.agents.middleware import wrap_tool_call, after_model
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

@wrap_tool_call
def store_artifact(request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage | Command]):
    result = handler(request)
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

            request.runtime.store.put(('artifact', config['user_id']), artifact_id, data)

            mime_type = "application/json"
            artifact_type = "json"

            request.runtime.store.put(
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
            
            request.runtime.store.put(('artifact', config['user_id']), artifact_id, html)
            
            mime_type = "text/html"
            artifact_type = "plotly_html"
            
            request.runtime.store.put(('manifest', config['user_id']), artifact_id,
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

