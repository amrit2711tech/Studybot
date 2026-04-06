import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -------------------------------
# ⚠️ DIRECT API KEY (TEMP FIX)
# -------------------------------
groq_api_key = "YOUR_GROQ_API_KEY_HERE"   # 👈 yahan apni key daalo

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="StudyBot", page_icon="🤖")
st.title("🤖 StudyBot AI Assistant")

# -------------------------------
# LLM
# -------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are StudyBot. Explain clearly using headings, bullet points and examples."),
    ("user", "{question}")
])

chain = prompt | llm

# -------------------------------
# Chat History
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# Input
# -------------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain.invoke({"question": user_input})
            reply = response.content

        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
