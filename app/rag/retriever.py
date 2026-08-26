from typing import List, Dict, Any
from app.rag.vector_store import VectorStore
from app.database.repositories import DecisionRepository, MeetingRepository

class HybridRetriever:
    def __init__(self, vector_store: VectorStore = None, db_path: str = None):
        self.vector_store = vector_store or VectorStore(persist_dir=None)
        self.decision_repo = DecisionRepository(db_path)
        self.meeting_repo = MeetingRepository(db_path)

    def retrieve_context(self, query: str, top_k: int = 8, project_filter: str = None) -> List[Dict[str, Any]]:
        # 1. Semantic Vector Search
        where_filter = {"project": project_filter} if project_filter else None
        vector_results = self.vector_store.query(query, top_k=top_k, where_filter=where_filter)
        
        # 2. Database Keyword & Entity Match
        db_results = []
        query_lower = query.lower()
        
        all_decisions = self.decision_repo.list_all_decisions()
        for d in all_decisions:
            if any(term in query_lower for term in [d.title.lower(), d.decision.lower(), "postgresql", "mongodb", "database"]):
                meeting = self.meeting_repo.get_meeting(d.source_meeting_id)
                m_title = meeting.title if meeting else "Meeting"
                m_date = meeting.date if meeting else "Unknown Date"
                
                text_repr = f"Decision in '{m_title}' ({m_date}) [{d.timestamp}]: {d.title} -> {d.decision}. Rationale: {', '.join(d.rationale)}. Alternatives: {', '.join(d.alternatives)}. Participants: {', '.join(d.participants)}."
                db_results.append({
                    "id": d.decision_id,
                    "text": text_repr,
                    "metadata": {
                        "meeting_id": d.source_meeting_id,
                        "title": m_title,
                        "date": m_date,
                        "type": "decision",
                        "decision_id": d.decision_id
                    }
                })

        # Deduplicate and combine
        seen_ids = set()
        combined = []
        for item in vector_results + db_results:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                combined.append(item)
                
        return combined[:top_k]
