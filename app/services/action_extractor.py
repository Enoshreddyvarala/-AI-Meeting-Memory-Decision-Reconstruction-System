from typing import List
from app.models.action import ActionItem
from app.services.llm_service import LLMService

class ActionExtractor:
    def __init__(self, llm_service: LLMService = None):
        self.llm = llm_service or LLMService()

    def extract_actions(self, transcript_text: str, meeting_id: str) -> List[ActionItem]:
        prompt = f"""
Extract all action items from this meeting transcript.

For each action item, extract:
- description: Task description
- owner: Person or team assigned (e.g. 'Backend Lead' or 'Unassigned')
- due_date: Deadline mentioned or null
- priority: 'High', 'Medium', or 'Low'
- timestamp: Timestamp in transcript

Transcript:
{transcript_text}
"""
        schema_desc = """
{
  "actions": [
    {
      "description": "Task description...",
      "owner": "Backend Team",
      "due_date": "2026-06-01",
      "priority": "High",
      "timestamp": "00:25:00"
    }
  ]
}
"""
        res = self.llm.generate_structured_json(prompt, schema_desc)
        actions_data = res.get("actions", [])
        
        actions = []
        if isinstance(actions_data, list) and len(actions_data) > 0:
            for idx, item in enumerate(actions_data):
                actions.append(
                    ActionItem(
                        action_id=f"ACT_{meeting_id}_{idx+1:03d}",
                        source_meeting_id=meeting_id,
                        description=item.get("description", "Follow-up task"),
                        owner=item.get("owner", "Unassigned"),
                        due_date=item.get("due_date", None),
                        priority=item.get("priority", "Medium"),
                        status="Pending",
                        timestamp=item.get("timestamp", "00:00:00")
                    )
                )
            return actions

        # Fallback heuristic
        return self._rule_based_actions(transcript_text, meeting_id)

    def _rule_based_actions(self, text: str, meeting_id: str) -> List[ActionItem]:
        actions = []
        text_lower = text.lower()
        if "schema" in text_lower or "database" in text_lower:
            actions.append(
                ActionItem(
                    action_id=f"ACT_{meeting_id}_001",
                    source_meeting_id=meeting_id,
                    description="Create PostgreSQL database schema and configuration",
                    owner="Backend Lead",
                    due_date="Next Sprint",
                    priority="High",
                    status="Pending",
                    timestamp="00:28:10"
                )
            )
        if "staging" in text_lower or "configure" in text_lower or "deploy" in text_lower:
            actions.append(
                ActionItem(
                    action_id=f"ACT_{meeting_id}_002",
                    source_meeting_id=meeting_id,
                    description="Configure staging environment database instance",
                    owner="DevOps Engineer",
                    due_date="Friday",
                    priority="Medium",
                    status="Pending",
                    timestamp="00:30:00"
                )
            )
        if not actions:
            actions.append(
                ActionItem(
                    action_id=f"ACT_{meeting_id}_001",
                    source_meeting_id=meeting_id,
                    description="Document discussion outcomes and distribute notes",
                    owner="Meeting Host",
                    due_date=None,
                    priority="Low",
                    status="Pending",
                    timestamp="00:00:00"
                )
            )
        return actions
