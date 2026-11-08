"""ChromaDB Vector Store Interface for Juris - Indian Legal Assistant.

Manages persistent ChromaDB multi-collection storage:
- acts_statutes: Indian Acts and statutory provisions.
- court_judgments: Supreme Court and High Court judgments.
- rules_regulations: Rules, regulations, and government notifications.
- legal_faqs: Explanatory legal FAQs and citizen summaries.
"""

from pathlib import Path
from typing import Dict, List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.config import config
from src.embeddings import get_embeddings_model
from src.logger import logger


class LegalVectorStore:
    """Manages multi-collection persistent ChromaDB for Indian legal authorities."""

    def __init__(self):
        self.persist_dir = str(config.CHROMA_DB_DIR)
        self._collections: Dict[str, Chroma] = {}

    def get_collection(self, collection_name: Optional[str] = None) -> Chroma:
        """Retrieves or lazy-loads a specific ChromaDB collection."""
        name = collection_name or config.COLLECTION_ACTS
        if name in self._collections:
            return self._collections[name]

        try:
            embeddings = get_embeddings_model()
            logger.info(f"Connecting to persistent ChromaDB collection '{name}' at {self.persist_dir}")
            chroma_instance = Chroma(
                collection_name=name,
                persist_directory=self.persist_dir,
                embedding_function=embeddings
            )
            self._collections[name] = chroma_instance
            return chroma_instance
        except Exception as e:
            logger.error(f"Failed to load ChromaDB collection '{name}': {e}")
            raise

    def get_db(self, collection_name: Optional[str] = None) -> Chroma:
        """Alias for backward compatibility with RAG retriever."""
        return self.get_collection(collection_name)

    def add_documents(self, documents: List[Document], collection_name: Optional[str] = None) -> bool:
        """Indexes section-aware document chunks into the specified legal collection in batches."""
        if not documents:
            logger.warning(f"No documents provided to add to collection '{collection_name}'.")
            return False

        import time
        col_name = collection_name or config.COLLECTION_ACTS
        try:
            db = self.get_collection(col_name)
            logger.info(f"Indexing {len(documents)} legal chunks into '{col_name}'...")
            batch_size = 25
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                for attempt in range(4):
                    try:
                        db.add_documents(batch)
                        break
                    except Exception as err:
                        if attempt < 3 and ("429" in str(err) or "RESOURCE_EXHAUSTED" in str(err)):
                            logger.warning(f"Embedding quota 429 hit. Waiting 20s before retrying batch {i//batch_size + 1}...")
                            time.sleep(20.0)
                        else:
                            logger.error(f"Failed to add batch starting at {i}: {err}")
                            raise err
            logger.info(f"Successfully indexed documents into '{col_name}'.")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to '{col_name}': {e}")
            return False

    def get_document_count(self, collection_name: Optional[str] = None) -> int:
        """Returns the chunk count for a specific collection, or total across all collections."""
        if collection_name:
            try:
                db = self.get_collection(collection_name)
                return db._collection.count()
            except Exception as e:
                logger.error(f"Error getting count for '{collection_name}': {e}")
                return 0

        # Total across all 4 legal collections
        total = 0
        for col in config.COLLECTIONS.keys():
            try:
                db = self.get_collection(col)
                total += db._collection.count()
            except Exception:
                pass
        return total

    def get_collection_counts(self) -> Dict[str, int]:
        """Returns document counts broken down by collection."""
        counts = {}
        for col_id, col_label in config.COLLECTIONS.items():
            try:
                db = self.get_collection(col_id)
                counts[col_id] = db._collection.count()
            except Exception:
                counts[col_id] = 0
        return counts

    def clean_database(self, collection_name: Optional[str] = None) -> bool:
        """Wipes a specific collection or all collections using Chroma client API."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_dir)
            existing = [c.name for c in client.list_collections()]
            if collection_name:
                if collection_name in existing:
                    client.delete_collection(collection_name)
                if collection_name in self._collections:
                    del self._collections[collection_name]
                logger.info(f"Cleaned collection '{collection_name}'.")
            else:
                for c in existing:
                    client.delete_collection(c)
                self._collections.clear()
                logger.info("Cleaned all ChromaDB collections via client API.")
            return True
        except Exception as e:
            logger.error(f"Error cleaning ChromaDB: {e}")
            return False
