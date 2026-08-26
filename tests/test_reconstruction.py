import tempfile
import os
from sample_data.seed_data import seed_data
from app.analysis.decision_reconstruction import DecisionReconstructionEngine

def test_decision_reconstruction_core_scenario():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    try:
        seed_data(db_path=db_path)
        engine = DecisionReconstructionEngine(db_path=db_path)
        
        result = engine.reconstruct_decision("Why did we choose PostgreSQL instead of MongoDB three months ago?")
        
        assert "answer" in result
        assert len(result["answer"]) > 0
        assert "reasons" in result
        assert len(result["reasons"]) > 0
        assert "alternatives" in result
        assert "MongoDB" in result["alternatives"] or "mongodb" in str(result["alternatives"]).lower()
        assert "confidence" in result
        assert result["confidence"] >= 0.50
        assert "sources" in result
        assert len(result["sources"]) > 0
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
