import time
import os
import re
import streamlit as st
from pathlib import Path

# Set Streamlit Page Configuration at the very top
st.set_page_config(
    page_title="Juris - AI Legal Assistant for Indian Citizens",
    layout="wide",
    initial_sidebar_state="expanded"
)

import importlib
import src.config
import src.styles
import src.utils
import src.vector_store
import src.prompts
import src.tools
import src.retriever
import src.agent
import src.memory
import src.router

importlib.reload(src.config)
importlib.reload(src.styles)
importlib.reload(src.utils)
importlib.reload(src.vector_store)
importlib.reload(src.prompts)
importlib.reload(src.tools)
importlib.reload(src.retriever)
importlib.reload(src.agent)
importlib.reload(src.memory)
importlib.reload(src.router)

from src.config import config
from src.logger import logger
from src.styles import apply_custom_css
from src.utils import exception_formatter, token_counter, format_user_followup_prompt
from src.vector_store import LegalVectorStore
from src.agent import LegalAgent
from src.memory import CitizenLegalMemory
from src.router import LegalIntentRouter

# Initialize session state components
if "agent" not in st.session_state:
    st.session_state["agent"] = None

if "vector_store" not in st.session_state:
    vs = LegalVectorStore()
    api_key = config.GOOGLE_API_KEY
    if not api_key:
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = str(st.secrets["GOOGLE_API_KEY"]).strip()
        except Exception:
            pass
    st.session_state["vector_store"] = vs

if "last_retrieved_docs" not in st.session_state:
    st.session_state["last_retrieved_docs"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(time.time())
if "pending_prompt" not in st.session_state:
    st.session_state["pending_prompt"] = None
if "executed_tools" not in st.session_state:
    st.session_state["executed_tools"] = []
if "sources_by_message_index" not in st.session_state:
    st.session_state["sources_by_message_index"] = {}

# Setup memory and router
memory = CitizenLegalMemory()
router = LegalIntentRouter()

# Apply Custom Pastel Lavender/Indigo UI Styles
apply_custom_css()

# Sidebar Layout
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #2563EB; font-weight: 700; margin-bottom: 2px;'>Juris</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #64748B; font-weight: 500;'>AI Legal Assistant for Indian Citizens</p>", unsafe_allow_html=True)
    st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
    
    # 1. Citizen Case Profile Card
    with st.expander("Citizen Case Profile", expanded=False):
        profile = memory.get_case_profile()
        
        input_user = st.text_input("Citizen ID / Name:", value=profile.get("complainant_name", ""))
        input_opposite = st.text_input("Opposing Party (Landlord / Seller / Employer):", value=profile.get("opposite_party", ""))
        
        cat_options = [
            "General Legal Query",
            "Rental & Landlord-Tenant",
            "Consumer Disputes & Defective Products",
            "Employment & Unpaid Wages",
            "Negotiable Instruments & Cheque Bounce",
            "Real Estate, Builder Disputes & RERA",
            "Cyber Crime & Online Banking Fraud",
            "Contracts & Financial Agreements",
            "Criminal Law & BNS Provisions"
        ]
        curr_cat = profile.get("dispute_category", "General Legal Query")
        cat_idx = cat_options.index(curr_cat) if curr_cat in cat_options else 0
        input_category = st.selectbox("Dispute Category:", cat_options, index=cat_idx)
        
        input_amount = st.text_input("Disputed Monetary Amount (INR):", value=profile.get("claim_amount", ""))
        input_date = st.text_input("Incident / Transaction Date:", value=profile.get("incident_date", ""))
        input_jurisdiction = st.text_input("Location / City / State:", value=profile.get("jurisdiction", ""))
        
        if st.button("Update Case Profile", key="btn_update_case", use_container_width=True):
            updated_profile = {
                "complainant_name": input_user,
                "opposite_party": input_opposite,
                "dispute_category": input_category,
                "claim_amount": input_amount,
                "incident_date": input_date,
                "jurisdiction": input_jurisdiction
            }
            memory.update_case_profile(updated_profile)
            memory.save_case_to_disk()
            st.success("Case profile updated and persisted securely.")

    # 2. Interactive Legal Problem Domains Grid
    st.markdown("<h4 style='font-size: 0.90rem; font-weight: 600; color: #221C35; margin-top: 0.5rem; margin-bottom: 8px;'>Legal Domains</h4>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="capability-grid">
            <div class="capability-box">
                <div class="capability-title">Tenancy & Rent</div>
                <div class="capability-desc">Security Deposit, Eviction, Model Tenancy Act</div>
            </div>
            <div class="capability-box">
                <div class="capability-title">Consumer Rights</div>
                <div class="capability-desc">Defective Products, Refunds, e-Daakhil DCDRC</div>
            </div>
            <div class="capability-box">
                <div class="capability-title">Employment & Salary</div>
                <div class="capability-desc">Unpaid Wages, Notice Periods, Labour Rights</div>
            </div>
            <div class="capability-box">
                <div class="capability-title">Cheque Bounce</div>
                <div class="capability-desc">Section 138 NI Act, 30-Day Notice Deadlines</div>
            </div>
            <div class="capability-box">
                <div class="capability-title">RERA & Property</div>
                <div class="capability-desc">Delayed Possession, Builder Grievances</div>
            </div>
            <div class="capability-box">
                <div class="capability-title">Cyber Fraud</div>
                <div class="capability-desc">UPI/Banking Frauds, Golden Hour (1930)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Expandable "How to Use Juris" Guide
    with st.expander("How to Use Juris", expanded=False):
        st.markdown(
            """
            <div style="font-size: 0.84rem; color: #4C3C91; line-height: 1.55;">
                <p><b>1. Describe Your Problem:</b> Explain your situation in plain English (e.g. <i>"My landlord won't refund my Rs 30,000 security deposit"</i>).</p>
                <p><b>2. Understand Your Rights:</b> Learn exact Acts and sections applicable under Indian law.</p>
                <p><b>3. Check Limitations & Fees:</b> Ask for limitation deadlines or court fees before filing.</p>
                <p><b>4. Draft Formal Notices:</b> Request a 15-day legal notice, consumer complaint, or reply.</p>
                <p><b>5. Role-Play Negotiation:</b> Practice your arguments against opposing party objections.</p>
                <p><b>6. Suggested Prompts:</b> Click any horizontal suggestion chip to ask immediate follow-up questions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Knowledge Base Status
    store = st.session_state["vector_store"]
    doc_count = store.get_document_count()
    
    if doc_count > 0:
        st.markdown(
            f"<div class='status-badge status-active'>Connected • {doc_count} Legal Chunks Indexed</div>", 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='status-badge status-inactive'>Legal Index: Ready for Ingestion</div>", 
            unsafe_allow_html=True
        )
        if st.button("Sync & Ingest Legal Datasets", key="seed_kb_btn", use_container_width=True):
            with st.spinner("Ingesting Indian Acts, Judgments & FAQs into ChromaDB..."):
                from src.loaders import LegalDocumentLoader
                from src.splitter import LegalTextSplitter
                from src.parser import LegalDocumentParser
                
                loader = LegalDocumentLoader(config.DATA_DIR)
                splitter = LegalTextSplitter()
                parser = LegalDocumentParser()
                
                # Ingest FAQs
                faq_docs = loader.load_faqs()
                if faq_docs:
                    faq_chunks = splitter.split_documents(faq_docs)
                    store.add_documents(faq_chunks, collection_name=config.COLLECTION_FAQS)
                    
                # Ingest Judgments
                judge_docs = loader.load_judgments(max_records=150)
                if judge_docs:
                    judge_chunks = splitter.split_documents(judge_docs)
                    store.add_documents(judge_chunks, collection_name=config.COLLECTION_JUDGMENTS)
                    
                st.rerun()

    st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)

    # 5. Session Controls
    st.markdown("<h4 style='font-size: 0.90rem; font-weight: 600; color: #221C35; margin-bottom: 6px;'>Session Controls</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Case", key="new_case_btn", use_container_width=True):
            memory.clear()
            st.session_state["last_retrieved_docs"] = []
            st.session_state["executed_tools"] = []
            st.session_state["sources_by_message_index"] = {}
            st.rerun()
    with col2:
        if st.button("Reset All", key="reset_all_btn", use_container_width=True):
            with st.spinner("Resetting..."):
                memory.clear_all()
                st.session_state["last_retrieved_docs"] = []
                st.session_state["executed_tools"] = []
                st.session_state["sources_by_message_index"] = {}
                st.success("Session Fully Reset!")
                st.rerun()
                
    # 6. Export Case & History Option
    chat_messages = memory.get_messages()
    if chat_messages:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        md_content = "# Juris - Citizen Legal Case File & Conversation Export\n\n"
        prof = memory.get_case_profile()
        md_content += (
            f"**Citizen**: {prof.get('complainant_name') or 'N/A'} | "
            f"**Opposing Party**: {prof.get('opposite_party') or 'N/A'} | "
            f"**Category**: {prof.get('dispute_category') or 'General'}\n\n"
            f"**Disputed Amount**: {prof.get('claim_amount') or 'N/A'} | "
            f"**Jurisdiction**: {prof.get('jurisdiction') or 'N/A'}\n\n"
            f"---\n\n"
        )
        for m in chat_messages:
            role_label = "Citizen" if m["role"] == "user" else "Juris Assistant"
            md_content += f"### {role_label}\n{m['content']}\n\n"
            
        st.download_button(
            label="Download Complete Case File (MD)",
            data=md_content,
            file_name="juris_case_file.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Official Citizen Helplines
    st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
    st.caption("National Legal Aid (NALSA): **15100** (Toll-Free)")
    st.caption("National Consumer Helpline: **1915**")
    st.caption("Cyber Crime Helpline: **1930** | Emergency: **112**")
    st.caption(config.DISCLAIMER)

# Main Application Header
st.markdown(
    """
    <div style="margin-bottom: 0.75rem;">
        <h1 style="font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 2px; display: flex; align-items: center; gap: 12px;">
            Juris
            <span style="font-size: 0.8rem; font-weight: 600; background-color: #FEF08A; color: #854D0E; border: 1px solid #FACC15; padding: 3px 10px; border-radius: 14px;">AI Legal Assistant for Indian Citizens</span>
        </h1>
        <div style="font-size: 0.90rem; color: #64748B; margin-top: 4px;">
            <b>Authoritative Sources:</b> The Gazette of India, Supreme Court of India, India Code, Consumer Affairs, and Ministry of Labour
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Visible Legal Information & Anti-Hallucination Disclaimer Banner
st.markdown(
    f"""
    <div class="legal-disclaimer-banner">
        <b>Notice</b>: Juris provides plain-language informational legal guidance grounded strictly in authentic Indian statutes and precedents. It does not constitute formal legal representation or an advocate-client relationship.
    </div>
    """,
    unsafe_allow_html=True
)

# Check for API Key
if not config.GOOGLE_API_KEY:
    st.info("Please set your GOOGLE_API_KEY in your .env file or environment variables to start chatting.")
    st.stop()

# Lazy load Legal Agent
if st.session_state["agent"] is None:
    try:
        st.session_state["agent"] = LegalAgent()
    except Exception as e:
        st.error(f"Failed to initialize Legal Agent: {exception_formatter(e)}")
        st.stop()

agent = st.session_state["agent"]

# Display chat messages history
messages = memory.get_messages()
for idx, msg in enumerate(messages):
    role = msg["role"]
    content = msg["content"]
    
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="⚖️"):
            clean_text = content
            suggested_questions = []
            follow_up_pattern = r"(Suggested Follow-ups:|Suggested Follow-up Questions:|Follow-up Questions:)\s*\n1\.\s*(.*?)\n2\.\s*(.*?)\n3\.\s*(.*?)(?:\n|$)"
            match = re.search(follow_up_pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                clean_text = content[:match.start()].strip()
                suggested_questions = [
                    format_user_followup_prompt(match.group(2)),
                    format_user_followup_prompt(match.group(3)),
                    format_user_followup_prompt(match.group(4))
                ]
            
            st.markdown(clean_text)
            
            # Display visible retrieved sources evidence if recorded for this message
            evidence_list = st.session_state["sources_by_message_index"].get(idx, [])
            if evidence_list:
                st.markdown(
                    "<div class='retrieval-evidence-card'>"
                    "<div class='retrieval-header'>Retrieved Statutory & Judicial Sources</div>"
                    + "".join([f"<div class='retrieval-item'>• <b>{item['source']}</b> — {item['section']} <span class='retrieval-relevance'>relevance: {item['score']:.0%}</span></div>" for item in evidence_list])
                    + "</div>",
                    unsafe_allow_html=True
                )

            # Display clickable follow-up questions horizontally for the latest assistant message
            if idx == len(messages) - 1 and suggested_questions:
                st.markdown("<p style='font-size: 0.88rem; font-weight: 600; color: #2563EB; margin-top: 10px; margin-bottom: 6px;'>Suggested Follow-up Prompts:</p>", unsafe_allow_html=True)
                followup_cols = st.columns(len(suggested_questions))
                for q_idx, q in enumerate(suggested_questions):
                    with followup_cols[q_idx]:
                        if st.button(q, key=f"hist_btn_{idx}_{q_idx}", use_container_width=True):
                            st.session_state["pending_prompt"] = q
                            st.rerun()

# Determine prompt to run
user_input = st.chat_input("Describe your legal dispute (e.g., landlord withholding deposit, consumer refund, salary delay)...")
prompt_to_run = None

if st.session_state.get("pending_prompt"):
    prompt_to_run = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None
elif user_input:
    prompt_to_run = user_input

if prompt_to_run:
    # 1. Add User Message to Memory and render immediately
    memory.add_message("user", prompt_to_run)
    with st.chat_message("user", avatar="👤"):
        st.write(prompt_to_run)
    
    # Reset tool metrics
    st.session_state["last_retrieved_docs"] = []
    st.session_state["executed_tools"] = []
    
    # 2. Routing & Execution
    case_context = memory.get_case_profile_string()
    history_str = memory.get_formatted_history_string()
    
    loader_placeholder = st.empty()
    loader_placeholder.markdown(
        """
        <div class="juris-ai-loader">
            <div class="juris-pulse-dot"></div>
            <div class="juris-pulse-dot"></div>
            <div class="juris-pulse-dot"></div>
            <span class="juris-loader-text">Juris is researching Indian legal authorities...</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    start_time = time.time()
    output_text = ""
    is_emergency = False
    
    try:
        routing_res = router.classify(prompt_to_run, history_str)
        is_emergency = routing_res.get("emergency_bypass", False)
        
        if is_emergency:
            emergency_type = routing_res.get("emergency_type", "general")
            from src.tools import emergency_legal_guide
            guide_str = emergency_legal_guide.invoke(emergency_type)
            output_text = guide_str
            
        elif "Greeting" in routing_res.get("intents", []):
            output_text = (
                "Namaste! I am Juris, your AI Legal Assistant. "
                "I can help you understand your rights under Indian law, evaluate dispute options, "
                "draft formal legal notices, and prepare for negotiations.\n\n"
                "What legal problem or dispute are you currently dealing with?\n\n"
                "Suggested Follow-up Questions:\n"
                "1. My landlord is refusing to return my rental security deposit, what are my options?\n"
                "2. An online shopping site cancelled my paid order and refused refund, what can I do?\n"
                "3. My employer is withholding my last month salary after I resigned, how can I recover it?"
            )
        else:
            langchain_hist = memory.get_langchain_messages()
            accumulated_tokens = []
            text_placeholder = None
            
            for event in agent.stream_run(prompt_to_run, langchain_hist, case_context):
                event_type = event.get("type")
                if event_type == "tool_start":
                    tool_name = event.get("name", "Legal Tool")
                    loader_placeholder.markdown(
                        f"""
                        <div class="juris-ai-loader">
                            <div class="juris-pulse-dot"></div>
                            <div class="juris-pulse-dot"></div>
                            <div class="juris-pulse-dot"></div>
                            <span class="juris-loader-text">Consulting {tool_name}...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif event_type == "token":
                    tok = event.get("content", "")
                    if tok:
                        if text_placeholder is None:
                            loader_placeholder.empty()
                            assistant_box = st.chat_message("assistant", avatar="⚖️")
                            text_placeholder = assistant_box.empty()
                        accumulated_tokens.append(tok)
                        text_placeholder.markdown("".join(accumulated_tokens) + "▌")
                elif event_type == "final_result":
                    output_text = event.get("result", {}).get("output", "")
                    
            if text_placeholder is not None and output_text:
                text_placeholder.markdown(output_text)
            elif not output_text and accumulated_tokens:
                output_text = "".join(accumulated_tokens)
                if text_placeholder is not None:
                    text_placeholder.markdown(output_text)
            elif not output_text:
                output_text = "I could not resolve your query."
                loader_placeholder.empty()
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(output_text)
            
        duration = time.time() - start_time
        logger.info(f"Legal query executed in {duration:.4f}s. Intents: {routing_res.get('intents')}")
        
    except Exception as e:
        output_text = f"An unexpected error occurred while processing your legal query: {exception_formatter(e)}"
        logger.error(f"UI chat error: {e}")
    finally:
        loader_placeholder.empty()
            
    # 4. Save Assistant Output to Memory
    memory.add_message("assistant", output_text)
    
    # 5. Save Retrieval Evidence for this message index
    assistant_msg_idx = len(memory.get_messages()) - 1
    retrieved_docs = st.session_state.get("last_retrieved_docs", [])
    if retrieved_docs and not is_emergency:
        evidence_items = []
        for doc in retrieved_docs[:4]:
            meta = doc.metadata
            src = meta.get("act_name") or meta.get("source_name", "Indian Legal Authority")
            sec = meta.get("section") or meta.get("category") or "General Provision"
            conf = meta.get("confidence_score", 0.90)
            evidence_items.append({
                "source": src,
                "section": sec,
                "score": conf
            })
        st.session_state["sources_by_message_index"][assistant_msg_idx] = evidence_items
        
    st.rerun()
