from chroma_manager import ChromaManager

db = ChromaManager()

db.store_manual(
    "P900",
    "Replace filter every 100 hours."
)

print("Done")