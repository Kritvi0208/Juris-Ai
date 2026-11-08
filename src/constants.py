"""Core Application Constants for Juris - Indian Citizen Legal Assistant."""

# 4 Key Legal Collections for ChromaDB
COLLECTION_ACTS = "acts_statutes"
COLLECTION_JUDGMENTS = "court_judgments"
COLLECTION_RULES = "rules_regulations"
COLLECTION_FAQS = "legal_faqs"

# Citizen Legal Problem Domains
LEGAL_CATEGORIES = [
    "Consumer Disputes & Defective Products",
    "Rental & Landlord-Tenant",
    "Employment & Unpaid Wages",
    "Negotiable Instruments & Cheque Bounce",
    "Contracts & Financial Agreements",
    "Real Estate, Builder Disputes & RERA",
    "Cyber Crime & Online Banking Fraud",
    "Criminal Law & BNS Provisions",
    "Family, Maintenance & Domestic Relations",
    "Constitutional Writs & Fundamental Rights",
    "Motor Accidents & Insurance Claims"
]

# Greetings mapping for direct conversational response
GREETING_WORDS = {
    "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
    "greetings", "namaste", "pranam", "help", "start"
}

# Critical Legal Emergencies requiring immediate escalation bypass
URGENT_LEGAL_FLAGS = {
    "arrest": "Imminent Police Arrest / Detention Without Warrant",
    "custody": "Police Custody / Illegal Confinement",
    "eviction": "Immediate Forcible / Unlawful Eviction Without Court Order",
    "violence": "Domestic Violence / Physical Threat / Assault",
    "threat": "Criminal Intimidation / Extortion / Immediate Threat to Life",
    "hearing": "Court Hearing / Notice Return Date Scheduled Within 24-48 Hours",
    "limitation": "Statutory Limitation Period Expiring Immediately",
    "cyber_fraud": "Active Banking Cyber Fraud / Account Drained in Golden Hour"
}

# Outdated and Repealed Law Warnings (Old Law -> Modern Enactment)
OUTDATED_LAW_MAPPINGS = {
    "consumer protection act 1986": (
        "The Consumer Protection Act, 1986 has been completely repealed and replaced by the "
        "Consumer Protection Act, 2019 (Act No. 35 of 2019), effective July 20, 2020. Key changes "
        "include electronic filing (e-Daakhil), product liability, mediation cells, and enhanced "
        "pecuniary jurisdiction (District Commission up to Rs 50 Lakhs)."
    ),
    "cpa 1986": (
        "The Consumer Protection Act, 1986 was repealed by the Consumer Protection Act, 2019."
    ),
    "indian penal code": (
        "The Indian Penal Code, 1860 (IPC) has been repealed and replaced by the Bharatiya Nyaya "
        "Sanhita, 2023 (BNS), effective July 1, 2024. For offences committed on or after July 1, "
        "2024, BNS sections apply (e.g., Cheating is now Section 318(4) BNS instead of Section 420 IPC)."
    ),
    "ipc": (
        "The Indian Penal Code (IPC) was replaced by the Bharatiya Nyaya Sanhita, 2023 (BNS) "
        "effective July 1, 2024."
    ),
    "code of criminal procedure": (
        "The Code of Criminal Procedure, 1973 (CrPC) has been repealed and replaced by the "
        "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS), effective July 1, 2024."
    ),
    "crpc": (
        "The Code of Criminal Procedure (CrPC) was replaced by the Bharatiya Nagarik Suraksha "
        "Sanhita, 2023 (BNSS) effective July 1, 2024."
    ),
    "indian evidence act": (
        "The Indian Evidence Act, 1872 has been replaced by the Bharatiya Sakshya Adhiniyam, 2023 "
        "(BSA), effective July 1, 2024, introducing modernized rules for electronic records and digital evidence."
    ),
    "section 420 ipc": (
        "Section 420 of IPC (Cheating and dishonestly inducing delivery of property) has been "
        "re-enacted as Section 318(4) of the Bharatiya Nyaya Sanhita, 2023 (BNS) for offences on or after July 1, 2024."
    ),
    "section 302 ipc": (
        "Section 302 of IPC (Punishment for murder) has been re-enacted as Section 103 of "
        "the Bharatiya Nyaya Sanhita, 2023 (BNS)."
    ),
    "section 154 crpc": (
        "Section 154 of CrPC (FIR registration) is now governed by Section 173 of the "
        "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS), which formally recognizes Zero FIR and e-FIR."
    )
}

# Statutory Limitation Periods (The Limitation Act, 1963)
STATUTORY_LIMITATIONS = {
    "consumer_complaint": {
        "statute": "Consumer Protection Act, 2019, Section 69",
        "period": "2 Years",
        "from_date": "Date on which the cause of action arose",
        "condonation": "Condonable by Commission if sufficient cause is shown in writing"
    },
    "recovery_of_money": {
        "statute": "The Limitation Act, 1963, Schedule Article 19 & 22",
        "period": "3 Years",
        "from_date": "Date on which the money became due or payment was refused"
    },
    "cheque_bounce_notice": {
        "statute": "Negotiable Instruments Act, 1881, Section 138(b)",
        "period": "30 Days",
        "from_date": "Receipt of memo of dishonour from the bank",
        "mandatory": True
    },
    "cheque_bounce_complaint": {
        "statute": "Negotiable Instruments Act, 1881, Section 142(1)(b)",
        "period": "1 Month",
        "from_date": "Expiry of 15 days from notice receipt without payment"
    },
    "rera_complaint": {
        "statute": "Real Estate (Regulation and Development) Act, 2016",
        "period": "No rigid limitation",
        "from_date": "Continuous cause of action until possession / refund is delivered"
    },
    "unpaid_wages": {
        "statute": "Payment of Wages Act, 1936, Section 15(2)",
        "period": "12 Months (1 Year)",
        "from_date": "Date on which the payment of wages was due",
        "condonation": "Condonable on sufficient cause"
    }
}

# Official Helpline Contacts for Citizen Referrals
LEGAL_HELPLINES = {
    "National Legal Services Authority (NALSA)": "15100 (Toll-Free National Legal Aid)",
    "National Consumer Helpline (NCH)": "1915 or SMS 8800001915",
    "National Cyber Crime Helpline": "1930 (Golden Hour reporting portal: cybercrime.gov.in)",
    "National Emergency Helpline": "112 (Police, Fire, Ambulance)",
    "Women in Distress Helpline": "1091",
    "Domestic Abuse (NCW)": "7827170170"
}
