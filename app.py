import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime

# -------------------------------
# 🔐 Load .env (if exists)
# -------------------------------
load_dotenv()

# -------------------------------
# 🎨 UI
# -------------------------------
st.set_page_config(page_title="StudyBot 🎓", layout="centered")
st.title("🎓 StudyBot")
st.write("Your AI-powered academic assistant")

# -------------------------------
# 🔑 Get API Keys (3-way fallback)
# -------------------------------
groq_api_key = os.getenv("GROQ_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# If not found → ask user manually (THIS PREVENTS ERROR)
if not groq_api_key:
    groq_api_key = st.text_input("🔑 Enter GROQ API Key", type="password")

if not mongo_uri:
    mongo_uri = st.text_input("🗄️ Enter MongoDB URI", type="password")

# -------------------------------
# 👤 User Inputs
# -------------------------------
user_id = st.text_input("Enter User ID")
question = st.text_input("Ask your question")

# -------------------------------
# 📝 Prompt
# -------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are StudyBot, an academic assistant. "
            "Answer in structured format with headings, bullet points, and examples."
        ),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

# -------------------------------
# 🚀 Run only if keys available
# -------------------------------
if st.button("Submit"):

    if not groq_api_key or not mongo_uri:
        st.warning("⚠️ Please provide API Key and MongoDB URI first")
    
    elif not user_id or not question:
        st.warning("⚠️ Please enter User ID and question")

    else:
        try:
            # MongoDB
            client = MongoClient(mongo_uri)
            db = client["Study"]
            collection = db["users"]

            # LLM
            llm = ChatGroq(
                api_key=groq_api_key,
                model="llama3-8b-8192"
            )

            chain = prompt | llm

            # Get history
            chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
            history = [(chat["role"], chat["message"]) for chat in chats]

            # Response
            with st.spinner("Thinking... 🤔"):
                response = chain.invoke({
                    "history": history,
                    "question": question
                })

            # Save chat
            collection.insert_one({
                "user_id": user_id,
                "role": "user",
                "message": question,
                "timestamp": datetime.utcnow()
            })

            collection.insert_one({
                "user_id": user_id,
                "role": "assistant",
                "message": response.content,
                "timestamp": datetime.utcnow()
            })

            # Output
            st.subheader("📖 Answer")
            st.write(response.content)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# -------------------------------
# 🕓 History
# -------------------------------
if user_id and mongo_uri:
    try:
        client = MongoClient(mongo_uri)
        db = client["Study"]
        collection = db["users"]

        chats = collection.find({"user_id": user_id}).sort("timestamp", 1)

        st.subheader("🕓 Chat History")
        for chat in chats:
            if chat["role"] == "user":
                st.markdown(f"**🧑 You:** {chat['message']}")
            else:
                st.markdown(f"**🤖 Bot:** {chat['message']}")
    except:
        pass
