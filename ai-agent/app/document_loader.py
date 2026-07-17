from pathlib import Path
from chunker import chunk_text

all_chunks = []

folder = Path("../data")

for file in folder.glob("*.txt"):

    text = file.read_text(encoding="utf-8")

    chunks = chunk_text(text)

    all_chunks.extend(chunks)

print(all_chunks)