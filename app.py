import streamlit as st
import requests

# -------------------------------
# ⚙️ CONFIG
# -------------------------------
API_URL = "https://studybot-hw9k.onrender.com/chat"  # your backend

st.set_page_config(page_title="StudyBot", page_icon="🤖")

# -------------------------------
# 🧠 SESSION STATE (Chat History)
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# 🎨 UI
# -------------------------------
st.title("🤖 StudyBot AI Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# 💬 INPUT
# -------------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Send to API
    try:
        response = requests.post(
            API_URL,
            json={
                "user_id": "user_1",
                "question": user_input
            }
        )

        data = response.json()
        bot_reply = data.get("response", "No response")

    except:
        bot_reply = "⚠️ Error connecting to backend"

    # Show bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.write(bot_reply)
