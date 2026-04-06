import datetime
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongo_uri)
db = client["chat"]
collection = db["users"]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a diet specialist, give me the output accordingly"),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

llm = ChatGroq(api_key = groq_api_key, model="openai/gpt-oss-20b")
chain = prompt | llm

user_id = "user3"

def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []

    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history

while True:
    question = input("Ask a question: ")
    
    if question.lower() in ["exit", "quit"]:
        break

    history = get_history(user_id)


    response = chain.invoke({"history": history, "question": question})

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

    print(response.content)


