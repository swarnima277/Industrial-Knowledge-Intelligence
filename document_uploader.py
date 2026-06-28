"""
DocumentUploader: Handles file intake, validation, and initial metadata creation.
Copies uploaded files to the uploads/ directory and assigns unique document IDs.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".xls"}


class DocumentUploader:
    def __init__(self, uploads_dir: str = "uploads", db_path: str = "database/documents.json"):
        self.uploads_dir = Path(uploads_dir)
        self.db_path = Path(db_path)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_metadata_store(self) -> dict:
        """Load existing document metadata from JSON store."""
        if self.db_path.exists():
            with open(self.db_path, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata_store(self, store: dict):
        """Persist document metadata to JSON store."""
        with open(self.db_path, "w") as f:
            json.dump(store, f, indent=2)

    def _generate_doc_id(self, store: dict) -> str:
        """Generate next sequential document ID (DOC001, DOC002, ...)."""
        if not store:
            return "DOC001"
        last_id = max(int(k.replace("DOC", "")) for k in store.keys())
        return f"DOC{last_id + 1:03d}"

    def upload(self, file_path: str) -> dict:
        """
        Validate, copy, and register a document.
        Returns metadata dict for the uploaded document.
        """
        source = Path(file_path.strip())

        # Validate file exists
        if not source.exists():
            raise FileNotFoundError(f"File not found: {source}")

        # Validate file type
        ext = source.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type '{ext}'. Supported: {SUPPORTED_EXTENSIONS}")

        # Load existing records and generate a new ID
        store = self._load_metadata_store()
        doc_id = self._generate_doc_id(store)

        # Copy file to uploads/ with doc_id as stem
        dest_filename = f"{doc_id}{ext}"
        dest_path = self.uploads_dir / dest_filename
        shutil.copy2(source, dest_path)

        # Build and persist metadata
        metadata = {
            "document_id": doc_id,
            "original_filename": source.name,
            "upload_date": datetime.now().isoformat(),
            "file_path": str(dest_path),
            "file_type": ext.lstrip("."),
            "file_size_bytes": dest_path.stat().st_size,
        }
        store[doc_id] = metadata
        self._save_metadata_store(store)

        print(f"\n{'='*50}")
        print(f"DOCUMENT UPLOADED")
        print(f"  ID       : {doc_id}")
        print(f"  File     : {source.name}")
        print(f"  Saved to : {dest_path}")
        print(f"{'='*50}")

        return metadata

    def list_documents(self) -> list:
        """Return list of all stored document metadata records."""
        store = self._load_metadata_store()
        return list(store.values())

    def get_document(self, doc_id: str) -> dict:
        """Retrieve metadata for a single document by ID."""
        store = self._load_metadata_store()
        if doc_id not in store:
            raise KeyError(f"Document ID '{doc_id}' not found.")
        return store[doc_id]
