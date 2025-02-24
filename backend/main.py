import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI components
llm = ChatOpenAI(temperature=0)

# Path to your context file
CONTEXT_FILE = "context.txt"

class ChatInput(BaseModel):
    question: str

def load_context():
    try:
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Context file not found: {CONTEXT_FILE}")
        return ""

@app.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        # Load the context
        context = load_context()
        if not context:
            raise HTTPException(status_code=400, detail="No context available")

        # Create the prompt with context
        prompt = f"""Context: {context}

Question: {chat_input.question}

Please answer the question based on the context provided above. If the answer cannot be found in the context, say so."""

        # Get response from OpenAI
        response = llm.invoke(prompt)
        
        return JSONResponse(content={
            "answer": response.content,
            "sources": ["context.txt"]
        })

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 