
AGENT_MCP_ACCESS_CONF = {
  'planner':{
    'enable_mcp': True,
    'mcp_servers': ['local_mcp'],
    'middleware': ['store_artifact','query_sanitizer']
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
