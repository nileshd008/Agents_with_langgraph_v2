import os
from pathlib import Path




MCP_SERVER_CONFIG = {
"local_mcp": {
    "transport": "http",
    "url": f"{os.environ['MCP_SERVER_URL']}"}
}


# MCP_SERVER_CONFIG = {
#     "local_mcp": {
#         "command": "python",
#         "args": [mcp_server_path],
#         "transport": "stdio",
#         "env": {
#             "database_name": os.getenv('database_name'),
#             "connection_name": os.getenv('connection_name'),
#             "username": os.getenv('username'),
#             "db_passward": os.getenv('db_passward'),
#             "sandbox_connection": os.getenv('sandbox_connection'),
#             'PYTHONBREAKPOINT': '0'
#         },
#     },

# }