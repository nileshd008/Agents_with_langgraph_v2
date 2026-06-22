
from core.contracts import ToolMeta

TOOL_REGISTRY = []

def registry_tool(
        *,
        tags = None,
        domains = None,
        source = 'local',
        visibility = 'private',
        allowed_agents = None,
        server_name = None
):
    tags = set(tags or [])
    domains = set(domains or [])
    allowed_agents = set(allowed_agents or [])

    def docorator(tool_obj):
        tool_obj._tool_meta = ToolMeta(
            tags = tags,
            domains = domains,
            source = source,
            allowed_agents = allowed_agents,
            visibility = visibility
        )

        TOOL_REGISTRY.append(tool_obj)
        return tool_obj
    
    return docorator



def register_external_tool(tool_obj, source, server_name):
    tags = set(tags or [])
    domains = set(domains or [])
    allowed_agents = set(allowed_agents or [])


    tool_obj._tool_meta = {
        'source': source,
        'server_name': server_name
        }
    
    TOOL_REGISTRY.append(tool_obj)


