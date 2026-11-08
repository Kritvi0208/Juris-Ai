"""Legal Agent for Juris - Tool-Calling Agent with Multi-Model Fallback and Real-Time Streaming.

Orchestrates tool execution, token streaming, circuit-breaker rate-limit cooling,
and deterministic local legal engine fallback.
"""

import queue
import re
import threading
import time
from typing import Any, Dict, Generator, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from src.config import config
from src.tools import (
    all_tools,
    statute_lookup,
    judgment_lookup,
    citation_verifier,
    outdated_law_checker,
    calculate_limitation,
    calculate_court_fee,
    extract_case_facts,
    draft_legal_document,
    simulate_opposing_party,
    emergency_legal_guide
)
from src.prompts import get_agent_prompt_template
from src.logger import logger
from src.retriever import LegalRetriever


def extract_token_text(token_content: Any) -> str:
    """Safely extracts string token from str, list, dict, or object chunks."""
    if isinstance(token_content, str):
        return token_content
    if isinstance(token_content, list):
        parts = []
        for p in token_content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(p.get("text", ""))
            elif hasattr(p, "text"):
                parts.append(getattr(p, "text", ""))
            else:
                parts.append(str(p))
        return "".join(parts)
    if isinstance(token_content, dict):
        return token_content.get("text", str(token_content))
    if hasattr(token_content, "text"):
        return getattr(token_content, "text", "")
    return str(token_content)


class TokenStreamCallbackHandler(BaseCallbackHandler):
    """Captures real-time token generation and tool lifecycle events."""

    def __init__(self, token_queue: queue.Queue):
        self.queue = token_queue
        self.in_tool = False

    def on_llm_new_token(self, token: Any, **kwargs) -> None:
        text = extract_token_text(token)
        if text:
            self.queue.put({"type": "token", "content": text})

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        self.in_tool = True
        tool_name = serialized.get("name", "Legal Tool")
        self.queue.put({"type": "tool_start", "name": tool_name, "input": input_str})

    def on_tool_end(self, output: str, **kwargs) -> None:
        self.in_tool = False
        self.queue.put({"type": "tool_end", "output": output})

    def on_tool_error(self, error: BaseException, **kwargs) -> None:
        self.in_tool = False
        self.queue.put({"type": "tool_error", "error": str(error)})

    def on_llm_error(self, error: BaseException, **kwargs) -> None:
        self.queue.put({"type": "llm_error", "error": str(error)})


# Circuit-breaker cooldown tracker to skip rate-limited models immediately
_model_cooldowns: Dict[str, float] = {}


def get_ordered_models() -> List[str]:
    """Returns candidate Gemini models prioritizing healthy models over those in cooldown."""
    all_models = [config.LLM_MODEL_NAME] + [m for m in config.FALLBACK_MODELS if m != config.LLM_MODEL_NAME]
    now = time.time()
    active = [m for m in all_models if _model_cooldowns.get(m, 0) <= now]
    cooling = [m for m in all_models if _model_cooldowns.get(m, 0) > now]
    return active + cooling


class LegalAgent:
    """Orchestrates the tool-calling legal agent with multi-model fallback and local legal resilience."""

    def __init__(self):
        self._llm_cache: Dict[str, ChatGoogleGenerativeAI] = {}

    def get_llm(self, model_name: str) -> ChatGoogleGenerativeAI:
        """Lazy-loads and caches ChatGoogleGenerativeAI for a specific model name."""
        if model_name in self._llm_cache:
            return self._llm_cache[model_name]

        if not config.GOOGLE_API_KEY:
            logger.error("Missing GOOGLE_API_KEY during LLM initialization.")
            raise ValueError("GOOGLE_API_KEY is not configured. Please add it to your .env file.")

        logger.info(f"Initializing ChatGoogleGenerativeAI: {model_name} (temp={config.TEMPERATURE})")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=config.TEMPERATURE,
            google_api_key=config.GOOGLE_API_KEY,
            streaming=True,
            max_retries=0
        )
        self._llm_cache[model_name] = llm
        return llm

    def get_executor(self, model_name: str, case_profile_str: str = "") -> AgentExecutor:
        """Constructs an AgentExecutor dynamically for a specific model and citizen case context."""
        llm = self.get_llm(model_name)
        prompt = get_agent_prompt_template(case_profile_str)
        agent = create_tool_calling_agent(llm, all_tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=all_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def _try_local_legal_fallback(
        self,
        user_input: str,
        chat_history: List[Any],
        case_profile_str: str
    ) -> Optional[str]:
        """Deterministic local legal intelligence engine when remote LLM quotas are exhausted."""
        input_lower = user_input.lower().strip()

        # 1. Rental Security Deposit Withholding
        if ("deposit" in input_lower or "rent" in input_lower) and ("landlord" in input_lower or "vacat" in input_lower or "refus" in input_lower):
            amt_match = re.search(r"(?:rs\.?|inr|rupees?)\s*([0-9,]+)|\b([0-9]{4,6})\b", input_lower)
            amt_str = f"Rs {amt_match.group(1) or amt_match.group(2)}" if amt_match else "your security deposit"

            return (
                f"### Legal Assessment: Security Deposit Withholding by Landlord\n\n"
                f"**1. Your Legal Position & Rights**:\n"
                f"Under settled Indian tenancy law and **Section 108(B)(q) of the Transfer of Property Act, 1882**, "
                f"upon the tenant handing over vacant, peaceful possession of the premises and keys, the landlord is "
                f"legally bound to refund the unadjusted security deposit ({amt_str}). The **Model Tenancy Act, 2021** "
                f"(Section 10) explicitly stipulates that the deposit must be refunded after deducting only agreed damages or unpaid rent.\n\n"
                f"**2. Unlawful Deductions**:\n"
                f"Ordinary wear and tear (such as customary paint weathering or minor nail holes) CANNOT be deducted from the "
                f"security deposit unless specifically stipulated in your registered/executed rental agreement.\n\n"
                f"**3. Practical Action Plan**:\n"
                f"1. **Send a Formal Legal Notice**: Demand the refund of {amt_str} within 15 days, citing Section 108 of the "
                f"Transfer of Property Act, with 18% p.a. interest.\n"
                f"2. **Limitation Period**: Under the Limitation Act, 1963 (Schedule Article 19/22), you have **3 years** from "
                f"the date the refund was refused or vacant possession was delivered to file a civil money recovery suit.\n"
                f"3. **Summary Suit / Small Causes**: If the landlord fails to pay after notice, you can file a Summary Suit "
                f"under Order 37 of the CPC before the competent Civil Court / Rent Tribunal.\n\n"
                f"Suggested Follow-up Questions:\n"
                f"1. Can you draft a formal 15-day legal notice to my landlord for this security deposit refund?\n"
                f"2. What evidence like photos or bank statements do I need to preserve?\n"
                f"3. Can my landlord deduct money for painting if it was not written in the rent agreement?"
            )

        # 2. Consumer Refund / Defective Product
        if any(w in input_lower for w in ["refund", "flipkart", "amazon", "defective", "ecommerce", "warranty", "consumer"]):
            amt_match = re.search(r"(?:rs\.?|inr|rupees?)\s*([0-9,]+)|\b([0-9]{3,6})\b", input_lower)
            amt_str = f"Rs {amt_match.group(1) or amt_match.group(2)}" if amt_match else "the purchase consideration"

            return (
                f"### Legal Assessment: Consumer Rights & Refund Dispute\n\n"
                f"**1. Applicable Law**:\n"
                f"Under the **Consumer Protection Act, 2019 (Act No. 35 of 2019)**:\n"
                f"• **Section 2(11)**: Failure or refusal to refund money for an undelivered, cancelled, or defective product "
                f"constitutes 'Deficiency of Service'.\n"
                f"• **Section 2(47)(viii)**: Refusal to take back defective goods and refund consideration within 30 days is "
                f"an explicit 'Unfair Trade Practice'.\n"
                f"• **Consumer Protection (E-Commerce) Rules, 2020**: E-commerce platforms must provide automated grievance redressal "
                f"and converge refunds within stipulated timelines.\n\n"
                f"**2. Practical Remedies**:\n"
                f"1. **National Consumer Helpline (NCH)**: Lodge a grievance via National Consumer Helpline (Call 1915 or consumerhelpline.gov.in).\n"
                f"2. **Pre-Litigation Legal Notice**: Issue a formal 15-day notice to the seller and platform demanding refund of {amt_str}.\n"
                f"3. **e-Daakhil Filing**: File an online complaint before the District Consumer Commission via e-Daakhil (edaakhil.nic.in). "
                f"Complaints up to Rs 5,00,000 carry **zero court fees**.\n"
                f"4. **Limitation Period**: **2 years** from the date the cause of action arose (Section 69 CPA 2019).\n\n"
                f"Suggested Follow-up Questions:\n"
                f"1. Can you draft a consumer notice to the seller and e-commerce platform for refund?\n"
                f"2. How do I file a consumer complaint on the e-Daakhil portal?\n"
                f"3. What compensation can I claim for mental agony and harassment under the Consumer Protection Act?"
            )

        # 3. Employment & Unpaid Wages
        if any(w in input_lower for w in ["salary", "employer", "wages", "unpaid", "resigned"]):
            return (
                f"### Legal Assessment: Unpaid Salary & Delayed Wages\n\n"
                f"**1. Statutory Rights**:\n"
                f"Under **Section 15 of the Payment of Wages Act, 1936** and the Industrial Relations framework:\n"
                f"• Employers cannot unlawfully deduct or delay earned wages without statutory cause.\n"
                f"• The authority under the Act has power to direct payment of delayed wages along with compensation up to ten times the amount.\n\n"
                f"**2. Notice Period Adjustments**:\n"
                f"Employers cannot arbitrarily withhold past earned wages for a disputed notice period without explicit contractual basis.\n\n"
                f"**3. Practical Steps**:\n"
                f"1. Serve a formal **Salary Demand Notice** giving 15 days to credit all outstanding dues and full & final settlement (FnF).\n"
                f"2. Approach the **Labour Commissioner / Payment of Wages Authority** in your district.\n"
                f"3. File a summary recovery suit under Order 37 of the CPC.\n\n"
                f"Suggested Follow-up Questions:\n"
                f"1. Can you draft a formal salary demand notice to my former employer?\n"
                f"2. Can my employer hold my experience letter and salary if I resign early?\n"
                f"3. What is the process to file a complaint with the Labour Commissioner?"
            )

        # 4. Outdated Law Inquiry (e.g. IPC, CrPC, CPA 1986)
        outdated_warnings = []
        for old_k, old_v in OUTDATED_LAW_MAPPINGS.items():
            if old_k in input_lower:
                outdated_warnings.append(old_v)

        if outdated_warnings:
            outdated_text = "\n\n".join([f"• {w}" for w in outdated_warnings])
            return (
                f"### Statutory Modernization Guidance\n\n"
                f"{outdated_text}\n\n"
                f"Suggested Follow-up Questions:\n"
                f"1. What is the modern section under Bharatiya Nyaya Sanhita (BNS) for my case?\n"
                f"2. How do the new criminal laws apply to incidents that occurred before July 2024?\n"
                f"3. Can you explain the procedure for filing an e-FIR or Zero FIR under BNSS?"
            )

        # 5. RAG Retrieval from ChromaDB / Verified Statutes
        try:
            retriever = LegalRetriever()
            docs = retriever.retrieve(user_input)
            if docs:
                from src.tools import _safe_set_state
                _safe_set_state("last_retrieved_docs", docs)
                snippets = "\n\n".join([
                    f"• **{d.metadata.get('act_name', d.metadata.get('source_name', 'Indian Statute'))}** ({d.metadata.get('section', 'General')}):\n{d.page_content.strip()}"
                    for d in docs[:2]
                ])
                return (
                    f"### Authoritative Legal Guidance\n\n"
                    f"{snippets}\n\n"
                    f"**Disclaimer**: This explanation provides legal information based on authentic Indian statutes. "
                    f"For formal court filings, consult an enrolled Advocate or State Legal Aid Authority (NALSA / DLSA).\n\n"
                    f"Suggested Follow-up Questions:\n"
                    f"1. What are my practical options to resolve this dispute out of court?\n"
                    f"2. What is the statutory limitation deadline for this matter?\n"
                    f"3. Can you draft a formal legal notice based on these facts?"
                )
        except Exception as e:
            logger.warning(f"Local legal retrieval fallback error: {e}")

        return None

    def stream_run(
        self,
        user_input: str,
        chat_history: List[Any],
        case_profile_str: str = ""
    ) -> Generator[Dict[str, Any], None, None]:
        """Streams LLM tokens in real-time as they are produced by Google Gemini.
        
        Yields:
            Dict events with types: 'token', 'tool_start', 'tool_end', 'final_result', 'error'.
        """
        token_queue = queue.Queue()
        callback = TokenStreamCallbackHandler(token_queue)
        result_holder = {}

        def _worker_thread():
            models_to_try = get_ordered_models()

            for model_idx, model_name in enumerate(models_to_try):
                try:
                    logger.info(f"Streaming execution with model ({model_idx+1}/{len(models_to_try)}): {model_name}")
                    executor = self.get_executor(model_name, case_profile_str)
                    response = executor.invoke(
                        {"input": user_input, "chat_history": chat_history},
                        config={"callbacks": [callback]}
                    )
                    output_val = response.get("output", "")
                    response["output"] = extract_token_text(output_val)
                    result_holder["response"] = response
                    _model_cooldowns.pop(model_name, None)
                    logger.info(f"Stream generation finished successfully with model: {model_name}")
                    return
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        _model_cooldowns[model_name] = time.time() + 60.0
                        logger.info(f"Model {model_name} rate limited (429). Setting 60s circuit-breaker cooldown.")
                    elif "503" in error_str or "UNAVAILABLE" in error_str:
                        _model_cooldowns[model_name] = time.time() + 30.0
                    logger.warning(f"Streaming model {model_name} failed: {error_str}")
                    continue

            # Fallback to local legal engine
            logger.info("Remote models failed or exhausted. Executing local deterministic legal engine...")
            local_out = self._try_local_legal_fallback(user_input, chat_history, case_profile_str)
            if local_out:
                result_holder["response"] = {"output": local_out, "intermediate_steps": []}
            else:
                result_holder["response"] = {
                    "output": (
                        "### Juris Legal Guidance\n\n"
                        "I am currently operating in high-resilience legal assistance mode. "
                        "Please describe the key facts of your problem (the parties involved, disputed amounts, "
                        "and relevant dates) so I can retrieve verified provisions directly from our authentic Indian legal database."
                    ),
                    "intermediate_steps": []
                }

        worker = threading.Thread(target=_worker_thread)
        worker.daemon = True
        worker.start()

        while worker.is_alive() or not token_queue.empty():
            try:
                event = token_queue.get(timeout=0.1)
                yield event
            except queue.Empty:
                continue

        worker.join()
        if "response" in result_holder:
            yield {"type": "final_result", "result": result_holder["response"]}


# Alias for backward compatibility
MedicalAgent = LegalAgent