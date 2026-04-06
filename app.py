import os
import streamlit as st

# Safe import
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    AI_READY = True
except:
    AI_READY = False

st.set_page_config(page_title="StudyBot AI", page_icon="🤖")

st.title("🤖 StudyBot AI Assistant")

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
             "Explain clearly using headings, bullet points and examples."),
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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# 💬 INPUT
# -------------------------------
user_input = st.chat_input("Ask your question...")

# -------------------------------
# 🤖 FALLBACK FUNCTION (NO ERROR)
# -------------------------------
def fallback_answer(q):
    q = q.lower()

    if "ai" in q:
        return """### 🤖 Artificial Intelligence (AI)

**AI** is a technology that allows machines to think and act like humans.

**Key Points:**
- Machines can learn from data
- Used in chatbots, self-driving cars
- Example: Siri, ChatGPT

**Simple Example:**
Netflix recommending movies based on your interest 🎬
"""

    elif "machine learning" in q:
        return """### 📊 Machine Learning

Machine Learning is a part of AI where systems learn from data.

**Types:**
- Supervised Learning
- Unsupervised Learning

**Example:**
Email spam detection 📧
"""

    else:
        return f"🤖 StudyBot: {q.capitalize()} is an important topic. Try asking more specific questions!"

# -------------------------------
# 💬 PROCESS INPUT
# -------------------------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):

            if chain:
                try:
                    response = chain.invoke({"question": user_input})
                    reply = response.content
                except:
                    reply = fallback_answer(user_input)
            else:
                reply = fallback_answer(user_input)

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
