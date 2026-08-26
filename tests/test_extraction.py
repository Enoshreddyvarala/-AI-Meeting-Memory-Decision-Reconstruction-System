from app.services.decision_extractor import DecisionExtractor
from app.services.action_extractor import ActionExtractor

def test_decision_extraction():
    extractor = DecisionExtractor()
    sample_text = "Rahul: We decided to select PostgreSQL. MongoDB was considered but rejected because of ACID transaction requirements."
    decisions = extractor.extract_decisions(sample_text, "TEST_M001")
    assert len(decisions) > 0
    dec = decisions[0]
    assert dec.source_meeting_id == "TEST_M001"
    assert "PostgreSQL" in dec.decision or "PostgreSQL" in dec.title

def test_action_extraction():
    extractor = ActionExtractor()
    sample_text = "Priya will create the PostgreSQL database schema by Friday."
    actions = extractor.extract_actions(sample_text, "TEST_M001")
    assert len(actions) > 0
    act = actions[0]
    assert act.source_meeting_id == "TEST_M001"
    assert "schema" in act.description.lower() or "database" in act.description.lower()
