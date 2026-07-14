import os
from dotenv import load_dotenv
load_dotenv()





MCP_SERVER_CONFIG = {
    "local_mcp": {
        "command": "python",
        "args": ["tools/mcp/server.py"],
        "transport": "stdio",
        "env": {
            "database_name": os.getenv('database_name'),
            "connection_name": os.getenv('connection_name'),
            "username": os.getenv('username'),
            "db_passward": os.getenv('db_passward'),
            "sandbox_connection": os.getenv('sandbox_connection'),
            'PYTHONBREAKPOINT': '0'
        },
    },

}