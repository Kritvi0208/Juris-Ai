"""Document Parser for Indian Legal Texts in Juris.

Cleans formatting, refines section headers, and structures legal metadata.
"""

import re
from typing import List
from langchain_core.documents import Document
from src.logger import logger


class LegalDocumentParser:
    """Parses legal text chunks to refine section metadata and clean legal syntax."""

    @staticmethod
    def clean_chunk_text(text: str) -> str:
        """Cleans formatting or syntax issues from a chunk."""
        # Normalize excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def parse_sections(self, chunks: List[Document]) -> List[Document]:
        """Iterates through chunks and detects legal section headings to refine chunk metadata."""
        parsed_chunks = []
        for chunk in chunks:
            content = chunk.page_content

            # Look for legal headers in chunk
            sec_match = re.search(r'^(?:#|##|###|\*\*)\s*(?:Section|Sec\.|Article|Art\.)\s*(\d+[A-Za-z0-9()]*)', content, re.MULTILINE)
            if sec_match:
                chunk.metadata["section"] = f"Section {sec_match.group(1)}"

            ch_match = re.search(r'^(?:#|##|###|\*\*)\s*CHAPTER\s+([IVXLCDM0-9]+)', content, re.MULTILINE)
            if ch_match:
                chunk.metadata["chapter"] = f"Chapter {ch_match.group(1)}"

            chunk.page_content = self.clean_chunk_text(content)
            parsed_chunks.append(chunk)

        return parsed_chunks


# Alias for backward compatibility
MedicalDocumentParser = LegalDocumentParser
