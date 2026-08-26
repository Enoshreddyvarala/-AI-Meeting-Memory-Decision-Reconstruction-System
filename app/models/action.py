from pydantic import BaseModel
from typing import Optional

class ActionItem(BaseModel):
    action_id: str
    source_meeting_id: str
    description: str
    owner: Optional[str] = "Unassigned"
    due_date: Optional[str] = None
    priority: str = "Medium"  # High, Medium, Low
    status: str = "Pending"   # Pending, In Progress, Completed
    timestamp: str = "00:00:00"
