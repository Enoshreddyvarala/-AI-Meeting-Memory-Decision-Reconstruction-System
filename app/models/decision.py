from pydantic import BaseModel, Field
from typing import List, Optional

class DecisionAlternative(BaseModel):
    alternative_id: Optional[str] = None
    name: str
    evaluation: Optional[str] = None
    rejected_reason: Optional[str] = None

class DecisionReason(BaseModel):
    reason_id: Optional[str] = None
    reason: str
    source_chunk_id: Optional[str] = None

class Decision(BaseModel):
    decision_id: str
    source_meeting_id: str
    title: str
    decision: str
    rationale: List[str] = []
    alternatives: List[str] = []
    participants: List[str] = []
    timestamp: str = "00:00:00"
    confidence: float = 0.90
    status: str = "Approved"  # Proposed, Approved, Implemented, Superseded, Cancelled
    is_explicit: bool = True

class DecisionTimelineItem(BaseModel):
    date: str
    meeting_id: str
    meeting_title: str
    event_type: str  # Problem, Proposed, Evaluated, Decision Made, Implemented, Superseded
    description: str
    decision_id: Optional[str] = None
