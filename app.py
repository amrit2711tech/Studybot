import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime

# -------------------------------
# 🔐 Load Secrets (Streamlit Cloud Safe)
# -------------------------------
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
    mongo_uri = st.secrets["MONGODB_URI"]
except Exception:
    st.error("❌ Missing secrets! Please add GROQ_API_KEY and MONGODB_URI in Streamlit Secrets.")
    st.stop()

# -------------------------------
# 🧠 MongoDB Connection
# -------------------------------
try:
    client = MongoClient(mongo_uri)
    db = client["Study"]
    collection = db["users"]
except Exception:
    st.error("❌ MongoDB connection failed!")
    st.stop()

# -------------------------------
# 🎨 Streamlit UI
# -------------------------------
st.set_page_config(page_title="StudyBot 🎓", layout="centered")

st.title("🎓 StudyBot")
st.write("Your AI-powered academic assistant")

# -------------------------------
# 👤 User Input
# -------------------------------
user_id = st.text_input("Enter your User ID")
question = st.text_input("Ask your question")

# -------------------------------
# 📝 Prompt Template
# -------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are StudyBot, an AI-powered academic assistant. "
            "Answer clearly using headings, bullet points, and examples. "
            "Explain step-by-step for concepts and format answers for exams."
        ),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

# -------------------------------
# 🤖 LLM Setup
# -------------------------------
try:
    llm = ChatGroq(
        api_key=groq_api_key,
        model="llama3-8b-8192"   # stable model
    )
    chain = prompt | llm
except Exception:
    st.error("❌ LLM initialization failed. Check API key.")
    st.stop()

# -------------------------------
# 📚 Get Chat History
# -------------------------------
def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []
    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history

# -------------------------------
# 🚀 Chat Logic
# -------------------------------
if st.button("Submit"):
    if not user_id or not question:
        st.warning("⚠️ Please enter both User ID and question.")
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

            # Display response
            st.subheader("📖 Answer")
            st.write(response.content)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# -------------------------------
# 🕓 Chat History Display
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
        st.warning("No chat history found.")
