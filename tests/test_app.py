import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1]))

from app import assess_payload


class AssessPayloadTests(unittest.TestCase):
    def test_complete_synthetic_claim_returns_approved_decision(self):
        decision = assess_payload(
            {
                "policy_number": "SYN-UI-1001",
                "claim_type": "life",
                "amount": "250000.00",
                "months_active": 24,
                "documents": ["death_certificate", "identity_document"],
            }
        )

        self.assertEqual(
            {
                "status": "approved",
                "approved_amount": "250000.00",
                "reasons": [],
            },
            decision,
        )

    def test_invalid_browser_payload_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Invalid claim payload"):
            assess_payload(
                {
                    "policy_number": "SYN-UI-1002",
                    "claim_type": "life",
                    "amount": "not-an-amount",
                    "months_active": 12,
                    "documents": [],
                }
            )


if __name__ == "__main__":
    unittest.main()