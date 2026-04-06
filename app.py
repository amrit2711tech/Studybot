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
# 🚀 FASTAPI APP
# -------------------------------
app = FastAPI()

# -------------------------------
# ✅ STATIC + TEMPLATE SETUP
# -------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
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
# 🔐 ENV VARIABLES (SAFE)
# -------------------------------
groq_api_key = os.environ.get("GROQ_API_KEY")
mongo_uri = os.environ.get("MONGODB_URI")

print("GROQ:", groq_api_key)
print("MONGO:", mongo_uri)

# -------------------------------
# 🧠 MongoDB (SAFE)
# -------------------------------
collection = None
try:
    if mongo_uri:
        client = MongoClient(mongo_uri)
        db = client["Study"]
        collection = db["users"]
except Exception as e:
    print("Mongo Error:", e)

# -------------------------------
# 📦 REQUEST MODEL
# -------------------------------
class ChatRequest(BaseModel):
    user_id: str
    question: str

# -------------------------------
# 🏠 HOME ROUTE (UI)
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": f"Template error: {str(e)}"}

# -------------------------------
# 💬 CHAT ROUTE (SAFE)
# -------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        question = request.question

        # Temporary response (no crash)
        answer = f"🤖 StudyBot: {question}"

        # Save if Mongo works
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
