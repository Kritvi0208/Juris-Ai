# Juris Legal Tools Reference

Juris provides 10 specialized legal tools enabling structured legal analysis, statutory verification, document drafting, and emergency escalation under Indian law.

## 1. Statutory & Case Law Research
- **`statute_lookup`**: Queries the `acts_statutes` ChromaDB collection to retrieve exact sections, subsections, and explanations of Indian Acts (e.g., BNS 2023, CPA 2019, NI Act 1881, Transfer of Property Act 1882, Specific Relief Act 1963).
- **`judgment_lookup`**: Queries the `court_judgments` collection for Supreme Court and High Court precedents, case citations, and judicial ratios on specific legal disputes.

## 2. Anti-Hallucination & Statutory Verification
- **`citation_verifier`**: Validates whether a cited legal section and Act actually exist in Indian law, returning authoritative statutory titles or explicitly rejecting non-existent sections (e.g. "Section 999 of the Indian Contract Act").
- **`outdated_law_checker`**: Detects repealed or superseded colonial-era statutes (e.g., IPC 1860, CrPC 1973, Indian Evidence Act 1872, Consumer Protection Act 1986) and maps them directly to the corresponding provisions in modern enactments (Bharatiya Nyaya Sanhita 2023, Bharatiya Nagarik Suraksha Sanhita 2023, Bharatiya Sakshya Adhiniyam 2023, CPA 2019).

## 3. Legal Calculations & Jurisdictional Analysis
- **`calculate_limitation`**: Computes the statutory deadline for filing legal action based on the cause of action date under the Limitation Act 1963 (e.g., 3 years for contract/debt recovery), Consumer Protection Act 2019 (2 years from cause of action), and Section 138 NI Act (15-day notice window, 30-day complaint filing).
- **`calculate_court_fee`**: Determines the appropriate forum and estimated court fee or filing fee based on disputed amount and claim category (e.g., District Consumer Commission up to ₹50 Lakh, State Commission ₹50 Lakh–₹2 Crore, NCDRC > ₹2 Crore).

## 4. Case Building & Fact Extraction
- **`extract_case_facts`**: Parses unstructured citizen narratives into structured legal entities: parties (Aggrieved Citizen vs. Opposing Party), incident dates, financial amounts, available evidence (written contracts, transaction receipts, communications), and missing facts needed to establish a prima facie case.

## 5. Document Drafting & Representation
- **`draft_legal_document`**: Generates formal, legally structured drafts populated with verified case facts:
  - **Legal Demand Notice**: Formal notice under Section 106 Transfer of Property Act or general civil recovery with a mandatory 15-day compliance window.
  - **Consumer Forum Complaint**: Formal petition under Section 35 of the Consumer Protection Act 2019 for the District Consumer Commission.
  - **Reply to Legal Notice**: Formal rebuttal countering allegations and setting out defenses.
  - **RTI Application**: Formal application under Section 6(1) of the Right to Information Act 2005.

## 6. Negotiation Practice & Opposition Simulation
- **`simulate_opposing_party`**: Role-plays as the counterparty (e.g., landlord refusing deposit return, merchant denying refund, or employer withholding salary). Raises realistic objections, tests citizen evidence, and offers constructive feedback on arguments.

## 7. Emergency Legal Escalation
- **`emergency_legal_guide`**: Provides immediate, non-delayed guidance and helplines for urgent legal emergencies:
  - Imminent arrest / police harassment (Article 22(1), D.K. Basu guidelines, NALSA 15100).
  - Unlawful eviction / dispossession (Section 6 Specific Relief Act, 112).
  - Domestic violence / physical danger (PWDVA Section 12, 181, 112).
  - Cyber financial fraud (National Cyber Crime Helpline 1930 / Golden Hour protocol).
  - Court hearing within 24-48 hours (DLSA legal aid & adjournment procedures).
