import os
import json
from pathlib import Path
from typing import List, Dict, Any
from app.rag.embeddings import EmbeddingService
from app.models.transcript import TranscriptSegment
from app.models.decision import Decision

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/vector_store")

class VectorStore:
    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or CHROMA_DIR
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.embedding_service = EmbeddingService()
        
        self.chroma_client = None
        self.collection = None
        self._init_chroma()

        # In-memory backup store for lightweight fallback
        self.fallback_docs: List[Dict[str, Any]] = []

    def _init_chroma(self):
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name="meeting_memories",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"[VectorStore] ChromaDB initialization skipped/failed: {e}. Using fallback in-memory store.")
            self.chroma_client = None

    def index_meeting_transcript(
        self,
        meeting_id: str,
        title: str,
        date: str,
        project: str,
        segments: List[TranscriptSegment]
    ):
        if not segments:
            return

        documents = []
        metadatas = []
        ids = []

        for seg in segments:
            doc_id = seg.segment_id
            text = f"Speaker: {seg.speaker} [{seg.start_time} - {seg.end_time}]: {seg.text}"
            meta = {
                "meeting_id": meeting_id,
                "title": title,
                "date": date,
                "project": project,
                "speaker": seg.speaker,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "type": "transcript"
            }
            documents.append(text)
            metadatas.append(meta)
            ids.append(doc_id)
            self.fallback_docs.append({"id": doc_id, "text": text, "metadata": meta})

        embeddings = self.embedding_service.embed_texts(documents)

        if self.collection:
            try:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            except Exception as e:
                print(f"[VectorStore] Failed to upsert to ChromaDB: {e}")

    def index_meeting_memory(
        self,
        meeting_id: str,
        title: str,
        date: str,
        project: str,
        summary: str,
        decisions: List[Decision]
    ):
        documents = []
        metadatas = []
        ids = []

        # Index summary
        sum_id = f"SUM_{meeting_id}"
        sum_text = f"Meeting Summary for '{title}' on {date}: {summary}"
        sum_meta = {
            "meeting_id": meeting_id,
            "title": title,
            "date": date,
            "project": project,
            "type": "summary"
        }
        documents.append(sum_text)
        metadatas.append(sum_meta)
        ids.append(sum_id)
        self.fallback_docs.append({"id": sum_id, "text": sum_text, "metadata": sum_meta})

        # Index decisions
        for d in decisions:
            dec_id = d.decision_id
            dec_text = f"Decision in '{title}' ({date}) at {d.timestamp}: {d.title} -> {d.decision}. Rationale: {', '.join(d.rationale)}. Alternatives considered: {', '.join(d.alternatives)}. Participants: {', '.join(d.participants)}."
            dec_meta = {
                "meeting_id": meeting_id,
                "title": title,
                "date": date,
                "project": project,
                "type": "decision",
                "decision_id": dec_id
            }
            documents.append(dec_text)
            metadatas.append(dec_meta)
            ids.append(dec_id)
            self.fallback_docs.append({"id": dec_id, "text": dec_text, "metadata": dec_meta})

        embeddings = self.embedding_service.embed_texts(documents)

        if self.collection:
            try:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            except Exception as e:
                print(f"[VectorStore] Failed to upsert memory to ChromaDB: {e}")

    def query(self, query_text: str, top_k: int = 5, where_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.embed_query(query_text)

        if self.collection:
            try:
                kwargs = {
                    "query_embeddings": [query_embedding],
                    "n_results": top_k
                }
                if where_filter:
                    kwargs["where"] = where_filter
                results = self.collection.query(**kwargs)
                
                docs = []
                if results and "documents" in results and results["documents"]:
                    matched_docs = results["documents"][0]
                    matched_metas = results["metadatas"][0] if "metadatas" in results else [{}]*len(matched_docs)
                    matched_ids = results["ids"][0] if "ids" in results else [""]*len(matched_docs)
                    
                    for i in range(len(matched_docs)):
                        docs.append({
                            "id": matched_ids[i],
                            "text": matched_docs[i],
                            "metadata": matched_metas[i]
                        })
                return docs
            except Exception as e:
                print(f"[VectorStore] Query failed in ChromaDB: {e}. Falling back to keyword/in-memory match.")

        # Fallback search matching keywords
        return self._fallback_query(query_text, top_k)

    def _fallback_query(self, query_text: str, top_k: int) -> List[Dict[str, Any]]:
        words = [w.lower() for w in query_text.split() if len(w) > 2]
        scored = []
        for doc in self.fallback_docs:
            score = sum(1 for w in words if w in doc["text"].lower())
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
