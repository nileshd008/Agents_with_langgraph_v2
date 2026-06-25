
from agents.sql.builder import sql_builder
from agents.visualization.builder import visualization_builder
from agents.planner.builder import planner_builder
from agents.registry import AgentRegistry
from .runtime import AppRuntime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os

def initialize(llm, selector, middleware_selectors, store, checkpoint):

    sql_agent = sql_builder(llm,
                            selector.for_agent('sql'),
                            checkpoint,
                            middleware_selectors.for_agent('sql'),
                            store
    )
    
    visulization_agent = visualization_builder(llm,
                            selector.for_agent('visualization'),
                            checkpoint,
                            middleware_selectors.for_agent('visualization'),
                            store = store
    )
    
    planner_agent = planner_builder(llm,
                            selector.for_agent('planner'), 
                            checkpoint, 
                            middleware_selectors.for_agent('planner'),
                            store = store
    )
    
    # Register Agents
    agent_registry = AgentRegistry()
    agent_registry.register('sql', sql_agent)
    agent_registry.register('visualization', visulization_agent)
    
    return AppRuntime(store, checkpoint, planner_agent, agent_registry)


