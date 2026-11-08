import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """Centralized configuration class for Juris - AI Legal Assistant for Indian Citizens."""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
    PROCESSED_DIR = DATA_DIR / "processed"
    RAW_DIR = DATA_DIR / "raw"
    USER_CASES_DIR = DATA_DIR / "user_cases"
    CHROMA_DB_DIR = BASE_DIR / "chroma_db"
    
    # Ensure dirs exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    USER_CASES_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # API configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    if not GOOGLE_API_KEY:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                GOOGLE_API_KEY = str(st.secrets["GOOGLE_API_KEY"]).strip()
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        except Exception:
            pass
    
    # Model configuration (High-speed, high-accuracy models with circuit-breaker fallback)
    LLM_MODEL_NAME = "gemini-3.6-flash"  # Primary accurate model
    FALLBACK_MODELS = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-flash-latest"
    ]
    EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"  # Default Google embedding model
    TEMPERATURE = 0.15  # Low temperature for precise legal grounding
    
    # Chroma Collections
    COLLECTION_ACTS = "acts_statutes"
    COLLECTION_JUDGMENTS = "court_judgments"
    COLLECTION_RULES = "rules_regulations"
    COLLECTION_FAQS = "legal_faqs"
    
    COLLECTIONS = {
        COLLECTION_ACTS: "Indian Acts & Statutory Provisions",
        COLLECTION_JUDGMENTS: "Supreme Court & High Court Judgments",
        COLLECTION_RULES: "Rules, Regulations & Government Notifications",
        COLLECTION_FAQS: "Legal FAQs & Explanatory Material"
    }
    
    # Retriever parameters
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    RETRIEVER_TOP_K = 4
    SIMILARITY_THRESHOLD = 0.5  # Filter out low-confidence matches
    
    # Memory config
    MAX_CHAT_HISTORY = 12  # Maximum number of conversations stored
    
    # Application settings
    APP_TITLE = "Juris - AI Legal Assistant"
    LOG_FILE = str(BASE_DIR / "juris.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Theme configuration (Pastel Light Indigo/Lavender Theme)
    COLOR_BG = "#FAF9FD"
    COLOR_ACCENT = "#5E4BB5"
    COLOR_TEXT = "#221C35"
    COLOR_MUTED = "#68617D"
    COLOR_CARD = "#FFFFFF"
    
    # Legal Disclaimer
    DISCLAIMER = (
        "Juris is an AI legal intelligence assistant designed to provide plain-language legal "
        "information grounded strictly in verified Indian statutes and judicial precedents. "
        "It does not constitute legal representation or formal legal advice and does not create an "
        "advocate-client relationship. In urgent, complex, or high-risk matters, please consult an "
        "enrolled Advocate or contact the State Legal Services Authority (NALSA / DLSA)."
    )

# Instantiate a global config object
config = AppConfig()
