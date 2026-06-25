
from .prompt import ROUTING_PROMPT
from .state import PlnnerState
from langchain.agents import create_agent


def planner_builder(llm, tools, checkpointer, middlewares, store):
    return create_agent(
        name = 'planner',
        model = llm,
        system_prompt = ROUTING_PROMPT,
        state_schema = PlnnerState,
        tools = tools,
        middleware = middlewares,
        checkpointer = checkpointer,
        store = store

    )