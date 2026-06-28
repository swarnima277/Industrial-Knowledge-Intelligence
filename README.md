# Industrial Knowledge Intelligence Platform
## Member 1: Document Intelligence & Data Pipeline

---

## Quick Start

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python main.py
```

---

## Supported File Types

| Extension       | Extraction Method                        |
|-----------------|------------------------------------------|
| `.pdf`          | PyMuPDF (text layer) + PaddleOCR fallback for scanned pages |
| `.png` `.jpg` `.jpeg` | PaddleOCR                          |
| `.xlsx` `.xls`  | Pandas (all sheets → readable text)      |

---

## Project Structure

```
industrial_knowledge_platform/
├── main.py                  ← Entry point (CLI menu)
├── document_uploader.py     ← File intake, ID generation, metadata
├── document_parser.py       ← Text extraction (PDF / Image / Excel)
├── entity_extractor.py      ← Regex-based entity extraction (LLM-ready)
├── chunk_processor.py       ← RecursiveCharacterTextSplitter (1000/200)
├── embedding_generator.py   ← all-MiniLM-L6-v2 sentence embeddings
├── storage_manager.py       ← Filesystem persistence layer
├── requirements.txt
│
├── uploads/                 ← Copied original files (DOC001.pdf, …)
└── database/
    ├── documents.json       ← Master metadata registry
    ├── text/                ← DOC001.txt (extracted text)
    ├── chunks/              ← DOC001.json (chunk records)
    └── embeddings/          ← DOC001.npy + DOC001_index.json
```

---

## Pipeline Stages

```
Upload Document
    ↓
Assign DOC ID & copy to uploads/
    ↓
Text Extraction (PDF / OCR / Excel)
    ↓
Entity Extraction (equipment, personnel, dates, params, standards)
    ↓
Chunking (size=1000, overlap=200)
    ↓
Embedding Generation (all-MiniLM-L6-v2, 384-dim)
    ↓
Persist all artefacts to database/
```

---

## Sample Terminal Session

```
MAIN MENU
  1. Upload Document
  2. View Stored Documents
  3. Exit

Select option (1/2/3): 1

Enter file path: /home/user/docs/maintenance_report.pdf

==================================================
DOCUMENT UPLOADED
  ID       : DOC001
  File     : maintenance_report.pdf
  Saved to : uploads/DOC001.pdf
==================================================

  [Parser] Extracting text from DOC001.pdf …

==================================================
TEXT EXTRACTION COMPLETE
  Characters extracted: 14,382
==================================================

==================================================
ENTITY EXTRACTION COMPLETE

Equipment Tags:
  - P-101
  - FT-202A

Personnel:
  - Rahul Sharma

Dates:
  - 15 March 2025

Process Parameters:
  - 120 bar
  - 85 °C

Regulatory References:
  - API 570
==================================================

==================================================
CHUNKING COMPLETE
  Total Chunks : 18
  Chunk Size   : 1000 chars (overlap: 200)
==================================================

  [Embedder] Loading SentenceTransformer 'all-MiniLM-L6-v2' …
  [Embedder] Encoding 18 chunks …

==================================================
EMBEDDING GENERATION COMPLETE
  Embedding Dimension : 384
  Total Embeddings    : 18
==================================================

==================================================
DOCUMENT STORED SUCCESSFULLY
  Document ID      : DOC001
  Chunks stored    : 18
  Embeddings stored: 18
==================================================
```

---

## Extending the System

### Replace regex with LLM entity extraction

In `entity_extractor.py`, implement `_llm_extract()` and update the `extract()` call:

```python
entities = extractor.extract(text, use_llm=True)
```

### Plug into a vector database

Load the saved `.npy` file into FAISS, Chroma, or Weaviate:

```python
import numpy as np
vectors = np.load("database/embeddings/DOC001.npy")
```

### Enable MongoDB

Replace `StorageManager`'s JSON read/write methods with `pymongo` calls
while keeping the same public interface — no other file changes required.
