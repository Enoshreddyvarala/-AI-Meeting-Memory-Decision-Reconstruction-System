from typing import List, Dict, Any

class ConfidenceScorer:
    def calculate_confidence(
        self,
        has_explicit_statement: bool,
        participant_count: int,
        has_followup_action: bool,
        supporting_meetings_count: int,
        has_contradictions: bool
    ) -> float:
        score = 0.50
        if has_explicit_statement:
            score += 0.20
        if participant_count > 1:
            score += 0.10
        if has_followup_action:
            score += 0.10
        if supporting_meetings_count > 1:
            score += 0.10
            
        if has_contradictions:
            score -= 0.25
            
        return min(max(round(score, 2), 0.10), 0.99)
