import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage, ToolMessage, SystemMessage
import asyncio
from threading import Thread
import sys
from pathlib import Path
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import run
import uuid


@st.cache_resource
def load_runtime():
    return run()

if 'runtime' not in st.session_state:
    st.session_state.runtime = load_runtime()


if 'runtime' in st.session_state:
    st.session_state.messages = st.session_state.runtime.get_state_messages(thread_id='thread-101', user_id='nil')


for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message('user'):
            st.text(message.content)

    if isinstance(message, AIMessage):
        with st.chat_message('assistant'):
            st.text(message.content)
    

input = st.chat_input('Describe your query')
st.session_state.snapshop = st.session_state.runtime.get_state_history(thread_id='thread-101', user_id='nil')

if input or st.session_state.snapshop:
    if st.session_state.snapshop:
        result = st.session_state.runtime.invoke(thread_id = 'thread-101', user_id = 'nil', tenant_id = '8888', project_id = 'sql_agent', user_input = None)

    else:
        with st.chat_message('user'):
            st.text(input)
        
        result = st.session_state.runtime.invoke(thread_id = 'thread-101', user_id = 'nil', tenant_id = '8888', project_id = 'sql_agent', user_input = input)

        with st.chat_message('assistant'):
            st.text(result['messages'][-1].content)



