# Juris Documentation

Welcome to the documentation for **Juris**, an AI Legal Assistant for Ordinary Citizens in India.

## Overview
Juris is a specialized Retrieval-Augmented Generation (RAG) assistant designed to help Indian citizens understand everyday legal problems, extract structured facts, calculate limitation periods, practice dispute negotiations, and generate legally sound documents (notices, complaints, replies).

- **Streamlit**: Modern pastel-themed citizen interface (light-indigo/lavender).
- **LangChain Core & Community**: Dynamic legal tool-calling, LCEL chains, and structured memory.
- **ChromaDB**: 4 persistent vector collections (`acts_statutes`, `court_judgments`, `rules_regulations`, `legal_faqs`).
- **Google Gemini Multi-Model Cascade**: Gemini 3.7 Flash with fallback to 3.6/3.5 and offline deterministic engine.
- **Section-Aware Chunking**: Hierarchical splitting (`Act → Chapter → Section → Subsection`) with breadcrumb headers.

## Key Capabilities
- **Authoritative Indian Legal RAG**: Official Acts (BNS, CPA 2019, NI Act, SRA, TPA, RERA) and Supreme Court / High Court precedents.
- **Structured Fact Extraction**: Parties, dates, amounts, locations, evidence, and chronological timelines.
- **Anti-Hallucination Guardrails**: Statutory citation verification, outdated law detection, and strict refusal to invent citations.
- **10 Legal Tools**:
  - `statute_lookup`: Retrieve exact statutory provisions and subsections.
  - `judgment_lookup`: Search Supreme Court and High Court precedents.
  - `citation_verifier`: Verify statutory references against official schedules.
  - `outdated_law_checker`: Map repealed laws (IPC/CrPC) to modern enactments (BNS/BNSS).
  - `calculate_limitation`: Calculate statutory deadlines under Limitation Act 1963 and CPA 2019.
  - `calculate_court_fee`: Determine consumer forum and court fee thresholds.
  - `extract_case_facts`: Extract parties, dates, claims, and missing details.
  - `draft_legal_document`: Generate formal notices, consumer complaints, and replies.
  - `simulate_opposing_party`: Practice negotiations against an opposing party.
  - `emergency_legal_guide`: Provide immediate guidance for arrest, eviction, and cyber fraud.
- **Citizen Case Memory**: Isolated per-user disk storage (`data/user_cases/{user_id}/`).
- **Emergency Safety Bypass**: Instant escalation for imminent arrest, unlawful eviction, domestic violence, hearings within 24h, and cyber fraud (1930 / 15100 / 112).
