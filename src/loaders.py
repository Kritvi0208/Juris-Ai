"""Document Loaders for Indian Legal Datasets in Juris.

Loads documents into 4 distinct legal collections:
1. acts_statutes: Central & State Acts, BNS, BNSS, BSA, CPA 2019, Model Tenancy Act, NI Act, etc.
2. court_judgments: Supreme Court and High Court judgments from judgments.csv / jsonl.
3. rules_regulations: E-Commerce Rules, RBI Directions, CERT-In Guidelines, Rent Control Rules.
4. legal_faqs: Explanatory Q&As from sft/train.jsonl and citizen guidance files.
"""

import csv
import json
import os
from pathlib import Path
from typing import Dict, Generator, List, Optional
from langchain_core.documents import Document
from src.config import config
from src.logger import logger


class LegalDocumentLoader:
    """Loads Indian Acts, court judgments, regulations, and legal FAQs."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = Path(base_data_dir or config.DATA_DIR)

    def load_statutes(self, directory_path: Optional[Path] = None) -> List[Document]:
        """Loads statutory enactments, Acts, and legislative codes."""
        statutes_dir = Path(directory_path or (self.base_dir / "knowledge_base" / "statutes"))
        documents = []
        if not statutes_dir.exists():
            return documents

        for file_path in statutes_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in [".md", ".txt", ".json"]:
                try:
                    if file_path.suffix.lower() == ".json":
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                content = item.get("text") or item.get("content") or str(item)
                                meta = {
                                    "act_name": item.get("act", file_path.stem),
                                    "section": item.get("section", "General"),
                                    "jurisdiction": item.get("jurisdiction", "Central (All India)"),
                                    "effective_date": item.get("effective_date", ""),
                                    "status": item.get("status", "In Force"),
                                    "source_type": "Statute",
                                    "source_url": item.get("official_url", "https://www.indiacode.nic.in"),
                                    "collection": config.COLLECTION_ACTS
                                }
                                documents.append(Document(page_content=content, metadata=meta))
                    else:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        meta = {
                            "act_name": file_path.stem.replace("_", " ").title(),
                            "section": "General",
                            "jurisdiction": "Central (All India)",
                            "source_type": "Statute",
                            "collection": config.COLLECTION_ACTS
                        }
                        documents.append(Document(page_content=content, metadata=meta))
                except Exception as e:
                    logger.error(f"Error loading statute file {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} statute documents.")
        return documents

    def load_faqs(self, sft_file: Optional[Path] = None) -> List[Document]:
        """Loads explanatory legal FAQs from sft/train.jsonl and sft/val.jsonl."""
        file_to_load = Path(sft_file or (self.base_dir / "sft" / "train.jsonl"))
        documents = []
        if not file_to_load.exists():
            return documents

        try:
            with open(file_to_load, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        instruction = record.get("instruction", "")
                        response = record.get("response", "")
                        if instruction and response:
                            content = f"Question/Issue: {instruction}\n\nLegal Explanation: {response}"
                            meta = {
                                "act_name": "Indian Legal FAQ & Explanatory Guide",
                                "section": f"Legal FAQ #{idx+1}",
                                "category": "Legal Explanation",
                                "source_type": "Explanatory FAQ",
                                "collection": config.COLLECTION_FAQS
                            }
                            documents.append(Document(page_content=content, metadata=meta))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error loading legal FAQs from {file_to_load}: {e}")

        logger.info(f"Loaded {len(documents)} explanatory legal FAQ documents.")
        return documents

    def load_judgments(self, judgments_csv: Optional[Path] = None, max_records: int = 100) -> List[Document]:
        """Loads Supreme Court / High Court case metadata and holdings from judgments.csv."""
        csv_path = Path(judgments_csv or (self.base_dir / "raw" / "judgments.csv"))
        documents = []
        if not csv_path.exists():
            return documents

        try:
            with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    if idx >= max_records:
                        break
                    pet = row.get("pet", "").strip()
                    res = row.get("res", "").strip()
                    case_no = row.get("case_no", "").strip()
                    bench = row.get("bench", "").strip()
                    dt = row.get("judgment_dates", "").strip()

                    title = f"{pet} v. {res}" if pet and res else case_no or f"Supreme Court Case #{idx+1}"
                    content = (
                        f"Case Title: {title}\n"
                        f"Court: Supreme Court of India\n"
                        f"Case / Diary No: {case_no} (Diary: {row.get('diary_no', '')})\n"
                        f"Bench Composition: {bench}\n"
                        f"Judgment Date: {dt}\n"
                        f"Authoring Judge: {row.get('judgement_by', '')}\n"
                    )
                    meta = {
                        "act_name": "Supreme Court Precedent",
                        "title": title,
                        "court": "Supreme Court of India",
                        "case_citation": case_no or row.get("diary_no", ""),
                        "judgment_date": dt,
                        "bench": bench,
                        "jurisdiction": "Supreme Court of India",
                        "source_type": "Judicial Precedent",
                        "collection": config.COLLECTION_JUDGMENTS
                    }
                    documents.append(Document(page_content=content, metadata=meta))
        except Exception as e:
            logger.error(f"Error loading judgments CSV from {csv_path}: {e}")

        logger.info(f"Loaded {len(documents)} judicial judgment documents.")
        return documents


# Alias for backward compatibility
MedicalDocumentLoader = LegalDocumentLoader
