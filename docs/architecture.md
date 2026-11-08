# Architecture Overview

This document describes the technical architecture of **Juris** — an AI Legal Assistant for Ordinary Citizens in India.

## Component Layout

```
Citizen Legal Query
 │
 ├──> Streamlit UI (app.py)
       │
       ├──> Legal Intent & Safety Router (src/router.py)
       │     ├──> Emergency Safety Bypass (Arrest, Eviction, Violence, 24h Hearing, Cyber Fraud)
       │     └──> Fast Informational Interception
       │
       ├──> Citizen Case Profile Memory (src/memory.py)
       │     ├──> User Case Isolation (data/user_cases/{user_id}/)
       │     └──> Structured Facts (Parties, Dates, Amounts, Evidence, Timeline)
       │
       └──> LangChain Legal Agent Executor (src/agent.py)
             │
             ├──> Multi-Model LLM Cascade (Gemini 3.7 / 3.6 / 3.5 Flash)
             │     └──> Deterministic Local Legal Fallback Engine
             │
             ├──> 10 Specialized Legal Tools (src/tools.py)
             │     ├──> Statutory Citation Verifier & Outdated Law Checker
             │     ├──> Limitation Period & Court Fee Calculators
             │     ├──> Structured Fact Extraction & Timeline Generator
             │     ├──> Legal Document Generator (Notices, Complaints, Replies)
             │     └──> Opposing Party Negotiation Simulator
             │
             └──> Hybrid Multi-Collection Retriever (src/retriever.py)
                   │
                   └──> ChromaDB Vector Store (src/vector_store.py)
                         ├──> acts_statutes (Official statutory enactments)
                         ├──> court_judgments (SC and HC precedents)
                         ├──> rules_regulations (Gazette rules & notifications)
                         └──> legal_faqs (Explanatory citizen FAQs)
```

## System Modules
- **`src/config.py`**: Central configuration for ChromaDB legal collections, model endpoints, fallback chains, and legal disclaimers.
- **`src/constants.py`**: Domain taxonomy, statutory limitation schedules (Limitation Act 1963, CPA 2019, NI Act 1881), outdated law mappings (IPC->BNS, CrPC->BNSS), and emergency helplines.
- **`src/logger.py`**: Structured rotating file logger (`juris.log`) tracking tool calls, retrieval latency, and fallback events.
- **`src/router.py`**: Deterministic keyword triage for high-stakes emergencies + LLM structured intent routing.
- **`src/retriever.py`**: Custom hybrid retriever supporting multi-collection queries, citation boosting, MMR, and confidence scoring.
- **`src/vector_store.py`**: Persistent ChromaDB manager with rate-limit batching (batches of 25) and automatic backoff retry.
- **`src/memory.py`**: Per-user isolated case vault managing structured case entities, timeline chronology, and missing facts.
- **`src/agent.py`**: Multi-model agent executor with real-time token streaming, circuit-breaker cooldowns, and offline rule fallback.
- **`src/tools.py`**: 10 legal tools implementing statute lookups, citation verification, document drafting, and opposing party simulation.
- **`src/styles.py`**: Modern pastel SaaS UI stylesheet with light-indigo and lavender theme accents.
