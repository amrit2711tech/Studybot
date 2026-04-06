import os
import streamlit as st

# Safe import (no crash if package issue)
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# -------------------------------
# 🎨 UI CONFIG
# -------------------------------
st.set_page_config(page_title="StudyBot", page_icon="🤖")
st.title("🤖 StudyBot AI Assistant")

# -------------------------------
# 🔑 GET API KEY
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")

# -------------------------------
# 🤖 AI SETUP (SAFE)
# -------------------------------
chain = None

if AI_AVAILABLE and groq_api_key:
    try:
        llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are StudyBot. Answer using:\n"
             "- Headings\n- Bullet points\n- Examples\n"
             "Explain in simple language."),
            ("user", "{question}")
        ])

        chain = prompt | llm
    except:
        chain = None

# -------------------------------
# 🧠 CHAT HISTORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# 💬 USER INPUT
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

    # -------------------------------
    # 🤖 GENERATE RESPONSE
    # -------------------------------
    if chain:
        try:
            response = chain.invoke({
                "question": user_input
            })
            reply = response.content
        except Exception as e:
            reply = "⚠️ API Error: Check your GROQ API key"
    else:
        if not groq_api_key:
            reply = "⚠️ GROQ_API_KEY missing. Add it in Secrets."
        elif not AI_AVAILABLE:
            reply = "⚠️ AI packages not installed"
        else:
            reply = "⚠️ AI not initialized"

    # Show bot reply
    with st.chat_message("assistant"):
        st.write(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
