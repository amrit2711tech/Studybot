import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime

# -------------------------------
# 🔐 ENV VARIABLES (SAFE VERSION)
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY", "demo_key")
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

print("GROQ KEY:", groq_api_key)
print("MONGO URI:", mongo_uri)

# -------------------------------
# 🧠 MongoDB (SAFE CONNECT)
# -------------------------------
try:
    client = MongoClient(mongo_uri)
    db = client["Study"]
    collection = db["users"]
except Exception as e:
    print("MongoDB Error:", e)
    collection = None

# -------------------------------
# 🚀 FASTAPI APP
# -------------------------------
app = FastAPI()

# STATIC FILES
app.mount("/static", StaticFiles(directory="static"), name="static")

# TEMPLATES
templates = Jinja2Templates(directory="templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 📦 REQUEST MODEL
# -------------------------------
class ChatRequest(BaseModel):
    user_id: str
    question: str

# -------------------------------
# 🏠 HOME (UI LOAD)
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------------
# 💬 CHAT (SAFE VERSION)
# -------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        question = request.question

        # Dummy response (SAFE)
        answer = f"🤖 StudyBot: You asked → {question}"

        # Save in Mongo (if connected)
        if collection:
            collection.insert_one({
                "user_id": request.user_id,
                "role": "user",
                "message": question,
                "timestamp": datetime.utcnow()
            })

            collection.insert_one({
                "user_id": request.user_id,
                "role": "assistant",
                "message": answer,
                "timestamp": datetime.utcnow()
            })

        return {"response": answer}

    except Exception as e:
        return {"error": str(e)}
