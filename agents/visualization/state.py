

from agents.state import MainRouter
from pydantic import ConfigDict, Field
from typing import Annotated, List, Optional
from langgraph.graph.message import add_messages



class VisualizeState(MainRouter):
    model_config = ConfigDict(extra='ignore')
    messages: Annotated[List[dict], add_messages]
    #structured_response: Optional[VISUALIZATIONOUTPUT] = Field(default = None, description = 'Response From Model') 
