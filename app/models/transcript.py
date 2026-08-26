from pydantic import BaseModel
from typing import List, Optional

class TranscriptSegment(BaseModel):
    segment_id: str
    meeting_id: str
    speaker: str
    start_time: str
    end_time: str
    text: str

class TranscriptChunk(BaseModel):
    chunk_id: str
    meeting_id: str
    topic: Optional[str] = None
    speakers: List[str] = []
    start_time: str
    end_time: str
    text: str

class Transcript(BaseModel):
    meeting_id: str
    full_text: str
    segments: List[TranscriptSegment] = []
