import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -------------------------------
# 🎨 PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="StudyBot AI", page_icon="🤖", layout="centered")

# -------------------------------
# 🌙 CUSTOM STYLE (PREMIUM LOOK)
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
.chat-bubble-user {
    background-color: #3b82f6;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    color: white;
}
.chat-bubble-bot {
    background-color: #334155;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 StudyBot AI Assistant")

# -------------------------------
# 🔑 API KEY
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

# -------------------------------
# 🤖 AI MODEL
# -------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are StudyBot, a smart academic tutor.\n"
     "Explain answers like a teacher using:\n"
     "- Headings\n- Bullet points\n- Examples\n"
     "Keep language simple and clear.\n"
     "If needed, give real-life examples."),
    ("user", "{question}")
])

chain = prompt | llm

# -------------------------------
# 🧠 CHAT MEMORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# 💬 INPUT
# -------------------------------
user_input = st.chat_input("Ask your study question...")

if user_input:
    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
                response = chain.invoke({"question": user_input})
                reply = response.content
            except:
                reply = "⚠️ Error: Check API key or try again"

        st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
