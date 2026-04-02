import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# MongoDB Connection
client = MongoClient(mongo_uri)
db = client["Study"]
collection = db["users"]

# Streamlit UI
st.set_page_config(page_title="StudyBot 🎓", layout="centered")

st.title("🎓 StudyBot")
st.write("Your AI-powered academic assistant")

# User ID input
user_id = st.text_input("Enter your User ID")

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are StudyBot, an AI-powered academic assistant. "
            "Answer study-related questions clearly and in structured format. "
            "Use headings, bullet points, and examples when necessary. "
            "If the question is conceptual, explain step-by-step. "
            "If it is exam-oriented, format the answer suitable for exams. "
            "Use previous conversation context if available."
        ),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

# LLM
llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-20b"
)

chain = prompt | llm

# Get chat history
def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []
    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history

# Chat input
question = st.text_input("Ask your question:")

if st.button("Submit") and user_id and question:
    
    history = get_history(user_id)

    response = chain.invoke({
        "history": history,
        "question": question
    })

    # Save user message
    collection.insert_one({
        "user_id": user_id,
        "role": "user",
        "message": question,
        "timestamp": datetime.utcnow()
    })

    # Save assistant response
    collection.insert_one({
        "user_id": user_id,
        "role": "assistant",
        "message": response.content,
        "timestamp": datetime.utcnow()
    })

    # Show response
    st.subheader("📖 Answer:")
    st.write(response.content)

# Show previous chats
if user_id:
    st.subheader("🕓 Chat History")
    history = get_history(user_id)
    
    for role, msg in history:
        if role == "user":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")
