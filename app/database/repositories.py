import json
from typing import List, Optional, Dict, Any
from .sqlite_db import get_db_connection, init_db
from app.models.meeting import Meeting
from app.models.decision import Decision
from app.models.action import ActionItem
from app.models.memory import MeetingMemory

class MeetingRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    def save_meeting(self, meeting: Meeting, summary: str = "", topics: List[str] = None, risks: List[str] = None, open_questions: List[str] = None):
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        topics_json = json.dumps(topics or [])
        risks_json = json.dumps(risks or [])
        questions_json = json.dumps(open_questions or [])
        
        cursor.execute("""
            INSERT OR REPLACE INTO meetings (meeting_id, title, date, project, audio_path, transcript_path, summary, topics, risks, open_questions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (meeting.meeting_id, meeting.title, meeting.date, meeting.project, meeting.audio_path, meeting.transcript_path, summary, topics_json, risks_json, questions_json))
        
        # Save participants
        cursor.execute("DELETE FROM participants WHERE meeting_id = ?", (meeting.meeting_id,))
        for p in meeting.participants:
            cursor.execute("INSERT INTO participants (meeting_id, name) VALUES (?, ?)", (meeting.meeting_id, p))
            
        conn.commit()
        conn.close()

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meetings WHERE meeting_id = ?", (meeting_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        cursor.execute("SELECT name FROM participants WHERE meeting_id = ?", (meeting_id,))
        participants = [r["name"] for r in cursor.fetchall()]
        conn.close()
        
        return Meeting(
            meeting_id=row["meeting_id"],
            title=row["title"],
            date=row["date"],
            project=row["project"],
            audio_path=row["audio_path"],
            transcript_path=row["transcript_path"],
            participants=participants,
            created_at=str(row["created_at"]) if row["created_at"] else None
        )

    def list_meetings(self) -> List[Meeting]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT meeting_id FROM meetings ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self.get_meeting(r["meeting_id"]) for r in rows if r["meeting_id"]]

class DecisionRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    def save_decision(self, decision: Decision):
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO decisions (decision_id, meeting_id, title, decision, timestamp, confidence, status, is_explicit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (decision.decision_id, decision.source_meeting_id, decision.title, decision.decision, decision.timestamp, decision.confidence, decision.status, 1 if decision.is_explicit else 0))
        
        # Save reasons
        cursor.execute("DELETE FROM decision_reasons WHERE decision_id = ?", (decision.decision_id,))
        for r in decision.rationale:
            cursor.execute("INSERT INTO decision_reasons (decision_id, reason) VALUES (?, ?)", (decision.decision_id, r))
            
        # Save alternatives
        cursor.execute("DELETE FROM decision_alternatives WHERE decision_id = ?", (decision.decision_id,))
        for a in decision.alternatives:
            cursor.execute("INSERT INTO decision_alternatives (decision_id, alternative) VALUES (?, ?)", (decision.decision_id, a))
            
        # Save participants
        cursor.execute("DELETE FROM decision_participants WHERE decision_id = ?", (decision.decision_id,))
        for p in decision.participants:
            cursor.execute("INSERT INTO decision_participants (decision_id, participant) VALUES (?, ?)", (decision.decision_id, p))
            
        conn.commit()
        conn.close()

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        cursor.execute("SELECT reason FROM decision_reasons WHERE decision_id = ?", (decision_id,))
        rationale = [r["reason"] for r in cursor.fetchall()]
        
        cursor.execute("SELECT alternative FROM decision_alternatives WHERE decision_id = ?", (decision_id,))
        alternatives = [r["alternative"] for r in cursor.fetchall()]
        
        cursor.execute("SELECT participant FROM decision_participants WHERE decision_id = ?", (decision_id,))
        participants = [r["participant"] for r in cursor.fetchall()]
        
        conn.close()
        
        return Decision(
            decision_id=row["decision_id"],
            source_meeting_id=row["meeting_id"],
            title=row["title"],
            decision=row["decision"],
            rationale=rationale,
            alternatives=alternatives,
            participants=participants,
            timestamp=row["timestamp"],
            confidence=row["confidence"],
            status=row["status"],
            is_explicit=bool(row["is_explicit"])
        )

    def list_decisions_by_meeting(self, meeting_id: str) -> List[Decision]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT decision_id FROM decisions WHERE meeting_id = ?", (meeting_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self.get_decision(r["decision_id"]) for r in rows]

    def list_all_decisions(self) -> List[Decision]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT decision_id FROM decisions")
        rows = cursor.fetchall()
        conn.close()
        return [self.get_decision(r["decision_id"]) for r in rows]

class ActionRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    def save_action(self, action: ActionItem):
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO actions (action_id, meeting_id, description, owner, due_date, priority, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (action.action_id, action.source_meeting_id, action.description, action.owner, action.due_date, action.priority, action.status, action.timestamp))
        conn.commit()
        conn.close()

    def list_actions_by_meeting(self, meeting_id: str) -> List[ActionItem]:
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actions WHERE meeting_id = ?", (meeting_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            ActionItem(
                action_id=r["action_id"],
                source_meeting_id=r["meeting_id"],
                description=r["description"],
                owner=r["owner"],
                due_date=r["due_date"],
                priority=r["priority"],
                status=r["status"],
                timestamp=r["timestamp"]
            )
            for r in rows
        ]

class MemoryRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.meeting_repo = MeetingRepository(db_path)
        self.decision_repo = DecisionRepository(db_path)
        self.action_repo = ActionRepository(db_path)

    def get_meeting_memory(self, meeting_id: str) -> Optional[MeetingMemory]:
        meeting = self.meeting_repo.get_meeting(meeting_id)
        if not meeting:
            return None
        
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT summary, topics, risks, open_questions FROM meetings WHERE meeting_id = ?", (meeting_id,))
        row = cursor.fetchone()
        conn.close()
        
        summary = row["summary"] if row and row["summary"] else ""
        topics = json.loads(row["topics"]) if row and row["topics"] else []
        risks = json.loads(row["risks"]) if row and row["risks"] else []
        questions = json.loads(row["open_questions"]) if row and row["open_questions"] else []
        
        decisions = self.decision_repo.list_decisions_by_meeting(meeting_id)
        actions = self.action_repo.list_actions_by_meeting(meeting_id)
        
        return MeetingMemory(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            date=meeting.date,
            project=meeting.project,
            participants=meeting.participants,
            summary=summary,
            topics=topics,
            decisions=decisions,
            actions=actions,
            risks=risks,
            open_questions=questions
        )
