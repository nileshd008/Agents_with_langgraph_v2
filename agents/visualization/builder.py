
from .prompt import VISUALIZATION_PROMPT
from .state import VisualizeState
from langchain.agents import create_agent


def visualization_build(llm, tools, checkpointer, middlewares, store):

    return create_agent(
        name = 'visualization',
        model = llm,
        system_prompt = VISUALIZATION_PROMPT,
        state_schema = VisualizeState,
        tools = tools,
        middleware = middlewares,
        checkpointer = checkpointer,
        store = store
    )