import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -------------------------------
# 🔐 Environment Variables (Render)
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")
mongo_uri = os.environ.get("MONGODB_URI")

# -------------------------------
# 🚨 Safety Check
# -------------------------------
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing in environment variables")

if not mongo_uri:
    raise ValueError("MONGODB_URI is missing in environment variables")

# -------------------------------
# 🧠 MongoDB
# -------------------------------
client = MongoClient(mongo_uri)
db = client["Study"]
collection = db["users"]

# -------------------------------
# 🚀 FastAPI App
# -------------------------------
app = FastAPI()

# Allow frontend (HTML) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 📦 Request Model
# -------------------------------
class ChatRequest(BaseModel):
    user_id: str
    question: str

# -------------------------------
# 📝 Prompt
# -------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are StudyBot. Answer clearly in structured format with headings, bullet points, and examples."),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

# -------------------------------
# 🤖 LLM
# -------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama3-8b-8192"
)

chain = prompt | llm

# -------------------------------
# 📚 Get History
# -------------------------------
def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    return [(chat["role"], chat["message"]) for chat in chats]

# -------------------------------
# 🏠 Home Route
# -------------------------------
@app.get("/")
def home():
    return {"message": "StudyBot API is running 🚀"}

# -------------------------------
# 💬 Chat Route
# -------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        history = get_history(request.user_id)

        response = chain.invoke({
            "history": history,
            "question": request.question
        })

        # Save user message
        collection.insert_one({
            "user_id": request.user_id,
            "role": "user",
            "message": request.question,
            "timestamp": datetime.utcnow()
        })

        # Save bot response
        collection.insert_one({
            "user_id": request.user_id,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.utcnow()
        })

        return {"response": response.content}

    except Exception as e:
        return {"error": str(e)}
