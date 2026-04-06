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
             "You are StudyBot, an expert tutor.\n"
             "Answer ALL questions clearly using:\n"
             "- Headings\n- Bullet points\n- Examples\n"
             "Subjects include: AI, ML, Maths, English, GK, Science.\n"
             "Never say 'I don't know'. Always try to explain."),
            ("user", "{question}")
        ])

        chain = prompt | llm
    except:
        chain = None

# -------------------------------
# 🧠 CHAT MEMORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# 💬 SMART FALLBACK (UPGRADED)
# -------------------------------
def smart_fallback(q):
    q = q.lower()

    if "machine learning" in q or "ml" in q:
        return """### 📊 Machine Learning (ML)

Machine Learning is a part of Artificial Intelligence.

**Definition:**
It allows machines to learn from data and improve automatically.

**Types:**
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning

**Example:**
Spam email detection 📧
"""

    elif "ai" in q:
        return """### 🤖 Artificial Intelligence (AI)

AI enables machines to perform tasks that require human intelligence.

**Uses:**
- Chatbots
- Self-driving cars
- Recommendation systems

**Example:**
Netflix suggestions 🎬
"""

    elif "math" in q or "solve" in q:
        return "📐 Please provide the full math problem so I can solve it step by step."

    elif "english" in q:
        return "📖 English help: Ask grammar, essay, or comprehension questions!"

    else:
        return f"""### 📚 StudyBot Answer

**Your Question:** {q}

This topic relates to general knowledge or academics.

👉 Try asking more specific like:
- Explain {q}
- Define {q}
- Examples of {q}

I'm here to help with all subjects! 😊
"""

# -------------------------------
# 💬 INPUT
# -------------------------------
user_input = st.chat_input("Ask anything (AI, ML, Maths, GK...)")

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
                    reply = smart_fallback(user_input)
            else:
                reply = smart_fallback(user_input)

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
