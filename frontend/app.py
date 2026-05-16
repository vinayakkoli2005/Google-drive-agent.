import streamlit as st
import requests
import uuid
import os

st.set_page_config(
    page_title="TailorTalk - Drive Agent",
    page_icon="📂",
    layout="centered"
)

st.markdown("""
<style>
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    .user-msg {
        background-color: #2b313e;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .bot-msg {
        background-color: #1e2329;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #4a90e2;
    }
</style>
""", unsafe_allow_html=True)

st.title("📂 Drive Discovery Agent")
st.markdown("Ask me to find, filter, or discover files in your designated Google Drive folder!")

# Streamlit Cloud uses st.secrets; fallback to env var for local/other platforms
try:
    _backend = st.secrets["BACKEND_URL"]
except Exception:
    _backend = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

API_URL = _backend.rstrip("/") + "/chat"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("E.g., Find the financial report from last week"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"message": prompt, "session_id": st.session_state.session_id},
                    timeout=60,
                )
                if response.status_code == 200:
                    data = response.json()
                    ai_text = data["response"]
                    # Keep the session_id returned by backend (consistent across restarts)
                    if data.get("session_id"):
                        st.session_state.session_id = data["session_id"]
                    st.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Make sure the FastAPI server is running or BACKEND_URL is set correctly.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The agent may be processing a complex query — please try again.")
