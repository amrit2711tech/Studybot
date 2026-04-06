from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# LLM setup
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are StudyBot, explain clearly with examples."),
    ("user", "{question}")
])

chain = prompt | llm

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = chain.invoke({
            "question": request.question
        })

        return {"response": response.content}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}
