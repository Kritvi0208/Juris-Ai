"""LCEL (LangChain Expression Language) Legal RAG Chain for Juris.

Executes context-enriched retrieval and generation grounded strictly in
verified Indian statutes, court precedents, and regulations.
"""

from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import config
from src.retriever import LegalRetriever
from src.prompts import get_agent_prompt_template
from src.logger import logger


class LegalRAGChain:
    """Implements LCEL for context-enriched legal queries."""

    def __init__(self, llm: ChatGoogleGenerativeAI, retriever: LegalRetriever):
        self.llm = llm
        self.retriever = retriever
        self._build_chain()

    def _format_docs(self, docs: List[Document]) -> str:
        """Formats Document content for injection into the prompt template."""
        if not docs:
            return "No verified statutory provisions or precedents found in database."

        formatted_chunks = []
        for idx, doc in enumerate(docs):
            formatted_chunks.append(
                f"--- Legal Authority {idx+1} ---\n"
                f"Act / Source: {doc.metadata.get('act_name') or doc.metadata.get('source_name', 'Unknown')}\n"
                f"Section / Provision: {doc.metadata.get('section', 'General')}\n"
                f"Court / Jurisdiction: {doc.metadata.get('court') or doc.metadata.get('jurisdiction', 'All India')}\n"
                f"Content: {doc.page_content}\n"
            )
        return "\n".join(formatted_chunks)

    def _build_chain(self):
        """Assembles the LCEL runnable chain."""
        def retrieve_and_format(inputs: Dict[str, Any]) -> str:
            query = inputs["input"]
            docs = self.retriever.retrieve(query)
            inputs["retrieved_docs"] = docs
            return self._format_docs(docs)

        # Basic LCEL pipeline
        self.chain = (
            RunnablePassthrough.assign(context=retrieve_and_format)
            | self.llm
            | StrOutputParser()
        )

    def run(self, user_input: str, chat_history: List[Any]) -> Dict[str, Any]:
        """Runs the RAG chain and returns both the answer text and source document metadata."""
        logger.info(f"Running Legal RAG Chain for query: '{user_input[:50]}...'")
        inputs = {
            "input": user_input,
            "chat_history": chat_history,
            "retrieved_docs": []
        }
        try:
            output = self.chain.invoke(inputs)
            return {
                "output": output,
                "sources": inputs.get("retrieved_docs", [])
            }
        except Exception as e:
            logger.error(f"Legal RAG Chain invocation failure: {e}")
            return {
                "output": f"Failed to retrieve legal context and generate response: {str(e)}",
                "sources": []
            }


# Aliases for backward compatibility
MedicalRAGChain = LegalRAGChain


def build_rag_chain(llm: ChatGoogleGenerativeAI, retriever: LegalRetriever) -> LegalRAGChain:
    return LegalRAGChain(llm, retriever)
