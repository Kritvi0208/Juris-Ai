# Prompt Engineering & Legal Guardrails

Juris uses tailored prompt instructions to enforce strict anti-hallucination protocols, structured legal formatting, and multi-turn citizen case building.

## System Prompt Design
The legal system prompt guides the LLM on:
1. **Plain-English Explanations**: Explaining complex statutory provisions (BNS, CPA 2019, NI Act, SRA, TPA) in accessible, non-technical terms.
2. **Strict Anti-Hallucination Guardrails**:
   - Every substantive legal claim must be supported by retrieved evidence or verified Indian law.
   - Exact Act names, section numbers, and court precedents must be verified; never fabricate sections or case citations.
   - Distinguish binding statutory enactments from judicial interpretations and explanatory materials.
   - Automatically flag repealed colonial statutes (e.g., IPC 1860, CrPC 1973) and provide the modern enactment (BNS 2023, BNSS 2023).
   - If legal evidence or facts are insufficient, explicitly state so instead of guessing.
3. **Structured Citizen Response Format**:
   - **Legal Summary & Plain-English Position**: Clear overview of rights and current standing.
   - **Applicable Indian Laws & Sections**: Specific statutory provisions and precedents.
   - **Practical Step-by-Step Options**: Immediate demand letters, mediation, forum filing.
   - **Missing Information & Key Questions**: Follow-up questions to clarify unknown facts.
   - **Statutory Limitation Deadlines**: Relevant filing deadlines.
   - **Source Citations & Non-Lawyer Disclaimer**: Explicit notice that the assistant is an informational tool and does not replace an enrolled advocate.
4. **First-Person Follow-Up Suggestions**: Formulates 3 actionable, first-person citizen follow-up prompts (e.g., "Draft a 15-day legal notice to my landlord", "What is the court fee for filing in the District Commission?").
