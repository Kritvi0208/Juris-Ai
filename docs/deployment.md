# Deployment Guidelines

Follow these practices to deploy **Juris** into local, staging, or cloud production environments.

## Local Deployment
Run Juris locally via Streamlit:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Cloud Deployment (Streamlit Community Cloud / Cloud Run / Hugging Face Spaces)
1. **Repository Setup**: Push the complete codebase to your repository.
2. **Environment Secrets**: Add `GOOGLE_API_KEY` to the cloud environment variables.
3. **Database Persistence**: Ensure `chroma_db/` is mounted to persistent storage or run `python scripts/ingest_legal_knowledge_base.py` as a post-install build step.
4. **Resilience**: The multi-tier model cascade (Gemini 3.7 -> 3.6 -> 3.5 -> local engine) guarantees zero downtime even under strict API rate limits.
