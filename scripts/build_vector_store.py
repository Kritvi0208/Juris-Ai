"""
Build / Ingest Legal Knowledge Base for Juris.
Redirects to scripts/ingest_legal_knowledge_base.py.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.ingest_legal_knowledge_base import ingest_all

if __name__ == "__main__":
    ingest_all()
