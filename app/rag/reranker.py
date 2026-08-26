from typing import List, Dict, Any

class Reranker:
    def rerank(self, query: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        
        def score_doc(doc):
            text = doc.get("text", "").lower()
            meta = doc.get("metadata", {})
            doc_type = meta.get("type", "")
            
            score = 0.0
            # Higher weight for decision and summary type docs
            if doc_type == "decision":
                score += 3.0
            elif doc_type == "summary":
                score += 2.0
                
            # Keyword matching
            overlap = sum(1 for w in query_words if len(w) > 2 and w in text)
            score += overlap * 1.5
            return score

        sorted_docs = sorted(docs, key=score_doc, reverse=True)
        return sorted_docs
