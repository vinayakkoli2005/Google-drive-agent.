from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.schemas import ChatRequest, ChatResponse
from backend.agent import run_agent
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = FastAPI(title="Google Drive Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session storage for development
sessions = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        
    if session_id not in sessions:
        sessions[session_id] = []
        
    chat_history = sessions[session_id]
    
    try:
        result = run_agent(request.message, chat_history)
        final_messages = result["messages"]
        
        # The new history is all the messages
        sessions[session_id] = final_messages
        
        # The last message is from the AI
        # gemini-2.5+ returns content as a list of parts; extract text
        raw = final_messages[-1].content
        if isinstance(raw, list):
            ai_response = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in raw
            ).strip()
        else:
            ai_response = raw
        
        return ChatResponse(response=ai_response, session_id=session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
