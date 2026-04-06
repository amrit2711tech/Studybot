import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🏠 HOME (NO TEMPLATE → NO ERROR)
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
        <title>StudyBot</title>
    </head>
    <body style="font-family: Arial; text-align:center; margin-top:50px;">
        <h1>🤖 StudyBot Running Successfully</h1>
        <input id="input" placeholder="Ask something"/>
        <button onclick="send()">Send</button>
        <p id="response"></p>

        <script>
        async function send(){
            let msg = document.getElementById("input").value;

            let res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    user_id: "user1",
                    question: msg
                })
            });

            let data = await res.json();
            document.getElementById("response").innerText = data.response;
        }
        </script>
    </body>
    </html>
    """

# -------------------------------
# 💬 CHAT (NO FAIL VERSION)
# -------------------------------
@app.post("/chat")
async def chat(data: dict):
    try:
        question = data.get("question", "")

        return {
            "response": f"🤖 StudyBot: {question}"
        }

    except Exception as e:
        return {"response": "Error handled safely"}
