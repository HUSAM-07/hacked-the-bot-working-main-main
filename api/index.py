from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    allow_origins=["https://subtle-kataifi-c6d4a1.netlify.app", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    llm = ChatOpenAI(api_key=api_key, temperature=0)
    logger.info("OpenAI client initialized successfully")
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

class ChatResponse(BaseModel):
    answer: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(input_data: ChatInput):
    try:
        # Log the incoming request
        logger.info(f"Received chat request with question: {input_data.question}")

        # Load context
        context = load_context()
        if not context:
            logger.error("Failed to load context")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course content not loaded. Please process documents first."
            )

        # Create prompt
        prompt = f"Context: {context}\n\nQuestion: {input_data.question}\n\nAnswer:"

        try:
            # Call OpenAI
            response = await llm.ainvoke(prompt)
            logger.info("Successfully received response from OpenAI")
            
            return ChatResponse(answer=response)

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error getting response from AI service: {str(e)}"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/check-context")
async def check_context():
    try:
        context = load_context()
        return {
            "status": "ok" if context else "error",
            "message": "Context loaded successfully" if context else "Context not found",
            "context_length": len(context) if context else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking context: {str(e)}"
        }

# Add this if you're running the file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 