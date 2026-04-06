import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -------------------------------
# ⚙️ CONFIG
# -------------------------------
st.set_page_config(page_title="StudyBot", page_icon="🤖")
st.title("🤖 StudyBot AI Assistant")

# -------------------------------
# 🔑 GET API KEY (IMPORTANT)
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

# -------------------------------
# 🤖 AI SETUP
# -------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are StudyBot, an academic assistant.\n"
     "Answer using:\n"
     "- Headings\n- Bullet points\n- Examples\n"
     "Explain in simple language."),
    ("user", "{question}")
])

chain = prompt | llm

# -------------------------------
# 🧠 CHAT HISTORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# 💬 INPUT
# -------------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = chain.invoke({
                    "question": user_input
                })
                reply = response.content
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.write(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
