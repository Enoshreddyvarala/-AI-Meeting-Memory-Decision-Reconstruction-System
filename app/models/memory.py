from pydantic import BaseModel
from typing import List
from .decision import Decision
from .action import ActionItem

class MeetingMemory(BaseModel):
    meeting_id: str
    title: str
    date: str
    project: str = "General"
    participants: List[str] = []
    summary: str
    topics: List[str] = []
    decisions: List[Decision] = []
    actions: List[ActionItem] = []
    risks: List[str] = []
    open_questions: List[str] = []
