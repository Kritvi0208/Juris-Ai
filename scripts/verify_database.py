"""
Verify Juris Legal Knowledge Base.
Redirects to scripts/verify_legal_knowledge_base.py.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.verify_legal_knowledge_base import main

if __name__ == "__main__":
    main()
