"""Persistent Citizen Case Memory and Multi-User Isolation for Juris.

Manages conversational message history, structured case profiles (parties, dates,
disputed amounts, evidence, timeline, missing facts), and isolated on-disk case files.
Strictly isolated per citizen/user: no user's case data is exposed to another user.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.config import config
from src.logger import logger


class CitizenLegalMemory:
    """Manages conversational chat history and isolated structured legal case memory."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_key: str = "chat_messages",
        profile_key: str = "case_profile",
        user_id_key: str = "user_id"
    ):
        self.session_key = session_key
        self.profile_key = profile_key
        self.user_id_key = user_id_key
        self._instance_user_id = user_id

        # Initialize current user identity
        if user_id:
            st.session_state[self.user_id_key] = user_id
            self.profile_key = f"{profile_key}_{user_id}"
            self.session_key = f"{session_key}_{user_id}"
        elif self.user_id_key not in st.session_state:
            st.session_state[self.user_id_key] = "citizen_default"

        # Initialize message history
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []
            logger.info("Initializing legal chat message session state memory.")

        # Initialize structured Citizen Case Profile
        if self.profile_key not in st.session_state:
            st.session_state[self.profile_key] = {
                "case_id": "case_001",
                "complainant_name": "",
                "opposite_party": "",
                "dispute_category": "General Legal Query",
                "claim_amount": "",
                "incident_date": "",
                "jurisdiction": "All India / Not Specified",
                "key_facts": [],
                "evidence_available": [],
                "missing_facts": [],
                "timeline": [],
                "notes": ""
            }
            logger.info("Initializing citizen legal case profile session state memory.")

    def get_user_id(self) -> str:
        """Returns the isolated identifier for the currently active citizen."""
        if self._instance_user_id:
            return self._instance_user_id
        return st.session_state.get(self.user_id_key, "citizen_default")

    def set_user_id(self, user_id: str) -> None:
        """Sets the active citizen identity and reloads their isolated cases."""
        st.session_state[self.user_id_key] = user_id.strip() or "citizen_default"
        logger.info(f"Switched active citizen user to: {st.session_state[self.user_id_key]}")

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to the memory buffer."""
        st.session_state[self.session_key].append({"role": role, "content": content})
        logger.info(f"Memory added: {role} -> {content[:50]}...")
        self._truncate_memory()

    def get_messages(self) -> List[Dict[str, str]]:
        """Returns all messages currently stored in the session."""
        return st.session_state.get(self.session_key, [])

    def clear(self) -> None:
        """Clears message history."""
        st.session_state[self.session_key] = []
        logger.info("Chat history cleared from memory.")

    def clear_all(self) -> None:
        """Resets both message history and the citizen case profile."""
        self.clear()
        st.session_state[self.profile_key] = {
            "case_id": "case_001",
            "complainant_name": "",
            "opposite_party": "",
            "dispute_category": "General Legal Query",
            "claim_amount": "",
            "incident_date": "",
            "jurisdiction": "All India / Not Specified",
            "key_facts": [],
            "evidence_available": [],
            "missing_facts": [],
            "timeline": [],
            "notes": ""
        }
        logger.info("Chat history and legal case profile fully reset.")

    def _truncate_memory(self) -> None:
        """Truncates conversation history to the configured maximum length."""
        history = st.session_state[self.session_key]
        max_len = config.MAX_CHAT_HISTORY * 2
        if len(history) > max_len:
            truncated = history[-max_len:]
            st.session_state[self.session_key] = truncated
            logger.info(f"Truncated memory. Retained last {max_len} messages.")

    def get_langchain_messages(self) -> List[BaseMessage]:
        """Converts internal messages into LangChain BaseMessage objects."""
        messages: List[BaseMessage] = []
        for msg in st.session_state[self.session_key]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def get_formatted_history_string(self) -> str:
        """Formats the chat history as a flat text block for prompt injection."""
        formatted = ""
        for msg in st.session_state[self.session_key]:
            role_label = "Citizen" if msg["role"] == "user" else "Juris Assistant"
            formatted += f"{role_label}: {msg['content']}\n"
        return formatted

    # Structured Case Profile Methods
    def get_case_profile(self) -> Dict[str, Any]:
        """Retrieves the active structured legal case profile."""
        return st.session_state[self.profile_key]

    def update_case_profile(self, profile_dict: Dict[str, Any]) -> None:
        """Updates the active legal case profile with newly extracted facts."""
        st.session_state[self.profile_key].update(profile_dict)
        logger.info("Citizen case profile memory updated.")

    def set_active_dispute(
        self,
        category: str,
        opposing_party: str,
        claim_amount: Any,
        incident_date: str = "",
        jurisdiction: str = ""
    ) -> None:
        """Sets primary dispute parameters in the active case profile."""
        amt_str = f"Rs {claim_amount:,.2f}" if isinstance(claim_amount, (int, float)) else str(claim_amount)
        self.update_case_profile({
            "dispute_category": category,
            "opposite_party": opposing_party,
            "claim_amount": amt_str,
            "incident_date": incident_date,
            "jurisdiction": jurisdiction
        })

    def add_timeline_event(self, date_str: str, description: str) -> None:
        """Appends a dated chronological event to the case timeline."""
        profile = self.get_case_profile()
        timeline = profile.get("timeline", [])
        timeline.append({"date": date_str, "description": description})
        self.update_case_profile({"timeline": timeline})

    def add_evidence(self, doc_name: str) -> None:
        """Appends an available document or evidence item to the case profile."""
        profile = self.get_case_profile()
        evidence = profile.get("evidence_available", [])
        if doc_name not in evidence:
            evidence.append(doc_name)
        self.update_case_profile({"evidence_available": evidence})

    def get_case_summary_text(self) -> str:
        """Returns the formatted summary string of the citizen case."""
        return self.get_case_profile_string()

    def get_case_profile_string(self) -> str:
        """Returns a concise, prompt-friendly summary of the citizen case."""
        p = self.get_case_profile()
        facts_str = "; ".join(p.get("key_facts", [])) or "None extracted yet"
        evidence_str = ", ".join(p.get("evidence_available", [])) or "No documents attached yet"
        missing_str = ", ".join(p.get("missing_facts", [])) or "None identified"

        return (
            f"Complainant/Citizen: {p.get('complainant_name') or 'Not specified'}\n"
            f"Opposing Party: {p.get('opposite_party') or 'Not specified'}\n"
            f"Dispute Category: {p.get('dispute_category') or 'General'}\n"
            f"Claim Amount: {p.get('claim_amount') or 'Not specified'}\n"
            f"Incident/Cause of Action Date: {p.get('incident_date') or 'Not specified'}\n"
            f"Jurisdiction/Location: {p.get('jurisdiction') or 'Not specified'}\n"
            f"Confirmed Facts: {facts_str}\n"
            f"Evidence Available: {evidence_str}\n"
            f"Missing Critical Information: {missing_str}\n"
            f"Additional Notes: {p.get('notes') or 'None'}"
        )

    # Secure Case Storage and Multi-User Isolation
    def save_case_to_disk(self, case_id: Optional[str] = None) -> Path:
        """Persists the current case profile and chat history into user-isolated storage."""
        user_id = self.get_user_id()
        cid = case_id or self.get_case_profile().get("case_id", "case_001")
        
        user_dir = config.USER_CASES_DIR / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        case_file = user_dir / f"{cid}.json"
        payload = {
            "user_id": user_id,
            "case_id": cid,
            "profile": self.get_case_profile(),
            "chat_history": self.get_messages()
        }
        with open(case_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Persisted isolated case {cid} for user {user_id} at {case_file}")
        return case_file

    def load_case_from_disk(self, case_id: str) -> bool:
        """Loads a case strictly belonging to the currently active user (user isolation)."""
        user_id = self.get_user_id()
        case_file = config.USER_CASES_DIR / user_id / f"{case_id}.json"
        if not case_file.exists():
            logger.warning(f"Access denied or case {case_id} does not exist for user {user_id}.")
            return False

        try:
            with open(case_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Verify user ownership
            if data.get("user_id") != user_id:
                logger.error(f"User isolation violation! Attempted to access {data.get('user_id')} case from {user_id}")
                return False

            st.session_state[self.profile_key] = data.get("profile", {})
            st.session_state[self.session_key] = data.get("chat_history", [])
            logger.info(f"Loaded isolated case {case_id} for user {user_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to load case {case_id}: {e}")
            return False

    def list_user_cases(self) -> List[str]:
        """Lists only the cases belonging to the currently authenticated user."""
        user_id = self.get_user_id()
        user_dir = config.USER_CASES_DIR / user_id
        if not user_dir.exists():
            return []
        return [p.stem for p in user_dir.glob("*.json")]


# Alias for backward compatibility
LegalMemory = CitizenLegalMemory
