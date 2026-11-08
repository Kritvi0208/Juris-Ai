"""Legal Intent Router and Emergency Safety Escalation Engine for Juris.

Detects critical legal emergencies requiring immediate escalation:
- Imminent police arrest, illegal detention, or custody.
- Forcible unlawful eviction without court decree.
- Domestic violence, physical assault, or threats to life.
- Court hearing or summons scheduled within 24-48 hours.
- Statutory limitation period expiring immediately.
- Active cyber financial fraud (Golden Hour).

Routes everyday citizen legal queries into:
- Case Building & Fact Intake
- Plain-Language Legal Rights & Statutory Options
- Legal Notice & Formal Document Drafting
- Opposing Party Negotiation Role-Play / Argument Practice
- Citation & Section Verification
"""

import re
from typing import Any, Dict, List, Optional
from src.config import config
from src.constants import URGENT_LEGAL_FLAGS, OUTDATED_LAW_MAPPINGS
from src.logger import logger


class LegalIntentRouter:
    """Classifies user queries into legal categories and flags critical safety emergencies."""

    SUPPORTED_INTENTS = [
        "Emergency_Bypass", "Case_Building", "Legal_Advice", "Document_Drafting",
        "Argument_Practice", "Citation_Verification", "Outdated_Law", "Greeting",
        "General_Legal_Query"
    ]

    # Keyword patterns for critical emergency escalation
    EMERGENCY_PATTERNS = {
        "arrest": [
            r"\bpolice\s+(?:are\s+at\s+my\s+door|threatening\s+to\s+arrest|arresting\s+me)\b",
            r"\barrest\s+(?:without\s+a?\s*warrant|warrant|imminent)\b",
            r"\bpolice\s+custody\b", r"\billegal\s+detention\b", r"\banticipatory\s+bail\s+urgently\b"
        ],
        "eviction": [
            r"\bthrown?\s+(?:out\s+on\s+the\s+street|out\s+of\s+my\s+(?:house|flat|apartment))\b",
            r"\blandlord\s+(?:locked\s+me\s+out|threw\s+my\s+belongings|disconnecting\s+electricity|cutting\s+water)\b",
            r"\bforcibl[ey]\s+evicting\b", r"\billegal\s+eviction\s+right\s+now\b"
        ],
        "violence": [
            r"\bdomestic\s+violence\b", r"\bhusband\s+is\s+beating\b", r"\bin-laws\s+are\s+threatening\b",
            r"\bphysical\s+assault\b", r"\bthreat\s+to\s+life\b", r"\bextortion\b", r"\bacid\s+attack\b"
        ],
        "hearing": [
            r"\bcourt\s+(?:hearing|summons?)\s+(?:tomorrow|in\s+24\s+hours|in\s+48\s+hours|today)\b",
            r"\bwarrant\s+issued\s+for\s+tomorrow\b", r"\bex-parte\s+order\s+tomorrow\b"
        ],
        "limitation": [
            r"\blimitation\s+(?:expires|period\s+ends)\s+(?:today|tomorrow|this\s+week)\b",
            r"\blast\s+day\s+to\s+file\b"
        ],
        "cyber_fraud": [
            r"\bmoney\s+just\s+debited\s+from\s+my\s+account\b", r"\botp\s+scam\b",
            r"\bcyber\s+fraud\b", r"\bbank\s+account\s+(?:hacked|drained|emptied)\b",
            r"\b(?:scammed|scam)\b.*\b(?:bank|account|money|rupees)\b",
            r"\bunauthorized\s+(?:debit|transaction|withdrawal)\b"
        ]
    }

    def classify(self, query: str, history_str: str = "") -> Dict[str, Any]:
        """Classifies incoming query and determines whether urgent escalation is triggered.
        
        Returns:
            Dict containing 'intents' (list), 'emergency_bypass' (bool), and 'matched_flag'.
        """
        query_lower = query.lower().strip()

        # 1. Rule-based emergency safety bypass (Highest Priority)
        for flag_name, patterns in self.EMERGENCY_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, query_lower):
                    logger.warning(f"Critical legal emergency triggered: {flag_name} ('{query[:60]}...')")
                    return {
                        "intents": ["Emergency_Bypass"],
                        "emergency_bypass": True,
                        "emergency_type": flag_name,
                        "matched_flag": URGENT_LEGAL_FLAGS.get(flag_name, flag_name)
                    }

        # 2. Greeting detection (instant 0ms response)
        greeting_pattern = r"^(hi+|he+y+|hello+|namaste|pranam|greetings|good\s+(morning|afternoon|evening)|start|help)\b"
        if re.match(greeting_pattern, query_lower):
            legal_keywords = ["landlord", "salary", "refund", "cheque", "notice", "police", "agreement", "deposit", "court"]
            if not any(k in query_lower for k in legal_keywords):
                return {
                    "intents": ["Greeting"],
                    "emergency_bypass": False,
                    "matched_flag": None
                }

        # 3. Document Drafting intent
        draft_pattern = r"\b(?:draft|generate|prepare|write|template|sample)\s+(?:a\s+)?(?:legal\s+notice|notice|complaint|reply|representation|application|affidavit|rti)\b"
        if re.search(draft_pattern, query_lower) or any(w in query_lower for w in ["draft notice", "draft complaint", "prepare notice", "send notice"]):
            return {
                "intents": ["Document_Drafting"],
                "emergency_bypass": False,
                "matched_flag": None
            }

        # 4. Argument Practice / Negotiation Role-Play intent
        roleplay_pattern = r"\b(?:roleplay|role\s+play|simulate|practi[sc]e\s+arguments?|cross\s+examine|opposing\s+party|negotiation|counter\s+argument)\b"
        if re.search(roleplay_pattern, query_lower):
            return {
                "intents": ["Argument_Practice"],
                "emergency_bypass": False,
                "matched_flag": None
            }

        # 5. Outdated Law check
        for old_term in OUTDATED_LAW_MAPPINGS.keys():
            if re.search(r'\b' + re.escape(old_term) + r'\b', query_lower):
                return {
                    "intents": ["Outdated_Law", "Legal_Advice"],
                    "emergency_bypass": False,
                    "matched_flag": None
                }

        # 6. Specific Citation / Section inquiry
        if re.search(r"\b(?:section|sec\.|article|art\.)\s*\d+", query_lower):
            return {
                "intents": ["Citation_Verification", "Legal_Advice"],
                "emergency_bypass": False,
                "matched_flag": None
            }

        # 7. Conversational Case Building vs Legal Advice
        # If user provides unstructured narrative with dates, amounts, parties
        has_amount = bool(re.search(r"(?:rs\.?|inr|rupees?|\b\d{3,}\b)", query_lower))
        has_parties = any(w in query_lower for w in ["landlord", "employer", "company", "seller", "flipkart", "amazon", "tenant", "dealer", "builder"])
        has_problem = any(w in query_lower for w in ["refusing", "withholding", "scam", "defective", "cheated", "not returned", "bounced", "fired", "evict"])

        if has_amount and has_parties and has_problem:
            return {
                "intents": ["Case_Building", "Legal_Advice"],
                "emergency_bypass": False,
                "matched_flag": None
            }

        return {
            "intents": ["Legal_Advice"],
            "emergency_bypass": False,
            "matched_flag": None
        }


# Alias for backward compatibility
IntentRouter = LegalIntentRouter
