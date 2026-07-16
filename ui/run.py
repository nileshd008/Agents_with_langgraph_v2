import streamlit as st
import requests
import os
import uuid
import time

API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

def touch_session(thread_id):
    """Updates the last touched time for a session to now."""
    st.session_state.all_sessions[thread_id] = time.time()

if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = {}


st.sidebar.title("Chat Management")

if st.sidebar.button("New Chat Session", use_container_width=True):
    for key in ["thread_id", "chat_history"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("History Logs")


sorted_sessions = sorted(
    st.session_state.all_sessions.items(), 
    key=lambda x: x[1], 
    reverse=True
)


for past_id, _ in sorted_sessions:
    is_active = "🔹 " if ("thread_id" in st.session_state and st.session_state.thread_id == past_id) else "📄 "
    if st.sidebar.button(f"{is_active}{past_id}", key=f"btn_{past_id}", use_container_width=True):
        st.session_state.thread_id = past_id
        st.session_state.chat_history = [] 
        
        touch_session(past_id)
        
        try:
            response = requests.post(
                f"{API_URL}/agent/state/messages", 
                json={"thread_id": st.session_state.thread_id, "user_id": st.session_state.user_id}
            )
            if response.status_code == 200:
                st.session_state.chat_history = response.json()
        except Exception as e:
            st.error(f"Failed to reload session: {e}")
        st.rerun()


if "thread_id" not in st.session_state:
    new_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.thread_id = new_id
    
    touch_session(new_id)
        
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


if st.session_state.thread_id not in st.session_state.all_sessions:
    touch_session(st.session_state.thread_id)


for msg in st.session_state.chat_history:
    content = msg.get("content", "").strip()
    if not content:
        continue

    role = "user" if msg.get("type") == "HumanMessage" else "assistant"
    with st.chat_message(role):
        st.write(content)

if user_input := st.chat_input("Ask something..."):

    with st.chat_message("user"):
        st.write(user_input)

    touch_session(st.session_state.thread_id)

    payload = {
        "thread_id": st.session_state.thread_id,
        "user_id": st.session_state.user_id,
        "tenant_id": st.session_state.tenant_id,
        "project_id": st.session_state.project_id,
        "user_input": user_input,
    }

    try:
        response = requests.post(f"{API_URL}/agent/invoke", json=payload)
        response.raise_for_status()

        res = response.json()

        if "messages" in res:
            st.session_state.chat_history = res["messages"]
        elif "output" in res:
            st.session_state.chat_history = res["output"].get("messages", [])

        touch_session(st.session_state.thread_id)
        st.rerun()

    except Exception as e:
        st.error(f"API invocation failed: {e}")