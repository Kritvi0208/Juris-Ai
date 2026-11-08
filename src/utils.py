import json
import time
import re
from pathlib import Path
from typing import Any, Dict, List
from src.logger import logger


def clean_text(text: str) -> str:
    """Cleans raw text by removing excessive whitespaces and formatting issues."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'<[^>]*>', '', text)
    return text.strip()


def format_sources(docs: List[Any]) -> str:
    """Formats retrieved legal document metadata into an authoritative citation block."""
    if not docs:
        return "No authoritative legal sources retrieved."

    formatted = "### Verified Legal Sources Cited:\n"
    seen_sources = set()

    for idx, doc in enumerate(docs):
        meta = getattr(doc, "metadata", {})
        act_name = meta.get("act_name") or meta.get("source_name") or "Indian Legal Authority"
        section = meta.get("section", "General Statutory Provision")
        court = meta.get("court", "")
        citation = meta.get("citation", "")
        jurisdiction = meta.get("jurisdiction", "All India")
        conf = meta.get("confidence_score")

        source_key = f"{act_name} - {section}"
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)

        line = f"- **Authority {idx+1}**: {act_name} — `{section}`"
        if court:
            line += f" ({court})"
        if citation:
            line += f" | Citation: *{citation}*"
        if conf is not None:
            line += f" | Relevance: {conf:.0%}"
        formatted += line + "\n"

        snippet = doc.page_content[:180].replace('\n', ' ') + "..."
        formatted += f"  - *Statutory / Judicial Holding*: \"{snippet}\"\n"

    return formatted


def time_formatter(seconds: float) -> str:
    """Formats a float representing seconds into a human-readable duration."""
    if seconds < 1.0:
        return f"{seconds * 1000:.2f} ms"
    return f"{seconds:.2f} seconds"


def token_counter(text: str) -> int:
    """Estimates the number of tokens in the given text using standard word boundaries."""
    if not text:
        return 0
    words = len(text.split())
    return int(words * 1.33) + 1


def exception_formatter(e: Exception) -> str:
    """Extracts a readable message from exceptions without tracebacks."""
    name = type(e).__name__
    message = str(e)
    return f"[{name}] {message}"


def load_json(filepath: Path) -> Dict[str, Any]:
    """Helper to safely read a JSON database file."""
    if not filepath.exists():
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON from {filepath}: {e}")
        return {}


def save_json(data: Dict[str, Any], filepath: Path) -> bool:
    """Helper to safely save a JSON database file."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON to {filepath}: {e}")
        return False


def format_user_followup_prompt(text: str) -> str:
    """Transforms follow-up suggestion questions into first-person citizen prompts/questions."""
    if not text:
        return ""
    p = text.strip()
    p = re.sub(r"^[\d\.\-\*\•\)\s]+", "", p).strip()

    conversions = [
        (r"^(?:are you interested in (?:learning (?:about |more about )?|knowing (?:about )?|learning )?)(.*)", r"What are \1"),
        (r"^(?:would you like to (?:know (?:more about |about )?|learn (?:more about |about )?|hear (?:about )?))(.*)", r"Tell me about \1"),
        (r"^(?:would you like (?:me to )?draft (?:a |an )?)(.*)", r"Can you draft a \1?"),
        (r"^(?:would you like (?:me to )?calculate (?:the |my )?)(.*)", r"Can you calculate the \1?"),
        (r"^(?:would you like (?:me to )?)(check|calculate|explain|recommend|suggest|provide|draft)(.*)", r"Can you \1\2?"),
        (r"^(?:would you like to )(.*)", r"How can I \1?"),
        (r"^(?:do you have any specific |do you have any )(.*?)(?:\s+you are hoping to achieve|\s+you want to ask|\s+you need assistance with|\s+you would like to discuss)?\??$", r"How can I manage my \1?"),
        (r"^(?:do you want to know (?:about )?|do you want to learn (?:about )?)(.*)", r"Tell me about \1"),
        (r"^(?:do you want (?:me to )?)(.*)", r"Can you \1?"),
        (r"^(?:what steps should be taken if )(.*)", r"What should I do if \1?"),
        (r"^(?:please provide |please share )(.*)", r"Can you explain \1?"),
    ]

    matched = False
    for pattern, replacement in conversions:
        if re.search(pattern, p, re.IGNORECASE):
            p = re.sub(pattern, replacement, p, flags=re.IGNORECASE).strip()
            matched = True
            break

    if matched:
        p = re.sub(r"\byour\b", "my", p, flags=re.IGNORECASE)
        p = re.sub(r"\byours\b", "mine", p, flags=re.IGNORECASE)
        p = re.sub(r"\byou are\b", "I am", p, flags=re.IGNORECASE)
        p = re.sub(r"\byou\b", "me", p, flags=re.IGNORECASE)

    p = re.sub(r"\s+", " ", p).strip()
    p = re.sub(r"\?+", "?", p)
    if re.match(r"^(?:tell me|suggest|explain|give me|draft)\b", p, re.IGNORECASE) and p.endswith("?"):
        p = p[:-1].strip()
    elif not p.endswith(("?", ".", "!")):
        p = p + "?"

    if p:
        p = p[0].upper() + p[1:]
    return p
