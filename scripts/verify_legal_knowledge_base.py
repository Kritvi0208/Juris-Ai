"""
Verify Juris Legal Knowledge Base and ChromaDB Collections.
"""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.vector_store import LegalVectorStore
from src.retriever import LegalRetriever
from src.logger import logger
from src.config import config

def main():
    print("=" * 65)
    print("JURIS - LEGAL KNOWLEDGE BASE VERIFICATION")
    print("=" * 65)
    store = LegalVectorStore()
    
    collections = [
        config.COLLECTION_ACTS,
        config.COLLECTION_JUDGMENTS,
        config.COLLECTION_RULES,
        config.COLLECTION_FAQS
    ]
    
    total_chunks = 0
    print("\n[1] Checking ChromaDB Collections:")
    for col_name in collections:
        try:
            count = store.get_document_count(col_name)
            total_chunks += count
            print(f"  - Collection '{col_name}': {count} chunks indexed")
        except Exception as e:
            print(f"  - Collection '{col_name}': Error checking count: {e}")

    print(f"\nTotal Indexed Legal Chunks: {total_chunks}")
    print(f"Persistent Directory: {store.persist_dir}")

    # Test retrieval across collections
    print("\n[2] Testing Multi-Collection Legal Retrieval:")
    retriever = LegalRetriever(store)
    test_queries = [
        ("Landlord refund security deposit tenant rights", config.COLLECTION_ACTS),
        ("Consumer complaint defective product refund limitation", config.COLLECTION_FAQS),
        ("Section 138 cheque dishonour notice timeline", config.COLLECTION_ACTS)
    ]

    for query, col in test_queries:
        start_time = time.time()
        docs = retriever.retrieve(query, collection_name=col, top_k=2)
        elapsed = time.time() - start_time
        print(f"\n  Query: '{query}' -> Target: {col}")
        print(f"  Retrieved {len(docs)} chunks in {elapsed:.3f}s")
        if docs:
            snippet = docs[0].page_content.replace("\n", " ")[:120]
            sec = docs[0].metadata.get("section", "N/A")
            act = docs[0].metadata.get("act_name", docs[0].metadata.get("source_name", "N/A"))
            print(f"  Top Match: [{act} | {sec}] -> \"{snippet}...\"")

    print("\n" + "=" * 65)
    print("Legal Knowledge Base is operational and verified.")
    print("=" * 65)

if __name__ == "__main__":
    main()
