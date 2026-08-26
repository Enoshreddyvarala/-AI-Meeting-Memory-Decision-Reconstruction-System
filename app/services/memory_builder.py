from typing import List, Optional
from app.models.meeting import Meeting
from app.models.memory import MeetingMemory
from app.models.transcript import Transcript
from app.services.summarizer import MeetingSummarizer
from app.services.decision_extractor import DecisionExtractor
from app.services.action_extractor import ActionExtractor
from app.services.participant_identifier import ParticipantIdentifier
from app.database.repositories import MeetingRepository, DecisionRepository, ActionRepository, MemoryRepository
from app.rag.vector_store import VectorStore

class MemoryBuilder:
    def __init__(self, db_path: str = None, vector_store: VectorStore = None):
        self.db_path = db_path
        self.summarizer = MeetingSummarizer()
        self.decision_extractor = DecisionExtractor()
        self.action_extractor = ActionExtractor()
        self.participant_identifier = ParticipantIdentifier()
        self.meeting_repo = MeetingRepository(db_path)
        self.decision_repo = DecisionRepository(db_path)
        self.action_repo = ActionRepository(db_path)
        self.memory_repo = MemoryRepository(db_path)
        self.vector_store = vector_store or VectorStore()

    def build_and_save_memory(
        self,
        meeting_id: str,
        title: str,
        date: str,
        project: str,
        transcript: Transcript,
        given_participants: List[str] = None
    ) -> MeetingMemory:
        full_text = transcript.full_text
        
        # 1. Identify participants
        participants = self.participant_identifier.extract_participants(full_text, given_participants)
        
        # 2. Summarize
        summary_data = self.summarizer.generate_summary(full_text)
        summary = summary_data.get("summary", "")
        topics = summary_data.get("topics", [])
        risks = summary_data.get("risks", [])
        open_questions = summary_data.get("open_questions", [])
        
        # 3. Extract Decisions
        decisions = self.decision_extractor.extract_decisions(full_text, meeting_id)
        
        # 4. Extract Actions
        actions = self.action_extractor.extract_actions(full_text, meeting_id)
        
        # 5. Create Meeting object & save to DB
        meeting = Meeting(
            meeting_id=meeting_id,
            title=title,
            date=date,
            project=project,
            participants=participants
        )
        self.meeting_repo.save_meeting(meeting, summary=summary, topics=topics, risks=risks, open_questions=open_questions)
        
        for d in decisions:
            self.decision_repo.save_decision(d)
            
        for a in actions:
            self.action_repo.save_action(a)
            
        # 6. Index into Vector Store
        self.vector_store.index_meeting_transcript(meeting_id, title, date, project, transcript.segments)
        self.vector_store.index_meeting_memory(meeting_id, title, date, project, summary, decisions)

        # 7. Construct MeetingMemory return
        return MeetingMemory(
            meeting_id=meeting_id,
            title=title,
            date=date,
            project=project,
            participants=participants,
            summary=summary,
            topics=topics,
            decisions=decisions,
            actions=actions,
            risks=risks,
            open_questions=open_questions
        )
