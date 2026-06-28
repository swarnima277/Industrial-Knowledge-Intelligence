"""
StorageManager: Persists all pipeline artefacts to the local filesystem.

Directory layout:
    database/
        documents.json          ← master metadata registry
        text/   DOC001.txt      ← extracted text
        chunks/ DOC001.json     ← chunk records
        embeddings/ DOC001.npy  ← embeddings as NumPy arrays (+ companion JSON)
"""

import json
import numpy as np
from pathlib import Path
from typing import List


class StorageManager:
    def __init__(self, base_dir: str = "database"):
        self.base       = Path(base_dir)
        self.text_dir   = self.base / "text"
        self.chunk_dir  = self.base / "chunks"
        self.embed_dir  = self.base / "embeddings"
        self.meta_path  = self.base / "documents.json"

        # Ensure all directories exist
        for d in (self.text_dir, self.chunk_dir, self.embed_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_meta(self) -> dict:
        if self.meta_path.exists():
            with open(self.meta_path) as f:
                return json.load(f)
        return {}

    def _save_meta(self, store: dict):
        with open(self.meta_path, "w") as f:
            json.dump(store, f, indent=2)

    # ------------------------------------------------------------------
    # Save operations (called after each pipeline stage)
    # ------------------------------------------------------------------
    def save_text(self, doc_id: str, text: str):
        """Write extracted text to database/text/<doc_id>.txt"""
        path = self.text_dir / f"{doc_id}.txt"
        path.write_text(text, encoding="utf-8")

    def save_chunks(self, doc_id: str, chunks: List[dict]):
        """Write chunk records to database/chunks/<doc_id>.json"""
        path = self.chunk_dir / f"{doc_id}.json"
        with open(path, "w") as f:
            json.dump(chunks, f, indent=2)

    def save_embeddings(self, doc_id: str, embeddings: List[dict]):
        """
        Save embeddings in two formats:
          - NumPy .npy  (fast binary; suitable for downstream FAISS/vector DB ingestion)
          - JSON        (human-readable / debug)
        """
        vectors = np.array([e["embedding"] for e in embeddings], dtype=np.float32)
        np.save(str(self.embed_dir / f"{doc_id}.npy"), vectors)

        # Lightweight JSON companion (chunk_id ↔ row index mapping)
        index_map = [
            {"row": i, "chunk_id": e["chunk_id"], "dimension": e["dimension"]}
            for i, e in enumerate(embeddings)
        ]
        with open(self.embed_dir / f"{doc_id}_index.json", "w") as f:
            json.dump(index_map, f, indent=2)

    def update_metadata(self, doc_id: str, extra: dict):
        """Merge extra keys (entities, counts, paths) into the document record."""
        store = self._load_meta()
        if doc_id in store:
            store[doc_id].update(extra)
            self._save_meta(store)

    # ------------------------------------------------------------------
    # Delete operation
    # ------------------------------------------------------------------
    def delete_document(self, doc_id: str) -> dict:
        """
        Remove all artefacts for a document:
          - uploads/<doc_id>.*          (original uploaded file)
          - database/text/<doc_id>.txt
          - database/chunks/<doc_id>.json
          - database/embeddings/<doc_id>.npy + _index.json
          - entry in documents.json

        Returns the deleted metadata record.
        Raises KeyError if the document ID does not exist.
        """
        store = self._load_meta()
        doc_id = doc_id.upper()

        if doc_id not in store:
            raise KeyError(f"Document '{doc_id}' not found in registry.")

        meta = store[doc_id]
        deleted_files = []

        # 1. Original uploaded file (path stored in metadata)
        upload_path = Path(meta.get("file_path", ""))
        if upload_path.exists():
            upload_path.unlink()
            deleted_files.append(str(upload_path))

        # 2. Extracted text
        text_path = self.text_dir / f"{doc_id}.txt"
        if text_path.exists():
            text_path.unlink()
            deleted_files.append(str(text_path))

        # 3. Chunks
        chunk_path = self.chunk_dir / f"{doc_id}.json"
        if chunk_path.exists():
            chunk_path.unlink()
            deleted_files.append(str(chunk_path))

        # 4. Embeddings — binary array and index map
        for fname in (f"{doc_id}.npy", f"{doc_id}_index.json"):
            p = self.embed_dir / fname
            if p.exists():
                p.unlink()
                deleted_files.append(str(p))

        # 5. Remove from the metadata registry and persist
        del store[doc_id]
        self._save_meta(store)

        return {"deleted_doc_id": doc_id, "deleted_files": deleted_files, "metadata": meta}

    # ------------------------------------------------------------------
    # Read operations (used by the viewer)
    # ------------------------------------------------------------------
    def load_text(self, doc_id: str) -> str:
        path = self.text_dir / f"{doc_id}.txt"
        if not path.exists():
            return "(text not found)"
        return path.read_text(encoding="utf-8")

    def load_chunks(self, doc_id: str) -> List[dict]:
        path = self.chunk_dir / f"{doc_id}.json"
        if not path.exists():
            return []
        with open(path) as f:
            return json.load(f)

    def load_embeddings_index(self, doc_id: str) -> List[dict]:
        path = self.embed_dir / f"{doc_id}_index.json"
        if not path.exists():
            return []
        with open(path) as f:
            return json.load(f)

    def all_documents(self) -> list:
        return list(self._load_meta().values())

    def get_document(self, doc_id: str) -> dict:
        store = self._load_meta()
        return store.get(doc_id, {})