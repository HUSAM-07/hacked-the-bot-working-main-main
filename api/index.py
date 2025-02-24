from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(temperature=0)

# Change this part in api/index.py
CONTEXT_FILE = "context.txt"

def load_context():
    try:
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "No context available"

class ChatInput(BaseModel):
    question: str

@app.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        context = load_context()
        if not context:
            raise HTTPException(status_code=400, detail="No context available")

        prompt = f"""Context: {context}

Question: {chat_input.question}

Please answer the question based on the context provided above. If the answer cannot be found in the context, say so."""

        response = llm.invoke(prompt)
        
        return JSONResponse(content={
            "answer": response.content,
            "sources": ["context.txt"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 