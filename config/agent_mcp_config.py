

# config for mcp serves to agents


AGENT_MCP_ACCESS_CONF = {
  'planner':{
    'enable_mcp': False,
    'mcp_servers': [],
    'middleware': ['store_artifact']
  },
  'sql':{
    'enable_mcp': True,
    'mcp_servers': ['local_mcp'],
    'middleware': ['store_artifact']
  },
  'visualization':{
    'enable_mcp': True,
    'mcp_servers': ['local_mcp'],
    'middleware': ['store_artifact']
  }
}
