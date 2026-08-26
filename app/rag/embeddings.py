import os
from typing import List

class EmbeddingService:
    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers").lower()
        self.model = None
        if self.provider == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[EmbeddingService] Failed to load SentenceTransformer: {e}. Falling back to mock embeddings.")
                self.model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            try:
                embeddings = self.model.encode(texts)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                print(f"[EmbeddingService] Encoding failed: {e}")

        # Deterministic mock embedding fallback
        return [self._mock_embedding(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]

    def _mock_embedding(self, text: str) -> List[float]:
        # Generate 384-dim dummy vector based on hash
        import hashlib
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        val = int(h, 16)
        vec = [((val >> (i % 32)) & 1) * 0.1 for i in range(384)]
        return vec
