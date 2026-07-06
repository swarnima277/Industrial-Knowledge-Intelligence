"""
main.py — Industrial Knowledge Intelligence Platform
Member 1: Document Intelligence & Data Pipeline

Entry point. Run from terminal:
    python main.py

Menu:
    1. Upload Document
    2. View Stored Documents
    3. Exit
"""

import sys
from document_uploader   import DocumentUploader
from document_parser     import DocumentParser
from entity_extractor    import EntityExtractor
from chunk_processor     import ChunkProcessor
from embedding_generator import EmbeddingGenerator
from storage_manager     import StorageManager


# ---------------------------------------------------------------------------
# Instantiate all pipeline components (shared across menu cycles)
# ---------------------------------------------------------------------------
uploader   = DocumentUploader(uploads_dir="uploads", db_path="database/documents.json")
parser     = DocumentParser()
extractor  = EntityExtractor()
chunker    = ChunkProcessor(chunk_size=1000, chunk_overlap=200)
embedder   = EmbeddingGenerator()
storage    = StorageManager(base_dir="database")


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------
def run_pipeline(file_path: str):
    """
    Full pipeline for a single document:
      Upload → Parse → Extract Entities → Chunk → Embed → Store

    If any stage after upload fails the uploaded file is cleaned up so no
    half-processed document is left in the registry.
    """
    # 1. Upload & register
    metadata = uploader.upload(file_path)
    doc_id   = metadata["document_id"]

    try:
        # 2. Text extraction
        text = parser.parse(metadata["file_path"])
        if not text.strip():
            raise ValueError("No text could be extracted from this file. "
                             "The image may be blank or unreadable.")
        storage.save_text(doc_id, text)

        # 3. Entity extraction
        entities = extractor.extract(text)

        # 4. Chunking
        chunks = chunker.chunk(text, doc_id=doc_id)
        storage.save_chunks(doc_id, chunks)

        # 5. Embedding generation
        embeddings = embedder.generate(chunks)
        storage.save_embeddings(doc_id, embeddings)

    except Exception as e:
        # Pipeline failed after upload — remove the partial record so the
        # user can retry cleanly without a ghost document in the registry.
        print(f"\n  [PIPELINE ERROR] {e}")
        print(f"  Cleaning up incomplete record {doc_id} …")
        try:
            storage.delete_document(doc_id)
        except Exception:
            pass
        raise

    # 6. Enrich stored metadata with pipeline results
    storage.update_metadata(doc_id, {
        "entities":        entities,
        "chunk_count":     len(chunks),
        "embedding_count": len(embeddings),
        "text_path":       f"database/text/{doc_id}.txt",
        "chunks_path":     f"database/chunks/{doc_id}.json",
        "embeddings_path": f"database/embeddings/{doc_id}.npy",
    })

    print(f"\n{'='*50}")
    print("DOCUMENT STORED SUCCESSFULLY")
    print(f"  Document ID      : {doc_id}")
    print(f"  Chunks stored    : {len(chunks)}")
    print(f"  Embeddings stored: {len(embeddings)}")
    print(f"{'='*50}\n")


# ---------------------------------------------------------------------------
# Viewer: inspect a stored document
# ---------------------------------------------------------------------------
def inspect_document(doc_id: str):
    doc = storage.get_document(doc_id.upper())
    if not doc:
        print(f"  [!] Document '{doc_id}' not found.\n")
        return

    print(f"\n{'='*50}")
    print(f"DOCUMENT DETAILS: {doc_id.upper()}")
    print(f"{'='*50}")
    print(f"  Original File  : {doc.get('original_filename','—')}")
    print(f"  Upload Date    : {doc.get('upload_date','—')}")
    print(f"  File Type      : {doc.get('file_type','—').upper()}")
    print(f"  File Size      : {doc.get('file_size_bytes', 0):,} bytes")
    print(f"  Chunks         : {doc.get('chunk_count','—')}")
    print(f"  Embeddings     : {doc.get('embedding_count','—')}")

    entities = doc.get("entities", {})
    if entities:
        print("\n  --- Extracted Entities ---")
        labels = {
            "named_equipment":       "Named Equipment",
            "instrument_tags":       "Instrument Tags",
            "equipment_tags":        "Equipment Tags",
            "pipe_lines":            "Pipe Lines",
            "personnel_names":       "Personnel",
            "dates":                 "Dates",
            "process_parameters":    "Process Parameters",
            "regulatory_references": "Regulatory References",
        }
        for key, label in labels.items():
            items = [str(x).replace("\n", " ") for x in entities.get(key, [])]
            if items:
                print(f"  {label}: {', '.join(items[:5])}" +
                      (" …" if len(items) > 5 else ""))

        # ADD THIS: Display the structural relationships stored in the database
        relationships = entities.get("relationships", [])
        if relationships:
            print("\n  --- Extracted Relationships ---")
            for rel in relationships:
                print(f"  ({rel.get('source_tag')}) -[{rel.get('relationship_type')}]-> ({rel.get('target_parameter')})")

    print(f"{'='*50}\n")


# ---------------------------------------------------------------------------
# Menu: Delete a Document
# ---------------------------------------------------------------------------
def delete_document():
    docs = storage.all_documents()
    if not docs:
        print("\n  No documents stored yet.\n")
        return

    # Show available documents first so the user can pick
    print(f"\n{'='*50}")
    print("STORED DOCUMENTS")
    print(f"{'='*50}")
    for doc in docs:
        print(f"  {doc['document_id']}  |  {doc.get('original_filename','—')}")
    print()

    doc_id = input("  Enter Document ID to delete (or press Enter to cancel): ").strip().upper()
    if not doc_id:
        print("  Cancelled.\n")
        return

    # Confirm before deleting — this is irreversible
    doc = storage.get_document(doc_id)
    if not doc:
        print(f"  [!] Document '{doc_id}' not found.\n")
        return

    print(f"\n  You are about to permanently delete:")
    print(f"    {doc_id}  —  {doc.get('original_filename','—')}")
    confirm = input("  Type YES to confirm: ").strip()
    if confirm != "YES":
        print("  Deletion cancelled.\n")
        return

    try:
        result = storage.delete_document(doc_id)
        print(f"\n{'='*50}")
        print(f"DOCUMENT DELETED: {doc_id}")
        print(f"  Files removed:")
        for f in result["deleted_files"]:
            print(f"    - {f}")
        print(f"  Registry entry removed from documents.json")
        print(f"{'='*50}\n")
    except KeyError as e:
        print(f"\n  [ERROR] {e}\n")


# ---------------------------------------------------------------------------
# Menu: View All Stored Documents
# ---------------------------------------------------------------------------
def view_documents():
    docs = storage.all_documents()
    if not docs:
        print("\n  No documents stored yet.\n")
        return

    print(f"\n{'='*50}")
    print(f"STORED DOCUMENTS ({len(docs)} total)")
    print(f"{'='*50}")
    for doc in docs:
        print(f"  {doc['document_id']}  |  {doc.get('original_filename','—')}"
              f"  |  {doc.get('upload_date','—')[:10]}")
    print()

    choice = input("  Enter a Document ID to inspect (or press Enter to go back): ").strip()
    if choice:
        inspect_document(choice)


# ---------------------------------------------------------------------------
# Main menu loop
# ---------------------------------------------------------------------------
def main():
    print("\n" + "="*60)
    print("  INDUSTRIAL KNOWLEDGE INTELLIGENCE PLATFORM")
    print("="*60)

    while True:
        print("\nMAIN MENU")
        print("  1. Upload Document")
        print("  2. View Stored Documents")
        print("  3. Delete a Document")
        print("  4. Exit")

        choice = input("\nSelect an option : ").strip()

        if choice == "1":
            file_path = input("\nEnter file path: ").strip().strip('"').strip("'")
            if not file_path:
                print("  [!] No path entered.")
                continue
            try:
                run_pipeline(file_path)
            except FileNotFoundError as e:
                print(f"\n  [ERROR] {e}")
            except ValueError as e:
                print(f"\n  [ERROR] {e}")
            except Exception as e:
                print(f"\n  [UNEXPECTED ERROR] {e}")
                import traceback; traceback.print_exc()

        elif choice == "2":
            view_documents()

        elif choice == "3":
            delete_document()

        elif choice == "4":
            print("\n  Goodbye!\n")
            sys.exit(0)

        else:
            print("  [!] Invalid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
