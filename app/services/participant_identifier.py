import re
from typing import List, Dict

class ParticipantIdentifier:
    def extract_participants(self, transcript_text: str, metadata_participants: List[str] = None) -> List[str]:
        participants = set(metadata_participants or [])
        
        # Regex for speaker labels in transcript like "Rahul:", "Priya:", "Speaker 1:", "Tech Lead:"
        speaker_matches = re.findall(r"^(?:Speaker\s*\d+|[A-Z][a-zA-Z0-9\s]{1,20}):", transcript_text, re.MULTILINE)
        for match in speaker_matches:
            name = match.rstrip(":").strip()
            if name:
                participants.add(name)
                
        # Common roles inference if speakers are default
        text_lower = transcript_text.lower()
        if "tech lead" in text_lower:
            participants.add("Tech Lead")
        if "backend engineer" in text_lower or "backend lead" in text_lower:
            participants.add("Backend Lead")
        if "product manager" in text_lower:
            participants.add("Product Manager")
            
        result = sorted(list(participants))
        return result if result else ["Engineering Team"]
