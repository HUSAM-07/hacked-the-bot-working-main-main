from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Verify OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY not found")

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://subtle-kataifi-c6d4a1.netlify.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    llm = ChatOpenAI(temperature=0)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

# Change this part in api/index.py
CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "context.txt")

def load_context():
    try:
        # First try the direct path
        if os.path.exists(CONTEXT_FILE):
            with open(CONTEXT_FILE, 'r', encoding='utf-8') as file:
                return file.read()
        
        # If not found, try the root directory
        root_context = os.path.join(os.getcwd(), "context.txt")
        if os.path.exists(root_context):
            with open(root_context, 'r', encoding='utf-8') as file:
                return file.read()
                
        logger.error("Context file not found in any location")
        return None
    except Exception as e:
        logger.error(f"Error reading context file: {str(e)}")
        return None

class ChatInput(BaseModel):
    question: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        # Log incoming request
        logger.info(f"Received chat request: {chat_input.question[:50]}...")

        # Load and validate context
        context = load_context()
        if not context:
            logger.error("No context available")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No context available. Please process documents first."
            )

        # Create prompt
        prompt = f"""Context: {context}

Question: {chat_input.question}

Please answer the question based on the context provided above. If the answer cannot be found in the context, say so."""

        # Get response from OpenAI
        try:
            response = llm.invoke(prompt)
            
            return JSONResponse(content={
                "answer": response.content,
                "sources": ["context.txt"]
            })
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error getting response from AI service"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Add this if you're running the file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 