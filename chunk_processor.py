"""
ChunkProcessor: Splits extracted text into overlapping chunks using LangChain's
RecursiveCharacterTextSplitter.

Configuration (per spec):
  chunk_size    = 1000 characters
  chunk_overlap = 200  characters
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size    = chunk_size
        self.chunk_overlap = chunk_overlap

        # RecursiveCharacterTextSplitter tries to split on paragraph/sentence/word
        # boundaries before falling back to raw character splits.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, text: str, doc_id: str = "") -> List[dict]:
        """
        Split text into chunks and return a list of chunk records.

        Each record:
            {
                "chunk_id"  : "DOC001_chunk_000",
                "doc_id"    : "DOC001",
                "chunk_index": 0,
                "text"      : "...",
                "char_count": 987,
            }
        """
        raw_chunks = self.splitter.split_text(text)

        chunks = []
        for idx, chunk_text in enumerate(raw_chunks):
            chunks.append({
                "chunk_id":    f"{doc_id}_chunk_{idx:03d}",
                "doc_id":      doc_id,
                "chunk_index": idx,
                "text":        chunk_text,
                "char_count":  len(chunk_text),
            })

        print(f"\n{'='*50}")
        print("CHUNKING COMPLETE")
        print(f"  Total Chunks : {len(chunks)}")
        print(f"  Chunk Size   : {self.chunk_size} chars (overlap: {self.chunk_overlap})")
        print(f"{'='*50}")

        return chunks
