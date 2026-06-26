
from core.contracts import AppRuntimeContext
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
import asyncio

class AppRuntime:
    def __init__(self, store, checkpoint, planner_agent, agent_registry):
        self.store = store
        self.checkpoint = checkpoint
        self.planner_agent = planner_agent
        self.agent_registry = agent_registry

    def get_state_messages(self, thread_id: str, user_id:str):
        return self.planner_agent.get_state(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}}).values['messages']
    
    def get_state_history(self, thread_id, user_id):
        "fault tolerance implementation in langgraph"
        return next(iter(self.planner_agent.get_state_history(config = {'configurable':{'thread_id': thread_id,'user_id': user_id}}))).next

    def invoke(self, thread_id: str, user_id:str, tenant_id:str, project_id:str, user_input:str = None):
        
        context = AppRuntimeContext(
                            user_id =  user_id,
                            tenant_id = tenant_id,
                            project_id = project_id,
                            agent_registry = self.agent_registry
                        )
        if user_input:  
            return self.planner_agent.invoke({'messages': [HumanMessage(content = user_input)]}, 
                                            context = context, 
                                            config = {'configurable':{'thread_id': thread_id,'user_id': user_id}})
        else:
            return self.planner_agent.invoke(None, 
                                            context = context, 
                                            config = {'configurable':{'thread_id': thread_id,'user_id': user_id}})

