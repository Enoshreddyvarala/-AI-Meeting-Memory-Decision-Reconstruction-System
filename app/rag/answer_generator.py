from typing import List, Dict, Any
from app.services.llm_service import LLMService

class AnswerGenerator:
    def __init__(self, llm_service: LLMService = None):
        self.llm = llm_service or LLMService()

    def generate_grounded_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_docs:
            return {
                "answer": "I could not find sufficient evidence in the available meeting records to answer your question.",
                "sources": []
            }

        formatted_context = ""
        sources = []
        seen_sources = set()

        for idx, doc in enumerate(context_docs):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Meeting")
            date = meta.get("date", "Unknown Date")
            timestamp = meta.get("start_time", meta.get("timestamp", "00:00:00"))
            meeting_id = meta.get("meeting_id", "")
            
            src_key = f"{title}_{date}_{timestamp}"
            if src_key not in seen_sources:
                seen_sources.add(src_key)
                sources.append({
                    "meeting_id": meeting_id,
                    "title": title,
                    "date": date,
                    "timestamp": timestamp
                })

            formatted_context += f"Evidence [{idx+1}] Source: {title} ({date}) [{timestamp}]\n{doc.get('text', '')}\n\n"

        prompt = f"""
You are an organizational memory assistant.
Answer the user's question grounded strictly in the provided meeting evidence.

Grounding rules:
1. Do not invent facts, participants, dates, or reasons.
2. Clearly cite sources using [Meeting Title, Date, Timestamp].
3. Detail what was decided, why, alternatives considered, participants, and follow-up actions.
4. If evidence is insufficient, say so.

Question:
{query}

Meeting Evidence:
{formatted_context}
"""
        answer_text = self.llm.generate_completion(prompt)
        return {
            "answer": answer_text,
            "sources": sources
        }
