
from agents.sql.builder import sql_builder
from agents.visualization.builder import visualization_builder
from agents.planner.builder import planner_builder
from agents.registry import AgentRegistry


AgentContext




def bootstrap(llm, selector, middleeare_selector, store, checkpoint):

    planner_tools = selector.for_agents('planner')
    sql_tools = selector.for_agents('sql')
    visualization_tools = selector.for_agents('visualization')

    

    sql_agent = sql_builder(llm,
                            sql_tools,
                            checkpoint,
                            middleeare_selector.for_agent('sql'),
                            store)
    
    visulization_agent = visualization_builder(llm,
                            visualization_tools,
                            checkpoint,
                            middleeare_selector.for_agent('visualization'),
                            store = store)
    
    planner_agent = planner_builder(llm,
                            planner_tools, 
                            checkpoint, 
                            middleeare_selector.for_agent('planner'),
                            store = store)
    
    agent_registry = AgentRegistry()
    agent_registry.register('sql', sql_agent)
    agent_registry.register('visualization', visulization_agent)
    

    return agent_registry, planner_agent


