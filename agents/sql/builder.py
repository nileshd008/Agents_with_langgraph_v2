
from .prompt import SQL_SPECIALIST_PROMPT
from .state import SqlState
from langchain.agents import create_agent


def sql_builder(llm, tools, checkpointer, middlewares, store):
    
    return create_agent(
        name = 'sql',
        model = llm,
        system_prompt = SQL_SPECIALIST_PROMPT,
        state_schema = SqlState,
        tools = tools,
        middleware = middlewares,
        checkpointer = checkpointer,
        store = store

    )