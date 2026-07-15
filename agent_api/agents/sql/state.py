

from agents.state import MainRouter
from pydantic import ConfigDict, Field
from typing import Annotated, List, Optional
from langgraph.graph.message import add_messages




class SqlState(MainRouter):
    model_config = ConfigDict(extra='ignore')
    messages: Annotated[List[dict], add_messages]
    #structured_response: Optional[SQLOUTPUT] = Field(default = None, description = 'Response From Model') 
