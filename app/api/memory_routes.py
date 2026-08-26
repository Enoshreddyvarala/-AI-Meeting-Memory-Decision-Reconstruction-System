from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.memory import MeetingMemory
from app.database.repositories import MemoryRepository
from app.analysis.decision_reconstruction import DecisionReconstructionEngine

router = APIRouter(tags=["Memory & RAG"])

class AskQuestionRequest(BaseModel):
    question: str
    project: Optional[str] = None

@router.post("/ask")
def ask_historical_question(req: AskQuestionRequest):
    engine = DecisionReconstructionEngine()
    result = engine.reconstruct_decision(req.question, project_filter=req.project)
    return result

@router.get("/meetings/{meeting_id}/memory", response_model=MeetingMemory)
def get_meeting_memory(meeting_id: str):
    repo = MemoryRepository()
    memory = repo.get_meeting_memory(meeting_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Meeting memory not found")
    return memory
