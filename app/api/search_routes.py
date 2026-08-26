from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.rag.retriever import HybridRetriever

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    project: Optional[str] = None

@router.post("")
def search_meetings(req: SearchRequest):
    retriever = HybridRetriever()
    results = retriever.retrieve_context(req.query, top_k=req.top_k, project_filter=req.project)
    return {"query": req.query, "results": results}
