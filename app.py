import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ✅ ADD THIS
from fastapi.templating import Jinja2Templates  # ✅ ADD THIS

from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -------------------------------
# 🔐 Environment Variables
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")
mongo_uri = os.environ.get("MONGODB_URI")

if not groq_api_key:
    raise Exception("❌ GROQ_API_KEY not found")

if not mongo_uri:
    raise Exception("❌ MONGODB_URI not found")

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

# ✅ STATIC FILES (IMPORTANT)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ TEMPLATES (IMPORTANT)
templates = Jinja2Templates(directory="templates")

# -------------------------------
# 🌐 CORS
# -------------------------------
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
         "You are StudyBot, an academic assistant. "
         "Answer clearly using headings, bullet points, and examples."),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

# -------------------------------
# 🤖 LLM
# -------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

chain = prompt | llm

# -------------------------------
# 📚 Chat History
# -------------------------------
def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    return [(chat["role"], chat["message"]) for chat in chats]

# -------------------------------
# 🏠 HOME (TEMPLATE RENDER 🔥)
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------------
# 💬 CHAT
# -------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        history = get_history(request.user_id)

        response = chain.invoke({
            "history": history,
            "question": request.question
        })

        collection.insert_one({
            "user_id": request.user_id,
            "role": "user",
            "message": request.question,
            "timestamp": datetime.utcnow()
        })

        collection.insert_one({
            "user_id": request.user_id,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.utcnow()
        })

        return {"response": response.content}

    except Exception as e:
        return {"error": str(e)}
