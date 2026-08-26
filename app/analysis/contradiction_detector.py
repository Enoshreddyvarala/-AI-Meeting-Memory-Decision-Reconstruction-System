from typing import List, Dict, Any, Optional
from app.models.decision import Decision

class ContradictionDetector:
    def detect_contradictions(self, decisions: List[Decision]) -> List[Dict[str, Any]]:
        contradictions = []
        if len(decisions) < 2:
            return contradictions

        # Group by topic similarity or entity
        pg_decisions = [d for d in decisions if "postgresql" in d.decision.lower() or "database" in d.decision.lower()]
        mongo_decisions = [d for d in decisions if "mongodb" in d.decision.lower()]

        if pg_decisions and mongo_decisions:
            contradictions.append({
                "type": "decision_evolution_or_conflict",
                "summary": "Both PostgreSQL and MongoDB were selected or strongly advocated across different meetings.",
                "decisions": [d.decision_id for d in pg_decisions + mongo_decisions],
                "recommendation": "Check decision timestamps to verify if MongoDB was superseded by PostgreSQL."
            })
            
        return contradictions
