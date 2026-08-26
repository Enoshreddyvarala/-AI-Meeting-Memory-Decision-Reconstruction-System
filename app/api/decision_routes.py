from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.decision import Decision, DecisionTimelineItem
from app.database.repositories import DecisionRepository
from app.analysis.decision_timeline import DecisionTimelineBuilder
from app.analysis.contradiction_detector import ContradictionDetector

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.get("", response_model=List[Decision])
def list_decisions():
    repo = DecisionRepository()
    return repo.list_all_decisions()

@router.get("/{decision_id}", response_model=Decision)
def get_decision(decision_id: str):
    repo = DecisionRepository()
    d = repo.get_decision(decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    return d

@router.get("/timeline/topic", response_model=List[DecisionTimelineItem])
def get_decision_timeline(topic: str = Query("database")):
    builder = DecisionTimelineBuilder()
    return builder.build_timeline_for_topic(topic)

@router.get("/contradictions/check")
def check_contradictions():
    repo = DecisionRepository()
    decisions = repo.list_all_decisions()
    detector = ContradictionDetector()
    return detector.detect_contradictions(decisions)
