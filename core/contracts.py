
from dataclasses import dataclass, field
from typing import Literal

TOOL_VISIBILITY = Literal['private', 'shared']
TOOLSOURCE = Literal['local', 'mcp']

@dataclass(frozen=True)
class ToolMeta:
    tags : set[str] = field(default_factory = set)
    domains: set[str] = field(default_factory = set)
    source : TOOLSOURCE = 'local'
    visibility: TOOL_VISIBILITY = 'private'
    allowed_agents : set[str] = field(default_factory= True)
    server_name: str = None


@dataclass(frozen=True)
class AppRuntimeContext:
    user_id: str
    tenant_id: str = field(default = None)
    project_id: str
    agent_registry: object



