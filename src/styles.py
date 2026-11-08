"""Custom CSS Styles and Pastel Blue & Butter Yellow UI Design for Juris."""

import streamlit as st

def apply_custom_css():
    """Applies a professional, minimalist SaaS UI with a Pastel Blue and Butter Yellow palette."""
    css = """
    <style>
    /* GLOBAL PASTEL BLUE & BUTTER YELLOW THEME */
    :root {
        --background-color: #F8FAFD !important;
        --secondary-background-color: #EEF5FC !important;
        --primary-color: #3B82F6 !important;
        --accent-butter: #FDE047 !important;
        --text-color: #1E293B !important;
    }
    
    /* Base App Container & Header */
    .stApp, .stApp > header, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8FAFD !important;
        color: #1E293B !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .main .block-container {
        max-width: 920px;
        margin: 0 auto;
        padding-top: 1.25rem;
        padding-bottom: 4.5rem;
    }
    
    /* Universal Text Color */
    .stApp, 
    .stApp p, 
    .stApp span, 
    .stApp h1, 
    .stApp h2, 
    .stApp h3, 
    .stApp h4, 
    .stApp h5, 
    .stApp h6, 
    .stApp li, 
    .stApp label,
    .stApp div[data-testid="stMarkdownContainer"] {
        color: #1E293B !important;
    }
    
    /* Hide Default Header & Footer */
    header, footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* Sidebar Styling - Soft Pastel Blue */
    section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #EEF5FC !important;
        border-right: 1px solid #D5E5F7 !important;
        padding-top: 0.5rem;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1E293B !important;
    }
    
    /* Inputs, Selectboxes, Dropdowns */
    .stTextInput input,
    .stTextInput > div,
    .stTextInput > div > div,
    .stSelectbox,
    .stSelectbox > div,
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] *,
    ul[role="listbox"],
    ul[role="listbox"] *,
    li[role="option"],
    li[role="option"] * {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border-color: #CFE2F5 !important;
    }
    
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #FEF9C3 !important;
        color: #854D0E !important;
    }
    
    /* Expander Container */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D5E5F7 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.05) !important;
        margin-bottom: 0.75rem !important;
    }
    
    div[data-testid="stExpander"] details {
        border-radius: 12px !important;
    }
    
    div[data-testid="stExpander"] summary {
        background-color: #F6FAFE !important;
        color: #1E3A8A !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 0.6rem 0.8rem !important;
    }
    
    div[data-testid="stExpander"] summary:hover {
        background-color: #FEF9C3 !important;
        color: #854D0E !important;
    }
    
    div[data-testid="stExpander"] summary svg {
        fill: #3B82F6 !important;
    }
    
    /* Interactive Legal Capabilities Grid Cards */
    .capability-grid {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 12px;
    }
    
    .capability-box {
        background-color: #FFFFFF;
        border: 1px solid #DCE9F6;
        border-left: 3.5px solid #3B82F6;
        border-radius: 8px;
        padding: 8px 10px;
        transition: all 0.2s ease-in-out;
    }
    
    .capability-box:nth-child(even) {
        border-left-color: #EAB308;
    }
    
    .capability-box:hover {
        background-color: #FEFCE8;
        border-color: #FDE047;
        transform: translateX(2px);
        box-shadow: 0 2px 8px rgba(234, 179, 8, 0.12);
    }
    
    .capability-title {
        font-size: 0.83rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    
    .capability-desc {
        font-size: 0.76rem;
        color: #475569;
        line-height: 1.35;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.80rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .status-badge.status-active {
        background-color: #FEF9C3 !important;
        color: #854D0E !important;
        border: 1px solid #FDE047 !important;
    }
    
    .status-badge.status-inactive {
        background-color: #F1F5F9 !important;
        color: #64748B !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* Primary Buttons - Pastel Blue */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        border-radius: 9px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.46rem 0.95rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.20) !important;
    }
    
    .stButton > button * {
        color: #FFFFFF !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.32) !important;
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        background: #1E40AF !important;
        transform: translateY(0);
    }
    
    /* Clean Avatar Circles */
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"],
    div[data-testid="chatAvatarIcon-user"],
    div[data-testid="chatAvatarIcon-assistant"] {
        background-color: #E0F2FE !important;
        border: 1px solid #BAE6FD !important;
        border-radius: 50% !important;
        color: #0284C7 !important;
    }
    
    /* Chat Message Cards */
    div[data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.1rem 1.25rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.04) !important;
    }
    
    /* User Chat Bubble - Soft Pastel Sky Blue Tint */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]),
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: #F0F7FF !important;
        border: 1px solid #CCE3F9 !important;
    }
    
    /* Chat Input Bar Fixed Dock */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stBottom"] * {
        background-color: #F8FAFD !important;
    }
    
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stChatInput"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CFE2F5 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.08) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(253, 224, 71, 0.40) !important;
    }
    
    textarea[data-testid="stChatInputTextArea"],
    div[data-testid="stChatInput"] textarea {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        font-size: 0.95rem !important;
    }
    
    textarea[data-testid="stChatInputTextArea"]::placeholder,
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    
    /* Horizontal Divider */
    .custom-hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(207, 226, 245, 0) 0%, #CFE2F5 50%, rgba(207, 226, 245, 0) 100%);
        margin: 1.1rem 0;
    }
    
    /* Legal Disclaimer Banner - Butter Yellow with Blue Border */
    .legal-disclaimer-banner {
        background-color: #FEFCE8;
        border: 1px solid #FEF08A;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 9px 14px;
        font-size: 0.83rem;
        color: #713F12;
        margin-bottom: 1rem;
        line-height: 1.45;
        box-shadow: 0 1px 4px rgba(234, 179, 8, 0.08);
    }
    
    /* Retrieved Sources Evidence Box - Pastel Blue with Butter Yellow Badges */
    .retrieval-evidence-card {
        background-color: #F0F7FF;
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 0.82rem;
    }
    
    .retrieval-header {
        font-weight: 700;
        color: #0284C7;
        margin-bottom: 6px;
        text-transform: uppercase;
        font-size: 0.76rem;
        letter-spacing: 0.5px;
    }
    
    .retrieval-item {
        color: #1E293B;
        margin-bottom: 4px;
        line-height: 1.35;
    }
    
    .retrieval-relevance {
        display: inline-block;
        background-color: #FEF9C3;
        color: #854D0E;
        border: 1px solid #FDE047;
        border-radius: 12px;
        padding: 1px 7px;
        font-size: 0.74rem;
        font-weight: 600;
        margin-left: 6px;
    }
    
    /* Emergency Alert Card */
    .emergency-alert-card, .urgent-safety-card {
        background-color: #FEF3C7 !important;
        border: 1.5px solid #F59E0B !important;
        border-left: 5px solid #DC2626 !important;
        color: #92400E !important;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.5;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.15);
    }
    
    /* Ultra-Smooth AI Loader with Pastel Blue & Butter Yellow Pulsing Dots */
    .juris-ai-loader {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
        border: 1.5px solid #BAE6FD;
        border-radius: 24px;
        padding: 8px 16px;
        margin: 8px 0 14px 0;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.10);
    }
    
    .juris-pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        animation: pulseAnimation 1.2s infinite ease-in-out;
    }
    
    .juris-pulse-dot:nth-child(1) {
        background-color: #3B82F6;
        animation-delay: 0s;
    }
    
    .juris-pulse-dot:nth-child(2) {
        background-color: #EAB308;
        animation-delay: 0.2s;
    }
    
    .juris-pulse-dot:nth-child(3) {
        background-color: #60A5FA;
        animation-delay: 0.4s;
    }
    
    @keyframes pulseAnimation {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1.15); opacity: 1; }
    }
    
    .juris-loader-text {
        font-size: 0.82rem;
        color: #1E40AF;
        font-weight: 600;
        margin-left: 4px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
