import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.models.meeting import Meeting, MeetingCreate
from app.models.memory import MeetingMemory
from app.services.speech_to_text import SpeechToTextService
from app.services.memory_builder import MemoryBuilder
from app.database.repositories import MeetingRepository, MemoryRepository

router = APIRouter(prefix="/meetings", tags=["Meetings"])

AUDIO_DIR = os.getenv("AUDIO_DIR", "./data/audio")

@router.post("/upload", response_model=MeetingMemory)
async def upload_and_process_meeting(
    file: Optional[UploadFile] = File(None),
    title: str = Form(...),
    date: str = Form(...),
    project: str = Form("General"),
    participants: str = Form(""),
    transcript_text: Optional[str] = Form(None)
):
    meeting_id = f"M_{uuid.uuid4().hex[:6]}"
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    stt_service = SpeechToTextService()
    builder = MemoryBuilder()
    
    parsed_participants = [p.strip() for p in participants.split(",") if p.strip()]

    if file:
        file_path = os.path.join(AUDIO_DIR, f"{meeting_id}_{file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        transcript = stt_service.transcribe_audio(file_path, meeting_id)
    elif transcript_text:
        transcript = stt_service.parse_transcript_text(transcript_text, meeting_id)
    else:
        raise HTTPException(status_code=400, detail="Either audio file or transcript_text must be provided.")

    memory = builder.build_and_save_memory(
        meeting_id=meeting_id,
        title=title,
        date=date,
        project=project,
        transcript=transcript,
        given_participants=parsed_participants
    )
    return memory

@router.get("", response_model=List[Meeting])
def list_meetings():
    repo = MeetingRepository()
    return repo.list_meetings()

@router.get("/{meeting_id}", response_model=Meeting)
def get_meeting(meeting_id: str):
    repo = MeetingRepository()
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting
