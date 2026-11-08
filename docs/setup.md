# Setup and Installation

Follow these steps to set up **Juris** in your local development environment.

## Prerequisites
- Python 3.11 or higher
- A Google AI Studio API key (Gemini API key)

## Step 1: Clone Repository
```bash
git clone https://github.com/your-username/Juris-Ai.git
cd "Juris Ai"
```

## Step 2: Virtual Environment Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
LOG_LEVEL=INFO
```

## Step 5: Ingest Legal Knowledge Base
Ingest the 4 official Indian legal collections (`acts_statutes`, `court_judgments`, `rules_regulations`, `legal_faqs`):
```bash
python scripts/ingest_legal_knowledge_base.py
```

## Step 6: Launch Web App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

## Step 7: Run Evaluation Scenarios
```bash
python tests/test_juris_scenarios.py
```
