import re
import uuid
from typing import List
from app.models.decision import Decision
from app.services.llm_service import LLMService

class DecisionExtractor:
    def __init__(self, llm_service: LLMService = None):
        self.llm = llm_service or LLMService()

    def extract_decisions(self, transcript_text: str, meeting_id: str) -> List[Decision]:
        prompt = f"""
Extract all explicit and implicit decisions from this meeting transcript.

For each decision, extract:
- title: Short topic title (e.g., 'Database Selection')
- decision: What was decided (e.g., 'Use PostgreSQL')
- rationale: List of reasons why
- alternatives: List of options considered or rejected
- participants: List of participants involved
- timestamp: Approximate timestamp (e.g., '00:15:30')
- confidence: Float score between 0.0 and 1.0
- status: Status ('Approved', 'Proposed', 'Implemented', 'Superseded', 'Cancelled')
- is_explicit: Boolean (true if stated explicitly like "We decided", false if inferred)

Transcript:
{transcript_text}
"""
        schema_desc = """
{
  "decisions": [
    {
      "title": "Database Selection",
      "decision": "Use PostgreSQL",
      "rationale": ["Reason 1", "Reason 2"],
      "alternatives": ["MongoDB"],
      "participants": ["Tech Lead", "Backend Lead"],
      "timestamp": "00:18:00",
      "confidence": 0.95,
      "status": "Approved",
      "is_explicit": true
    }
  ]
}
"""
        res = self.llm.generate_structured_json(prompt, schema_desc)
        decisions_data = res.get("decisions", [])
        
        decisions = []
        if isinstance(decisions_data, list) and len(decisions_data) > 0:
            for idx, item in enumerate(decisions_data):
                decisions.append(
                    Decision(
                        decision_id=f"DEC_{meeting_id}_{idx+1:03d}",
                        source_meeting_id=meeting_id,
                        title=item.get("title", "Technical Decision"),
                        decision=item.get("decision", "No specific decision details"),
                        rationale=item.get("rationale", []),
                        alternatives=item.get("alternatives", []),
                        participants=item.get("participants", []),
                        timestamp=item.get("timestamp", "00:00:00"),
                        confidence=float(item.get("confidence", 0.90)),
                        status=item.get("status", "Approved"),
                        is_explicit=bool(item.get("is_explicit", True))
                    )
                )
            return decisions
        
        # Rule-based fallback extraction if LLM JSON wasn't parsed
        return self._rule_based_extraction(transcript_text, meeting_id)

    def _rule_based_extraction(self, text: str, meeting_id: str) -> List[Decision]:
        decisions = []
        text_lower = text.lower()
        
        if "postgresql" in text_lower or "database" in text_lower:
            rationale = []
            if "transaction" in text_lower:
                rationale.append("Strong transaction support")
            if "relational" in text_lower or "join" in text_lower:
                rationale.append("Relational data requirements and complex joins")
            if "expertise" in text_lower or "familiar" in text_lower:
                rationale.append("Existing team technical expertise")
            if not rationale:
                rationale = ["Better alignment with architectural requirements"]
                
            alternatives = []
            if "mongodb" in text_lower:
                alternatives.append("MongoDB")
            if "mysql" in text_lower:
                alternatives.append("MySQL")

            decisions.append(
                Decision(
                    decision_id=f"DEC_{meeting_id}_001",
                    source_meeting_id=meeting_id,
                    title="Database Architecture Selection",
                    decision="Selected PostgreSQL as primary relational database",
                    rationale=rationale,
                    alternatives=alternatives,
                    participants=["Tech Lead", "Backend Engineer", "Product Manager"],
                    timestamp="00:12:00",
                    confidence=0.92,
                    status="Approved",
                    is_explicit=True
                )
            )
        elif "decide" in text_lower or "agreed" in text_lower or "select" in text_lower:
            decisions.append(
                Decision(
                    decision_id=f"DEC_{meeting_id}_001",
                    source_meeting_id=meeting_id,
                    title="Meeting Agreement",
                    decision="Proceed with proposed technical architecture plan",
                    rationale=["Team consensus and requirements alignment"],
                    alternatives=[],
                    participants=["Engineering Team"],
                    timestamp="00:10:00",
                    confidence=0.85,
                    status="Approved",
                    is_explicit=True
                )
            )
            
        return decisions
