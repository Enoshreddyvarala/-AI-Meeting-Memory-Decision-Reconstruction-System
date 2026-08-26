import tempfile
import os
from app.database.sqlite_db import init_db
from sample_data.seed_data import seed_data
from app.rag.retriever import HybridRetriever

def test_hybrid_retrieval():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    try:
        from sample_data.seed_data import seed_data
        seed_data(db_path=db_path)
        
        retriever = HybridRetriever(db_path=db_path)
        results = retriever.retrieve_context("Why did we choose PostgreSQL?", top_k=5)
        assert len(results) > 0
        text_content = " ".join([r["text"] for r in results]).lower()
        assert "postgresql" in text_content or "mongodb" in text_content
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
