# Course Handout Chatbot

A chatbot that allows students to interact with their course handouts using natural language. Built with FastAPI, LangChain, and OpenAI.

# RUN ONLY WITH PYTHON 3.10 OR BELOW
## Features

- Process PDF and DOCX course handouts
- Natural language interaction with course materials
- Modern and responsive UI
- Source attribution for answers

## Prerequisites

- Python 3.8+
- Node.js (for serving the frontend)
- OpenAI API key

## Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Docker Setup for ChromaDB

1. Start ChromaDB using Docker:
   ```bash
   docker-compose up -d chroma
   ```

2. Wait a few seconds for ChromaDB to initialize

3. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8080
   ```

Note: We're using port 8080 for the FastAPI backend since ChromaDB uses port 8000

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Serve the frontend:
   You can use any static file server. For example, with Python:
   ```bash
   cd frontend
   python -m http.server 3000
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Place your course handouts (PDF or DOCX) in the `course-handouts` directory
2. Click the "Process Documents" button in the UI
3. Once processing is complete, you can start asking questions about your course materials
4. The chatbot will provide answers with references to the source materials

## Technical Details

- Backend: FastAPI + LangChain + ChromaDB
- Frontend: HTML + CSS + JavaScript
- Document Processing: PyPDF + docx2txt
- Embeddings: OpenAI Ada
- LLM: OpenAI GPT

## Notes

- The system uses ChromaDB for vector storage, which allows for efficient semantic search
- All processed documents are stored locally in the `data` directory
- The UI is responsive and works well on both desktop and mobile devices 