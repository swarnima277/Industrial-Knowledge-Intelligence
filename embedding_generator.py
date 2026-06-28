"""
EmbeddingGenerator: Produces dense vector embeddings for each text chunk using
the all-MiniLM-L6-v2 Sentence Transformer model (384-dimensional, ~80 MB).

No API keys required — model is downloaded from HuggingFace on first run.
"""

from typing import List
import numpy as np


class EmbeddingGenerator:
    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self):
        self._model = None  # lazy load to avoid slow startup when not needed

    def _load_model(self):
        if self._model is None:
            print(f"  [Embedder] Loading SentenceTransformer '{self.MODEL_NAME}' …")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
            print(f"  [Embedder] Model loaded. Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
        return self._model

    def generate(self, chunks: List[dict]) -> List[dict]:
        """
        Generate an embedding for each chunk.

        Returns a list of embedding records:
            {
                "chunk_id"  : "DOC001_chunk_000",
                "doc_id"    : "DOC001",
                "embedding" : [0.123, -0.456, ...],   # list of floats
                "dimension" : 384,
            }
        """
        model = self._load_model()
        texts = [c["text"] for c in chunks]

        # Encode all chunks in one batched call (faster than one-by-one)
        print(f"  [Embedder] Encoding {len(texts)} chunks …")
        vectors = model.encode(texts, show_progress_bar=True, batch_size=32)
        dim = vectors.shape[1]

        embeddings = []
        for chunk, vec in zip(chunks, vectors):
            embeddings.append({
                "chunk_id":  chunk["chunk_id"],
                "doc_id":    chunk["doc_id"],
                "embedding": vec.tolist(),   # JSON-serialisable list
                "dimension": dim,
            })

        print(f"\n{'='*50}")
        print("EMBEDDING GENERATION COMPLETE")
        print(f"  Embedding Dimension : {dim}")
        print(f"  Total Embeddings    : {len(embeddings)}")
        print(f"{'='*50}")

        return embeddings
