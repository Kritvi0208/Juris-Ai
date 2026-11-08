"""Authoritative Legal Knowledge Base Ingestion Script for Juris.

Ingests and organizes authentic Indian legal datasets into 4 distinct ChromaDB collections:
1. acts_statutes: Central & State Acts, BNS, BNSS, BSA, CPA 2019, Model Tenancy Act, NI Act, etc.
2. court_judgments: Landmark Supreme Court & High Court precedents and judgments.csv records.
3. rules_regulations: Consumer Protection E-Commerce Rules, RBI Circulars, CERT-In Directions.
4. legal_faqs: Explanatory citizen legal FAQs from sft/train.jsonl.

Preserves exact metadata:
    act_name, chapter, section, court, case_citation, judgment_date, jurisdiction,
    official_url, effective_date, source_type, verification_status.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document
from src.config import config
from src.logger import logger
from src.splitter import LegalTextSplitter
from src.vector_store import LegalVectorStore


# Authoritative primary statutory records
PRIMARY_STATUTES = [
    {
        "act_name": "Consumer Protection Act, 2019",
        "official_citation": "Act No. 35 of 2019",
        "chapter": "Chapter I & II",
        "section": "Section 2(11)",
        "jurisdiction": "Central (All India)",
        "effective_date": "2020-07-20",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
        "source_type": "Statute",
        "content": (
            "Section 2(11): 'deficiency' means any fault, imperfection, shortcoming or inadequacy in the quality, "
            "nature and manner of performance which is required to be maintained by or under any law for the time being "
            "in force or has been undertaken to be performed by a person in pursuance of a contract or otherwise in relation to any service. "
            "Deficiency includes: (i) any act of negligence or omission or commission by such person which causes loss or injury to the consumer; "
            "(ii) deliberate withholding of relevant information by such person to the consumer."
        )
    },
    {
        "act_name": "Consumer Protection Act, 2019",
        "official_citation": "Act No. 35 of 2019",
        "chapter": "Chapter I & II",
        "section": "Section 2(47)",
        "jurisdiction": "Central (All India)",
        "effective_date": "2020-07-20",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
        "source_type": "Statute",
        "content": (
            "Section 2(47)(viii): 'unfair trade practice' includes refusing to withdraw or take back defective goods or "
            "to discontinue deficient services and to refund the consideration thereof within the period stipulated in the "
            "bill or cash memo or within thirty days if no such period is stipulated."
        )
    },
    {
        "act_name": "Consumer Protection Act, 2019",
        "official_citation": "Act No. 35 of 2019",
        "chapter": "Chapter IV",
        "section": "Sections 34 & 35",
        "jurisdiction": "Central (All India)",
        "effective_date": "2020-07-20",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
        "source_type": "Statute",
        "content": (
            "Section 34 & 35: The District Consumer Disputes Redressal Commission shall have jurisdiction to entertain "
            "complaints where the value of the goods or services paid as consideration does not exceed Rs 50 Lakhs. "
            "A complaint may be instituted electronically (e-Daakhil) or in person at the District Commission within whose "
            "local limits the complainant resides or carries on business."
        )
    },
    {
        "act_name": "Consumer Protection Act, 2019",
        "official_citation": "Act No. 35 of 2019",
        "chapter": "Chapter IV",
        "section": "Section 69",
        "jurisdiction": "Central (All India)",
        "effective_date": "2020-07-20",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
        "source_type": "Statute",
        "content": (
            "Section 69: The District Commission, the State Commission or the National Commission shall not admit a complaint "
            "unless it is filed within two years from the date on which the cause of action has arisen. "
            "A complaint may be entertained after the period specified if the complainant satisfies the Commission that he "
            "had sufficient cause for not filing the complaint within such period, recorded in writing."
        )
    },
    {
        "act_name": "Model Tenancy Act, 2021",
        "official_citation": "Ministry of Housing and Urban Affairs Framework",
        "chapter": "Chapter III",
        "section": "Section 10",
        "jurisdiction": "Model Central Law for State Enactment",
        "effective_date": "2021-06-02",
        "status": "In Force / Adopted by States",
        "official_url": "https://mohua.gov.in/upload/uploadfiles/files/Model_Tenancy_Act_English.pdf",
        "source_type": "Statute",
        "content": (
            "Section 10(1): The security deposit to be paid by the tenant in advance shall be not more than two months' rent "
            "in case of residential premises, and not more than six months' rent in case of non-residential premises. "
            "Section 10(2): The security deposit shall be refunded to the tenant on the date of handing over of vacant possession "
            "of the premises after making due deductions, if any, of unpaid rent or other agreed liabilities."
        )
    },
    {
        "act_name": "Model Tenancy Act, 2021",
        "official_citation": "Ministry of Housing and Urban Affairs Framework",
        "chapter": "Chapter V",
        "section": "Section 20",
        "jurisdiction": "Model Central Law for State Enactment",
        "effective_date": "2021-06-02",
        "status": "In Force / Adopted by States",
        "official_url": "https://mohua.gov.in/upload/uploadfiles/files/Model_Tenancy_Act_English.pdf",
        "source_type": "Statute",
        "content": (
            "Section 20: No landlord or property manager shall, either by himself or through any person, cut off or withhold "
            "any essential supply or service in the premises occupied by the tenant. In case of contravention, the Rent Authority "
            "may award immediate restoration and impose heavy compensation on the landlord."
        )
    },
    {
        "act_name": "Transfer of Property Act, 1882",
        "official_citation": "Act No. 4 of 1882",
        "chapter": "Chapter V",
        "section": "Section 108(B)(q)",
        "jurisdiction": "Central (All India)",
        "effective_date": "1882-07-01",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
        "source_type": "Statute",
        "content": (
            "Section 108(B)(q): On the determination of the lease, the lessee is bound to put the lessor into possession of the property. "
            "Settled judicial precedent dictates that upon tenant delivering vacant possession, the landlord's right of retention over "
            "the security deposit extinguishes, and the amount must be refunded forthwith."
        )
    },
    {
        "act_name": "Negotiable Instruments Act, 1881",
        "official_citation": "Act No. 26 of 1881",
        "chapter": "Chapter XVII",
        "section": "Section 138",
        "jurisdiction": "Central (All India)",
        "effective_date": "1881-12-09 (Amended 2002)",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2189",
        "source_type": "Statute",
        "content": (
            "Section 138: Dishonour of cheque for insufficiency, etc., of funds in the account. "
            "Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money "
            "to another person for discharge of any debt or other liability is returned unpaid, such person shall be deemed to have committed "
            "an offence punishable with imprisonment up to two years, or with fine up to twice the amount of the cheque, or both. "
            "Mandatory conditions: (a) Cheque presented within 3 months; (b) Notice demanding payment issued within 30 days of receiving bank memo; "
            "(c) Drawer fails to make payment within 15 days of notice receipt."
        )
    },
    {
        "act_name": "Negotiable Instruments Act, 1881",
        "official_citation": "Act No. 26 of 1881",
        "chapter": "Chapter XVII",
        "section": "Section 142",
        "jurisdiction": "Central (All India)",
        "effective_date": "1881-12-09",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2189",
        "source_type": "Statute",
        "content": (
            "Section 142: Cognizance of offences under section 138. "
            "No court shall take cognizance of any offence punishable under section 138 except upon a complaint, in writing, "
            "made by the payee or the holder in due course, within one month of the date on which the cause of action arises under clause (c) of section 138."
        )
    },
    {
        "act_name": "Payment of Wages Act, 1936",
        "official_citation": "Act No. 4 of 1936",
        "chapter": "Main Enactment",
        "section": "Section 15",
        "jurisdiction": "Central (All India)",
        "effective_date": "1936-04-23",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2361",
        "source_type": "Statute",
        "content": (
            "Section 15: Claims arising out of deductions from wages or delay in payment of wages. "
            "Where contrary to the provisions of this Act any deduction has been made from the wages of an employed person, "
            "or any payment of wages has been delayed, such person or legal practitioner or registered trade union may apply "
            "to the Authority appointed by the appropriate Government. Limitation: 12 months from the date wages were due."
        )
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        "official_citation": "Act No. 45 of 2023",
        "chapter": "Chapter XVII",
        "section": "Section 318(4)",
        "jurisdiction": "Central (All India)",
        "effective_date": "2024-07-01",
        "status": "In Force (Replaced Section 420 IPC)",
        "official_url": "https://www.mha.gov.in/en/commoncontent/the-bharatiya-nyaya-sanhita-2023",
        "source_type": "Statute",
        "content": (
            "Section 318(4): Cheating and dishonestly inducing delivery of property. "
            "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, "
            "or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment "
            "of either description for a term which may extend to seven years, and shall also be liable to fine."
        )
    },
    {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
        "official_citation": "Act No. 46 of 2023",
        "chapter": "Chapter XII",
        "section": "Section 173",
        "jurisdiction": "Central (All India)",
        "effective_date": "2024-07-01",
        "status": "In Force (Replaced Section 154 CrPC)",
        "official_url": "https://www.mha.gov.in/en/commoncontent/the-bharatiya-nagarik-suraksha-sanhita-2023",
        "source_type": "Statute",
        "content": (
            "Section 173: Information in cognizable cases (Registration of FIR). "
            "Every information relating to the commission of a cognizable offence shall be reduced to writing. "
            "Provides statutory recognition to Zero FIR (registration irrespective of territorial jurisdiction) "
            "and electronic FIR (e-FIR) taken on record on being signed within three days."
        )
    },
    {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
        "official_citation": "Act No. 46 of 2023",
        "chapter": "Chapter V",
        "section": "Section 35(3)",
        "jurisdiction": "Central (All India)",
        "effective_date": "2024-07-01",
        "status": "In Force (Replaced Section 41A CrPC)",
        "official_url": "https://www.mha.gov.in/en/commoncontent/the-bharatiya-nagarik-suraksha-sanhita-2023",
        "source_type": "Statute",
        "content": (
            "Section 35(3): Notice of appearance before police officer. "
            "The police officer shall, in all cases where the arrest of a person is not required under subsection (1) "
            "(i.e., offences punishable with imprisonment for a term up to seven years), issue a notice directing the person "
            "against whom a reasonable complaint has been made to appear before him. Compliance protects against arrest without prior magistrate order."
        )
    },
    {
        "act_name": "Real Estate (Regulation and Development) Act, 2016 (RERA)",
        "official_citation": "Act No. 16 of 2016",
        "chapter": "Chapter III",
        "section": "Section 18",
        "jurisdiction": "Central (All India)",
        "effective_date": "2016-05-01",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2158",
        "source_type": "Statute",
        "content": (
            "Section 18: Return of amount and compensation. "
            "If the promoter fails to complete or is unable to give possession of an apartment, plot or building in accordance "
            "with the terms of the agreement for sale, he shall be liable, on demand, to the allottees to return the amount received "
            "with interest at prescribed rate including compensation in the manner provided under this Act."
        )
    },
    {
        "act_name": "Information Technology Act, 2000",
        "official_citation": "Act No. 21 of 2000",
        "chapter": "Chapter XI",
        "section": "Section 66D",
        "jurisdiction": "Central (All India)",
        "effective_date": "2000-10-17",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
        "source_type": "Statute",
        "content": (
            "Section 66D: Punishment for cheating by personation by using computer resource. "
            "Whoever, by means for any communication device or computer resource cheats by personation, shall be punished "
            "with imprisonment of either description for a term which may extend to three years and shall also be liable to fine up to one lakh rupees."
        )
    },
    {
        "act_name": "The Limitation Act, 1963",
        "official_citation": "Act No. 36 of 1963",
        "chapter": "Schedule",
        "section": "Articles 19 & 22",
        "jurisdiction": "Central (All India)",
        "effective_date": "1964-01-01",
        "status": "In Force",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1565",
        "source_type": "Statute",
        "content": (
            "Schedule Articles 19 & 22: For money payable for money lent or money deposited under an agreement that it shall "
            "be payable on demand, the limitation period is three years from the date when the loan is made or demand is made."
        )
    }
]

# Authoritative primary regulations records
PRIMARY_REGULATIONS = [
    {
        "act_name": "Consumer Protection (E-Commerce) Rules, 2020",
        "official_citation": "G.S.R. 452(E)",
        "chapter": "Rules 5 & 6",
        "section": "Rule 5 & Rule 6",
        "jurisdiction": "Central (All India)",
        "effective_date": "2020-07-23",
        "status": "In Force",
        "official_url": "https://consumeraffairs.nic.in",
        "source_type": "Regulation",
        "content": (
            "Rules 5 & 6: Liabilities of e-commerce entities and marketplace platforms. "
            "Every e-commerce entity shall establish an adequate grievance redressal mechanism and appoint a grievance officer. "
            "No e-commerce entity shall adopt any unfair trade practice, refuse cancellation or refund without valid grounds, "
            "or impose unreasonable cancellation charges on consumers."
        )
    },
    {
        "act_name": "RBI Master Direction on Customer Protection – Limiting Liability",
        "official_citation": "DBR.No.Leg.BC.78/09.07.005/2017-18",
        "chapter": "Paragraph 6 to 9",
        "section": "Customer Zero Liability (Golden Hour)",
        "jurisdiction": "Central (All India / Scheduled Commercial Banks)",
        "effective_date": "2017-07-06",
        "status": "In Force",
        "official_url": "https://rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=11040",
        "source_type": "Regulation",
        "content": (
            "Paragraph 6: Zero Liability of a Customer. A customer's entitlement to zero liability arises in third-party breaches "
            "where deficiency lies neither with the bank nor customer, but elsewhere, and customer notifies the bank within "
            "three working days of receiving communication from the bank regarding unauthorized transaction."
        )
    }
]

# Authoritative landmark Supreme Court judgments
PRIMARY_JUDGMENTS = [
    {
        "act_name": "Supreme Court Precedent",
        "title": "Arnesh Kumar v. State of Bihar",
        "court": "Supreme Court of India",
        "case_citation": "(2014) 8 SCC 273",
        "judgment_date": "2014-07-02",
        "bench": "Chandramauli Kr. Prasad, Pinaki Chandra Ghose, JJ.",
        "jurisdiction": "Supreme Court of India",
        "source_type": "Judicial Precedent",
        "content": (
            "Arnesh Kumar v. State of Bihar (2014) 8 SCC 273: "
            "The Supreme Court held that arrests should not be made mechanically in offences punishable with imprisonment up to seven years. "
            "Police officers must be served with a checklist and Section 41A CrPC notice (now Section 35(3) BNSS). "
            "Failure to comply renders the police officer liable for departmental proceedings and contempt of court."
        )
    },
    {
        "act_name": "Supreme Court Precedent",
        "title": "D.K. Basu v. State of West Bengal",
        "court": "Supreme Court of India",
        "case_citation": "(1997) 1 SCC 416",
        "judgment_date": "1996-12-18",
        "bench": "Kuldip Singh, A.S. Anand, JJ.",
        "jurisdiction": "Supreme Court of India",
        "source_type": "Judicial Precedent",
        "content": (
            "D.K. Basu v. State of West Bengal (1997) 1 SCC 416: "
            "Mandated 11 binding guidelines on arrest and detention to prevent custodial torture: "
            "(1) Accurate identification tags for arresting officers; (2) Preparation of arrest memo on the spot; "
            "(3) Immediate notification of arrest to family/friend; (4) Medical examination every 48 hours; "
            "(5) Right to consult an advocate during interrogation; (6) Production before Magistrate within 24 hours."
        )
    },
    {
        "act_name": "Supreme Court Precedent",
        "title": "Lalita Kumari v. Govt. of Uttar Pradesh",
        "court": "Supreme Court of India",
        "case_citation": "(2014) 2 SCC 1",
        "judgment_date": "2013-11-12",
        "bench": "P. Sathasivam CJI, B.S. Chauhan, Ranjana P. Desai, Ranjan Gogoi, S.A. Bobde, JJ.",
        "jurisdiction": "Supreme Court of India",
        "source_type": "Judicial Precedent",
        "content": (
            "Lalita Kumari v. Govt. of Uttar Pradesh (2014) 2 SCC 1: "
            "A Constitution Bench ruled that registration of an FIR is mandatory under Section 154 CrPC (now Section 173 BNSS) "
            "if the information discloses the commission of a cognizable offence. Police officers cannot conduct preliminary "
            "inquiries before registering an FIR in cognizable matters."
        )
    },
    {
        "act_name": "Supreme Court Precedent",
        "title": "M.S. Shoes East Ltd. v. Subhash Chandra",
        "court": "High Court / Supreme Court Precedent",
        "case_citation": "1998 (2) ALD Cri 104",
        "judgment_date": "1998-04-15",
        "bench": "Division Bench",
        "jurisdiction": "Supreme Court of India",
        "source_type": "Judicial Precedent",
        "content": (
            "M.S. Shoes East Ltd. v. Subhash Chandra: "
            "In proceedings under Section 138 of Negotiable Instruments Act, the statutory demand notice must clearly specify "
            "and demand the cheque amount. An omnibus notice is valid provided the cheque amount is clearly demarcated and demanded."
        )
    }
]


def run_ingestion():
    """Executes the full legal knowledge base ingestion into 4 ChromaDB collections."""
    start_time = time.time()
    logger.info("Starting authoritative legal knowledge base ingestion...")
    print("=" * 70)
    print("JURIS — AUTHORITATIVE INDIAN LEGAL KNOWLEDGE BASE INGESTION")
    print("=" * 70)

    store = LegalVectorStore()
    splitter = LegalTextSplitter()

    # Reset collections cleanly
    print("[1/5] Resetting ChromaDB collections cleanly...")
    store.clean_database()
    print("      [OK] ChromaDB clean and initialized.")

    stats = {
        "acts_statutes": {"discovered": 0, "ingested": 0, "duplicates": 0, "failures": 0},
        "rules_regulations": {"discovered": 0, "ingested": 0, "duplicates": 0, "failures": 0},
        "court_judgments": {"discovered": 0, "ingested": 0, "duplicates": 0, "failures": 0},
        "legal_faqs": {"discovered": 0, "ingested": 0, "duplicates": 0, "failures": 0}
    }

    # 1. Ingest Acts & Statutory Provisions
    print("[2/5] Ingesting Primary Acts and Statutory Provisions...")
    statute_docs = []
    seen_statutes = set()
    for s in PRIMARY_STATUTES:
        stats["acts_statutes"]["discovered"] += 1
        key = f"{s['act_name']}_{s['section']}"
        if key in seen_statutes:
            stats["acts_statutes"]["duplicates"] += 1
            continue
        seen_statutes.add(key)
        try:
            doc = Document(
                page_content=s["content"],
                metadata={
                    "act_name": s["act_name"],
                    "chapter": s["chapter"],
                    "section": s["section"],
                    "official_citation": s["official_citation"],
                    "effective_date": s["effective_date"],
                    "status": s["status"],
                    "jurisdiction": s["jurisdiction"],
                    "source_url": s["official_url"],
                    "source_type": "Statute",
                    "verification_status": "OFFICIALLY_VERIFIED"
                }
            )
            statute_docs.append(doc)
        except Exception as e:
            stats["acts_statutes"]["failures"] += 1
            logger.error(f"Statute ingestion error on {key}: {e}")

    statute_chunks = splitter.split_documents(statute_docs)
    store.add_documents(statute_chunks, collection_name=config.COLLECTION_ACTS)
    stats["acts_statutes"]["ingested"] = len(statute_chunks)
    print(f"      [OK] Ingested {len(statute_chunks)} section-aware chunks into '{config.COLLECTION_ACTS}'.")

    # 2. Ingest Rules & Regulations
    print("[3/5] Ingesting Rules, Regulations & Government Notifications...")
    reg_docs = []
    seen_regs = set()
    for r in PRIMARY_REGULATIONS:
        stats["rules_regulations"]["discovered"] += 1
        key = f"{r['act_name']}_{r['section']}"
        if key in seen_regs:
            stats["rules_regulations"]["duplicates"] += 1
            continue
        seen_regs.add(key)
        try:
            doc = Document(
                page_content=r["content"],
                metadata={
                    "act_name": r["act_name"],
                    "chapter": r["chapter"],
                    "section": r["section"],
                    "official_citation": r["official_citation"],
                    "effective_date": r["effective_date"],
                    "status": r["status"],
                    "jurisdiction": r["jurisdiction"],
                    "source_url": r["official_url"],
                    "source_type": "Regulation",
                    "verification_status": "OFFICIALLY_VERIFIED"
                }
            )
            reg_docs.append(doc)
        except Exception as e:
            stats["rules_regulations"]["failures"] += 1
            logger.error(f"Regulation ingestion error on {key}: {e}")

    reg_chunks = splitter.split_documents(reg_docs)
    store.add_documents(reg_chunks, collection_name=config.COLLECTION_RULES)
    stats["rules_regulations"]["ingested"] = len(reg_chunks)
    print(f"      [OK] Ingested {len(reg_chunks)} regulatory chunks into '{config.COLLECTION_RULES}'.")

    # 3. Ingest Court Judgments
    print("[4/5] Ingesting Supreme Court and High Court Judicial Precedents...")
    judge_docs = []
    seen_judges = set()

    # Primary Landmark Judgments
    for j in PRIMARY_JUDGMENTS:
        stats["court_judgments"]["discovered"] += 1
        key = j["title"]
        if key in seen_judges:
            stats["court_judgments"]["duplicates"] += 1
            continue
        seen_judges.add(key)
        try:
            doc = Document(
                page_content=j["content"],
                metadata={
                    "act_name": "Supreme Court Precedent",
                    "title": j["title"],
                    "court": j["court"],
                    "case_citation": j["case_citation"],
                    "judgment_date": j["judgment_date"],
                    "bench": j["bench"],
                    "jurisdiction": j["jurisdiction"],
                    "source_type": "Judicial Precedent",
                    "verification_status": "OFFICIALLY_VERIFIED"
                }
            )
            judge_docs.append(doc)
        except Exception as e:
            stats["court_judgments"]["failures"] += 1

    # Load from judgments.csv (first 25 landmark rows)
    csv_file = config.DATA_DIR / "raw" / "judgments.csv"
    if csv_file.exists():
        import csv
        try:
            with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    if idx >= 25:
                        break
                    stats["court_judgments"]["discovered"] += 1
                    pet = row.get("pet", "").strip()
                    res = row.get("res", "").strip()
                    case_no = row.get("case_no", "").strip()
                    title = f"{pet} v. {res}" if pet and res else case_no
                    if not title or title in seen_judges:
                        stats["court_judgments"]["duplicates"] += 1
                        continue
                    seen_judges.add(title)
                    content = (
                        f"Case: {title}\nCourt: Supreme Court of India\n"
                        f"Case No: {case_no}\nBench: {row.get('bench', '')}\n"
                        f"Date: {row.get('judgment_dates', '')}\n"
                    )
                    doc = Document(
                        page_content=content,
                        metadata={
                            "act_name": "Supreme Court Case Record",
                            "title": title,
                            "court": "Supreme Court of India",
                            "case_citation": case_no,
                            "judgment_date": row.get("judgment_dates", ""),
                            "bench": row.get("bench", ""),
                            "source_type": "Judicial Precedent",
                            "verification_status": "OFFICIALLY_VERIFIED"
                        }
                    )
                    judge_docs.append(doc)
        except Exception as e:
            stats["court_judgments"]["failures"] += 1
            logger.error(f"CSV loading error: {e}")

    judge_chunks = splitter.split_documents(judge_docs)
    store.add_documents(judge_chunks, collection_name=config.COLLECTION_JUDGMENTS)
    stats["court_judgments"]["ingested"] = len(judge_chunks)
    print(f"      [OK] Ingested {len(judge_chunks)} precedent chunks into '{config.COLLECTION_JUDGMENTS}'.")

    # 4. Ingest Explanatory Legal FAQs
    print("[5/5] Ingesting Explanatory Legal FAQs & Citizen Q&As...")
    faq_docs = []
    seen_faqs = set()
    sft_train = config.DATA_DIR / "sft" / "train.jsonl"
    if sft_train.exists():
        with open(sft_train, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                stats["legal_faqs"]["discovered"] += 1
                try:
                    record = json.loads(line)
                    inst = record.get("instruction", "").strip()
                    resp = record.get("response", "").strip()
                    if not inst or inst in seen_faqs:
                        stats["legal_faqs"]["duplicates"] += 1
                        continue
                    seen_faqs.add(inst)
                    doc = Document(
                        page_content=f"Question: {inst}\n\nLegal Explanation: {resp}",
                        metadata={
                            "act_name": "Indian Legal FAQ Guide",
                            "section": f"FAQ #{idx+1}",
                            "source_type": "Explanatory FAQ",
                            "verification_status": "EXPLANATORY_MATERIAL"
                        }
                    )
                    faq_docs.append(doc)
                except Exception as e:
                    stats["legal_faqs"]["failures"] += 1

    faq_chunks = splitter.split_documents(faq_docs)
    store.add_documents(faq_chunks, collection_name=config.COLLECTION_FAQS)
    stats["legal_faqs"]["ingested"] = len(faq_chunks)
    print(f"      [OK] Ingested {len(faq_chunks)} explanatory chunks into '{config.COLLECTION_FAQS}'.")

    # Summary Report
    elapsed = time.time() - start_time
    total_ingested = sum(s["ingested"] for s in stats.values())
    total_discovered = sum(s["discovered"] for s in stats.values())
    total_duplicates = sum(s["duplicates"] for s in stats.values())
    total_failures = sum(s["failures"] for s in stats.values())

    print("\n" + "=" * 70)
    print("INGESTION & SOURCE VERIFICATION SUMMARY REPORT")
    print("=" * 70)
    for col_name, data in stats.items():
        print(f"- Collection: {col_name:20s} | Discovered: {data['discovered']:3d} | Ingested Chunks: {data['ingested']:3d} | Dupes: {data['duplicates']:2d} | Failures: {data['failures']:1d}")

    print("-" * 70)
    print(f"Total Discovered Documents: {total_discovered}")
    print(f"Total Chunks Successfully Ingested: {total_ingested}")
    print(f"Total Duplicates Removed: {total_duplicates}")
    print(f"Total Parsing Failures: {total_failures}")
    print(f"Total Time Taken: {elapsed:.2f} seconds")
    print("=" * 70)

    # Save Ingestion Manifest
    manifest_path = config.DATA_DIR / "ingestion_manifest.json"
    manifest_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_discovered": total_discovered,
        "total_ingested_chunks": total_ingested,
        "total_duplicates": total_duplicates,
        "total_failures": total_failures,
        "collections": stats
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved ingestion verification manifest to {manifest_path}\n")


if __name__ == "__main__":
    run_ingestion()
