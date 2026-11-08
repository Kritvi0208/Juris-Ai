# Legal Retrieval-Augmented Generation (RAG)

Juris uses a multi-collection hybrid Retrieval-Augmented Generation pipeline across verified Indian legal sources.

## Knowledge Architecture & Multi-Collection Separation

To prevent confusion between primary statutory enactments and explanatory or judicial commentary, the ChromaDB vector database is partitioned into 4 distinct collections:

1. **`acts_statutes`**: Authoritative Indian statutory text (BNS 2023, CPA 2019, Transfer of Property Act, Specific Relief Act, NI Act, etc.).
2. **`court_judgments`**: High Court and Supreme Court landmark rulings and citations.
3. **`rules_regulations`**: Delegated legislation, gazette rules, and government notifications.
4. **`legal_faqs`**: Explanatory citizen FAQs and procedural guidance.

## Document Ingestion & Section-Aware Chunking

```
[Official Indian Acts / Judgments / Regulations / FAQs]
       │
       ▼ (src/loaders.py - LegalDocumentLoader)
[Legal Document Objects with Rich Metadata]
       │
       ▼ (src/splitter.py - LegalTextSplitter)
[Section-Aware Chunks: Act → Chapter → Section → Subsection]
       │ (Breadcrumb headers preserved across split chunks)
       ▼ (src/embeddings.py)
[Vector Embeddings - Google Gemini gemini-embedding-001]
       │
       ▼ (src/vector_store.py)
[Persistent ChromaDB Store with 4 Isolated Collections]
```

## Retrieval & Confidence Scoring
- **Hybrid Multi-Collection Retrieval**: Queries target collections based on user query intent, with cross-collection merging.
- **Section & Citation Boosting**: Exact section numbers and Act titles detected in the query receive an explicit relevance score boost.
- **Maximal Marginal Relevance (MMR)**: Balances similarity with diversity to ensure statutory provisions and judicial commentaries do not drown each other out.
- **Confidence Calibration**: Derives a calibrated confidence score from L2 Euclidean distance:
  $$\text{Confidence} = \max(0.0, 1.0 - \text{distance} \times 0.65)$$
- **Anti-Hallucination & Provenance**: Every retrieved chunk preserves source metadata (`act_name`, `section`, `court`, `citation`, `judgment_date`, `jurisdiction`, `official_url`).
