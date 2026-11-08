"""Section-Aware Text Splitter for Indian Legal Documents in Juris.

Performs hierarchical chunking:
    Act → Chapter → Section → Subsection
Preserving essential legal source metadata:
    act_name, chapter, section, subsection, court, case_citation, judgment_date,
    jurisdiction, source_url, effective_date, source_type.
"""

import re
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import config
from src.logger import logger


class LegalTextSplitter:
    """Section-aware chunker for Indian statutory provisions, judgments, and legal FAQs."""

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP

        # Hierarchical legal boundary separators
        self.legal_separators = [
            "\n\nCHAPTER ",
            "\nCHAPTER ",
            "\n\nSection ",
            "\nSection ",
            "\n\nArticle ",
            "\nArticle ",
            "\n\n(",
            "\n(",
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.legal_separators,
            keep_separator=True
        )

    def _extract_section_header(self, text: str) -> Optional[str]:
        """Detects section or article numbers in chunk header."""
        match = re.search(r"\b(?:Section|Sec\.|Article|Art\.)\s*(\d+[A-Za-z0-9()]*)", text, re.IGNORECASE)
        if match:
            return f"Section {match.group(1)}"
        return None

    def _extract_chapter_header(self, text: str) -> Optional[str]:
        """Detects chapter Roman/Arabic numerals in chunk."""
        match = re.search(r"\bCHAPTER\s+([IVXLCDM0-9]+)\b", text, re.IGNORECASE)
        if match:
            return f"Chapter {match.group(1).upper()}"
        return None

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Splits legal documents while extracting and propagating section-aware metadata."""
        if not documents:
            logger.warning("Empty documents list passed to LegalTextSplitter.")
            return []

        logger.info(f"Splitting {len(documents)} legal documents (size={self.chunk_size}, overlap={self.chunk_overlap}).")
        raw_chunks = self.splitter.split_documents(documents)
        enriched_chunks: List[Document] = []

        current_chapter = "General"
        current_section = "General Provision"

        for idx, chunk in enumerate(raw_chunks):
            content = chunk.page_content
            meta = dict(chunk.metadata)

            # Check if this chunk introduces a new Chapter or Section
            detected_ch = self._extract_chapter_header(content)
            if detected_ch:
                current_chapter = detected_ch

            detected_sec = self._extract_section_header(content)
            if detected_sec:
                current_section = detected_sec

            # Inherit or populate metadata
            if not meta.get("chapter") or meta.get("chapter") == "General":
                meta["chapter"] = current_chapter

            if not meta.get("section") or meta.get("section") == "General Provision":
                meta["section"] = current_section

            # Clean and standardise source title
            act_name = meta.get("act_name") or meta.get("source_name") or "Indian Legal Authority"
            meta["act_name"] = act_name
            meta["source_name"] = act_name
            meta["chunk_id"] = f"{act_name}_{meta.get('section', 'sec')}_chunk_{idx}"

            # Append section breadcrumb header to content for embedding retrieval boost
            breadcrumb = f"[{act_name} | {meta.get('chapter')} | {meta.get('section')}]\n"
            if not content.startswith("["):
                chunk.page_content = breadcrumb + content

            chunk.metadata = meta
            enriched_chunks.append(chunk)

        logger.info(f"Created {len(enriched_chunks)} section-aware legal chunks.")
        return enriched_chunks


# Alias for backward compatibility
MedicalTextSplitter = LegalTextSplitter
