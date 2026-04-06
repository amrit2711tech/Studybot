import os
import streamlit as st

# Safe import (no crash)
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    AI_READY = True
except:
    AI_READY = False

# -------------------------------
# 🎨 UI CONFIG
# -------------------------------
st.set_page_config(page_title="StudyBot AI", page_icon="🤖")

# Premium header
st.markdown("<h1 style='text-align:center;'>🤖 StudyBot AI Assistant</h1>", unsafe_allow_html=True)

# -------------------------------
# 🔑 API KEY
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")

# -------------------------------
# 🤖 AI SETUP
# -------------------------------
chain = None

if AI_READY and groq_api_key:
    try:
        llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are StudyBot, a smart academic tutor.\n"
             "Explain using:\n"
             "- Headings\n- Bullet points\n- Examples\n"
             "Keep answers simple and clear."),
            ("user", "{question}")
        ])

        chain = prompt | llm
    except Exception as e:
        st.error(f"AI Setup Error: {e}")

# -------------------------------
# 🧠 CHAT MEMORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
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

    # -------------------------------
    # 🤖 RESPONSE
    # -------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):

            if not groq_api_key:
                reply = "⚠️ API key missing. Add GROQ_API_KEY in Secrets."
            elif not AI_READY:
                reply = "⚠️ AI libraries not installed properly."
            elif chain:
                try:
                    response = chain.invoke({"question": user_input})
                    reply = response.content
                except Exception as e:
                    reply = f"⚠️ API Error: {str(e)}"
            else:
                reply = "⚠️ AI not initialized."

        st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
