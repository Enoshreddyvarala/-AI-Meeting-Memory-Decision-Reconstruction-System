from typing import List, Dict, Any
from app.models.decision import DecisionTimelineItem, Decision
from app.database.repositories import DecisionRepository, MeetingRepository, ActionRepository

class DecisionTimelineBuilder:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.decision_repo = DecisionRepository(db_path)
        self.meeting_repo = MeetingRepository(db_path)
        self.action_repo = ActionRepository(db_path)

    def build_timeline_for_topic(self, topic: str = "database") -> List[DecisionTimelineItem]:
        timeline: List[DecisionTimelineItem] = []
        all_meetings = self.meeting_repo.list_meetings()
        
        # Sort meetings by date
        all_meetings.sort(key=lambda m: m.date)
        
        for meeting in all_meetings:
            decisions = self.decision_repo.list_decisions_by_meeting(meeting.meeting_id)
            actions = self.action_repo.list_actions_by_meeting(meeting.meeting_id)
            
            # Check decisions matching topic
            for d in decisions:
                if topic.lower() in d.title.lower() or topic.lower() in d.decision.lower() or topic.lower() in " ".join(d.alternatives).lower() or topic.lower() in " ".join(d.rationale).lower():
                    event_type = "Decision Made"
                    if d.status == "Superseded":
                        event_type = "Superseded"
                    elif d.status == "Proposed":
                        event_type = "Proposed"
                        
                    timeline.append(
                        DecisionTimelineItem(
                            date=meeting.date,
                            meeting_id=meeting.meeting_id,
                            meeting_title=meeting.title,
                            event_type=event_type,
                            description=f"{d.title}: {d.decision} (Alternatives: {', '.join(d.alternatives)})",
                            decision_id=d.decision_id
                        )
                    )
            
            # Check actions matching topic
            for a in actions:
                if topic.lower() in a.description.lower():
                    timeline.append(
                        DecisionTimelineItem(
                            date=meeting.date,
                            meeting_id=meeting.meeting_id,
                            meeting_title=meeting.title,
                            event_type="Implementation Action",
                            description=f"Action assigned to {a.owner}: {a.description}",
                            decision_id=None
                        )
                    )
                    
        return timeline
