"""
Juris Unit & Component Test Runner.
"""
import sys
import os
import unittest
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.utils import clean_text, time_formatter, token_counter, format_sources
from src.constants import LEGAL_CATEGORIES, STATUTORY_LIMITATIONS, LEGAL_HELPLINES, OUTDATED_LAW_MAPPINGS
from src.tools import (
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
from src.router import LegalIntentRouter
from src.memory import CitizenLegalMemory


class TestJurisComponents(unittest.TestCase):
    
    def test_utils(self):
        """Test utility helper functions."""
        self.assertEqual(clean_text("  Legal   Notice \n"), "Legal Notice")
        self.assertEqual(time_formatter(0.005), "5.00 ms")
        self.assertEqual(time_formatter(2.5), "2.50 seconds")
        self.assertGreater(token_counter("Testing the token counter for legal text"), 0)

    def test_tools_citation_verifier(self):
        """Test citation verification tool with real and fake sections."""
        # Valid section
        valid_res = citation_verifier.invoke({"citation_or_section": "Section 138 Negotiable Instruments Act"})
        self.assertIn("VERIFIED", valid_res)
        self.assertIn("Negotiable Instruments Act", valid_res)

        # Invalid section
        invalid_res = citation_verifier.invoke({"citation_or_section": "Section 9999 of Fictitious Act"})
        self.assertIn("FAILED", invalid_res)

    def test_tools_outdated_law_checker(self):
        """Test outdated colonial law mapping."""
        res_ipc = outdated_law_checker.invoke({"legal_reference": "Section 420 IPC"})
        self.assertIn("Repealed", res_ipc)
        self.assertIn("318", res_ipc)
        self.assertIn("Bharatiya Nyaya Sanhita", res_ipc)

    def test_tools_calculate_limitation(self):
        """Test limitation period calculator."""
        res = calculate_limitation.invoke({"cause_of_action": "consumer_complaint", "incident_date": "2024-01-01"})
        self.assertIn("Consumer Protection Act, 2019", res)
        self.assertIn("2 Years", res)

        res_contract = calculate_limitation.invoke({"cause_of_action": "recovery_of_money", "incident_date": "2023-05-15"})
        self.assertIn("Limitation Act, 1963", res_contract)
        self.assertIn("3 Years", res_contract)

    def test_tools_calculate_court_fee(self):
        """Test court fee & pecuniary jurisdiction calculator."""
        res_dist = calculate_court_fee.invoke({"claim_amount_inr": 2500000.0, "forum_type": "Consumer Commission"})
        self.assertIn("District Commission", res_dist)

        res_state = calculate_court_fee.invoke({"claim_amount_inr": 6000000.0, "forum_type": "Consumer Commission"})
        self.assertIn("State Commission", res_state)

    def test_tools_draft_legal_document(self):
        """Test legal document drafting tool."""
        res = draft_legal_document.invoke({
            "document_type": "rent_deposit_notice",
            "complainant_name": "Amit Sharma",
            "opposite_party": "Rajesh Gupta",
            "facts": "Unreturned rental deposit of Rs 75,000 despite vacating on Jan 31.",
            "amount": "Rs 75,000",
            "jurisdiction": "Bengaluru, Karnataka"
        })
        self.assertIn("LEGAL NOTICE", res)
        self.assertIn("Amit Sharma", res)
        self.assertIn("Rajesh Gupta", res)
        self.assertIn("75,000", res)
        self.assertTrue("15" in res and "DAYS" in res.upper())

    def test_emergency_bypass_router(self):
        """Test emergency bypass in router for urgent situations."""
        router = LegalIntentRouter()
        
        # Arrest emergency
        res_arrest = router.classify("The police are at my door threatening to arrest me right now!")
        self.assertTrue(res_arrest.get("emergency_bypass"))
        self.assertEqual(res_arrest.get("emergency_type"), "arrest")

        # Cyber fraud emergency
        res_cyber = router.classify("I was just scammed 50000 rupees from my bank account 10 minutes ago!")
        self.assertTrue(res_cyber.get("emergency_bypass"))
        self.assertEqual(res_cyber.get("emergency_type"), "cyber_fraud")

    def test_citizen_memory_and_isolation(self):
        """Test citizen memory storage and per-user isolation."""
        mem1 = CitizenLegalMemory(user_id="user_alpha")
        mem1.set_active_dispute(
            category="tenancy",
            opposing_party="Landlord Sharma",
            claim_amount=50000,
            incident_date="2024-02-01",
            jurisdiction="Bengaluru, Karnataka"
        )
        mem1.add_timeline_event("2024-02-01", "Vacated flat and requested deposit return")
        mem1.add_evidence("Rent Agreement dated 2023-01-01")

        summary = mem1.get_case_summary_text()
        self.assertIn("tenancy", summary)
        self.assertIn("50,000", summary)
        self.assertIn("Landlord Sharma", summary)

        # Check another user has isolated state
        mem2 = CitizenLegalMemory(user_id="user_beta")
        summary2 = mem2.get_case_summary_text()
        self.assertNotIn("Landlord Sharma", summary2)


if __name__ == "__main__":
    unittest.main()
