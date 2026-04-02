import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime

# -------------------------------
# 🔐 Load Environment (LOCAL + CLOUD SAFE)
# -------------------------------
load_dotenv()

def get_secret(key):
    # First try Streamlit secrets (Cloud)
    if key in st.secrets:
        return st.secrets[key]
    # Then try .env (Local)
    return os.getenv(key)

groq_api_key = get_secret("GROQ_API_KEY")
mongo_uri = get_secret("MONGODB_URI")

if not groq_api_key or not mongo_uri:
    st.error("❌ API Key or MongoDB URI missing!\n\n👉 Use .env file (local) OR Streamlit secrets (cloud).")
    st.stop()

# -------------------------------
# 🧠 MongoDB Connection
# -------------------------------
try:
    client = MongoClient(mongo_uri)
    db = client["Study"]
    collection = db["users"]
except Exception as e:
    st.error(f"❌ MongoDB connection failed: {e}")
    st.stop()

# -------------------------------
# 🎨 UI
# -------------------------------
st.set_page_config(page_title="StudyBot 🎓", layout="centered")

st.title("🎓 StudyBot")
st.write("Your AI-powered academic assistant")

# -------------------------------
# 👤 Inputs
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
# 🤖 LLM
# -------------------------------
try:
    llm = ChatGroq(
        api_key=groq_api_key,
        model="llama3-8b-8192"
    )
    chain = prompt | llm
except Exception as e:
    st.error(f"❌ LLM Error: {e}")
    st.stop()

# -------------------------------
# 📚 History
# -------------------------------
def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    return [(chat["role"], chat["message"]) for chat in chats]

# -------------------------------
# 🚀 Chat
# -------------------------------
if st.button("Submit"):
    if not user_id or not question:
        st.warning("⚠️ Please enter both fields")
    else:
        try:
            history = get_history(user_id)

            with st.spinner("Thinking... 🤔"):
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

            # Save bot response
            collection.insert_one({
                "user_id": user_id,
                "role": "assistant",
                "message": response.content,
                "timestamp": datetime.utcnow()
            })

            st.subheader("📖 Answer")
            st.write(response.content)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# -------------------------------
# 🕓 History UI
# -------------------------------
if user_id:
    st.subheader("🕓 Chat History")
    try:
        history = get_history(user_id)
        for role, msg in history:
            if role == "user":
                st.markdown(f"**🧑 You:** {msg}")
            else:
                st.markdown(f"**🤖 Bot:** {msg}")
    except:
        st.write("No history found")
