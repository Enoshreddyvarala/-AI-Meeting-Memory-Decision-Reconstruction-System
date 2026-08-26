from pydantic import BaseModel, Field
from typing import List, Optional

class MeetingMetadata(BaseModel):
    project: Optional[str] = "General"
    location: Optional[str] = None
    tags: List[str] = []

class MeetingCreate(BaseModel):
    title: str
    date: str
    project: str = "General"
    participants: List[str] = []
    transcript_text: Optional[str] = None

class Meeting(BaseModel):
    meeting_id: str
    title: str
    date: str
    project: str = "General"
    participants: List[str] = []
    audio_path: Optional[str] = None
    transcript_path: Optional[str] = None
    created_at: Optional[str] = None
