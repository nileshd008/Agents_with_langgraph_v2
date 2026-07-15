
from dataclasses import dataclass, field
from typing import Literal
from agents.registry import AgentRegistry

TOOL_VISIBILITY = Literal['private', 'shared']
TOOLSOURCE = Literal['local', 'mcp']

@dataclass(frozen=True)
class ToolMeta:
    source :str = 'local'
    visibility: str = 'private'
    server_name: str = None
    allowed_agents : set[str] = field(default_factory= True)
    tags : set[str] = field(default_factory = True)
    domains: set[str] = field(default_factory = True)


@dataclass(frozen=True)
class AppRuntimeContext:
    user_id: str
    project_id: str
    agent_registry: AgentRegistry
    tenant_id: str
