from app.services.speech_to_text import SpeechToTextService

def test_parse_transcript_text():
    service = SpeechToTextService()
    text = """
00:01:30 - Rahul: We should select PostgreSQL over MongoDB.
00:04:00 - Priya: I agree because of transactional requirements.
"""
    transcript = service.parse_transcript_text(text, "TEST_M001")
    assert transcript.meeting_id == "TEST_M001"
    assert len(transcript.segments) >= 2
    assert transcript.segments[0].speaker == "Rahul"
    assert "PostgreSQL" in transcript.segments[0].text
