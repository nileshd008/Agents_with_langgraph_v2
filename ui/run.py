import streamlit as st
import requests
import os

API_URL = os.getenv('BACKEND_API_URL')


if "thread_id" not in st.session_state:
    st.session_state.thread_id = "session_abc_123"
    st.session_state.user_id = "user_456"
    st.session_state.tenant_id = "8888"
    st.session_state.project_id = "agent"
    st.session_state.chat_history = []

    try:
        response = requests.post(
            f"{API_URL}/agent/state/messages", 
            json={"thread_id": st.session_state.thread_id, "user_id": st.session_state.user_id}
        )
        if response.status_code == 200:
            st.session_state.chat_history = response.json()
    except Exception as e:
        st.error(f"Failed to pull initialization state: {e}")

for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["type"] == "HumanMessage" else "assistant"):
        st.write(msg["content"])


if user_input := st.chat_input("Ask something..."):
    with st.chat_message("user"):
        st.write(user_input)

    payload = {
        "thread_id": st.session_state.thread_id,
        "user_id": st.session_state.user_id,
        "tenant_id": st.session_state.tenant_id,
        "project_id": st.session_state.project_id,
        "user_input": user_input
    }
    
    res = requests.post(f"{API_URL}/agent/invoke", json=payload).json()

    for msg in res.get("messages", []):
        if msg["type"] == "AIMessage":
            with st.chat_message("assistant"):
                st.write(msg["content"])