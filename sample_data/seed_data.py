import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.database.sqlite_db import init_db
from app.services.speech_to_text import SpeechToTextService
from app.services.memory_builder import MemoryBuilder

SEED_MEETINGS = [
    {
        "meeting_id": "M001",
        "title": "Architecture Requirement Discussion",
        "date": "2026-05-10",
        "project": "AI Platform",
        "participants": ["Rahul (Tech Lead)", "Priya (Backend Engineer)", "Arjun (Product Manager)"],
        "transcript_text": """
00:01:00 - Rahul (Tech Lead): Welcome everyone. We need to define our storage architecture for the new GenAI memory platform.
00:02:15 - Arjun (Product Manager): The core requirement is that we must track decision evolution, user preferences, and complex transactional records.
00:03:40 - Priya (Backend Engineer): We expect complex relational queries, multi-table joins, and strict ACID transaction consistency.
00:05:10 - Rahul (Tech Lead): Let's explore document stores like MongoDB vs relational systems like PostgreSQL before making the call.
"""
    },
    {
        "meeting_id": "M002",
        "title": "Backend Storage Evaluation",
        "date": "2026-05-15",
        "project": "AI Platform",
        "participants": ["Rahul (Tech Lead)", "Priya (Backend Engineer)", "Arjun (Product Manager)"],
        "transcript_text": """
00:02:00 - Priya (Backend Engineer): MongoDB was proposed for schema flexibility, but our data model has rigid foreign key relationships and audit log requirements.
00:04:30 - Rahul (Tech Lead): MongoDB handles document nesting well, but multi-document transaction guarantees and complex joins are harder to maintain at scale.
00:06:50 - Priya (Backend Engineer): PostgreSQL gives us full SQL compliance, reliable transactions, JSONB for semi-structured fields, and strong team expertise.
00:08:15 - Arjun (Product Manager): Will PostgreSQL scale for our initial customer load?
00:09:40 - Rahul (Tech Lead): Yes, easily. Managed PostgreSQL on cloud with read replicas gives us everything we need.
"""
    },
    {
        "meeting_id": "M003",
        "title": "Architecture Decision Meeting",
        "date": "2026-05-20",
        "project": "AI Platform",
        "participants": ["Rahul (Tech Lead)", "Priya (Backend Engineer)", "Arjun (Product Manager)"],
        "transcript_text": """
00:10:00 - Rahul (Tech Lead): Today we finalize our primary database selection.
00:12:30 - Priya (Backend Engineer): Based on our evaluation, we officially choose PostgreSQL over MongoDB.
00:15:00 - Rahul (Tech Lead): Agreed. Reasons: 1) Strong transaction consistency, 2) Relational data requirements & complex joins, 3) Infrastructure compatibility, 4) Existing team expertise.
00:18:20 - Arjun (Product Manager): Great. MongoDB is rejected for the core store due to relational transaction constraints.
00:22:10 - Priya (Backend Engineer): I will take the action item to create the PostgreSQL database schema and configure our staging instance by next week.
"""
    },
    {
        "meeting_id": "M004",
        "title": "Database Implementation Review",
        "date": "2026-05-25",
        "project": "AI Platform",
        "participants": ["Rahul (Tech Lead)", "Priya (Backend Engineer)"],
        "transcript_text": """
00:01:30 - Priya (Backend Engineer): Update on PostgreSQL implementation: Schema creation complete and staging DB is online.
00:03:00 - Rahul (Tech Lead): Excellent work. The relational schemas for meetings, decisions, and action items are functioning smoothly.
00:05:40 - Priya (Backend Engineer): Next action is configuring automated data migrations and backup policies.
"""
    }
]

def seed_data(db_path: str = None):
    print("[SeedData] Initializing database schema...")
    init_db(db_path)
    
    stt_service = SpeechToTextService()
    builder = MemoryBuilder(db_path=db_path)
    
    for meeting_info in SEED_MEETINGS:
        print(f"[SeedData] Processing seed meeting '{meeting_info['title']}' ({meeting_info['meeting_id']})...")
        transcript = stt_service.parse_transcript_text(
            meeting_info["transcript_text"],
            meeting_info["meeting_id"]
        )
        builder.build_and_save_memory(
            meeting_id=meeting_info["meeting_id"],
            title=meeting_info["title"],
            date=meeting_info["date"],
            project=meeting_info["project"],
            transcript=transcript,
            given_participants=meeting_info["participants"]
        )
    print("[SeedData] Seeding successfully completed!")

if __name__ == "__main__":
    seed_data()
