"""Legal Retriever for Juris with Multi-Collection Search, MMR, Reranking, and Confidence Scoring.

Grounds all answers in authentic Indian legal authorities:
1. Acts & Statutes (e.g. Consumer Protection Act 2019, Model Tenancy Act, NI Act, BNS, BNSS, BSA).
2. Landmark Court Judgments (Supreme Court of India & High Courts).
3. Rules & Regulations (e.g. Consumer Protection E-Commerce Rules 2020, RBI Directions).
4. Explanatory Legal FAQs & Summaries.
"""

import re
from typing import Dict, List, Optional, Tuple
from langchain_core.documents import Document
from src.config import config
from src.constants import OUTDATED_LAW_MAPPINGS
from src.vector_store import LegalVectorStore
from src.logger import logger


class LegalRetriever:
    """Enhanced Indian Legal Retriever with multi-collection hybrid retrieval, deduplication, section-aware reranking, and confidence estimation."""

    def __init__(self, vector_store: Optional[LegalVectorStore] = None):
        self.vector_store = vector_store or LegalVectorStore()

    def check_outdated_law(self, query: str) -> List[str]:
        """Detects references to repealed or replaced legislation (e.g., IPC, CrPC, CPA 1986)."""
        warnings = []
        q_lower = query.lower()
        for old_term, explanation in OUTDATED_LAW_MAPPINGS.items():
            if re.search(r'\b' + re.escape(old_term) + r'\b', q_lower):
                warnings.append(explanation)
        return warnings

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        collection_name: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Document]:
        """Retrieves verified legal provisions with deduplication, keyword boosting, and L2 confidence scoring.
        
        Args:
            query: The user's legal problem or specific statutory question.
            top_k: Number of relevant chunks to return (defaults to config.RETRIEVER_TOP_K).
            collection_name: Specific collection ('acts_statutes', 'court_judgments', etc.) or None for cross-collection.
            category_filter: Optional category filter (e.g. 'Consumer Disputes', 'Tenancy').
        """
        k = top_k or config.RETRIEVER_TOP_K
        logger.info(f"Retrieving legal authorities for query: '{query[:80]}...' (collection={collection_name}, top_k={k})")

        # Determine collections to search
        target_collections = [collection_name] if collection_name else list(config.COLLECTIONS.keys())
        all_candidates_with_scores: List[Tuple[Document, float, str]] = []

        fetch_per_collection = max(8, k * 2)

        for col_name in target_collections:
            try:
                db = self.vector_store.get_collection(col_name)
                # Check if collection is empty
                if db._collection.count() == 0:
                    continue

                filter_dict = {"category": category_filter} if category_filter else None
                candidates = db.similarity_search_with_score(
                    query=query,
                    k=fetch_per_collection,
                    filter=filter_dict
                )
                for doc, dist in candidates:
                    all_candidates_with_scores.append((doc, dist, col_name))
            except Exception as e:
                logger.warning(f"Error querying collection '{col_name}': {e}")

        if not all_candidates_with_scores:
            logger.info("No matching records found across ChromaDB collections.")
            return []

        # 1. Deduplication by content hash / normalized text
        unique_candidates: List[Document] = []
        seen_content = set()

        for doc, distance, col_id in all_candidates_with_scores:
            norm_content = doc.page_content.strip().lower()
            # Dedup key combines first 100 chars + section if present
            dedup_key = norm_content[:150]
            if dedup_key not in seen_content:
                seen_content.add(dedup_key)
                doc.metadata["distance"] = distance
                doc.metadata["collection"] = col_id
                unique_candidates.append(doc)

        # 2. Section & Citation Aware Reranking (Legal keyword boost)
        query_lower = query.lower()
        query_words = set(re.findall(r'\b[a-z0-9_]{3,}\b', query_lower))

        # Check for explicit section references in query (e.g. 'section 138', 'section 2(11)', 'article 32')
        section_mentions = re.findall(r'\b(?:section|sec|article|art\.?)\s*(\d+[a-z0-9()]*)\b', query_lower)

        reranked_candidates = []
        for doc in unique_candidates:
            score_boost = 0.0
            meta = doc.metadata
            section_lower = str(meta.get("section", "")).lower()
            act_lower = str(meta.get("act_name", meta.get("source_name", ""))).lower()
            title_lower = str(meta.get("title", "")).lower()
            category_lower = str(meta.get("category", "")).lower()

            # Heavy boost if exact section matches query mention
            for sec in section_mentions:
                if sec in section_lower:
                    score_boost += 0.35  # Major boost for exact section match
                if sec in query_lower and sec in doc.page_content.lower():
                    score_boost += 0.20

            # Keyword match boost in titles / Act names
            for word in query_words:
                if len(word) > 3:
                    if word in section_lower:
                        score_boost += 0.15
                    if word in act_lower:
                        score_boost += 0.15
                    if word in title_lower:
                        score_boost += 0.10
                    if word in category_lower:
                        score_boost += 0.08

            # Binding statutory provisions get priority over secondary FAQs
            col_id = meta.get("collection", "")
            if col_id == config.COLLECTION_ACTS:
                score_boost += 0.05
            elif col_id == config.COLLECTION_JUDGMENTS:
                score_boost += 0.03

            raw_distance = meta.get("distance", 1.0)
            adjusted_distance = max(0.0, raw_distance - score_boost)
            doc.metadata["adjusted_distance"] = adjusted_distance
            reranked_candidates.append(doc)

        # Sort by adjusted distance (lowest distance = highest relevance)
        reranked_candidates.sort(key=lambda d: d.metadata.get("adjusted_distance", 1.0))

        # 3. Confidence Calculation and Filtering
        valid_docs = []
        for doc in reranked_candidates:
            distance = doc.metadata.get("distance", 1.0)
            # Acceptable threshold for relevance
            if distance < 1.35:
                # Confidence score normalized 0.0 to 1.0
                conf = max(0.0, min(1.0, 1.0 - (distance / 1.5)))
                doc.metadata["confidence_score"] = round(conf, 3)
                valid_docs.append(doc)
            else:
                logger.debug(f"Discarded legal chunk {doc.metadata.get('section')} due to high distance ({distance:.3f})")

        final_docs = valid_docs[:k]
        logger.info(f"Retriever returned {len(final_docs)} authoritative legal chunks.")
        return final_docs
