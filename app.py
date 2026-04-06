import os
import streamlit as st

# Try importing AI (safe)
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# -------------------------------
# ⚙️ CONFIG
# -------------------------------
st.set_page_config(page_title="StudyBot", page_icon="🤖")

st.title("🤖 StudyBot AI Assistant")

# -------------------------------
# 🧠 SESSION (Chat History)
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# 🔑 GET API KEY
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")

# -------------------------------
# 🤖 AI SETUP (SAFE)
# -------------------------------
if AI_AVAILABLE and groq_api_key:
    try:
        llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are StudyBot. Answer clearly using:\n"
             "- Headings\n- Bullet points\n- Examples\n- Simple language"),
            ("user", "{question}")
        ])

        chain = prompt | llm
    except:
        chain = None
else:
    chain = None

# -------------------------------
# 💬 SHOW CHAT HISTORY
# -------------------------------
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

    # Generate response
    if chain:
        try:
            response = chain.invoke({
                "question": user_input
            })
            bot_reply = response.content
        except:
            bot_reply = "⚠️ AI error, try again"
    else:
        bot_reply = f"🤖 StudyBot: {user_input} (AI not configured)"

    # Show bot response
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    with st.chat_message("assistant"):
        st.write(bot_reply)
