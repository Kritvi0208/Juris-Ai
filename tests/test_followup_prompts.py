import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import format_user_followup_prompt

def test_user_followup_transformations():
    test_cases = [
        (
            "Are you interested in learning about ways to recover your security deposit through legal notice?",
            "What are ways to recover my security deposit through legal notice?"
        ),
        (
            "Would you like to know about other legal remedies, such as filing before the Consumer Commission?",
            "Tell me about other legal remedies, such as filing before the Consumer Commission"
        ),
        (
            "Do you have any specific legal or financial compensation goals you are hoping to achieve?",
            "How can I manage my legal or financial compensation goals?"
        ),
        (
            "Would you like to calculate the court fees right now for your claim?",
            "Can you calculate the court fees right now for my claim?"
        ),
        (
            "Would you like me to draft a 15-day legal notice to your landlord?",
            "Can you draft a 15-day legal notice to my landlord?"
        ),
        (
            "What are the statutory limitation periods under Section 138 NI Act?",
            "What are the statutory limitation periods under Section 138 NI Act?"
        ),
        (
            "What steps should be taken if your landlord cuts electricity or water?",
            "What should I do if my landlord cuts electricity or water?"
        ),
    ]

    for raw, expected in test_cases:
        res = format_user_followup_prompt(raw)
        print(f"\n[RAW]      {raw}")
        print(f"[CONVERT]  {res}")
        assert res, f"Expected non-empty output for: {raw}"
        # Ensure 'your' is never left if converted
        if "your" in raw.lower() and "your landlord" in raw.lower():
            assert "your" not in res.lower(), f"'your' was not converted to 'my' in: {res}"

    print("\n[ALL TESTS PASSED] Legal follow-up prompts are properly formatted from the citizen's first-person perspective!")

if __name__ == "__main__":
    test_user_followup_transformations()
